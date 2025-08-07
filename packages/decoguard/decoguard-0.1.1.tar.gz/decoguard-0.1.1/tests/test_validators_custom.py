from inspect import signature

from decoguard.decorators import validate_decorated
from decoguard.errors import DecoratorUsageValidationError
from decoguard.validators import *


def test_custom_validator_ok():
    def check_name_starts_with_test(func):
        return func.__name__.startswith("test_")

    @validate_decorated(custom_validator(check_name_starts_with_test))
    def deco(f):
        return f

    @deco
    def test_myfunc():
        pass

    @validate_decorated(
        custom_validator(
            check_name_starts_with_test, "function name must start with 'test_'"
        )
    )
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def test_another_func():
        pass


def test_custom_validator_fail():
    def check_name_starts_with_test(func):
        return func.__name__.startswith("test_")

    @validate_decorated(custom_validator(check_name_starts_with_test))
    def deco(f):
        return f

    try:

        @deco
        def badfunc():
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_custom_validator_fail_with_custom_message():
    def check_has_docstring(func):
        return func.__doc__ is not None

    @validate_decorated(
        custom_validator(check_has_docstring, "function must have a docstring")
    )
    def deco(f):
        return f

    try:

        @deco
        def badfunc():
            pass

    except DecoratorUsageValidationError as e:
        assert "function must have a docstring" in str(e)
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_custom_validator_factory_fail():
    def check_param_count(func):
        return len(signature(func).parameters) >= 2

    @validate_decorated(
        custom_validator(check_param_count, "function must have at least 2 parameters")
    )
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    try:

        @deco_factory("test")
        def badfunc(x):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_custom_validator_exception_handling():
    def broken_validator(func):
        raise ValueError("Something went wrong")

    @validate_decorated(custom_validator(broken_validator))
    def deco(f):
        return f

    try:

        @deco
        def badfunc():
            pass

    except DecoratorUsageValidationError as e:
        assert "custom validation failed with error" in str(e)
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_custom_validator_invalid_arguments():
    try:
        custom_validator("not a function")  # type: ignore
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError"

    def valid_func(f):
        return True

    try:
        custom_validator(valid_func, 123)  # type: ignore
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError"
