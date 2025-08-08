# src/adnus/main.py
"""
adnus (AdNuS): A Python library for Advanced Number Systems.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from fractions import Fraction
import math
from typing import List, Union, Generator, Tuple

class AdvancedNumber(ABC):
    """Abstract Base Class for advanced number systems."""

    @abstractmethod
    def __add__(self, other):
        pass

    @abstractmethod
    def __sub__(self, other):
        pass

    @abstractmethod
    def __mul__(self, other):
        pass

    @abstractmethod
    def __truediv__(self, other):
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


@dataclass(frozen=True)
class BicomplexNumber(AdvancedNumber):
    """
    Represents a bicomplex number z = z1 + z2j, where z1 and z2 are complex
    numbers and j^2 = -1, but j is an independent imaginary unit from i.
    """
    z1: complex
    z2: complex

    def __add__(self, other: BicomplexNumber) -> BicomplexNumber:
        if not isinstance(other, BicomplexNumber):
            return NotImplemented
        return BicomplexNumber(self.z1 + other.z1, self.z2 + other.z2)

    def __sub__(self, other: BicomplexNumber) -> BicomplexNumber:
        if not isinstance(other, BicomplexNumber):
            return NotImplemented
        return BicomplexNumber(self.z1 - other.z1, self.z2 - other.z2)

    def __mul__(self, other: Union[BicomplexNumber, float, int, complex]) -> BicomplexNumber:
        if isinstance(other, (float, int, complex)):
            return BicomplexNumber(self.z1 * other, self.z2 * other)
        if not isinstance(other, BicomplexNumber):
            return NotImplemented
        # (z1 + z2j)(w1 + w2j) = (z1w1 - z2w2) + (z1w2 + z2w1)j
        return BicomplexNumber(
            self.z1 * other.z1 - self.z2 * other.z2,
            self.z1 * other.z2 + self.z2 * other.z1
        )

    def __truediv__(self, other: BicomplexNumber) -> BicomplexNumber:
        # Division is more complex and requires the inverse.
        # For simplicity, this is left as an exercise. A common method involves
        # multiplying by the conjugate and dividing by the squared modulus.
        raise NotImplementedError("Division for bicomplex numbers is not implemented.")

    def __eq__(self, other) -> bool:
        if not isinstance(other, BicomplexNumber):
            return NotImplemented
        return self.z1 == other.z1 and self.z2 == other.z2

    def __repr__(self) -> str:
        return f"({self.z1}) + ({self.z2})j"

    def norm(self) -> float:
        """Returns the Euclidean norm of the bicomplex number."""
        return math.sqrt(abs(self.z1)**2 + abs(self.z2)**2)


@dataclass(frozen=True)
class NeutrosophicNumber(AdvancedNumber):
    """
    Represents a neutrosophic number z = a + bI, where 'a' is the determinate part,
    'b' is the indeterminate part, and I is the indeterminacy, satisfying I^2 = I.
    """
    a: float
    b: float

    def __add__(self, other: NeutrosophicNumber) -> NeutrosophicNumber:
        if not isinstance(other, NeutrosophicNumber):
            return NotImplemented
        return NeutrosophicNumber(self.a + other.a, self.b + other.b)

    def __sub__(self, other: NeutrosophicNumber) -> NeutrosophicNumber:
        if not isinstance(other, NeutrosophicNumber):
            return NotImplemented
        return NeutrosophicNumber(self.a - other.a, self.b - other.b)

    def __mul__(self, other: NeutrosophicNumber) -> NeutrosophicNumber:
        if not isinstance(other, NeutrosophicNumber):
            return NotImplemented
        # (a + bI)(c + dI) = ac + (ad + bc + bd)I
        return NeutrosophicNumber(
            self.a * other.a,
            self.a * other.b + self.b * other.a + self.b * other.b
        )

    def __truediv__(self, other: NeutrosophicNumber) -> NeutrosophicNumber:
        # Division is not uniquely defined without further constraints.
        raise NotImplementedError("Division for neutrosophic numbers is not implemented.")

    def __eq__(self, other) -> bool:
        if not isinstance(other, NeutrosophicNumber):
            return NotImplemented
        return self.a == other.a and self.b == other.b

    def __repr__(self) -> str:
        return f"{self.a} + {self.b}I"


@dataclass(frozen=True)
class NeutrosophicComplexNumber(AdvancedNumber):
    """
    Represents a neutrosophic complex number z = (a + bi) + (c + di)I.
    This can be seen as a neutrosophic number whose determinate and indeterminate
    parts are complex numbers.
    """
    determinate: complex
    indeterminate: complex

    def __add__(self, other: NeutrosophicComplexNumber) -> NeutrosophicComplexNumber:
        if not isinstance(other, NeutrosophicComplexNumber):
            return NotImplemented
        return NeutrosophicComplexNumber(
            self.determinate + other.determinate,
            self.indeterminate + other.indeterminate
        )

    def __sub__(self, other: NeutrosophicComplexNumber) -> NeutrosophicComplexNumber:
        if not isinstance(other, NeutrosophicComplexNumber):
            return NotImplemented
        return NeutrosophicComplexNumber(
            self.determinate - other.determinate,
            self.indeterminate - other.indeterminate
        )

    def __mul__(self, other: NeutrosophicComplexNumber) -> NeutrosophicComplexNumber:
        if not isinstance(other, NeutrosophicComplexNumber):
            return NotImplemented
        # (A + BI)(C + DI) = AC + (AD + BC + BD)I, where A, B, C, D are complex.
        determinate_part = self.determinate * other.determinate
        indeterminate_part = (self.determinate * other.indeterminate +
                              self.indeterminate * other.determinate +
                              self.indeterminate * other.indeterminate)
        return NeutrosophicComplexNumber(determinate_part, indeterminate_part)

    def __truediv__(self, other: NeutrosophicComplexNumber) -> NeutrosophicComplexNumber:
        raise NotImplementedError("Division for neutrosophic complex numbers is not implemented.")

    def __eq__(self, other) -> bool:
        if not isinstance(other, NeutrosophicComplexNumber):
            return NotImplemented
        return self.determinate == other.determinate and self.indeterminate == other.indeterminate

    def __repr__(self) -> str:
        return f"({self.determinate}) + ({self.indeterminate})I"


@dataclass(frozen=True)
class NeutrosophicBicomplexNumber(AdvancedNumber):
    """
    Represents a neutrosophic bicomplex number z = (z1 + z2j) + (w1 + w2j)I.
    This can be seen as a neutrosophic number whose determinate and indeterminate
    parts are bicomplex numbers.
    """
    determinate: BicomplexNumber
    indeterminate: BicomplexNumber

    def __add__(self, other: NeutrosophicBicomplexNumber) -> NeutrosophicBicomplexNumber:
        if not isinstance(other, NeutrosophicBicomplexNumber):
            return NotImplemented
        return NeutrosophicBicomplexNumber(
            self.determinate + other.determinate,
            self.indeterminate + other.indeterminate
        )

    def __sub__(self, other: NeutrosophicBicomplexNumber) -> NeutrosophicBicomplexNumber:
        if not isinstance(other, NeutrosophicBicomplexNumber):
            return NotImplemented
        return NeutrosophicBicomplexNumber(
            self.determinate - other.determinate,
            self.indeterminate - other.indeterminate
        )

    def __mul__(self, other: NeutrosophicBicomplexNumber) -> NeutrosophicBicomplexNumber:
        if not isinstance(other, NeutrosophicBicomplexNumber):
            return NotImplemented
        # (A + BI)(C + DI) = AC + (AD + BC + BD)I, where A, B, C, D are bicomplex.
        determinate_part = self.determinate * other.determinate
        indeterminate_part = (self.determinate * other.indeterminate +
                              self.indeterminate * other.determinate +
                              self.indeterminate * other.indeterminate)
        return NeutrosophicBicomplexNumber(determinate_part, indeterminate_part)

    def __truediv__(self, other: NeutrosophicBicomplexNumber) -> NeutrosophicBicomplexNumber:
        raise NotImplementedError("Division for neutrosophic bicomplex numbers is not implemented.")

    def __eq__(self, other) -> bool:
        if not isinstance(other, NeutrosophicBicomplexNumber):
            return NotImplemented
        return self.determinate == other.determinate and self.indeterminate == other.indeterminate

    def __repr__(self) -> str:
        return f"({self.determinate}) + ({self.indeterminate})I"


@dataclass(frozen=True)
class HyperrealNumber(AdvancedNumber):
    """
    Represents a hyperreal number as a sequence of real numbers.
    Note: This is a conceptual implementation. A full implementation requires
    a non-principal ultrafilter, which is non-constructive.
    """
    sequence_func: callable

    def __post_init__(self):
        if not callable(self.sequence_func):
            raise TypeError("sequence_func must be a callable function.")

    def __add__(self, other: HyperrealNumber) -> HyperrealNumber:
        if not isinstance(other, HyperrealNumber):
            return NotImplemented
        return HyperrealNumber(lambda n: self.sequence_func(n) + other.sequence_func(n))

    def __sub__(self, other: HyperrealNumber) -> HyperrealNumber:
        if not isinstance(other, HyperrealNumber):
            return NotImplemented
        return HyperrealNumber(lambda n: self.sequence_func(n) - other.sequence_func(n))

    def __mul__(self, other: HyperrealNumber) -> HyperrealNumber:
        if not isinstance(other, HyperrealNumber):
            return NotImplemented
        return HyperrealNumber(lambda n: self.sequence_func(n) * other.sequence_func(n))

    def __truediv__(self, other: HyperrealNumber) -> HyperrealNumber:
        # Avoid division by zero in the sequence
        def div_func(n):
            denominator = other.sequence_func(n)
            if denominator == 0:
                # This case needs a more rigorous definition based on the ultrafilter.
                # For simplicity, we return 0, but this is not generally correct.
                return 0
            return self.sequence_func(n) / denominator
        return HyperrealNumber(div_func)

    def __eq__(self, other) -> bool:
        # Equality for hyperreals means the set of indices where sequences are equal
        # belongs to the ultrafilter. This cannot be implemented directly.
        raise NotImplementedError("Equality for hyperreal numbers cannot be determined constructively.")

    def __repr__(self) -> str:
        return f"Hyperreal(sequence: {self.sequence_func(1)}, {self.sequence_func(2)}, ...)"


# =============================================
# Helper Functions
# =============================================

def oresme_sequence(n_terms: int) -> List[float]:
    """Generates the first n terms of the Oresme sequence (n / 2^n)."""
    if n_terms <= 0:
        return []
    return [n / (2 ** n) for n in range(1, n_terms + 1)]


def harmonic_numbers(n_terms: int) -> Generator[Fraction, None, None]:
    """
    Generates the first n harmonic numbers (H_n = 1 + 1/2 + ... + 1/n)
    as exact fractions.
    """
    if n_terms <= 0:
        return
    current_sum = Fraction(0)
    for i in range(1, n_terms + 1):
        current_sum += Fraction(1, i)
        yield current_sum


def binet_formula(n: int) -> float:
    """Calculates the nth Fibonacci number using Binet's formula."""
    if n < 0:
        raise ValueError("The Fibonacci sequence is not defined for negative integers.")
    sqrt5 = math.sqrt(5)
    phi = (1 + sqrt5) / 2
    return (phi**n - (1 - phi)**n) / sqrt5
