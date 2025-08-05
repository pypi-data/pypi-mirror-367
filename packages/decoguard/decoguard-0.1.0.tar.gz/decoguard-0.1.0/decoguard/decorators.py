
from functools import wraps
from typing import Callable, Any
from decoguard.asserts import is_decorator, is_decorator_factory
from decoguard.config import DEFAULT_DECORATOR_CHECKS_MODE

def validate_decorated(*validators: Callable[[Callable[..., Any], Any], Callable[..., Any]]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    For all provided validators, ensures that any function using the decorated decorator complies with those validators.
    Can only be applied to decorators or decorator factories.

    Parameters:
        *validators: Validator functions that check if the decorated function meets certain criteria

    Raises:
        TypeError: if used on a regular function or if a non-callable argument is provided
    """
    def meta_decorator(decorated_func: Callable[..., Any]) -> Callable[..., Any]:
        if not is_decorator(decorated_func, DEFAULT_DECORATOR_CHECKS_MODE) and not is_decorator_factory(decorated_func, DEFAULT_DECORATOR_CHECKS_MODE):
            raise TypeError("@validate_decorated can only be applied to decorators or decorator factories.")
    
        for validator in validators:
            if not callable(validator):
                raise TypeError(f"Validator '{validator}' is not callable.")

        @wraps(decorated_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            if is_decorator(decorated_func, DEFAULT_DECORATOR_CHECKS_MODE):
                func = args[0]
                for validator in validators:
                    func = validator(func, decorated_func)
                return decorated_func(func)
            
            else:
                def actual_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                    for validator in validators:
                        func = validator(func, decorated_func)
                        
                    inner_decorator = decorated_func(*args, **kwargs)
                    return inner_decorator(func)
                
                return actual_decorator
        return wrapper
    return meta_decorator