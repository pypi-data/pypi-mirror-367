"""
This module provides a class to represent elements in a finite field E(Z/pZ).
It overloads standard arithmetic operators (+, -, *, /, **).

Definition of Field E(Z/pZ) for the elliptic curve : y² = x³ + ax + b

The Group operation for the curve are under the Field E(Z/pZ).
The operations like : - Addition       (+)
                      - Multiplication (*)
                      - Subtraction    (-)
                      - Power          (^)
"""

from __future__ import annotations


class FieldElement:
    """Represents an element in a finite field Fp."""

    def __init__(self, num: int, prime: int):
        if not isinstance(num, int) or not isinstance(prime, int):
            raise TypeError("Number and prime must be integers.")

        if prime <= 1:
            raise ValueError("Prime must be greater than 1.")

        self.num = num % prime
        self.prime = prime

    def _normalize(self, other: int | FieldElement) -> FieldElement:
        """Helper function to check type, and convert integer to FieldElement"""
        if isinstance(other, int):
            return FieldElement(other, self.prime)

        if isinstance(other, FieldElement):
            if self.prime == other.prime:
                return other
            else:
                raise TypeError(
                    "Cannot operate on FieldElements from different fields."
                )

        raise TypeError(
            f"Unsupported operand type(s) for FieldElement: '{type(other).__name__}'"
        )

    def __add__(self, other: int | FieldElement) -> FieldElement:
        other = self._normalize(other)
        return FieldElement((self.num + other.num) % self.prime, self.prime)

    def __radd__(self, other: int | FieldElement) -> FieldElement:
        return self + other

    def __sub__(self, other: int | FieldElement) -> FieldElement:
        other = self._normalize(other)
        return FieldElement((self.num - other.num) % self.prime, self.prime)

    def __rsub__(self, other: int | FieldElement) -> FieldElement:
        return self - other

    def __mul__(self, other: int | FieldElement) -> FieldElement:
        other = self._normalize(other)
        return FieldElement((self.num * other.num) % self.prime, self.prime)

    def __rmul__(self, other: int | FieldElement) -> FieldElement:
        return self * other

    def __truediv__(self, other: int | FieldElement) -> FieldElement:
        other = self._normalize(other)

        inv = pow(other.num, -1, self.prime)
        num = (self.num * inv) % self.prime

        return FieldElement(num, self.prime)

    def __rtruediv__(self, other: int | FieldElement) -> FieldElement:
        other = self._normalize(other)
        return other / self

    def __pow__(self, exponent: int) -> FieldElement:
        if not isinstance(exponent, int):
            raise TypeError("Exponent must be an integer.")

        # Fermat's Little Theorem
        exponent = exponent % (self.prime - 1)
        return FieldElement(pow(self.num, exponent, self.prime), self.prime)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FieldElement):
            return NotImplemented

        return self.num == other.num and self.prime == other.prime

    def __neg__(self) -> FieldElement:
        return FieldElement(-self.num, self.prime)

    def __repr__(self) -> str:
        return f"F_{self.prime}({self.num})"
