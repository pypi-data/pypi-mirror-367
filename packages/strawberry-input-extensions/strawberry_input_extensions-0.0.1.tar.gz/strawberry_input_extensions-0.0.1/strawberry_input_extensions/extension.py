"""Extension module for Strawberry GraphQL that provides input validation and transformation.

This module implements a flexible extension system for Strawberry GraphQL that enables
validation and transformation of input values in GraphQL operations. It supports both
synchronous and asynchronous operations, and handles nested input types, lists, and
optional values.

Key Components:
- InputExtensionMetaclass: Metaclass that provides caching for extension instances
- InputExtension: Base class for creating custom input extensions
- ExtensionResolver: Base resolver class that handles extension chains
- Specialized resolvers (ScalarResolver, OptionalResolver, ListResolver, InputResolver)
- InputExtensionsExtension: Strawberry extension that integrates with GraphQL schema

Example usage:
    ```python
    class UpperCase(InputExtension):
        def resolve(self, value, info, next_, path):
            return next_(value.upper())

    @strawberry.mutation(extensions=[InputExtensionsExtension()])
    def update_user(self, name: Annotated[str, UpperCase()]) -> User:
        return User(name=name)  # name will be uppercase
    ```
"""

import functools
from typing import Annotated, get_origin, get_args, Union, List, Any, Callable, Dict, Tuple, Optional

from strawberry import UNSET, Info
from strawberry.extensions import FieldExtension
from strawberry.extensions.field_extension import SyncExtensionResolver, AsyncExtensionResolver
from strawberry.schema.compat import is_input_type
from strawberry.types.field import StrawberryField
from strawberry.utils.await_maybe import await_maybe

from .exceptions import InputExtensionFieldException, InputExtensionException, VALIDATION_EXCEPTION_CLASSES


class InputExtensionMetaclass(type):
    """Metaclass for InputExtension that provides instance caching.
    
    Uses functools.lru_cache to cache extension instances, improving performance
    when the same extension is used multiple times.
    """
    @functools.lru_cache(maxsize=1000, typed=True)
    def __call__(cls, *args, **kwargs):
        self = cls.__new__(cls, *args, **kwargs)
        cls.__init__(self, *args, **kwargs)
        return self


