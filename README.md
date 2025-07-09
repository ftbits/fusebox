# Fusebox

**Fusebox** is a lightweight and Pythonic dependency injection (DI) container built for simplicity and minimalism. It allows you to easily register and resolve classes and inject dependencies into functions with automatic dependency resolution.

> ⚡️ No magic. No runtime patching. Just clean, type-safe DI.

---

## 🚀 Features

- Minimal API surface
- Automatic class registration and constructor-based dependency injection for classes using the `@component` decorator
- Function parameter injection with `@inject` decorator
- Interface-to-implementation binding
- Caches singletons automatically
- Pure Python, zero dependencies

---

## 📦 Installation

```bash
poetry add fusebox
```

## 📐 Quick Example

```python
from fusebox import Container, component

@component
class ServiceA:
  def greet(self):
    return "Hello from A"

@component
class ServiceB:
  def __init__(self, service_a: ServiceA):
    self.service_a = service_a

  def greet_with_service_a(self) -> str:
    return f"ServiceB says: {self.service_a.greet()}"

service_b = Container.get(ServiceB)
print(service_b.greet_with_service_a())  # ServiceB says: Hello from A
```

## 🔁 Interface Binding

Bind an abstract base class (ABC) to a concrete implementation:

```python
from abc import ABC, abstractmethod
from fusebox import component, Container

class Greeter(ABC):
    @abstractmethod
    def greet(self): pass

@component
class HelloGreeter(Greeter):
    def greet(self):
        return "Hello!"

greeter = Container.get(Greeter)
print(greeter.greet())  # Hello!
```

## 🪄 Function Injection with `@inject`

You can also inject dependencies directly into functions using the `@inject` decorator:

```python
from fusebox import component, inject, Container

@component
class ServiceA:
    def greet(self):
        return "Hello from A"

@inject
def greet_with_a(a: ServiceA):
    return a.greet()

print(greet_with_a())  # Hello from A
```

## 🔀 Mixed Injection

You can combine injected dependencies with explicit parameters:

```python
from fusebox import component, inject, Container

@component
class ServiceA:
    def greet(self):
        return "Hello from A"

@inject
def greet_with_message(a: ServiceA, message: str):
    return f"{a.greet()} - {message}"

# 'a' is injected, 'message' is passed explicitly
print(greet_with_message(message="Welcome!"))  # Hello from A - Welcome!

# You can also override injected dependencies
custom_a = ServiceA()
print(greet_with_message(a=custom_a, message="Override!"))  # Hello from A - Override!
```

## 🧾 License

MIT License. See [LICENSE][1] file.

## 🌍 Links

📦 [PyPI][2]

💻 [GitHub][3]

## 🙌 Contributing

Pull requests are welcome! Please submit issues and suggestions to help improve the project.

[1]: LICENSE
[2]: https://pypi.org/project/fusebox
[3]: https://github.com/ftbits/fusebox
