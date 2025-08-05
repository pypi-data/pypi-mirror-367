from inspect import signature, Parameter, getsource
from typing import Callable, Any, get_type_hints, get_origin
from collections.abc import Callable as abc_Callable
from types import FunctionType
import ast
import textwrap

__all__ = ["is_decorator", "is_decorator_factory", "unwarp_function", "get_signature_arg_types"]

def _dummy() -> None:
    """A dummy function used for decorator checks."""
    pass

def _parse_function_source(func: Callable) -> ast.Module | None:
    """
    Parse the source code of a function into an AST.
    Returns None if parsing fails.
    """
    try:
        source = getsource(func)
        source = textwrap.dedent(source)
        return ast.parse(source)
    except (OSError, TypeError, SyntaxError):
        return None

def _find_function_node(tree: ast.Module, func_name: str) -> ast.FunctionDef | None:
    """
    Find a function definition node by name in the AST tree.
    Falls back to the first function if not found by name.
    """
    target_func = None
    
    # Search for the function definition by name
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            target_func = node
            break
    
    # If we didn't find it by name, try to use the first function
    if target_func is None:
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                target_func = node
                break
    
    return target_func

def unwarp_function(func: Callable) -> Callable:
    """
    Unwraps a function if it is a closure wrapping another function.
    If the function is not a closure, it returns the function itself.

    Parameters:
        func: The callable to unwrap

    Raises:
        TypeError: if the provided argument is not callable
    """
    if not callable(func):
        raise TypeError(f"Expected a callable, got {type(func).__name__}")

    closure = getattr(func, "__closure__", None)
    if closure:
        for cell in closure:
            cell_value = cell.cell_contents
            if callable(cell_value) and hasattr(cell_value, "__name__"):
                return cell_value
    return func

def _get_returned_function_node(func: Callable) -> Any:
    """
    Gets the AST node of the function returned by the outer function, if any.
    """
    tree = _parse_function_source(func)
    if tree is None:
        return None

    target_func = _find_function_node(tree, func.__name__)
    if target_func is None:
        return None

    defined_funcs = {}
    returned_func_name = None
    returned_lambda = None

    for stmt in target_func.body:
        if isinstance(stmt, ast.FunctionDef):
            defined_funcs[stmt.name] = stmt
        elif isinstance(stmt, ast.Return):
            val = stmt.value
            if isinstance(val, ast.Name):
                returned_func_name = val.id
            elif isinstance(val, ast.Lambda):
                returned_lambda = val

    if returned_lambda:
        return returned_lambda

    if returned_func_name and returned_func_name in defined_funcs:
        return defined_funcs[returned_func_name]

    return None


def _has_single_argument(args: ast.arguments) -> bool:
    """
    Check if function arguments represent a single positional argument.
    """
    return len(args.args) == 1 and not args.vararg and not args.kwarg

def _returned_function_looks_like_decorator_static(func: Callable) -> bool:
    """
    AST-only: determines whether the returned function looks like a decorator.
    """
    if not isinstance(func, FunctionType):
        return False

    returned_func = _get_returned_function_node(func)
    if returned_func is None:
        return False

    if isinstance(returned_func, ast.Lambda):
        return True

    if isinstance(returned_func, ast.FunctionDef):
        return _has_single_argument(returned_func.args)

    return False


def is_decorator_factory(func: Callable, mode: str = "static") -> bool:
    """
    Returns True if the function is a decorator factory.
    In 'static' mode, no execution is performed.
    In 'hybrid' mode, dynamically inspect the callable, should not be used with side-effecting functions.

    Parameters:
        func: The callable to check
        mode: The inspection mode - 'static' (no execution) or 'hybrid' (dynamic inspection)

    Raises:
        ValueError: if `mode` is invalid

    Returns:
        bool: True if the function is a decorator factory, False otherwise
    """
    if not isinstance(func, FunctionType):
        return False

    if mode == "static":
        return _returned_function_looks_like_decorator_static(func)

    elif mode == "hybrid":
        if _returned_function_looks_like_decorator_static(func):
            return True

        try:
            inner = unwarp_function(func)
            if inner is not func and is_decorator(inner, mode="hybrid"):
                return True
        except Exception:
            pass

        return False

    else:
        raise ValueError("mode must be 'static' or 'hybrid'")

def is_decorator(func: Callable, mode: str = "static") -> bool:
    """
    Returns True if the function is a decorator (takes a function and returns a function).
    In 'static' mode, no execution is performed.
    In 'hybrid' mode, dynamically inspect the callable, should not be used with side-effecting functions.

    Parameters:
        func: The callable to check
        mode: The inspection mode - 'static' (no execution) or 'hybrid' (dynamic inspection)

    Raises:
        ValueError: if `mode` is invalid

    Returns:
        bool: True if the function is a decorator, False otherwise
    """
    if not isinstance(func, FunctionType):
        return False

    if is_decorator_factory(func, mode=mode):
        return False

    if mode == "static":
        try:
            tree = _parse_function_source(func)
            if tree is None:
                return False
            
            target_func = _find_function_node(tree, func.__name__)
            if target_func is None:
                return False
            
            if not _has_single_argument(target_func.args):
                return False

            for node in ast.walk(target_func):
                if isinstance(node, ast.Return):
                    val = node.value

                    # Identity decorator
                    if isinstance(val, ast.Name) and val.id == target_func.args.args[0].arg:
                        return True
                    
                    if isinstance(val, (ast.FunctionDef, ast.Lambda)):
                        return True
                    
                    if isinstance(val, ast.Name):
                        for stmt in target_func.body:
                            if isinstance(stmt, ast.FunctionDef) and stmt.name == val.id:
                                return True
            return False
        except Exception:
            return False

    elif mode == "hybrid":
        try:
            sig = signature(func)
            params = list(sig.parameters.values())
        except (ValueError, TypeError):
            return False

        if (
            len(params) != 1
            or params[0].kind not in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
            or params[0].default is not Parameter.empty
            or params[0].kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD)
        ):
            return False

        try:
            dummy = lambda: None
            result = func(dummy)
            return callable(result)
        except Exception:
            return False

    else:
        raise ValueError("mode must be 'static' or 'hybrid'")

def get_signature_arg_types(func: Callable) -> dict[str, tuple[type, ...]]:
    """
    Produce a dictionary of parameter names and their types from the function's signature, even if wrapped or incorrectly warped.
    If a parameter has no type hint, it defaults to Any.

    Parameters:
        func: The callable to analyze

    Raises:
        TypeError: if the provided argument is not callable

    Returns:
        dict[str, tuple[type, ...]]: Dictionary mapping parameter names to their type annotations
    """

    def _decompose_union(annotation):
        origin = getattr(annotation, '__origin__', None)
        if origin is None and hasattr(annotation, '__args__'):
            args = getattr(annotation, '__args__', ())
            if args:
                return list(args)
        elif origin is not None and origin is getattr(__import__('typing'), 'Union', None):
            return list(getattr(annotation, '__args__', ()))
        return annotation
    
    if not callable(func):
        raise TypeError(f"Expected a callable, got {type(func).__name__}")

    func = unwarp_function(func)

    return {k: tuple(_decompose_union(v.annotation)) if hasattr(v.annotation, '__args__') and v.annotation.__args__ else (v.annotation if v.annotation != v.empty else Any,)
            for k, v in signature(func).parameters.items()}