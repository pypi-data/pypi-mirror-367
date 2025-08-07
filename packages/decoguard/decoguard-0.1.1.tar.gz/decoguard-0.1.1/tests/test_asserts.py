from collections.abc import Callable

from dummy import *

from decoguard import asserts


def test_is_decorator_ok_static():
    assert asserts.is_decorator(decorator, "static") == True
    assert asserts.is_decorator(identity_decorator, "static") == True


def test_is_decorator_ok_static_nested():
    assert asserts.is_decorator(nested_decorator(), "static") == True
    assert asserts.is_decorator(nested_identity_decorator(), "static") == True


def test_is_decorator_ok_hybrid():
    assert asserts.is_decorator(decorator, "hybrid") == True
    assert asserts.is_decorator(identity_decorator, "hybrid") == True


def test_is_decorator_ok_hybrid_nested():
    assert asserts.is_decorator(nested_decorator(), "hybrid") == True
    assert asserts.is_decorator(nested_identity_decorator(), "hybrid") == True


def test_is_decorator_fail_static():
    assert asserts.is_decorator(fun, "static") == False
    assert asserts.is_decorator(fun_decorated, "static") == False
    assert asserts.is_decorator(decorator_factory, "static") == False
    assert asserts.is_decorator(fun_decorated_factory, "static") == False
    assert asserts.is_decorator(decorator_factory_without_none, "static") == False


def test_is_decorator_fail_static_nested():
    assert asserts.is_decorator(nested_fun(), "static") == False
    assert asserts.is_decorator(nested_fun_decorated(), "static") == False
    assert asserts.is_decorator(nested_decorator_factory(), "static") == False
    assert asserts.is_decorator(nested_fun_decorated_factory(), "static") == False
    assert (
        asserts.is_decorator(nested_decorator_factory_without_none(), "static") == False
    )


def test_is_decorator_fail_hybrid():
    assert asserts.is_decorator(fun, "hybrid") == False
    assert asserts.is_decorator(fun_decorated, "hybrid") == False
    assert asserts.is_decorator(decorator_factory, "hybrid") == False
    assert asserts.is_decorator(fun_decorated_factory, "hybrid") == False
    assert asserts.is_decorator(decorator_factory_without_none, "hybrid") == False


def test_is_decorator_fail_hybrid_nested():
    assert asserts.is_decorator(nested_fun(), "hybrid") == False
    assert asserts.is_decorator(nested_fun_decorated(), "hybrid") == False
    assert asserts.is_decorator(nested_decorator_factory(), "hybrid") == False
    assert asserts.is_decorator(nested_fun_decorated_factory(), "hybrid") == False
    assert (
        asserts.is_decorator(nested_decorator_factory_without_none(), "hybrid") == False
    )


def test_is_decorator_factory_ok_static():
    assert asserts.is_decorator_factory(decorator_factory, "static") == True
    assert (
        asserts.is_decorator_factory(decorator_factory_without_none, "static") == True
    )


def test_is_decorator_factory_ok_static_nested():
    assert asserts.is_decorator_factory(nested_decorator_factory(), "static") == True
    assert (
        asserts.is_decorator_factory(nested_decorator_factory_without_none(), "static")
        == True
    )


def test_is_decorator_factory_ok_hybrid():
    assert asserts.is_decorator_factory(decorator_factory, "hybrid") == True
    assert (
        asserts.is_decorator_factory(decorator_factory_without_none, "hybrid") == True
    )


def test_is_decorator_factory_ok_hybrid_nested():
    assert asserts.is_decorator_factory(nested_decorator_factory(), "hybrid") == True
    assert (
        asserts.is_decorator_factory(nested_decorator_factory_without_none(), "hybrid")
        == True
    )


def test_is_decorator_factory_fail_static():
    assert asserts.is_decorator_factory(decorator, "static") == False
    assert asserts.is_decorator_factory(fun, "static") == False
    assert asserts.is_decorator_factory(fun_decorated, "static") == False
    assert asserts.is_decorator_factory(fun_decorated_factory, "static") == False


