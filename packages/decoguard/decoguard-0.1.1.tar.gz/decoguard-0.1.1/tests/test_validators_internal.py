import builtins

from decoguard.decorators import validate_decorated
from decoguard.validators import (
    _asserts_tuple_expected_params,
    _has_meaningful_return_statements,
    require_at_least_n_params,
    require_params,
)


def test_has_meaningful_return_statements_edge_cases():
    def func_with_none_name_return():
        return None

    def func_with_constant_none():
        return None

    assert _has_meaningful_return_statements(func_with_none_name_return) == False
    assert _has_meaningful_return_statements(func_with_constant_none) == False


def test_additional_edge_cases():
    result = _has_meaningful_return_statements(builtins.len)
    assert result == True

    result = _has_meaningful_return_statements(builtins.print)
    assert result == True


def test_asserts_tuple_expected_params_no_params():
    try:
        _asserts_tuple_expected_params()
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_asserts_tuple_expected_params_invalid_type_in_tuple():
    try:
        _asserts_tuple_expected_params(("param1", "not_a_type"))  # type: ignore
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_has_meaningful_return_none_id():
    def func_with_none_id():
        return None

    result = _has_meaningful_return_statements(func_with_none_id)
    assert result == False


def test_require_at_least_n_params_zero():
    try:
        @validate_decorated(require_at_least_n_params(0, "x"))
        def deco_zero(f):
            return f
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_require_at_least_n_params_edge_cases():
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


def test_validator_error_cases():
    try:
        @validate_decorated(require_params(("param1",)))
        def bad_decorator(f):
            return f
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_validator_chaining():
    @validate_decorated(require_params("a"), require_params("b"))
    def deco(f):
        return f

    @deco
    def chained_func(a, b, c):
        pass


def test_unicode_parameter_names():
    @validate_decorated(require_params("α"))
    def deco(f):
        return f

    @deco
    def unicode_func(α):
        pass


def test_edge_case_parameters_with_defaults():
    @validate_decorated(require_params("a", "b", "c"))
    def deco(f):
        return f

    @deco
    def myfunc(a, b, c=None):
        pass

    @deco
    def anotherfunc(a, b=None, c=None):
        pass


def test_edge_case_parameters_with_varargs():
    @validate_decorated(require_params("a", "b"))
    def deco(f):
        return f

    @deco
    def myfunc(a, b, *args):
        pass

    @deco
    def anotherfunc(a, b, *args, **kwargs):
        pass


def test_function_with_annotations():
    @validate_decorated(require_params("a", "b"))
    def deco(f):
        return f

    @deco
    def annotated_func(a: int, b: str) -> bool:
        return True
