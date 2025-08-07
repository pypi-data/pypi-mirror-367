"""Type definitions for ZMK layout models."""

from typing import TYPE_CHECKING, TypeAlias


if TYPE_CHECKING:
    from .core import LayoutBinding

# Parameter value can be string or integer
ParamValue = str | int

# Type aliases for common parameter types
ConfigValue: TypeAlias = str | int | bool
LayerIndex: TypeAlias = int

# Template-aware numeric type that accepts integers or template strings
TemplateNumeric: TypeAlias = int | str | None

# This type alias improves type safety and makes future changes easier
LayerBindings: TypeAlias = list["LayoutBinding"]