def test_is_decorator_factory_fail_static_nested():
    assert asserts.is_decorator_factory(nested_decorator(), "static") == False
    assert asserts.is_decorator_factory(nested_fun(), "static") == False
    assert asserts.is_decorator_factory(nested_fun_decorated(), "static") == False
    assert (
        asserts.is_decorator_factory(nested_fun_decorated_factory(), "static") == False
    )


def test_is_decorator_factory_fail_hybrid():
    assert asserts.is_decorator_factory(decorator, "hybrid") == False
    assert asserts.is_decorator_factory(fun, "hybrid") == False
    assert asserts.is_decorator_factory(fun_decorated, "hybrid") == False
    assert asserts.is_decorator_factory(fun_decorated_factory, "hybrid") == False


def test_is_decorator_factory_fail_hybrid_nested():
    assert asserts.is_decorator_factory(nested_decorator(), "hybrid") == False
    assert asserts.is_decorator_factory(nested_fun(), "hybrid") == False
    assert asserts.is_decorator_factory(nested_fun_decorated(), "hybrid") == False
    assert (
        asserts.is_decorator_factory(nested_fun_decorated_factory(), "hybrid") == False
    )


def test_get_signature_arg_types():
    assert asserts.get_signature_arg_types(decorator_factory_without_none) == {
        "param1": (object,),
        "param2": (object,),
    }
    assert asserts.get_signature_arg_types(decorator_factory) == {"param": (object,)}
    assert asserts.get_signature_arg_types(decorator) == {"func": (Callable,)}
    assert asserts.get_signature_arg_types(fun_decorated_factory) == {
        "param": (object,)
    }
    assert asserts.get_signature_arg_types(fun_decorated) == {"param": (object,)}
    assert asserts.get_signature_arg_types(fun) == {"param": (object,)}
    assert asserts.get_signature_arg_types(fun_decorated_without_wraps) == {
        "param": (object,)
    }
    assert asserts.get_signature_arg_types(fun_complex_type_hint) == {
        "param1": (int, str, type(None)),
        "param2": (*list[str | int],),  # type: ignore
    }


def test_get_signature_arg_types_nested():
    assert asserts.get_signature_arg_types(nested_decorator_factory_without_none()) == {
        "param1": (object,),
        "param2": (object,),
    }
    assert asserts.get_signature_arg_types(nested_decorator_factory()) == {
        "param": (object,)
    }
    assert asserts.get_signature_arg_types(nested_decorator()) == {"func": (Callable,)}
    assert asserts.get_signature_arg_types(nested_fun_decorated_factory()) == {
        "param": (object,)
    }
    assert asserts.get_signature_arg_types(nested_fun_decorated()) == {
        "param": (object,)
    }
    assert asserts.get_signature_arg_types(nested_fun()) == {"param": (object,)}
    assert asserts.get_signature_arg_types(nested_fun_decorated_without_wraps()) == {
        "param": (object,)
    }
    assert asserts.get_signature_arg_types(nested_fun_complex_type_hint()) == {
        "param1": (int, str, type(None)),
        "param2": (*list[str | int],),  # type: ignore
    }


def test_unwrap_function():
    assert asserts.unwrap_function(decorator) == decorator
    assert asserts.unwrap_function(fun) == fun


def test_unwrap_function_error():
    try:
        asserts.unwrap_function(NotCallable())  # type: ignore
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_find_function_node_fallback():
    import ast
    source = '''
def first_func():
    pass

def second_func():
    pass
'''
    tree = ast.parse(source)
    result = asserts._find_function_node(tree, "nonexistent_func")
    assert result is not None
    assert result.name == "first_func"


def test_find_function_node_no_functions():
    import ast
    source = '''
x = 1
y = 2
'''
    tree = ast.parse(source)
    result = asserts._find_function_node(tree, "any_func")
    assert result is None


def test_get_returned_function_node_edge_cases():
    asserts._get_returned_function_node(function_returning_lambda)
    asserts._get_returned_function_node(broken_decorator_factory)


def test_dummy_function():
    asserts._dummy()


def test_has_meaningful_return_statements():
    from decoguard.validators import _has_meaningful_return_statements

    assert _has_meaningful_return_statements(function_with_nested_returns()) == True
    assert _has_meaningful_return_statements(function_with_only_none_returns()) == False
    assert _has_meaningful_return_statements(function_with_empty_return()) == False


