from decoguard.errors import DecoratorUsageValidationError
from decoguard.decorators import *
from decoguard.validators import *

def test_require_params_ok():
    @validate_decorated(require_params("x", "y"))
    def deco(f): return f

    @deco
    def myfunc(x, y): pass

    @validate_decorated(require_params("x", "y", "z"))
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    @deco_factory("test")
    def myfunc_with_z(x, y, z): pass

def test_require_params_typed_ok():
    @validate_decorated(require_params(("x", int), ("y", str)))
    def deco(f): return f

    @deco
    def myfunc(x: int, y: str): pass

    @validate_decorated(require_params(("x", int, float), ("y", str)))
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    @deco_factory("test")
    def myfunc_with_z(x: int | float, y: str, z: float): pass


def test_require_params_fail():
    @validate_decorated(require_params("x"))
    def deco(f): return f

    try:
        @deco
        def badfunc(y): pass
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
        def myfunc_with_z(x: float, y: str, z: float): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected ValidationError"

def test_missused_validate_decorated():
    try:
        @validate_decorated(require_params("x"))
        def not_a_decorator(f, x): return f
    except TypeError:
        return
    assert False, "Expected TypeError"


def test_require_n_params_ok():
    @validate_decorated(require_at_least_n_params(2, "x", "y"))
    def deco(f): return f

    @deco
    def myfunc(x, y): pass

    @validate_decorated(require_at_least_n_params(2, "x", "y", "z"))
    def deco_factory(param):
        def inner(f):
            return f
        return inner

    @deco_factory("test")
    def myfunc_with_z(x, y, z): pass

    @validate_decorated(require_at_least_n_params(1, "x", "y", "z"))
    def deco(f): return f

    @deco
    def myfunc(z): pass

    @validate_decorated(require_at_least_n_params(1, "x", "y", "z"))
    def deco_factory(param):
        def inner(f):
            return f
        return inner

    @deco_factory("test")
    def myfunc_with_z(z): pass

def test_require_n_params_typed_ok():
    @validate_decorated(require_at_least_n_params(1, ("x", int), ("y", str)))
    def deco(f): return f

    @deco
    def myfunc(x: int, y: str): pass

    @validate_decorated(require_at_least_n_params(1, ("x", int, float), ("x", str)))
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    @deco_factory("test")
    def myfunc_with_z(x: int | float, y: str, z: float): pass

def test_require_n_params_fail():
    @validate_decorated(require_at_least_n_params(1, "x"))
    def deco(f): return f

    try:
        @deco
        def badfunc(y): pass
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
        def myfunc_with_z(x: float, y: str): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected ValidationError"

def test_require_n_params_missused():
    try:
        @validate_decorated(require_at_least_n_params(2, "x"))
        def deco(f): return f
    except TypeError:
        return
    assert False, "Expected TypeError"

def test_no_params_ok():
    @validate_decorated(no_params())
    def deco(f): return f

    @deco
    def myfunc(): pass

    @validate_decorated(no_params())
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    @deco_factory("test")
    def myfunc_no_params(): pass

def test_no_params_ok_with_self():
    @validate_decorated(no_params())
    def deco(f): return f

    @deco
    def method(self): pass

def test_no_params_fail():
    @validate_decorated(no_params())
    def deco(f): return f

    try:
        @deco
        def badfunc(x): pass
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
        def badfunc(x, y, z): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_no_optional_params_ok():
    @validate_decorated(no_optional_params())
    def deco(f): return f

    @deco
    def myfunc(x, y): pass

    @validate_decorated(no_optional_params())
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    @deco_factory("test")
    def myfunc_no_optional(x, y, z): pass

def test_no_optional_params_ok_with_self():
    @validate_decorated(no_optional_params())
    def deco(f): return f

    @deco
    def method(self, x, y): pass

def test_no_optional_params_ok_no_params():
    @validate_decorated(no_optional_params())
    def deco(f): return f

    @deco
    def myfunc(): pass

