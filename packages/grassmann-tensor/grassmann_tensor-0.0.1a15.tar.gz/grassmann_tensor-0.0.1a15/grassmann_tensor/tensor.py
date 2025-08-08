"""
A Grassmann tensor class.
"""

from __future__ import annotations

__all__ = ["GrassmannTensor"]

import dataclasses
import functools
import typing
import torch


@dataclasses.dataclass
class GrassmannTensor:
    """
    A Grassmann tensor class, which stores a tensor along with information about its edges.
    Each dimension of the tensor is composed of an even and an odd part, represented as a pair of integers.
    """

    _arrow: tuple[bool, ...]
    _edges: tuple[tuple[int, int], ...]
    _tensor: torch.Tensor
    _parity: tuple[torch.Tensor, ...] | None = None
    _mask: torch.Tensor | None = None

    @property
    def arrow(self) -> tuple[bool, ...]:
        """
        The arrow of the tensor, represented as a tuple of booleans indicating the order of the fermion operators.
        """
        return self._arrow

    @property
    def edges(self) -> tuple[tuple[int, int], ...]:
        """
        The edges of the tensor, represented as a tuple of pairs (even, odd).
        """
        return self._edges

    @property
    def tensor(self) -> torch.Tensor:
        """
        The underlying tensor data.
        """
        return self._tensor

    @property
    def parity(self) -> tuple[torch.Tensor, ...]:
        """
        The parity of each edge, represented as a tuple of tensors.
        """
        if self._parity is None:
            self._parity = tuple(self._edge_mask(even, odd) for (even, odd) in self._edges)
        return self._parity

    @property
    def mask(self) -> torch.Tensor:
        """
        The mask of the tensor, which has the same shape as the tensor and indicates which elements could be non-zero based on the parity.
        """
        if self._mask is None:
            self._mask = self._tensor_mask()
        return self._mask

    def to(self, whatever: torch.device | torch.dtype | str | None = None, *, device: torch.device | None = None, dtype: torch.dtype | None = None) -> GrassmannTensor:
        """
        Copy the tensor to a specified device or copy it to a specified data type.
        """
        if whatever is None:
            pass
        elif isinstance(whatever, torch.device):
            assert device is None, "Duplicate device specification."
            device = whatever
        elif isinstance(whatever, torch.dtype):
            assert dtype is None, "Duplicate dtype specification."
            dtype = whatever
        elif isinstance(whatever, str):
            assert device is None, "Duplicate device specification."
            device = torch.device(whatever)
        else:
            raise TypeError(f"Unsupported type for 'to': {type(whatever)}. Expected torch.device, torch.dtype, or str.")
        match (device, dtype):
            case (None, None):
                return self
            case (None, _):
                return dataclasses.replace(
                    self,
                    _tensor=self._tensor.to(dtype=dtype),
                )
            case (_, None):
                return dataclasses.replace(
                    self,
                    _tensor=self._tensor.to(device=device),
                    _parity=tuple(p.to(device) for p in self._parity) if self._parity is not None else None,
                    _mask=self._mask.to(device) if self._mask is not None else None,
                )
            case _:
                return dataclasses.replace(
                    self,
                    _tensor=self._tensor.to(device=device, dtype=dtype),
                    _parity=tuple(p.to(device=device) for p in self._parity) if self._parity is not None else None,
                    _mask=self._mask.to(device=device) if self._mask is not None else None,
                )

    def update_mask(self) -> GrassmannTensor:
        """
        Update the mask of the tensor based on its parity.
        """
        self._tensor = torch.where(self.mask, 0, self._tensor)
        return self

    def permute(self, before_by_after: tuple[int, ...]) -> GrassmannTensor:
        """
        Permute the indices of the Grassmann tensor.
        """
        assert set(before_by_after) == set(range(self.tensor.dim())), "Permutation indices must cover all dimensions."

        arrow = tuple(self.arrow[i] for i in before_by_after)
        edges = tuple(self.edges[i] for i in before_by_after)
        tensor = self.tensor.permute(before_by_after)
        parity = tuple(self.parity[i] for i in before_by_after)
        mask = self.mask.permute(before_by_after)

        total_parity = functools.reduce(
            torch.logical_xor,
            (
                torch.logical_and(self._unsqueeze(parity[i], i, self.tensor.dim()), self._unsqueeze(parity[j], j, self.tensor.dim()))
                for j in range(self.tensor.dim())
                for i in range(0, j)  # all 0 <= i < j < dim
                if before_by_after[i] > before_by_after[j]),
            torch.zeros([], dtype=torch.bool, device=self.tensor.device),
        )
        tensor = torch.where(total_parity, -tensor, +tensor)

        return dataclasses.replace(
            self,
            _arrow=arrow,
            _edges=edges,
            _tensor=tensor,
            _parity=parity,
            _mask=mask,
        )

    def reverse(self, indices: tuple[int, ...]) -> GrassmannTensor:
        """
        Reverse the specified indices of the Grassmann tensor.

        A single sign is generated during reverse, which should be applied to one of the connected two tensors.
        This package always applies it to the tensor with arrow as True.
        """
        assert len(set(indices)) == len(indices), f"Indices must be unique. Got {indices}."
        assert all(0 <= i < self.tensor.dim() for i in indices), f"Indices must be within tensor dimensions. Got {indices}."

        arrow = tuple(self.arrow[i] ^ i in indices for i in range(self.tensor.dim()))
        tensor = self.tensor

        total_parity = functools.reduce(
            torch.logical_xor,
            (self._unsqueeze(parity, index, self.tensor.dim()) for index, parity in enumerate(self.parity) if index in indices and self.arrow[index]),
            torch.zeros([], dtype=torch.bool, device=self.tensor.device),
        )
        tensor = torch.where(total_parity, -tensor, +tensor)

        return dataclasses.replace(
            self,
            _arrow=arrow,
            _tensor=tensor,
        )

    def __post_init__(self) -> None:
        assert len(self._arrow) == self._tensor.dim(), f"Arrow length ({len(self._arrow)}) must match tensor dimensions ({self._tensor.dim()})."
        assert len(self._edges) == self._tensor.dim(), f"Edges length ({len(self._edges)}) must match tensor dimensions ({self._tensor.dim()})."
        for dim, (even, odd) in zip(self._tensor.shape, self._edges):
            assert even >= 0 and odd >= 0 and dim == even + odd, f"Dimension {dim} must equal sum of even ({even}) and odd ({odd}) parts, and both must be non-negative."

    def _unsqueeze(self, tensor: torch.Tensor, index: int, dim: int) -> torch.Tensor:
        return tensor.view([-1 if i == index else 1 for i in range(dim)])

    def _edge_mask(self, even: int, odd: int) -> torch.Tensor:
        return torch.cat([torch.zeros(even, dtype=torch.bool, device=self.tensor.device), torch.ones(odd, dtype=torch.bool, device=self.tensor.device)])

    def _tensor_mask(self) -> torch.Tensor:
        return functools.reduce(
            torch.logical_xor,
            (self._unsqueeze(parity, index, self._tensor.dim()) for index, parity in enumerate(self.parity)),
            torch.zeros_like(self._tensor, dtype=torch.bool),
        )

    def _validate_edge_compatibility(self, other: GrassmannTensor) -> None:
        """
        Validate that the edges of two ParityTensor instances are compatible for arithmetic operations.
        """
        assert self._arrow == other.arrow, f"Arrows must match for arithmetic operations. Got {self._arrow} and {other.arrow}."
        assert self._edges == other.edges, f"Edges must match for arithmetic operations. Got {self._edges} and {other.edges}."

    def __pos__(self) -> GrassmannTensor:
        return dataclasses.replace(
            self,
            _tensor=+self._tensor,
        )

    def __neg__(self) -> GrassmannTensor:
        return dataclasses.replace(
            self,
            _tensor=-self._tensor,
        )

    def __add__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            return dataclasses.replace(
                self,
                _tensor=self._tensor + other._tensor,
            )
        try:
            result = self._tensor + other
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __radd__(self, other: typing.Any) -> GrassmannTensor:
        try:
            result = other + self._tensor
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __iadd__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            self._tensor += other._tensor
        else:
            self._tensor += other
        return self

    def __sub__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            return dataclasses.replace(
                self,
                _tensor=self._tensor - other._tensor,
            )
        try:
            result = self._tensor - other
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __rsub__(self, other: typing.Any) -> GrassmannTensor:
        try:
            result = other - self._tensor
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __isub__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            self._tensor -= other._tensor
        else:
            self._tensor -= other
        return self

    def __mul__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            return dataclasses.replace(
                self,
                _tensor=self._tensor * other._tensor,
            )
        try:
            result = self._tensor * other
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __rmul__(self, other: typing.Any) -> GrassmannTensor:
        try:
            result = other * self._tensor
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __imul__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            self._tensor *= other._tensor
        else:
            self._tensor *= other
        return self

    def __truediv__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            return dataclasses.replace(
                self,
                _tensor=self._tensor / other._tensor,
            )
        try:
            result = self._tensor / other
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __rtruediv__(self, other: typing.Any) -> GrassmannTensor:
        try:
            result = other / self._tensor
        except TypeError:
            return NotImplemented
        if isinstance(result, torch.Tensor):
            return dataclasses.replace(
                self,
                _tensor=result,
            )
        return NotImplemented

    def __itruediv__(self, other: typing.Any) -> GrassmannTensor:
        if isinstance(other, GrassmannTensor):
            self._validate_edge_compatibility(other)
            self._tensor /= other._tensor
        else:
            self._tensor /= other
        return self
