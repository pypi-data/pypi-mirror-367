from decoguard.decorators import validate_decorated
from decoguard.errors import DecoratorUsageValidationError
from decoguard.validators import *


def test_require_params_ok():

    @validate_decorated(require_params("x", "y"))
    def deco(f):
        return f

    @deco
    def myfunc(x, y):
        pass

    @validate_decorated(require_params("x", "y", "z"))
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_with_z(x, y, z):
        pass


def test_require_params_typed_ok():
    @validate_decorated(require_params(("x", int), ("y", str)))
    def deco(f):
        return f

    @deco
    def myfunc(x: int, y: str):
        pass

    @validate_decorated(require_params(("x", int, float), ("y", str)))
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_with_z(x: int | float, y: str, z: float):
        pass


def test_require_params_fail():
    @validate_decorated(require_params("x"))
    def deco(f):
        return f

    try:

        @deco
        def badfunc(y):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected ValidationError"


def test_require_params_typed_fail():
    @validate_decorated(require_params(("x", int, float), ("y", str)))
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    try:

        @deco_factory("test")
        def myfunc_with_z(x: float, y: str, z: float):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected ValidationError"


def test_require_n_params_ok():
    @validate_decorated(require_at_least_n_params(2, "x", "y"))
    def deco(f):
        return f


def test_require_at_least_n_params_complete():
    @validate_decorated(require_at_least_n_params(2, "x", "y"))
    def deco(f):
        return f

    @deco
    def myfunc(x, y):
        pass

    @validate_decorated(require_at_least_n_params(2, "x", "y", "z"))
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_with_z(x, y, z):
        pass

    @validate_decorated(require_at_least_n_params(1, "x", "y", "z"))
    def deco2(f):
        return f

    @deco2
    def myfunc2(z):
        pass

    @validate_decorated(require_at_least_n_params(1, "x", "y", "z"))  # type: ignore
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")  # type: ignore
    def myfunc_with_z(z):
        pass


def test_require_n_params_typed_ok():
    @validate_decorated(require_at_least_n_params(1, ("x", int), ("y", str)))
    def deco(f):
        return f

    @deco
    def myfunc(x: int, y: str):
        pass

    @validate_decorated(require_at_least_n_params(1, ("x", int, float), ("x", str)))
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_with_z(x: int | float, y: str, z: float):
        pass


def test_require_n_params_fail():
    @validate_decorated(require_at_least_n_params(1, "x"))
    def deco(f):
        return f

    try:

        @deco
        def badfunc(y):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected ValidationError"


def test_require_n_params_typed_fail():
    @validate_decorated(require_at_least_n_params(2, ("x", int, float), ("y", str)))
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    try:

        @deco_factory("test")
        def myfunc_with_z(x: float, y: str):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected ValidationError"


def test_require_n_params_missused():
    try:

        @validate_decorated(require_at_least_n_params(2, "x"))
        def deco(f):
            return f

    except TypeError:
        return
    assert False, "Expected TypeError"


def test_no_params_ok():
    @validate_decorated(no_params())
    def deco(f):
        return f

    @deco
    def myfunc():
        pass

    @validate_decorated(no_params())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_no_params():
        pass


def test_no_params_ok_with_self():
    @validate_decorated(no_params())
    def deco(f):
        return f

    @deco
    def method(self):
        pass


def test_no_params_fail():
    @validate_decorated(no_params())
    def deco(f):
        return f

    try:

        @deco
        def badfunc(x):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_no_params_fail_multiple():
    @validate_decorated(no_params())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    try:

        @deco_factory("test")
        def badfunc(x, y, z):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_no_optional_params_ok():
    @validate_decorated(no_optional_params())
    def deco(f):
        return f

    @deco
    def myfunc(x, y):
        pass

    @validate_decorated(no_optional_params())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    @deco_factory("test")
    def myfunc_no_optional(x, y, z):
        pass


def test_no_optional_params_ok_with_self():
    @validate_decorated(no_optional_params())
    def deco(f):
        return f

    @deco
    def method(self, x, y):
        pass


def test_no_optional_params_ok_no_params():
    @validate_decorated(no_optional_params())
    def deco(f):
        return f

    @deco
    def myfunc():
        pass


def test_no_optional_params_fail():
    @validate_decorated(no_optional_params())
    def deco(f):
        return f

    try:

        @deco
        def badfunc(x, y=10):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_no_optional_params_fail_multiple():
    @validate_decorated(no_optional_params())
    def deco_factory(param):
        def inner(f):
            return f

        return inner

    try:

        @deco_factory("test")
        def badfunc(x, y=10, z="hello"):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_no_optional_params_fail_mixed():
    @validate_decorated(no_optional_params())
    def deco(f):
        return f

    try:

        @deco
        def badfunc(x, y, z=None):
            pass

    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"


def test_require_at_least_n_params_edge_cases():
    @validate_decorated(require_at_least_n_params(1, "x"))
    def deco_one(f):
        return f

    @deco_one
    def func_one_param(x):
        pass

    try:
        @validate_decorated(require_at_least_n_params(3, "x", "y"))
        def deco_mismatch(f):
            return f
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_require_at_least_n_params_zero():
    try:
        @validate_decorated(require_at_least_n_params(0, "x"))
        def deco_zero(f):
            return f
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_require_at_least_n_params_validation_with_n_greater_than_params():
    try:
        require_at_least_n_params(5, "x", "y")
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "Expected n >= 1 and n <=" in str(e)


def test_require_at_least_n_params_with_negative_n():
    try:
        require_at_least_n_params(-1, "x", "y")
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "Expected n >= 1" in str(e)


def test_require_at_least_n_params_with_wrong_type_n():
    try:
        require_at_least_n_params("not_int", "x", "y")  # type: ignore
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "got not_int of type" in str(e)


def test_require_at_least_n_params_no_params():
    """Test require_at_least_n_params with no expected parameters"""
    try:
        require_at_least_n_params(1)
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "Expected at least one expected parameter, got none" in str(e)
