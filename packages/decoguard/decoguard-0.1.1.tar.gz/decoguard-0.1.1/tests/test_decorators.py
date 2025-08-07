from decoguard.decorators import validate_decorated
from decoguard.errors import DecoratorUsageValidationError
from decoguard.validators import require_params


def test_factory_decorator_simple():
    @validate_decorated(require_params("x"))
    def decorator_factory(param):
        def decorator(func):
            return func
        return decorator

    @decorator_factory("test")
    def myfunc(x):
        pass


def test_factory_decorator_fail():
    @validate_decorated(require_params("x"))
    def decorator_factory(param):
        def decorator(func):
            return func
        return decorator

    try:
        @decorator_factory("test")
        def badfunc(y):
            pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_nested_decorator():
    @validate_decorated(require_params("a"))
    def outer_deco(f):
        return f

    @validate_decorated(require_params("b"))
    def inner_deco(f):
        return f

    @outer_deco
    @inner_deco
    def nested_func(a, b):
        pass
