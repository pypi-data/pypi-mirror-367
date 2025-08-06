import functools
import inspect
from typing import TypeVar, Callable

from pydantic import BaseModel, TypeAdapter, ValidationError

# Define a generic type variable that is a subclass of BaseModel
T = TypeVar("T", bound=BaseModel)


def validate_inputs(func: Callable) -> Callable:
    """
    A decorator that validates function arguments against their Pydantic type hints.

    This version uses `pydantic.TypeAdapter` to handle complex types like
    `List[BaseModel]`, `Dict[str, BaseModel]`, `Union[BaseModel, None]`, etc.

    Args:
        func: The function to decorate.

    Returns:
        The wrapped function with validation logic.

    Raises:
        ValueError: If Pydantic validation fails for any argument.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param in sig.parameters.items():
            # Skip parameters without a type annotation
            if param.annotation is inspect.Parameter.empty:
                continue

            if param_name in bound_args.arguments:
                data_to_validate = bound_args.arguments[param_name]
                try:
                    # Use TypeAdapter for any type hint. It gracefully handles
                    # BaseModel, List[BaseModel], simple types, etc.
                    adapter = TypeAdapter(param.annotation)

                    # Validate the data and update the argument with the
                    # validated/coerced model instance(s).
                    validated_data = adapter.validate_python(data_to_validate)
                    bound_args.arguments[param_name] = validated_data

                except ValidationError as e:
                    # Re-raise with a user-friendly message
                    raise ValueError(
                        f"Argument '{param_name}' failed validation for type "
                        f"'{param.annotation}':\n{e}"
                    )
                except TypeError:
                    # This can happen if the annotation is not a valid type for TypeAdapter,
                    # like a TypeVar. In such cases, we can safely ignore it.
                    pass

        return func(*bound_args.args, **bound_args.kwargs)

    return wrapper
