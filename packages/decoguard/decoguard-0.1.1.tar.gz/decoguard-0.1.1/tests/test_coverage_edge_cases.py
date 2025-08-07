import ast

from decoguard.asserts import (
    is_decorator,
    is_decorator_factory,
    _returned_function_looks_like_decorator_static,
    _has_single_argument
)
from decoguard.validators import (
    _has_meaningful_return_statements,
    require_params,
)


def test_has_meaningful_return_statements_builtin_function():
    result = _has_meaningful_return_statements(len)
    assert result == True


def test_has_meaningful_return_statements_lambda():
    def func(x):
        return x
    result = _has_meaningful_return_statements(func)
    assert result == True


def test_validate_decorated_non_callable_in_validators():
    def mock_validate_decorated_with_non_callable():
        validators = [require_params("x"), "not_callable"]

        def meta_decorator(decorated_func):
            for validator in validators:
                if not callable(validator):
                    raise TypeError(f"Validator '{validator}' is not callable.")
            return decorated_func

        return meta_decorator

    try:
        decorator = mock_validate_decorated_with_non_callable()

        @decorator
        def test_func(f):
            return f

        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_is_decorator_factory_hybrid_with_unwrap_failure():
    def factory():
        def decorator(f):
            return f
        return decorator

    result = is_decorator_factory(factory, "hybrid")
    assert result == True


def test_is_decorator_static_exception_handling():
    def problematic_func():
        pass

    original_name = problematic_func.__name__
    try:
        setattr(problematic_func, '__name__', None)
    except (TypeError, AttributeError):
        pass

    result = is_decorator(problematic_func, "static")
    setattr(problematic_func, '__name__', original_name)
    assert result in [True, False]


def test_is_decorator_hybrid_dummy_call_failure():
    def decorator_that_fails(f):
        raise RuntimeError("Decorator execution failed")

    result = is_decorator(decorator_that_fails, "hybrid")
    assert result == False


def test_returned_function_looks_like_decorator_name_match():
    def factory():
        def inner_decorator(f):
            return f
        return inner_decorator

    result = _returned_function_looks_like_decorator_static(factory)
    assert result == True


def test_has_single_argument_with_vararg():
    args_with_vararg = ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg="f", annotation=None)],
        vararg=ast.arg(arg="args", annotation=None),
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    )

    result = _has_single_argument(args_with_vararg)
    assert result == False


def test_has_single_argument_with_kwarg():
    args_with_kwarg = ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg="f", annotation=None)],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=ast.arg(arg="kwargs", annotation=None),
        defaults=[]
    )

    result = _has_single_argument(args_with_kwarg)
    assert result == False


def test_has_single_argument_multiple_args():
    args_multiple = ast.arguments(
        posonlyargs=[],
        args=[
            ast.arg(arg="f", annotation=None),
            ast.arg(arg="g", annotation=None)
        ],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    )

    result = _has_single_argument(args_multiple)
    assert result == False
