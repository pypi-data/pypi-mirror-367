from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, Union, Callable, Any

""" Generic error wrapper to be used as default Error type in Result."""


class Error:
    def __init__(self, error):
        self._error = error

    @property
    def error(self):
        return self._error


class NoneValueError(Error):
    """Indicates that an expected value was None."""

    def __init__(self, message: str = "Unexpected None"):
        super().__init__(message)


T = TypeVar("T")
U = TypeVar("U")


class Result(Generic[T]):
    """Base class for Ok and Err; supports helper methods if you like."""

    def __bool__(self) -> bool:
        return self.is_ok()

    def is_ok(self) -> bool:
        return isinstance(self, Ok)

    def is_err(self) -> bool:
        return isinstance(self, Err)

    def unwrap(self) -> T:
        if isinstance(self, Ok):
            return self.value
        raise Exception(f"Called unwrap on Err({self.error!r})")

    def as_dict(self) -> dict:
        if self.is_ok():
            unwrapped = self.unwrap()
            if isinstance(unwrapped, (dict, int, float, str)):
                return {"ok": True, "value": unwrapped}
            # Removed YMpcObject reference - not needed in YAPP
            return {"ok": True, "value": str(unwrapped)}
        return {"ok": False, "value": self.as_error}

    @property
    @abstractmethod
    def as_error(self) -> dict:
        ...

    @classmethod
    def error(cls, message: Union[str, dict]) -> "Result[T]":
        """Create an Err result with the given error message."""
        return Err(message)
    
    # ===== FLUENT API METHODS (inspired by Rust Result) =====
    
    def and_then(self, func: Callable[[T], "Result[U]"] ) -> "Result[U]":
        """Chain operations that return Results - like flatMap.
        
        If this Result is Ok(value), calls func(value) and returns its Result.
        If this Result is Err, returns the Err unchanged.
        """
        if self.is_ok():
            return func(self.unwrap())
        else:
            return Err(self.as_error)
    
    def or_else(self, func: Callable[[dict], "Result[T]"]) -> "Result[T]":
        """Handle errors by providing alternative Results.
        
        If this Result is Err(error), calls func(error) and returns its Result.
        If this Result is Ok, returns the Ok unchanged.
        """
        if self.is_err():
            return func(self.as_error)
        else:
            return self
    
    def map(self, func: Callable[[T], U]) -> "Result[U]":
        """Transform Ok values, pass through Err unchanged.
        
        If this Result is Ok(value), returns Ok(func(value)).
        If this Result is Err, returns the Err unchanged.
        """
        if self.is_ok():
            return Ok(func(self.unwrap()))
        else:
            return Err(self.as_error)
    
    def map_err(self, func: Callable[[dict], dict]) -> "Result[T]":
        """Transform Err values, pass through Ok unchanged.
        
        If this Result is Err(error), returns Err(func(error)).
        If this Result is Ok, returns the Ok unchanged.
        """
        if self.is_err():
            return Err(func(self.as_error))
        else:
            return self
    
    def unwrap_or(self, default: T) -> T:
        """Return value or default if Err.
        
        If this Result is Ok(value), returns value.
        If this Result is Err, returns default.
        """
        return self.unwrap() if self.is_ok() else default
    
    def unwrap_or_else(self, func: Callable[[dict], T]) -> T:
        """Return value or call function with error.
        
        If this Result is Ok(value), returns value.
        If this Result is Err(error), returns func(error).
        """
        return self.unwrap() if self.is_ok() else func(self.as_error)
    
    def inspect(self, func: Callable[[T], None]) -> "Result[T]":
        """Call function with Ok value for side effects, return self unchanged.
        
        Useful for debugging or logging without changing the Result.
        """
        if self.is_ok():
            func(self.unwrap())
        return self
    
    def inspect_err(self, func: Callable[[dict], None]) -> "Result[T]":
        """Call function with Err value for side effects, return self unchanged.
        
        Useful for debugging or logging errors without changing the Result.
        """
        if self.is_err():
            func(self.as_error)
        return self


@dataclass(frozen=True)
class Ok(Result[T]):
    value: T

    @property
    def as_error(self) -> dict:
        raise AttributeError("Ok does not have an error; use is_ok() to check.")


@dataclass(frozen=True)
class Err(Result[T]):
    _error: dict

    @property
    def as_error(self) -> dict:
        return self._error


def non_none_result(
    value: Optional[T], err: str = "unexpected None value"
) -> Result[T]:
    if value is None:
        return Result.error(err)
    return Ok(value)
