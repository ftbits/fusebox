from typing import Protocol

import pytest

from fusebox.container import Container


class ServiceA:
  def __init__(self) -> None:
    self.name = "ServiceA"


class ServiceB:
  def __init__(self, service_a: ServiceA) -> None:
    self.service_a = service_a


class AbstractService(Protocol):
  def greet(self) -> str: ...


class ImplService(AbstractService):
  def greet(self) -> str:
    return "Hello from ImplService"


class MissingTypeHint:
  def __init__(self, dep):
    self.dep = dep


@pytest.fixture(autouse=True)
def reset_container():
  """Automatically clear the container state before each test."""
  Container._registrations.clear()
  Container._instances.clear()


def test_register_and_get_self():
  Container.register(ServiceA)
  instance = Container.get(ServiceA)
  assert isinstance(instance, ServiceA)


def test_singleton_behavior():
  Container.register(ServiceA)
  instance1 = Container.get(ServiceA)
  instance2 = Container.get(ServiceA)
  assert instance1 is instance2


def test_dependency_injection():
  Container.register(ServiceA)
  Container.register(ServiceB)
  service_b = Container.get(ServiceB)
  assert isinstance(service_b, ServiceB)
  assert isinstance(service_b.service_a, ServiceA)


def test_interface_to_implementation():
  Container.register(AbstractService, ImplService)
  service = Container.get(AbstractService)
  assert isinstance(service, ImplService)
  assert service.greet() == "Hello from ImplService"


def test_error_on_missing_type_hint():
  Container.register(ServiceA)
  Container.register(MissingTypeHint)
  with pytest.raises(ValueError, match="Type hint required for parameter"):
    Container.get(MissingTypeHint)


def test_inject_decorator_simple():
  from fusebox.decorators import inject

  Container.register(ServiceA)

  @inject
  def func(a: ServiceA):
    return a

  result = func()
  assert isinstance(result, ServiceA)


def test_inject_decorator_with_args():
  from fusebox.decorators import inject

  Container.register(ServiceA)
  Container.register(ServiceB)

  @inject
  def func(a: ServiceA, b: ServiceB):
    return (a, b)

  a, b = func()
  assert isinstance(a, ServiceA)
  assert isinstance(b, ServiceB)
  assert b.service_a is a


def test_inject_decorator_with_override():
  from fusebox.decorators import inject

  Container.register(ServiceA)

  @inject
  def func(a: ServiceA):
    return a

  custom = ServiceA()
  result = func(a=custom)
  assert result is custom


def test_inject_decorator_type_hint_required():
  from fusebox.decorators import inject

  @inject
  def func(a):
    return a

  with pytest.raises(ValueError, match="Type hint required for parameter"):
    func()
