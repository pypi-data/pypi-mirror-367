import sys
from collections.abc import Callable
from types import NoneType
from typing import Any, Optional, TypeAlias, TypeVar, Protocol, overload

from fxdc.exceptions import ClassAlreadyInitialized

T = TypeVar("T", bound=type)
class IdentityDeco(Protocol):
    def __call__(self, arg: T, /) -> T:
        ...
        
TB = TypeVar("TB", bound=type)

AcceptableTypes: TypeAlias = (
    int | float | str | bool | list[Any] | dict[str, Any] | NoneType
)


class _customclass:
    def __init__(
        self,
        classname: str,
        class_: type[TB],
        from_data: Optional[Callable[..., TB]] = None,
        to_data: Optional[Callable[[object], dict[str, AcceptableTypes]]] = None,
    ) -> None:
        self.classname = classname
        self.class_ = class_
        self.from_data = from_data
        if not from_data:
            if hasattr(class_, "__fromdata__"):
                self.from_data = class_.__fromdata__
        self.to_data = to_data
        if not to_data:
            if hasattr(class_, "__todata__"):
                self.to_data = class_.__todata__

    def __call__(self, *args: Any, **kwargs: Any) -> object:
        if self.from_data:
            return self.from_data(*args, **kwargs)
        return self.class_(*args, **kwargs)

    def __repr__(self) -> str:
        return self.classname

    def return_data(self, obj: object) -> dict[str, Any]:
        if self.to_data:
            return self.to_data(obj)
        return obj.__dict__

    def __str__(self) -> str:
        return "Custom Class: " + self.classname

    def __eq__(self, o: object) -> bool:
        if isinstance(o, _customclass):
            return self.classname == o.classname
        elif isinstance(o, str):
            return self.classname == o
        return False


class _config:
    def __init__(self) -> None:
        self.custom_classes: list[_customclass] = []
        self.custom_classes_names: list[str] = []
        self.debug__: bool = False

    @overload
    def add_class(self, class_: T, /) -> T:
        ...
        
    @overload
    def add_class(
        self,
        *,
        name: Optional[str] = None,
        from_data: Optional[Callable[..., object]] = None,
        to_data: Optional[Callable[..., dict[str, AcceptableTypes]]] = None,
    ) -> IdentityDeco:
        ...

    @overload
    def add_class(
        self,
        class_: Optional[T] = None,
        *,
        name: Optional[str] = None,
        from_data: Optional[Callable[..., object]] = None,
        to_data: Optional[Callable[..., dict[str, AcceptableTypes]]] = None,
    ) -> T:
        ...
        
    def add_class(
        self,
        class_: Optional[object] = None,
        *,
        name: Optional[str] = None,
        from_data: Optional[Callable[..., object]] = None,
        to_data: Optional[Callable[..., dict[str, AcceptableTypes]]] = None,
    ) -> object:
        """Add a custom class to the config

        Args:
            classname (Optional[str], optional): Name For The Class. Defaults to `class_.__name__`.
            from_data (Optional[Callable[..., object]], optional): Function to convert data to class. Defaults to class_.__fromdata__ if it exists. or class_.__init__ or class.__new__
            to_data (Optional[Callable[..., dict[str, Any]]], optional): Function to convert class to data. Defaults to class_.__todata__ if it exists. or class_.__dict__
            class_ (Optional[type], optional): Class to add. If not provided, it will return a decorator.
        Returns:
            if Class_ is provided, it will add and return the class
            if class_ is not provided, it will return a decorator to add on top of the class

        Usage:
            ```py
            @Config.add_class
            class MyClass:
                def __init__(self, data):
                    self.data = data
            ```
            OR
            ```py
            class MyClass:
                def __init__(self, data):
                    self.data = data


            Config.add_class("MyClass", class_=MyClass)"""

        def wrapper(class_: T) -> T:
            if self.get_class_name(class_) in self.custom_classes_names:
                raise ClassAlreadyInitialized(
                    f"Class {name} already exists"
                )

            c: _customclass = _customclass(
                name or class_.__name__, class_, from_data, to_data
            )
            self.custom_classes_names.append(c.classname)
            self.custom_classes.append(c)
            setattr(self, c.classname, c)
            return class_

        if class_:
            return wrapper(class_)
        return wrapper

    def remove_class(self, classname: str) -> None:
        delattr(self, classname)
        self.custom_classes.pop(self.custom_classes_names.index(classname))

    def set_recursion_limit(self, limit: int = 1000) -> None:
        sys.setrecursionlimit(limit)

    def get_class_name(self, class_: type) -> str:
        for customclass in self.custom_classes:
            if customclass.class_ is class_:
                return customclass.classname
        return class_.__name__


Config = _config()