class InputExtension(metaclass=InputExtensionMetaclass):
    """Base class for creating custom input extensions.
    
    Extensions can modify or validate input values in GraphQL operations.
    Subclasses must implement the resolve method.
    """
    def resolve(self, value: Any, info: Info, next_: Callable, path: List[Union[str, int]]):
        """Process an input value and optionally transform it.
        
        Args:
            value: The input value to process
            info: GraphQL resolver info
            next_: The next extension in the chain
            path: Path to the current field
            
        Returns:
            Processed value
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"{self.__class__.__name__}.resolve Not Implemented")

    async def resolve_async(self, value: Any, info: Info, next_: Callable, path: List[Union[str, int]]):
        """Asynchronous version of resolve."""
        return await await_maybe(self.resolve(value, info, next_, path))

    def __class_getitem__(cls, params):
        """Enables using extensions as type annotations."""
        if not isinstance(params, tuple):
            params = (params,)
        type_ = params[0]
        args = params[1:]
        return Annotated[type_, cls(*args)]

    @classmethod
    def decorator(cls, *args):
        """Creates a decorator for applying the extension."""
        def _decorator(type_):
            return Annotated[type_, cls(*args)]
        return _decorator


def is_optional(field: Any) -> bool:
    origin = get_origin(field)
    if origin is Union:
        return type(None) in get_args(field)
    if origin is Annotated:
        return is_optional(get_args(field)[0])
    return False


def get_optional_child_type(field: Any) -> Any:
    origin = get_origin(field)
    if origin is Union:
        return [f for f in get_args(field) if f][0]
    if origin is Annotated:
        return get_optional_child_type(get_args(field)[0])
    return None


def is_list(field: Any) -> bool:
    origin = get_origin(field)
    if origin is Annotated:
        return is_list(get_args(field)[0])
    return origin in (list, List)


def get_list_child_type(field: Any) -> Any:
    origin = get_origin(field)
    if origin is Annotated:
        return get_list_child_type(get_args(field)[0])
    return get_args(field)[0]


def get_input_base_type(field_type: Any) -> Any:
    origin = get_origin(field_type)
    if origin is Annotated:
        return get_args(field_type)[0]
    return field_type


def get_field_extensions_from_metadata(field: Any) -> Optional[List[InputExtension]]:
    if metadata := getattr(field, '__metadata__', None):
        extensions = []
        for m in metadata:
            if isinstance(m, InputExtension):
                extensions.append(m)

        if extensions:
            return extensions
    return None


def extension_tail(value: Any) -> Any:
    return value


class ExtensionResolver:
    """Base resolver class that handles chains of extensions.
    
    Manages the execution of multiple extensions in sequence, handling both
    synchronous and asynchronous operations.
    """
    def __init__(self, extensions: List[InputExtension]):
        """Initialize resolver with a list of extensions."""
        self.extensions = extensions

    def resolve_extensions(self, value: Any, path: List[Union[str, int]], info: Info):
        """Execute extensions chain synchronously."""
        if not self.extensions:
            return value, []

        try:
            chain = extension_tail
            for extension in self.extensions:
                chain = functools.partial(extension.resolve, next_=chain, info=info, path=path)
            return chain(value), []
        except InputExtensionFieldException as e:
            e.path = path + e.path
            return value, [e]
        except tuple(VALIDATION_EXCEPTION_CLASSES) as e:
            return value, [InputExtensionFieldException(e, path, info)]

    async def resolve_extensions_async(self, value: Any, path: List[Union[str, int]], info: Info):
        """Execute extensions chain asynchronously."""
        if not self.extensions:
            return value, []

        try:
            chain = extension_tail
            for extension in self.extensions:
                chain = functools.partial(extension.resolve_async, next_=chain, info=info, path=path)
            return await chain(value), []
        except InputExtensionFieldException as e:
            return value, [e]
        except tuple(VALIDATION_EXCEPTION_CLASSES) as e:
            return value, [InputExtensionFieldException(e, path, info)]

    def resolve(self, value: Any, path: List[Union[str, int]], info: Info) -> Tuple[Any, List[InputExtensionFieldException]]:
        return self.resolve_extensions(value, path, info)

    async def resolve_async(self, value: Any, path: List[Union[str, int]], info: Info) -> Tuple[Any, List[InputExtensionFieldException]]:
        return await self.resolve_extensions_async(value, path, info)


class ScalarResolver(ExtensionResolver):
    """Resolver for scalar types.
    
    Applies extensions directly to the scalar value.
    """
    @classmethod
    def get_resolver(cls, field: Any) -> Optional[ExtensionResolver]:
        """Get resolver for scalar field."""
        if extensions := get_field_extensions_from_metadata(field):
            return cls(extensions)
        return None


class OptionalResolver(ExtensionResolver):
    """Resolver for optional types.
    
    Handles the case where the input value might be None.
    """
    @classmethod
    def get_resolver(cls, field: Any) -> Optional[ExtensionResolver]:
        """Get resolver for optional field."""
        child_type = get_optional_child_type(field)
        child_resolver = get_extension_resolver(child_type)
        extensions = get_field_extensions_from_metadata(field)

        if not extensions and not child_resolver:
            return None

        return cls(extensions, child_resolver)

    def __init__(self, extensions: List[InputExtension], child_resolver: Optional[ExtensionResolver]):
        """Initialize resolver with extensions and a child resolver."""
        self.child_resolver = child_resolver
        super().__init__(extensions)

    def resolve(self, value: Any, path: List[str], info: Info) -> Tuple[Any, List[InputExtensionFieldException]]:
        """Resolve optional field synchronously."""
        if value is not None and self.child_resolver:
            new_value, errors = self.child_resolver.resolve(value, path, info)
            if errors:
                return value, errors
            value = new_value
        return super().resolve(value, path, info)

    async def resolve_async(self, value: Any, path: List[Union[str, int]], info: Info) -> Tuple[Any, List[InputExtensionFieldException]]:
        """Resolve optional field asynchronously."""
        if value is not None and self.child_resolver:
            new_value, errors = await self.child_resolver.resolve_async(value, path, info)
            if errors:
                return value, errors
            value = new_value
        return await super().resolve_async(value, path, info)


class ListResolver(ExtensionResolver):
    """Resolver for list types.
    
    Applies extensions to each element in the list.
    """
    @classmethod
    def get_resolver(cls, field: Any) -> Optional[ExtensionResolver]:
        """Get resolver for list field."""
        child_type = get_list_child_type(field)
        child_resolver = get_extension_resolver(child_type)
        extensions = get_field_extensions_from_metadata(field)

        if not extensions and not child_resolver:
            return None

        return cls(extensions, child_resolver)

    def __init__(self, extensions: List[InputExtension], child_resolver: Optional[ExtensionResolver]):
        """Initialize resolver with extensions and a child resolver."""
        self.child_resolver = child_resolver
        super().__init__(extensions)

    def resolve(self, value: List, path: List[Union[str, int]], info: Info) -> Tuple[List, List[InputExtensionFieldException]]:
        """Resolve list field synchronously."""
        if self.child_resolver:
            errors = []
            new_list = []
            for index, item in enumerate(value):
                result, child_errors = self.child_resolver.resolve(item, path + [index], info)
                new_list.append(result)
                if child_errors:
                    errors.extend(child_errors)
            if errors:
                return value, errors
            value = new_list
        return super().resolve(value, path, info)

    async def resolve_async(self, value: List, path: List[Union[str, int]], info: Info) -> Tuple[List, List[InputExtensionFieldException]]:
        """Resolve list field asynchronously."""
        if self.child_resolver:
            errors = []
            new_list = []
            for index, item in enumerate(value):
                result, child_errors = await self.child_resolver.resolve_async(item, path + [index], info)
                new_list.append(result)
                if child_errors:
                    errors.extend(child_errors)
            if errors:
                return value, errors
            value = new_list
        return await super().resolve_async(value, path, info)


class InputResolver(ExtensionResolver):
    """Resolver for input types.
    
    Recursively resolves extensions for each field in the input type.
    """
    @classmethod
    def get_resolver(cls, field: Any) -> Optional[ExtensionResolver]:
        """Get resolver for input field."""
        extensions = get_field_extensions_from_metadata(field)
        input_base_type = get_input_base_type(field)
        annotations = getattr(input_base_type, '__annotations__', {})
        child_resolvers: Dict[str, ExtensionResolver] = {}
        has_child_resolvers = False
        for child_field_name, child_field in annotations.items():
            if resolver := get_extension_resolver(child_field):
                child_resolvers[child_field_name] = resolver
                has_child_resolvers = True

        if not extensions and not has_child_resolvers:
            return None

        return cls(extensions, child_resolvers)

    def __init__(self, extensions: List[InputExtension], child_resolvers: Dict[str, ExtensionResolver]):
        """Initialize resolver with extensions and child resolvers."""
        self.child_resolvers = child_resolvers
        super().__init__(extensions)

    def resolve(self, value: Any, path: List[Union[str, int]], info: Info) -> Tuple[Any, List[InputExtensionFieldException]]:
        """Resolve input field synchronously."""
        if self.child_resolvers:
            errors = []
            new_values = {}
            for child_field_name, child_resolver in self.child_resolvers.items():
                if (field_value := getattr(value, child_field_name, UNSET)) is not UNSET:
                    new_values[child_field_name], child_errors = child_resolver.resolve(
                        field_value,
                        path + [child_field_name],
                        info
                    )
                    if child_errors:
                        errors.extend(child_errors)
            if errors:
                return value, errors
            for child_field_name, child_field_value in new_values.items():
                setattr(value, child_field_name, child_field_value)
        return super().resolve(value, path, info)

    async def resolve_async(self, value: Any, path: List[Union[str, int]], info: Info) -> Tuple[Any, List[InputExtensionFieldException]]:
        """Resolve input field asynchronously."""
        if self.child_resolvers:
            errors = []
            new_values = {}
            for child_field_name, child_resolver in self.child_resolvers.items():
                if (field_value := getattr(value, child_field_name, UNSET)) is not UNSET:
                    new_values[child_field_name], child_errors = await child_resolver.resolve_async(
                        field_value,
                        path + [child_field_name],
                        info
                    )
                    if child_errors:
                        errors.extend(child_errors)
            if errors:
                return value, errors
            for child_field_name, child_field_value in new_values.items():
                setattr(value, child_field_name, child_field_value)
        return await super().resolve_async(value, path, info)


def get_extension_resolver(field: Any) -> Optional[ExtensionResolver]:
    """Get the appropriate extension resolver for a given field.
    
    This function determines the correct resolver based on the field's type,
    handling optional types, lists, input types, and scalar types.
    """
    if is_optional(field):
        return OptionalResolver.get_resolver(field)
    elif is_list(field):
        return ListResolver.get_resolver(field)
    elif is_input_type(field):
        return InputResolver.get_resolver(field)
    else:
        return ScalarResolver.get_resolver(field)


class InputExtensionsExtension(FieldExtension):
    """Strawberry extension that applies input extensions to input arguments.
    
    This extension integrates with the GraphQL schema and applies the configured
    input extensions to the input arguments of GraphQL fields.
    """
    def __init__(self) -> None:
        """Initialize extension."""
        self.argument_resolvers: Dict[str, ExtensionResolver] = {}
        super().__init__()

    def apply(self, field: StrawberryField) -> None:
        """Apply the extension to a GraphQL field.
        
        Extracts argument resolvers from the field's annotations.
        """
        for field_name, field in field.base_resolver.annotations.items():
            if resolver := get_extension_resolver(field):
                self.argument_resolvers[field_name] = resolver

    def resolve(self, next_: SyncExtensionResolver, source: Any, info: Info, **kwargs: dict) -> Any:
        """Resolve input arguments synchronously."""
        if self.argument_resolvers:
            errors: List[InputExtensionFieldException] = []
            for key, argument_resolver in self.argument_resolvers.items():
                if (value := kwargs.get(key, UNSET)) is not UNSET:
                    kwargs[key], argument_errors = argument_resolver.resolve(value, [key], info)
                    if argument_errors:
                        errors.extend(argument_errors)
            if errors:
                raise InputExtensionException(errors=errors)
        return next_(source, info, **kwargs)

    async def resolve_async(self, next_: AsyncExtensionResolver, source: Any, info: Info, **kwargs: dict) -> Any:
        """Resolve input arguments asynchronously."""
        if self.argument_resolvers:
            errors: List[InputExtensionFieldException] = []
            for key, argument_resolver in self.argument_resolvers.items():
                if (value := kwargs.get(key, UNSET)) is not UNSET:
                    kwargs[key], argument_errors = await argument_resolver.resolve_async(value, [key], info)
                    if argument_errors:
                        errors.extend(argument_errors)
            if errors:
                raise InputExtensionException(errors=errors)
        return await next_(source, info, **kwargs)