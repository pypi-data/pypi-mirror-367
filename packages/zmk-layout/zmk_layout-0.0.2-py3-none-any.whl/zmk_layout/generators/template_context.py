"""Template processing service for layout data."""

import re
from typing import TYPE_CHECKING, Any, Literal, TypeAlias


if TYPE_CHECKING:
    pass

from typing import Protocol

from zmk_layout.models import LayoutData
from zmk_layout.providers import LayoutProviders


# Type aliases for better readability
TemplateContext: TypeAlias = dict[str, Any]
ResolutionStage: TypeAlias = Literal["basic", "behaviors", "layers", "custom"]


class TemplateError(Exception):
    """Base exception for template processing errors."""


class CircularReferenceError(TemplateError):
    """Exception raised when circular template dependencies are detected."""


class TemplateServiceProtocol(Protocol):
    """Protocol for template service capabilities."""

    def process_layout_data(self, layout_data: LayoutData) -> LayoutData:
        """Process layout data with template resolution."""
        ...

    def validate_template_syntax(self, layout_data: LayoutData) -> list[str]:
        """Validate template syntax in layout data."""
        ...


class TemplateService:
    """Service for processing Jinja2 templates in layout data.

    This service handles multi-pass template resolution to properly handle
    complex nested template dependencies in layout data structures.
    """

    def __init__(self, providers: LayoutProviders) -> None:
        """Initialize template service with provider injection.

        Args:
            providers: Layout providers for configuration, template, logger, and file operations
        """
        self.providers = providers
        self._resolution_cache: dict[str, Any] = {}

    def log_error_with_context(
        self,
        message: str,
        error: Exception,
        **context: Any,
    ) -> None:
        """Override to use provider logger instead of base service logger."""
        self.providers.logger.error(
            message, error=str(error), error_type=type(error).__name__, **context
        )

    def process_layout_data(self, layout_data: LayoutData) -> LayoutData:
        """Process layout data with multi-pass template resolution.

        Args:
            layout_data: The layout data containing template expressions

        Returns:
            Processed layout data with all templates resolved

        Raises:
            TemplateError: If template processing fails
            CircularReferenceError: If circular dependencies are detected
        """
        try:
            self.providers.logger.debug(
                "starting_multipass_template_resolution",
                operation="process_layout_data",
            )
            self._resolution_cache.clear()

            # Convert to dict for processing
            data = layout_data.model_dump(mode="json", by_alias=True)

            # Skip processing if no variables or templates
            if not self._has_templates(data):
                self.providers.logger.debug(
                    "no_templates_found",
                    operation="process_layout_data",
                    action="skipping",
                )
                return layout_data

            # Multi-pass resolution
            data = self._resolve_basic_fields(data)
            data = self._resolve_behaviors(data)
            data = self._resolve_layers(data)
            data = self._resolve_custom_code(data)

            # Create new LayoutData instance with resolved data
            resolved_layout = LayoutData.model_validate(data)

            self.providers.logger.debug(
                "template_resolution_completed",
                operation="process_layout_data",
                result="success",
            )
            return resolved_layout

        except Exception as e:
            self.log_error_with_context(
                "template_processing_failed", e, operation="process_layout_data"
            )
            raise TemplateError(f"Template processing failed: {e}") from e

    def create_template_context(
        self, layout_data: LayoutData, stage: str
    ) -> TemplateContext:
        """Create template context for given resolution stage.

        Args:
            layout_data: The layout data to create context from
            stage: Resolution stage ('basic', 'behaviors', 'layers', 'custom')

        Returns:
            Template context dictionary for Jinja2 rendering
        """
        # Convert to dict for internal processing
        data = layout_data.model_dump(mode="json", by_alias=True)
        return self._create_template_context_from_dict(data, stage)

    def _create_template_context_from_dict(
        self, layout_data: dict[str, Any], stage: str
    ) -> TemplateContext:
        """Create template context from dict data for given resolution stage."""
        # Base context always available
        context: TemplateContext = {
            "variables": layout_data.get("variables", {}),
            "keyboard": layout_data.get("keyboard", ""),
            "title": layout_data.get("title", ""),
            "layer_names": layout_data.get("layer_names", []),
        }

        # Add optional metadata fields only if they exist and are not empty/default values
        optional_fields = ["creator", "uuid", "tags", "config_parameters"]
        for field in optional_fields:
            if field in layout_data and layout_data[field]:
                context[field] = layout_data[field]

        # Handle version only if it's not the default "1.0.0"
        if (
            "version" in layout_data
            and layout_data["version"]
            and layout_data["version"] != "1.0.0"
        ):
            context["version"] = layout_data["version"]

        # Handle date only if it's explicitly set (not auto-generated current time)
        # We'll include it if it's in the original data and seems to be a specific timestamp
        if "date" in layout_data and layout_data["date"]:
            # Only include if it's not a very recent timestamp (indicating it was set intentionally)
            import time

            current_time = time.time()
            if isinstance(layout_data["date"], int | float):
                # If the date is more than 1 minute old, assume it was set intentionally
                if abs(current_time - layout_data["date"]) > 60:
                    context["date"] = layout_data["date"]
            else:
                # Non-numeric date, include it
                context["date"] = layout_data["date"]

        # Add layer utilities
        layer_names = context["layer_names"]
        context["layer_name_to_index"] = {
            name: idx for idx, name in enumerate(layer_names)
        }
        context["get_layer_index"] = lambda name: context["layer_name_to_index"].get(
            name, -1
        )

        # Add stage-specific context
        if stage in ("behaviors", "layers", "custom"):
            # Add resolved behaviors from cache
            context.update(
                {
                    "holdTaps": self._resolution_cache.get("holdTaps", []),
                    "combos": self._resolution_cache.get("combos", []),
                    "macros": self._resolution_cache.get("macros", []),
                }
            )

        if stage in ("layers", "custom"):
            # Add layer content utilities
            layers_by_name = self._resolution_cache.get("layers_by_name", {})
            context.update(
                {
                    "layers_by_name": layers_by_name,
                    "get_layer_bindings": lambda name: layers_by_name.get(name, []),
                }
            )

        return context

    def validate_template_syntax(self, layout_data: LayoutData) -> list[str]:
        """Validate all template syntax in layout data.

        Args:
            layout_data: The layout data to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: list[str] = []
        data = layout_data.model_dump(mode="json", by_alias=True)

        try:
            self._validate_templates_in_structure(data, "", errors)
        except Exception as e:
            self.log_error_with_context(
                "template_validation_failed", e, operation="validate_template_syntax"
            )
            errors.append(f"Validation error: {e}")

        return errors

    def process_raw_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process templates directly on raw dictionary data.

        This method is used when we need to process templates before model validation.

        Args:
            data: Raw dictionary data containing templates

        Returns:
            Dictionary with resolved templates

        Raises:
            TemplateError: If template processing fails
        """
        return self._process_raw_data(data)

    def _process_raw_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process templates directly on raw dictionary data.

        This method is used when we need to process templates before model validation.

        Args:
            data: Raw dictionary data containing templates

        Returns:
            Dictionary with resolved templates

        Raises:
            TemplateError: If template processing fails
        """
        try:
            self.providers.logger.debug(
                "processing_templates_raw_data", operation="process_raw_data"
            )
            self._resolution_cache.clear()

            # Skip processing if no variables or templates
            if not self._has_templates(data):
                self.providers.logger.debug(
                    "no_templates_found",
                    operation="process_raw_data",
                    action="skipping",
                )
                return data

            # Create a copy to avoid modifying the original
            processed_data = data.copy()

            # Multi-pass resolution on raw data
            processed_data = self._resolve_basic_fields(processed_data)
            processed_data = self._resolve_behaviors(processed_data)
            processed_data = self._resolve_layers(processed_data)
            processed_data = self._resolve_custom_code(processed_data)

            self.providers.logger.debug(
                "raw_data_template_resolution_completed",
                operation="process_raw_data",
                result="success",
            )
            return processed_data

        except Exception as e:
            self.log_error_with_context(
                "raw_data_template_processing_failed", e, operation="process_raw_data"
            )
            raise TemplateError(f"Raw data template processing failed: {e}") from e

    def _has_templates(self, data: dict[str, Any]) -> bool:
        """Check if data contains any Jinja2 template syntax."""
        return self._scan_for_templates(data)

    def _scan_for_templates(self, obj: Any) -> bool:
        """Recursively scan object for Jinja2 template syntax."""
        if isinstance(obj, str):
            return bool(re.search(r"\{\{|\{%|\{#", obj))
        elif isinstance(obj, dict):
            return any(self._scan_for_templates(v) for v in obj.values())
        elif isinstance(obj, list):
            return any(self._scan_for_templates(item) for item in obj)
        return False

    def _resolve_basic_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """Resolve basic metadata fields that don't reference complex structures."""
        self.providers.logger.debug(
            "resolving_basic_fields", operation="resolve_basic_fields"
        )
        context = self._create_template_context_from_dict(data, "basic")

        # Process basic metadata fields
        basic_fields = ["title", "notes", "creator", "tags", "layer_names"]
        for field in basic_fields:
            if field in data:
                data[field] = self._process_field_value(data[field], context)

        return data

    def _resolve_behaviors(self, data: dict[str, Any]) -> dict[str, Any]:
        """Resolve behavior definitions with enriched context."""
        self.providers.logger.debug(
            "resolving_behavior_definitions", operation="resolve_behaviors"
        )
        context = self._create_template_context_from_dict(data, "behaviors")

        # Process behavior arrays
        behavior_fields = ["holdTaps", "combos", "macros"]
        for field in behavior_fields:
            if field in data and data[field]:
                processed = self._process_field_value(data[field], context)
                data[field] = processed
                self._resolution_cache[field] = processed

        return data

    def _resolve_layers(self, data: dict[str, Any]) -> dict[str, Any]:
        """Resolve layer content with full behavior context."""
        self.providers.logger.debug(
            "resolving_layer_content", operation="resolve_layers"
        )
        context = self._create_template_context_from_dict(data, "layers")

        # Process layers
        if "layers" in data and data["layers"]:
            processed_layers = self._process_field_value(data["layers"], context)
            data["layers"] = processed_layers

            # Cache layers by name for context building
            layer_names = data.get("layer_names", [])
            if len(layer_names) == len(processed_layers):
                layers_by_name = dict(zip(layer_names, processed_layers, strict=False))
                self._resolution_cache["layers_by_name"] = layers_by_name

        return data

    def _resolve_custom_code(self, data: dict[str, Any]) -> dict[str, Any]:
        """Resolve custom DTSI/behavior code with full layout context."""
        self.providers.logger.debug(
            "resolving_custom_code", operation="resolve_custom_code"
        )
        context = self._create_template_context_from_dict(data, "custom")

        # Process custom code fields
        custom_fields = ["custom_defined_behaviors", "custom_devicetree"]
        for field in custom_fields:
            if field in data:
                data[field] = self._process_field_value(data[field], context)

        return data

    def _process_field_value(self, value: Any, context: TemplateContext) -> Any:
        """Process a field value, applying templates where found."""
        if isinstance(value, str):
            return self._process_string_field(value, context)
        elif isinstance(value, dict):
            return {k: self._process_field_value(v, context) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._process_field_value(item, context) for item in value]
        else:
            return value

    def _process_string_field(self, value: str, context: TemplateContext) -> Any:
        """Process string field with potential template conversion."""
        if not re.search(r"\{\{|\{%|\{#", value):
            return value

        try:
            rendered = self.providers.template.render_string(value, context)
            return self._convert_to_appropriate_type(rendered)
        except Exception as e:
            self.log_error_with_context(
                "template_rendering_failed",
                e,
                operation="process_string_field",
                template_preview=value[:50],
            )
            raise TemplateError(f"Template rendering failed: {e}") from e

    def _convert_to_appropriate_type(self, value: str) -> Any:
        """Convert string value to appropriate type (int, bool, float, str)."""
        # Try bool conversion first (before int conversion to handle "1" and "0" as booleans)
        lower_value = value.lower()
        if lower_value in ("true", "yes", "1"):
            return True
        elif lower_value in ("false", "no", "0"):
            return False

        # Try int conversion
        try:
            return int(value)
        except ValueError:
            pass

        # Try float conversion
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _validate_templates_in_structure(
        self, obj: Any, path: str, errors: list[str]
    ) -> None:
        """Recursively validate template syntax in data structure."""
        if isinstance(obj, str):
            if re.search(r"\{\{|\{%|\{#", obj):
                # For string template validation, try to render with empty context
                try:
                    # Try to parse template syntax by attempting to render
                    self.providers.template.render_string(obj, {})
                    # If no exception, template syntax is valid
                except Exception:
                    # Template syntax is invalid
                    errors.append(f"Invalid template syntax at {path}: {obj[:50]}")
        elif isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                self._validate_templates_in_structure(value, new_path, errors)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                self._validate_templates_in_structure(item, new_path, errors)


def create_template_service(
    providers: LayoutProviders,
) -> TemplateServiceProtocol:
    """Create a TemplateService instance with provider injection.

    Args:
        providers: Layout providers for configuration, template, logger, and file operations

    Returns:
        TemplateService instance implementing TemplateServiceProtocol

    Use create_glovebox_providers() to create the required providers:
    - create_glovebox_providers(profile, file_adapter, template_adapter, logger_name)
    """
    return TemplateService(providers)


def create_jinja2_template_service() -> TemplateServiceProtocol:
    """Create a TemplateService instance with default template adapter.

    This factory function creates the template adapter dependency and
    provides a convenient way to create a template service with defaults.

    Returns:
        TemplateService instance with default TemplateAdapter
    """
    # Use the default providers from the factory
    from zmk_layout.providers.factory import create_default_providers

    providers = create_default_providers()

    return create_template_service(providers)
