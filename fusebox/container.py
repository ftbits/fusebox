import inspect
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")

logger = logging.getLogger("uvicorn")


class Container:
  _registrations: Dict[Type[Any], Type[Any]] = {}
  _instances: Dict[Type[Any], Any] = {}

  @classmethod
  def register(
    cls, interface: Type[T], implementation: Optional[Type[T]] = None
  ) -> None:
    if implementation is None:
      implementation = interface

    cls._registrations[interface] = implementation

  @classmethod
  def get(cls, interface: Type[T]) -> T:
    if interface not in cls._instances:
      implementation = cls._registrations.get(interface, interface)
      instance = cls._create_instance(implementation)
      cls._instances[interface] = instance

    return cls._instances[interface]

  @classmethod
  def _create_instance(cls, implementation: Type[Any]) -> Any:
    logger.debug(f"Creating instance of: {implementation}")

    constructor = inspect.signature(implementation.__init__)
    parameters = constructor.parameters
    args: list[Any] = []

    for name, param in list(parameters.items())[1:]:  # Skip `self`
      # Skip *args and **kwargs
      if param.kind in (
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
      ):
        continue

      logger.debug(f"Processing parameter '{name}': annotation={param.annotation}")
      param_type = param.annotation
      logger.debug(f"Resolved '{name}' to actual type: {param_type}")

      if param_type == inspect.Parameter.empty:
        raise ValueError(
          f"Type hint required for parameter '{name}' in {implementation.__name__}"
        )

      dep = cls.get(param_type)
      args.append(dep)

    return implementation(*args)