def test_no_optional_params_fail():
    @validate_decorated(no_optional_params())
    def deco(f): return f

    try:
        @deco
        def badfunc(x, y=10): pass
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
        def badfunc(x, y=10, z="hello"): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_no_optional_params_fail_mixed():
    @validate_decorated(no_optional_params())
    def deco(f): return f

    try:
        @deco
        def badfunc(x, y, z=None): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_has_return_ok():
    @validate_decorated(has_return())
    def deco(f): return f

    @deco
    def myfunc() -> int: return 42

    @validate_decorated(has_return())
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    @deco_factory("test")
    def myfunc_with_return() -> str: return "hello"

def test_has_return_fail():
    @validate_decorated(has_return())
    def deco(f): return f

    try:
        @deco
        def badfunc(): pass
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
        def badfunc(): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_has_return_fail_return_none():
    @validate_decorated(has_return())
    def deco(f): return f

    try:
        @deco
        def badfunc() -> int: 
            return None
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_has_return_fail_only_empty_return():
    @validate_decorated(has_return())
    def deco(f): return f

    try:
        @deco
        def badfunc() -> int: 
            if True:
                return
            return None
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_has_return_ok_mixed_returns():
    @validate_decorated(has_return())
    def deco(f): return f

    @deco
    def myfunc() -> int: 
        if False:
            return None
        return 42

def test_no_return_ok():
    @validate_decorated(no_return())
    def deco(f): return f

    @deco
    def myfunc(): pass

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
    def deco(f): return f

    @deco
    def myfunc(): 
        x = 1
        if x == 1:
            return
        print("hello")

def test_no_return_fail_has_annotation():
    @validate_decorated(no_return())
    def deco(f): return f

    try:
        @deco
        def badfunc() -> int: pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_no_return_fail_has_meaningful_return():
    @validate_decorated(no_return())
    def deco(f): return f

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

def test_custom_validator_ok():
    def check_name_starts_with_test(func):
        return func.__name__.startswith("test_")
    
    @validate_decorated(custom_validator(check_name_starts_with_test))
    def deco(f): return f

    @deco
    def test_myfunc(): pass

    @validate_decorated(custom_validator(check_name_starts_with_test, "function name must start with 'test_'"))
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    @deco_factory("test")
    def test_another_func(): pass

def test_custom_validator_fail():
    def check_name_starts_with_test(func):
        return func.__name__.startswith("test_")
    
    @validate_decorated(custom_validator(check_name_starts_with_test))
    def deco(f): return f

    try:
        @deco
        def badfunc(): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_custom_validator_fail_with_custom_message():
    def check_has_docstring(func):
        return func.__doc__ is not None
    
    @validate_decorated(custom_validator(check_has_docstring, "function must have a docstring"))
    def deco(f): return f

    try:
        @deco
        def badfunc(): pass
    except DecoratorUsageValidationError as e:
        assert "function must have a docstring" in str(e)
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_custom_validator_factory_fail():
    def check_param_count(func):
        from inspect import signature
        return len(signature(func).parameters) >= 2
    
    @validate_decorated(custom_validator(check_param_count, "function must have at least 2 parameters"))
    def deco_factory(param):
        def inner(f):
            return f
        return inner
    
    try:
        @deco_factory("test")
        def badfunc(x): pass
    except DecoratorUsageValidationError:
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_custom_validator_exception_handling():
    def broken_validator(func):
        raise ValueError("Something went wrong")
    
    @validate_decorated(custom_validator(broken_validator))
    def deco(f): return f

    try:
        @deco
        def badfunc(): pass
    except DecoratorUsageValidationError as e:
        assert "custom validation failed with error" in str(e)
        return
    assert False, "Expected DecoratorUsageValidationError"

def test_custom_validator_invalid_arguments():
    try:
        custom_validator("not a function")
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError"
    
    def valid_func(f): return True
    try:
        custom_validator(valid_func, 123)
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError"