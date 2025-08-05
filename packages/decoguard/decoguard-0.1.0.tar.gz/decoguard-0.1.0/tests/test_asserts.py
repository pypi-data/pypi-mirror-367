from decoguard import asserts
from dummy import *
from typing import Callable, Any

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
    assert asserts.is_decorator(nested_decorator_factory_without_none(), "static") == False

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
    assert asserts.is_decorator(nested_decorator_factory_without_none(), "hybrid") == False

def test_is_decorator_factory_ok_static():
    assert asserts.is_decorator_factory(decorator_factory, "static") == True
    assert asserts.is_decorator_factory(decorator_factory_without_none, "static") == True

def test_is_decorator_factory_ok_static_nested():
    assert asserts.is_decorator_factory(nested_decorator_factory(), "static") == True
    assert asserts.is_decorator_factory(nested_decorator_factory_without_none(), "static") == True

def test_is_decorator_factory_ok_hybrid():
    assert asserts.is_decorator_factory(decorator_factory, "hybrid") == True
    assert asserts.is_decorator_factory(decorator_factory_without_none, "hybrid") == True

def test_is_decorator_factory_ok_hybrid_nested():
    assert asserts.is_decorator_factory(nested_decorator_factory(), "hybrid") == True
    assert asserts.is_decorator_factory(nested_decorator_factory_without_none(), "hybrid") == True

def test_is_decorator_factory_fail_static():
    assert asserts.is_decorator_factory(decorator, "static") == False
    assert asserts.is_decorator_factory(fun, "static") == False
    assert asserts.is_decorator_factory(fun_decorated, "static") == False
    assert asserts.is_decorator_factory(fun_decorated_factory, "static") == False

def test_is_decorator_factory_fail_static_nested():
    assert asserts.is_decorator_factory(nested_decorator(), "static") == False
    assert asserts.is_decorator_factory(nested_fun(), "static") == False
    assert asserts.is_decorator_factory(nested_fun_decorated(), "static") == False
    assert asserts.is_decorator_factory(nested_fun_decorated_factory(), "static") == False

def test_is_decorator_factory_fail_hybrid():
    assert asserts.is_decorator_factory(decorator, "hybrid") == False
    assert asserts.is_decorator_factory(fun, "hybrid") == False
    assert asserts.is_decorator_factory(fun_decorated, "hybrid") == False
    assert asserts.is_decorator_factory(fun_decorated_factory, "hybrid") == False

def test_is_decorator_factory_fail_hybrid_nested():
    assert asserts.is_decorator_factory(nested_decorator(), "hybrid") == False
    assert asserts.is_decorator_factory(nested_fun(), "hybrid") == False
    assert asserts.is_decorator_factory(nested_fun_decorated(), "hybrid") == False
    assert asserts.is_decorator_factory(nested_fun_decorated_factory(), "hybrid") == False

def test_get_signature_arg_types():
    assert asserts.get_signature_arg_types(decorator_factory_without_none) == {'param1' : (object,), 'param2': (object,)}
    assert asserts.get_signature_arg_types(decorator_factory) == {'param': (object,)}
    assert asserts.get_signature_arg_types(decorator) == {'func': (Callable,)}
    assert asserts.get_signature_arg_types(fun_decorated_factory) == {'param': (object,)}
    assert asserts.get_signature_arg_types(fun_decorated) == {'param': (object,)}
    assert asserts.get_signature_arg_types(fun) == {'param': (object,)}
    assert asserts.get_signature_arg_types(fun_decorated_without_wraps) == {'param': (object,)}
    assert asserts.get_signature_arg_types(fun_complex_type_hint) == {'param1': (int, str, type(None)), 'param2': (*list[str | int],)}

def test_get_signature_arg_types_nested():
    assert asserts.get_signature_arg_types(nested_decorator_factory_without_none()) == {'param1' : (object,), 'param2': (object,)}
    assert asserts.get_signature_arg_types(nested_decorator_factory()) == {'param': (object,)}
    assert asserts.get_signature_arg_types(nested_decorator()) == {'func': (Callable,)}
    assert asserts.get_signature_arg_types(nested_fun_decorated_factory()) == {'param': (object,)}
    assert asserts.get_signature_arg_types(nested_fun_decorated()) == {'param': (object,)}
    assert asserts.get_signature_arg_types(nested_fun()) == {'param': (object,)}
    assert asserts.get_signature_arg_types(nested_fun_decorated_without_wraps()) == {'param': (object,)}
    assert asserts.get_signature_arg_types(nested_fun_complex_type_hint()) == {'param1': (int, str, type(None)), 'param2': (*list[str | int],)}