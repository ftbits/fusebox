from abc import ABC, abstractmethod

import pytest

from fusebox import Container, component, inject


def setup_function():
  Container._registrations.clear()
  Container._instances.clear()


def test_component_registers_class():
  @component
  class Service:
    pass

  assert Service in Container._registrations
  assert Container._registrations[Service] is Service


def test_component_registers_abc_base():
  class BaseService(ABC):
    @abstractmethod
    def run(self) -> str:
      pass

  @component
  class ConcreteService(BaseService):
    def run(self) -> str:
      return "Running"

  assert ConcreteService in Container._registrations
  assert Container._registrations[BaseService] is ConcreteService

  instance = Container.get(BaseService)
  assert isinstance(instance, ConcreteService)
  assert instance.run() == "Running"


def test_component_with_multiple_inheritance():
  class InterfaceA(ABC):
    @abstractmethod
    def foo(self) -> str:
      pass

  class OtherBase:
    pass

  @component
  class Impl(OtherBase, InterfaceA):
    def foo(self) -> str:
      return "Bar"

  assert Container._registrations[InterfaceA] is Impl
  instance = Container.get(InterfaceA)
  assert isinstance(instance, Impl)
  assert instance.foo() == "Bar"


def test_component_does_not_register_non_abc_base():
  class NonABCBase:
    pass

  @component
  class Service(NonABCBase):
    pass

  assert Service in Container._registrations
  assert NonABCBase not in Container._registrations


# --- inject decorator tests ---


def test_inject_decorator_simple():
  class Service:
    pass

  Container.register(Service)

  @inject
  def func(a: Service):
    return a

  result = func()
  assert isinstance(result, Service)


def test_inject_decorator_with_args():
  class ServiceA:
    pass

  class ServiceB:
    def __init__(self, a: ServiceA):
      self.a = a

  Container.register(ServiceA)
  Container.register(ServiceB)

  @inject
  def func(a: ServiceA, b: ServiceB):
    return (a, b)

  a, b = func()
  assert isinstance(a, ServiceA)
  assert isinstance(b, ServiceB)
  assert b.a is a


def test_inject_decorator_with_override():
  class Service:
    pass

  Container.register(Service)

  @inject
  def func(a: Service):
    return a

  custom = Service()
  result = func(a=custom)
  assert result is custom


def test_inject_decorator_type_hint_required():
  @inject
  def func(a):
    return a

  with pytest.raises(ValueError, match="Type hint required for parameter"):
    func()


def test_inject_decorator_mixed_injection():
  class Service:
    pass

  Container.register(Service)

  @inject
  def func(a: Service, b: str):
    return (a, b)

  # 'a' should be injected, 'b' should be passed explicitly
  service, text = func(b="hello")
  assert isinstance(service, Service)
  assert text == "hello"

  # Both can be passed explicitly
  custom_service = Service()
  service, text = func(a=custom_service, b="world")
  assert service is custom_service
  assert text == "world"
