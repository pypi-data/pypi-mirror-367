"""Expression parser for transformations."""

import ast
import operator
from typing import Any, Dict
import pandas as pd
import numpy as np


class SafeExpressionParser:
    """Safe expression parser for data transformations."""

    # Allowed operations
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
        ast.In: lambda x, y: x in y,
        ast.NotIn: lambda x, y: x not in y,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
        ast.Invert: operator.invert,
    }

    # Safe built-in functions
    SAFE_FUNCTIONS = {
        "abs": abs,
        "max": max,
        "min": min,
        "round": round,
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "sum": sum,
        "any": any,
        "all": all,
        "sorted": sorted,
        "reversed": reversed,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
        "list": list,
        "tuple": tuple,
        "set": set,
        "dict": dict,
    }

    # String methods
    STRING_METHODS = {
        "upper",
        "lower",
        "title",
        "capitalize",
        "strip",
        "lstrip",
        "rstrip",
        "replace",
        "split",
        "join",
        "startswith",
        "endswith",
        "find",
        "count",
        "isdigit",
        "isalpha",
        "isalnum",
        "isspace",
        "isupper",
        "islower",
    }

    def __init__(self):
        """Initialize the parser with safe functions and operators."""
        pass

    def parse(self, expression: str, context: Dict[str, Any]) -> Any:
        """Parse and evaluate a safe expression."""
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode="eval")

            # Validate the AST for safety
            self._validate_ast(tree)

            # Evaluate the expression
            return self._eval_node(tree.body, context)

        except Exception as e:
            raise ValueError(f"Error parsing expression '{expression}': {str(e)}")

    def _validate_ast(self, node: ast.AST) -> None:
        """Validate AST for safe operations only."""
        for child in ast.walk(node):
            # Check for allowed node types
            if isinstance(
                child,
                (
                    ast.Name,
                    ast.Constant,
                    ast.Num,
                    ast.Str,
                    ast.Bytes,
                    ast.NameConstant,
                    ast.Ellipsis,
                ),
            ):
                continue
            elif isinstance(child, ast.BinOp):
                if type(child.op) not in self.SAFE_OPERATORS:
                    raise ValueError(
                        f"Unsafe binary operator: {type(child.op).__name__}"
                    )
            elif isinstance(child, ast.UnaryOp):
                if type(child.op) not in self.SAFE_OPERATORS:
                    raise ValueError(
                        f"Unsafe unary operator: {type(child.op).__name__}"
                    )
            elif isinstance(child, ast.Compare):
                for op in child.ops:
                    if type(op) not in self.SAFE_OPERATORS:
                        raise ValueError(
                            f"Unsafe comparison operator: {type(op).__name__}"
                        )
            elif isinstance(
                child,
                (
                    ast.Call,
                    ast.Attribute,
                    ast.Subscript,
                    ast.List,
                    ast.Tuple,
                    ast.Dict,
                    ast.Set,
                    ast.ListComp,
                    ast.SetComp,
                    ast.DictComp,
                    ast.IfExp,
                    ast.BoolOp,
                    ast.Expression,
                    ast.Load,
                    ast.Store,
                    ast.Del,
                    ast.And,
                    ast.Or,
                    ast.Index,
                    ast.Slice,
                ),
            ):  # Add context types
                continue
            # Allow operator nodes that are part of the safe operators
            elif type(child) in self.SAFE_OPERATORS:
                continue
            else:
                raise ValueError(f"Unsafe AST node type: {type(child).__name__}")

    def _eval_node(self, node: ast.AST, context: Dict[str, Any]) -> Any:
        """Evaluate an AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, (ast.Num, ast.Str, ast.Bytes)):
            return node.n if hasattr(node, "n") else node.s
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            elif node.id in self.SAFE_FUNCTIONS:
                return self.SAFE_FUNCTIONS[node.id]
            else:
                raise NameError(f"Name '{node.id}' is not defined")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op_func = self.SAFE_OPERATORS[type(node.op)]
            return op_func(left, right)  # type: ignore

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            op_func = self.SAFE_OPERATORS[type(node.op)]
            return op_func(operand)  # type: ignore

        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            result = True
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, context)
                op_func = self.SAFE_OPERATORS[type(op)]
                result = result and op_func(left, right)  # type: ignore
                left = right
            return result

        elif isinstance(node, ast.Call):
            func = self._eval_node(node.func, context)
            args = [self._eval_node(arg, context) for arg in node.args]
            kwargs = {
                kw.arg: self._eval_node(kw.value, context) for kw in node.keywords
            }
            return func(*args, **kwargs)

        elif isinstance(node, ast.Attribute):
            value = self._eval_node(node.value, context)
            attr_name = node.attr

            # Allow string methods
            if isinstance(value, str) and attr_name in self.STRING_METHODS:
                return getattr(value, attr_name)
            # Allow pandas Series/DataFrame methods (limited set)
            elif isinstance(value, (pd.Series, pd.DataFrame)):
                allowed_pandas_methods = {
                    "isna",
                    "notna",
                    "fillna",
                    "dropna",
                    "astype",
                    "str",
                    "dt",
                    "cat",
                    "apply",
                    "map",
                    "replace",
                }
                if attr_name in allowed_pandas_methods:
                    return getattr(value, attr_name)
            # Allow numpy array methods
            elif isinstance(value, np.ndarray):
                allowed_numpy_methods = {
                    "round",
                    "sum",
                    "mean",
                    "std",
                    "var",
                    "min",
                    "max",
                    "argmin",
                    "argmax",
                    "sort",
                    "argsort",
                    "flatten",
                    "reshape",
                    "astype",
                }
                if attr_name in allowed_numpy_methods:
                    return getattr(value, attr_name)
            # Allow numpy-like methods on Series values
            elif hasattr(value, attr_name) and attr_name in {
                "round",
                "sum",
                "mean",
                "std",
                "var",
                "min",
                "max",
            }:
                return getattr(value, attr_name)

            raise AttributeError(f"Access to attribute '{attr_name}' is not allowed")

        elif isinstance(node, ast.Subscript):
            value = self._eval_node(node.value, context)
            slice_val = self._eval_node(node.slice, context)
            return value[slice_val]

        elif isinstance(node, ast.List):
            return [self._eval_node(elt, context) for elt in node.elts]

        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt, context) for elt in node.elts)

        elif isinstance(node, ast.Dict):
            keys = [
                self._eval_node(k, context) if k is not None else None
                for k in node.keys
            ]
            values = [self._eval_node(v, context) for v in node.values]
            return dict(zip(keys, values))

        elif isinstance(node, ast.IfExp):
            test = self._eval_node(node.test, context)
            if test:
                return self._eval_node(node.body, context)
            else:
                return self._eval_node(node.orelse, context)

        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval_node(value, context) for value in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._eval_node(value, context) for value in node.values)

        elif isinstance(node, ast.Index):
            # Handle ast.Index nodes (used in older Python versions for subscript operations)
            return self._eval_node(node.value, context)  # type: ignore

        elif isinstance(node, ast.Slice):
            # Handle slice operations
            lower = self._eval_node(node.lower, context) if node.lower else None
            upper = self._eval_node(node.upper, context) if node.upper else None
            step = self._eval_node(node.step, context) if node.step else None
            return slice(lower, upper, step)

        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")


class ExpressionParser:
    """High-level expression parser for data transformations."""

    def __init__(self):
        """Initialize the expression parser."""
        self.safe_parser = SafeExpressionParser()

    def evaluate(self, expression: str, row_data: pd.Series) -> Any:
        """Evaluate expression against a row of data."""
        # Create context with row data and common functions
        context = dict(row_data)

        # Add numpy functions
        context.update(
            {
                "np": np,
                "pd": pd,
                "nan": np.nan,
                "inf": np.inf,
            }
        )

        return self.safe_parser.parse(expression, context)

    def evaluate_vectorized(self, expression: str, df: pd.DataFrame) -> pd.Series:
        """Evaluate expression in a vectorized manner across DataFrame."""
        # For simple column references, return directly
        if expression in df.columns:
            return df[expression]

        # Check for dataset-prefixed column references (e.g., "users.name" -> "name_users")
        # This helps with joined datasets that may have column suffixes
        if "." in expression and expression.count(".") == 1:
            dataset, column = expression.split(".")
            # Try common suffix patterns
            for suffix_pattern in [
                f"{column}_{dataset}",
                f"{column}_{dataset.lower()}",
                f"{dataset}_{column}",
                f"{dataset.lower()}_{column}",
            ]:
                if suffix_pattern in df.columns:
                    return df[suffix_pattern]

        # For complex expressions, evaluate row by row
        try:
            # Try vectorized evaluation first
            context = {}
            for col in df.columns:
                context[col] = df[col]
                # Also add dataset-prefixed aliases for easier reference
                if "_" in col:
                    parts = col.split("_")
                    if len(parts) == 2:
                        # Add "dataset.column" style access
                        context[f"{parts[1]}.{parts[0]}"] = df[col]
                        context[f"{parts[0]}.{parts[1]}"] = df[col]

            context.update(
                {
                    "np": np,
                    "pd": pd,
                    "nan": np.nan,
                    "inf": np.inf,
                }
            )

            result = self.safe_parser.parse(expression, context)
            if isinstance(result, pd.Series):
                return result
            else:
                return pd.Series([result] * len(df))

        except Exception as e:
            # Provide better error messages for missing columns
            if "not defined" in str(e):
                available_cols = list(df.columns)
                raise ValueError(
                    f"Column reference '{expression}' not found. "
                    f"Available columns: {available_cols[:10]}"
                    f"{'...' if len(available_cols) > 10 else ''}"
                )
            # Fall back to row-by-row evaluation
            return df.apply(lambda row: self.evaluate(expression, row), axis=1)
