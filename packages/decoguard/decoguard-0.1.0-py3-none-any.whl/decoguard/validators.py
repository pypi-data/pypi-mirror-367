from typing import Callable, Any
from decoguard.errors import DecoratorUsageValidationError
from decoguard.asserts import get_signature_arg_types, _parse_function_source, _find_function_node
from inspect import signature, Parameter
import ast

def _create_validation_error(func_name: str, decorator_name: str, message: str) -> DecoratorUsageValidationError:
    """
    Helper function to create standardized validation error messages.
    """
    return DecoratorUsageValidationError(
        f"Function '{func_name}()' is using '@{decorator_name}' decorator which {message}"
    )

def _has_meaningful_return_statements(func: Callable[..., Any]) -> bool:
    """
    Check if a function has at least one meaningful return statement (not 'return None' or empty return).
    Returns True if meaningful return statements are found, False otherwise.
    """
    tree = _parse_function_source(func)
    if tree is None:
        return True  # If we can't parse, assume it's valid
    
    target_func = _find_function_node(tree, func.__name__)
    if target_func is None:
        return True  # If we can't find the function, assume it's valid
    
    for node in ast.walk(target_func):
        if isinstance(node, ast.Return):
            if node.value is None:
                continue
            elif isinstance(node.value, ast.Constant) and node.value.value is None:
                continue
            elif isinstance(node.value, ast.Name) and node.value.id == 'None':
                continue
            else:
                return True  # Found a meaningful return
    
    return False  # No meaningful return found

def _asserts_tuple_expected_params(*expected_params: str |  tuple[str, *tuple[type, ...]]) -> bool:
    """
    Ensure that the expected parameters are either strings or tuples starting with a string followed by types.
    Raises TypeError if any of the expected parameters is not a string or a tuple with the correct format.
    """
    if not expected_params:
        raise TypeError("Expected at least one expected parameter, got none.")

    for expected_p in expected_params:
        if not isinstance(expected_p, str):
            if isinstance(expected_p, tuple) and len(expected_p) >= 2 and isinstance(expected_p[0], str):

                for val in expected_p[1:]:
                    if not isinstance(val, type):
                        raise TypeError(f"'{val}' is a ill-formated tuple, it needs to start with a string, followed by accepted types, got {type(val).__name__}")

            else:
                raise TypeError(f"All required parameter names must be strings or tuples that start with a string then followed by accepted types, got {type(expected_p).__name__}: {expected_p}")

def _validate_function_params(func: Callable[..., Any], expected_params: tuple) -> list[str]:
    """
    Helper function to validate function parameters against expected parameters.
    Returns a list of valid parameter names that match the expected criteria.
    """
    func_params = get_signature_arg_types(func)
    valid_params = []
    
    for expected_p in expected_params:
        is_expected_str_format = isinstance(expected_p, str)
        expected_name = expected_p if is_expected_str_format else expected_p[0]
        expected_types = Any if is_expected_str_format else expected_p[1:]
        
        is_name_in_params = expected_name in func_params.keys()
        
        if is_name_in_params:
            is_type_correct = Any == expected_types or all(t in func_params[expected_name] for t in expected_types)
            
            if is_type_correct:
                valid_params.append(expected_name)
                
    return valid_params

def _format_expected_params(expected_params: tuple) -> list[str]:
    """
    Helper function to format expected parameters for error messages.
    """
    return [f"{name} (of type {' or '.join(f"'{t.__name__}'" for t in types)})" if types != Any else name 
            for expected_p in expected_params 
            for name, types in [(expected_p if isinstance(expected_p, str) else expected_p[0], 
                               Any if isinstance(expected_p, str) else expected_p[1:])]]    

def require_params(*expected_params: str |  tuple[str, *tuple[type, ...]]) -> Callable[[Callable[..., Any], Any], Callable[..., Any]]:
    """
    Ensure that the decorated function has the required parameters.
    Take parameter names as strings or tuples composed of the parameter names and the expected types.
    Type requirement is done by parsing the type hint, so it's not type-safe.

    Parameters:
        *expected_params: Parameter names as strings or tuples composed of the parameter names and the expected types

    Raises:
        TypeError: if arguments are not str or not (str, type, ..., type)
        DecoratorUsageValidationError: if the decorated decorator is not used correctly
    """
    
    return require_at_least_n_params(len(expected_params), *expected_params)

def require_at_least_n_params(n: int, *expected_params: str | tuple[str, *tuple[type, ...]]) -> Callable[[Callable[..., Any], Any], Callable[..., Any]]:
    """
    Ensure that the decorated function has at least n required parameters.
    Take parameter names as strings or tuples composed of the parameter names and the expected types.
    Type requirement is done by parsing the type hint, so it's not type-safe.

    Parameters:
        n: Minimum number of required parameters that must be present
        *expected_params: Parameter names as strings or tuples composed of the parameter names and the expected types

    Raises:
        TypeError: if `n` is not a positive integer or if arguments are not str or not (str, type, ..., type)
        DecoratorUsageValidationError: if the decorated decorator is not used correctly
    """

    if not expected_params:
        raise TypeError("Expected at least one expected parameter, got none.")

    if not isinstance(n, int) or 1 > n or n > len(expected_params):
        raise TypeError(f"Expected n >= 1 and n <= {len(expected_params)}, got {n} of type {type(n).__name__}")

    _asserts_tuple_expected_params(*expected_params)

    def validator(func: Callable[..., Any], _decorator: Any = None) -> Callable[..., Any]:
        valid_params = _validate_function_params(func, expected_params)
        
        if len(valid_params) < n:
            formated_expected = _format_expected_params(expected_params)
            message = (f"requires at least {n if n != len(expected_params) else 'all'} of the following parameters, "
                      f"but only {len(valid_params)} are present: {', '.join(formated_expected)}"
                      f"\nType requirement implies that the parameter must be annotated with a type hint in function definition.")
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        return func
    return validator

