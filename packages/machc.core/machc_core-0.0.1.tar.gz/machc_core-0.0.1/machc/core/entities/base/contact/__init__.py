"""
Initialization for the `machc.core.entities.base.contact` package.

This module provides access to classes related to contact management, including
unique addressing identifiers and structured address entities. It forms part of
the Machc framework's base entity layer.
"""

from .address import Address
from .address_id import AddressId

__all__ = [
    "Address",
    "AddressId",
]