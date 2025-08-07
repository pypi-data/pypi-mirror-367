from decoguard.decorators import validate_decorated
from decoguard.errors import DecoratorUsageValidationError
from decoguard.validators import *


def test_has_return_ok():
    @validate_decorated(has_return())
    def deco(f):
        return f

    @deco
    def myfunc() -> int:
        return 42

    @validate_decorated(has_return())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_with_return() -> str:
        return "hello"


def test_has_return_fail():
    @validate_decorated(has_return())
    def deco(f):
        return f

    try:

        @deco
        def badfunc():
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_has_return_factory_fail():
    @validate_decorated(has_return())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    try:

        @deco_factory("test")
        def badfunc():
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_has_return_fail_return_none():
    @validate_decorated(has_return())
    def deco(f):
        return f

    try:

        @deco
        def badfunc() -> int:
            return None  # type: ignore

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_has_return_fail_only_empty_return():
    @validate_decorated(has_return())
    def deco(f):
        return f

    try:

        @deco
        def badfunc() -> int:
            if True:
                return  # type: ignore
            return None  # type: ignore

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_has_return_ok_mixed_returns():
    @validate_decorated(has_return())
    def deco(f):
        return f

    @deco
    def myfunc() -> int:
        if False:
            return None  # type: ignore
        return 42


def test_no_return_ok():
    @validate_decorated(no_return())
    def deco(f):
        return f

    @deco
    def myfunc():
        pass

    @validate_decorated(no_return())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_with_none():
        return None


def test_no_return_ok_empty_return():
    @validate_decorated(no_return())
    def deco(f):
        return f

    @deco
    def myfunc():
        x = 1
        if x == 1:
            return
        print("hello")


def test_no_return_fail_has_annotation():
    @validate_decorated(no_return())
    def deco(f):
        return f

    try:

        @deco
        def badfunc() -> int:  # type: ignore
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_no_return_fail_has_meaningful_return():
    @validate_decorated(no_return())
    def deco(f):
        return f

    try:

        @deco
        def badfunc():
            return 42

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_no_return_factory_fail():
    @validate_decorated(no_return())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    try:

        @deco_factory("test")
        def badfunc() -> str:
            return "hello"

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"