def no_params() -> Callable[[Callable[..., Any], Any], Callable[..., Any]]:
    """
    Ensure that the decorated function takes no parameters (except self for methods).
    This validator checks that the function signature has no required or optional parameters.
    The `self` parameter is automatically ignored to allow usage with methods.

    Raises:
        DecoratorUsageValidationError: if the decorated function has any parameters (other than `self`)
    """
    
    def validator(func: Callable[..., Any], _decorator: Any = None) -> Callable[..., Any]:
        func_params = get_signature_arg_types(func)
        
        filtered_params = {name: types for name, types in func_params.items() if name != 'self'}
        
        if filtered_params:
            param_names = list(filtered_params.keys())
            message = f"requires no parameters, but found {len(param_names)} parameter(s): {', '.join(param_names)}"
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        return func
    return validator

def no_optional_params() -> Callable[[Callable[..., Any], Any], Callable[..., Any]]:
    """
    Ensure that the decorated function has no optional parameters (except self for methods).
    This validator checks that all function parameters are required (no default values).
    The `self` parameter is automatically ignored to allow usage with methods.

    Raises:
        DecoratorUsageValidationError: if the decorated function has any optional parameters (parameters with default values)
    """
    
    def validator(func: Callable[..., Any], _decorator: Any = None) -> Callable[..., Any]:
        sig = signature(func)
        optional_params = []
        
        for name, param in sig.parameters.items():
            if name != 'self' and param.default != Parameter.empty:
                optional_params.append(name)
        
        if optional_params:
            message = f"requires no optional parameters, but found {len(optional_params)} optional parameter(s): {', '.join(optional_params)}"
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        return func
    return validator

def has_return() -> Callable[[Callable[..., Any], Any], Callable[..., Any]]:
    """
    Ensure that the decorated function has a return type annotation and contains at least one return statement that is not 'return None'.
    This validator checks that the function signature includes a return type annotation and that the function body contains meaningful return statements.

    Raises:
        DecoratorUsageValidationError: if the decorated function does not have a return type annotation or does not contain at least one meaningful return statement (not 'return None' or empty return)
    """
    
    def validator(func: Callable[..., Any], _decorator: Any = None) -> Callable[..., Any]:
        sig = signature(func)
        
        if sig.return_annotation == sig.empty:
            message = "requires a return type annotation, but none found"
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        
        if not _has_meaningful_return_statements(func):
            message = "requires at least one return statement that is not 'return None'"
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        
        return func
    return validator

def no_return() -> Callable[[Callable[..., Any], Any], Callable[..., Any]]:
    """
    Ensure that the decorated function has no return type annotation and contains no meaningful return statements.
    This validator checks that the function signature has no return type annotation and that the function body contains no meaningful return statements.

    Raises:
        DecoratorUsageValidationError: if the decorated function has a return type annotation or contains at least one meaningful return statement
    """
    
    def validator(func: Callable[..., Any], _decorator: Any = None) -> Callable[..., Any]:
        sig = signature(func)
        
        if sig.return_annotation != sig.empty:
            message = "requires no return type annotation, but found one"
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        
        if _has_meaningful_return_statements(func):
            message = "requires no meaningful return statements, but found at least one"
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        
        return func
    return validator

def custom_validator(validation_func: Callable[[Callable[..., Any]], bool], error_message: str = "does not meet custom validation requirements") -> Callable[[Callable[..., Any], Any], Callable[..., Any]]:
    """
    Allow users to define their own validation logic using a custom function.
    The validation function should take the decorated function as input and return True if valid, False otherwise.
    
    Parameters:
        validation_func: A function that takes the decorated function and returns True if valid, False if invalid
        error_message: Custom error message to display when validation fails (optional)

    Raises:
        TypeError: if `validation_func` is not callable or `error_message` is not a string
        DecoratorUsageValidationError: if the custom validation fails or if the validation function raises an exception
    """
    
    if not callable(validation_func):
        raise TypeError("validation_func must be callable")
    
    if not isinstance(error_message, str):
        raise TypeError("error_message must be a string")
    
    def validator(func: Callable[..., Any], _decorator: Any = None) -> Callable[..., Any]:
        try:
            is_valid = validation_func(func)
        except Exception as e:
            message = f"custom validation failed with error: {str(e)}"
            raise _create_validation_error(func.__name__, _decorator.__name__, message)
        
        if not is_valid:
            raise _create_validation_error(func.__name__, _decorator.__name__, error_message)
        
        return func
    return validator