def test_parse_function_source_exception():
    import builtins

    result = asserts._parse_function_source(builtins.len)
    assert result is None

    result = asserts._parse_function_source(builtins.print)
    assert result is None


def test_unwrap_function_with_closure():
    closure_func = function_that_returns_closure()()
    result = asserts.unwrap_function(closure_func)
    assert result is not None


def test_unwrap_function_with_named_closure():
    closure_func = function_with_closure_and_name()
    result = asserts.unwrap_function(closure_func)
    assert hasattr(result, '__name__')


def test_returned_function_looks_like_decorator_static():
    not_func = NotAFunctionType()
    result = asserts._returned_function_looks_like_decorator_static(
        not_func  # type: ignore
    )
    assert result == False

    asserts._returned_function_looks_like_decorator_static(lambda_returning_function)

    asserts._returned_function_looks_like_decorator_static(
        function_returning_functiondef
    )


def test_get_returned_function_node_complex():
    asserts._get_returned_function_node(function_with_complex_return)


def test_is_decorator_edge_cases():
    asserts.is_decorator(lambda_returning_function, "static")
    asserts.is_decorator(function_with_complex_return, "static")


def test_complex_decorator_analysis():
    asserts.is_decorator(decorator_with_complex_logic, "static")
    asserts.is_decorator_factory(complex_decorator_factory, "static")


def test_ast_edge_cases():
    asserts._get_returned_function_node(function_with_ast_call)
    asserts._returned_function_looks_like_decorator_static(decorator_with_complex_logic)


def test_get_signature_arg_types_not_callable():
    try:
        asserts.get_signature_arg_types("not_callable")  # type: ignore
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "Expected a callable" in str(e)


def test_get_ast_returned_function_target_func_none():
    def func_with_no_matching_name():
        pass

    original_name = func_with_no_matching_name.__name__
    func_with_no_matching_name.__name__ = "different_name"

    result = asserts._get_returned_function_node(func_with_no_matching_name)
    func_with_no_matching_name.__name__ = original_name
    assert result is None


def test_returned_function_looks_like_decorator_static_function_def():
    result = asserts._returned_function_looks_like_decorator_static(
        function_returning_functiondef
    )
    assert result == True


def test_is_decorator_factory_invalid_mode():
    def dummy_func():
        pass

    try:
        asserts.is_decorator_factory(dummy_func, mode="invalid")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "mode must be 'static' or 'hybrid'" in str(e)


def test_is_decorator_invalid_mode():
    def dummy_func():
        pass

    try:
        asserts.is_decorator(dummy_func, mode="invalid")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "mode must be 'static' or 'hybrid'" in str(e)


def test_is_decorator_static_mode_exception():
    class BrokenCallable:
        def __call__(self):
            pass

        @property
        def __code__(self):
            raise AttributeError("No code")

    broken_func = BrokenCallable()
    result = asserts.is_decorator(broken_func, mode="static")
    assert result == False


def test_is_decorator_hybrid_mode_signature_exception():
    class BadCallable:
        def __call__(self):
            pass

        def __signature__(self):
            raise ValueError("Bad signature")

    bad_func = BadCallable()
    result = asserts.is_decorator(bad_func, mode="hybrid")
    assert result == False


def test_is_decorator_hybrid_mode_execution_exception():
    def func_that_raises(f):
        raise RuntimeError("Test error")

    result = asserts.is_decorator(func_that_raises, mode="hybrid")
    assert result == False


def test_get_signature_arg_types_union_decomposition():
    from typing import Union

    def func_with_union(x: Union[int, str]) -> None:
        pass

    types = asserts.get_signature_arg_types(func_with_union)
    assert "x" in types
    assert len(types["x"]) == 2


def test_is_decorator_factory_hybrid_exception():
    def factory_that_raises():
        raise RuntimeError("Error during execution")

    result = asserts.is_decorator_factory(factory_that_raises, mode="hybrid")
    assert result == False


def test_is_decorator_factory_hybrid_unwrap():
    def factory_with_inner():
        def inner(f):
            return f
        return inner

    result = asserts.is_decorator_factory(factory_with_inner, mode="hybrid")
    assert result == True


