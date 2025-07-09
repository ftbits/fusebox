import inspect
from abc import ABC
from typing import Callable, Type, TypeVar

from fusebox.container import Container

T = TypeVar("T")


def component(cls: Type[T]) -> Type[T]:
  Container.register(cls)

  for base in cls.__mro__:
    if base is cls:
      continue

    if issubclass(base, ABC) and hasattr(base, "__abstractmethods__"):
      Container.register(base, cls)
      break

  return cls


def inject(func: Callable) -> Callable:
  sig = inspect.signature(func)

  def wrapper(*args, **kwargs):
    bound = sig.bind_partial(*args, **kwargs)

    for name, param in sig.parameters.items():
      if name in bound.arguments:
        continue

      if param.kind in (
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
      ):
        continue

      if param.annotation == inspect.Parameter.empty:
        raise ValueError(
          f"Type hint required for parameter '{name}' in function '{func.__name__}'"
        )

      bound.arguments[name] = Container.get(param.annotation)

    return func(*bound.args, **bound.kwargs)

  return wrapper
