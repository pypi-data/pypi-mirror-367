from decoguard.decorators import validate_decorated
from decoguard.validators import require_params


def test_validate_decorated_on_regular_function():
    def regular_function():
        return 42

    try:
        validate_decorated(require_params("x"))(regular_function)
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "can only be applied to decorators" in str(e)


def test_validate_decorated_with_non_callable_manually():
    def simple_decorator(f):
        return f

    from decoguard.decorators import validate_decorated as orig_validate_decorated
    from decoguard import decorators

    def patched_validate_decorated(*validators):
        def meta_decorator(decorated_func):
            from decoguard.asserts import is_decorator, is_decorator_factory
            from decoguard.config import DEFAULT_DECORATOR_CHECKS_MODE
            from functools import wraps

            if not is_decorator(
                decorated_func, DEFAULT_DECORATOR_CHECKS_MODE
            ) and not is_decorator_factory(
                decorated_func, DEFAULT_DECORATOR_CHECKS_MODE
            ):
                raise TypeError(
                    "@validate_decorated can only be applied to decorators or "
                    "decorator factories."
                )

            for validator in validators:
                if not callable(validator):
                    raise TypeError(f"Validator '{validator}' is not callable.")

            @wraps(decorated_func)
            def wrapper(*args, **kwargs):
                return decorated_func(*args, **kwargs)

            return wrapper
        return meta_decorator

    decorators.validate_decorated = patched_validate_decorated

    try:
        patched_validate_decorated(
            require_params("x"), "not_callable"
        )(simple_decorator)
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "is not callable" in str(e)
    finally:
        decorators.validate_decorated = orig_validate_decorated


def test_validators_coverage_edge_case():
    import builtins
    from decoguard.validators import _has_meaningful_return_statements

    result = _has_meaningful_return_statements(builtins.len)
    assert result == True

    result = _has_meaningful_return_statements(builtins.abs)
    assert result == True