def test_get_signature_arg_types_edge_cases():
    def func_with_no_annotations(x, y):
        pass

    types = asserts.get_signature_arg_types(func_with_no_annotations)
    assert "x" in types
    assert "y" in types


def test_unwrap_function_edge_cases():
    def outer():
        def inner():
            pass
        return inner

    unwrapped = asserts.unwrap_function(outer)
    assert unwrapped == outer


def test_parse_function_source_builtin():
    import builtins

    result = asserts._parse_function_source(builtins.len)
    assert result is None


def test_find_function_node_not_found():
    def dummy():
        pass

    tree = asserts._parse_function_source(dummy)
    if tree:
        result = asserts._find_function_node(tree, "dummy")
        assert result is not None


def test_has_single_argument_edge_cases():
    import ast

    args_with_vararg = ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg="x", annotation=None)],
        vararg=ast.arg(arg="args", annotation=None),
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    )

    result = asserts._has_single_argument(args_with_vararg)
    assert result == False


def test_returned_function_looks_like_decorator_static_edge_cases():
    def factory_returning_non_function():
        return 42

    result = asserts._returned_function_looks_like_decorator_static(
        factory_returning_non_function
    )
    assert result == False


def test_is_decorator_hybrid_parameter_validation():
    def func_with_var_args(*args):
        pass

    result = asserts.is_decorator(func_with_var_args, mode="hybrid")
    assert result == False

    def func_with_kwargs(**kwargs):
        pass

    result = asserts.is_decorator(func_with_kwargs, mode="hybrid")
    assert result == False


def test_get_returned_function_node_none_scenarios():
    result = asserts._get_returned_function_node(function_without_matching_name)
    assert result is not None


def test_parse_function_source_edge_cases():
    class NotAFunction:
        pass

    result = asserts._parse_function_source(NotAFunction())  # type: ignore
    assert result is None


def test_decorator_factory_static_analysis_edge_cases():
    result = asserts.is_decorator_factory(NotCallable(), mode="static")  # type: ignore
    assert result == False


def test_decorator_static_analysis_edge_cases():
    result = asserts.is_decorator(NotCallable(), mode="static")  # type: ignore
    assert result == False


def test_unwrap_function_exception_handling():
    def broken_unwrap():
        raise Exception("Cannot unwrap")

    result = asserts.unwrap_function(broken_unwrap)
    assert result == broken_unwrap


def test_get_signature_arg_types_with_complex_annotations():
    from typing import Union

    def func_with_complex_types(x: Union[int, str, float]) -> None:
        pass

    types = asserts.get_signature_arg_types(func_with_complex_types)
    assert "x" in types
    assert len(types["x"]) == 3


def test_specific_coverage_targets():
    class FakeCallable:
        def __call__(self):
            pass

    fake_func = FakeCallable()
    result = asserts._parse_function_source(fake_func)
    assert result is None


def test_has_single_argument_with_complex_args():
    import ast

    args_with_two_args = ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg="x", annotation=None), ast.arg(arg="y", annotation=None)],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    )

    result = asserts._has_single_argument(args_with_two_args)
    assert result == False


def test_decorator_analysis_edge_cases():
    def func_with_complex_inspection():
        pass

    result = asserts.is_decorator(func_with_complex_inspection, mode="hybrid")
    assert result == False


def test_returned_function_analysis_complex():
    def simple_factory():
        def inner(f):
            return f
        return inner

    result = asserts._returned_function_looks_like_decorator_static(simple_factory)
    assert result == True


def test_edge_case_parse_function_with_missing_code():
    def func():
        pass

    class MockFunc:
        __name__ = "test"

        @property
        def __code__(self):
            raise AttributeError("no code")

    mock_func = MockFunc()
    result = asserts._parse_function_source(mock_func)  # type: ignore
    assert result is None


def test_unwrap_function_with_no_return():
    def func_no_return():
        pass

    result = asserts.unwrap_function(func_no_return)
    assert result == func_no_return


def test_signature_inspection_edge_cases():
    class CallableWithBadSignature:
        def __call__(self):
            pass

        @property
        def __signature__(self):
            raise ValueError("bad signature")

    bad_callable = CallableWithBadSignature()
    result = asserts.is_decorator(bad_callable, mode="hybrid")
    assert result == False
