"""Dependency resolution for column transformations."""

import ast
import re
from typing import Any, Dict, List, Set, Tuple
from collections import defaultdict, deque


class DependencyAnalyzer:
    """Analyze column dependencies in transformations."""

    def __init__(self):
        """Initialize the dependency analyzer."""
        self.column_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.defined_columns: Set[str] = set()

    def analyze_expression(
        self, expression: str, available_columns: Set[str]
    ) -> Set[str]:
        """Analyze an expression to find column dependencies."""
        dependencies = set()

        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode="eval")

            # Walk the AST to find column references
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    name = node.id
                    # If it's a column name and not a built-in function
                    if name in available_columns and name not in {
                        "str",
                        "int",
                        "float",
                        "bool",
                        "len",
                        "abs",
                        "max",
                        "min",
                        "round",
                        "sum",
                        "any",
                        "all",
                        "np",
                        "pd",
                        "re",
                    }:
                        dependencies.add(name)

                elif isinstance(node, ast.Attribute):
                    # Handle dataset.column references (for joins)
                    if isinstance(node.value, ast.Name):
                        attr_name = f"{node.value.id}.{node.attr}"
                        if attr_name in available_columns:
                            dependencies.add(attr_name)

        except SyntaxError:
            # Fall back to regex-based analysis for complex expressions
            dependencies.update(self._regex_analyze(expression, available_columns))

        return dependencies

    def _regex_analyze(self, expression: str, available_columns: Set[str]) -> Set[str]:
        """Fallback regex-based dependency analysis."""
        dependencies = set()

        # Find all potential column references (alphanumeric + underscore)
        potential_refs = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", expression)

        for ref in potential_refs:
            if ref in available_columns:
                dependencies.add(ref)

        # Handle dataset.column references
        dataset_refs = re.findall(
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\b", expression
        )
        for ref in dataset_refs:
            if ref in available_columns:
                dependencies.add(ref)

        return dependencies

    def analyze_operations(
        self, operations: List[Dict[str, Any]], available_columns: Set[str]
    ) -> Set[str]:
        """Analyze dependencies in column operations."""
        dependencies = set()

        for operation in operations:
            op_type = operation.get("type")

            if op_type == "map" and "function" in operation:
                deps = self.analyze_expression(operation["function"], available_columns)
                dependencies.update(deps)

            elif op_type == "filter" and "condition" in operation:
                deps = self.analyze_expression(
                    operation["condition"], available_columns
                )
                dependencies.update(deps)

            elif op_type == "reduce" and "function" in operation:
                deps = self.analyze_expression(operation["function"], available_columns)
                dependencies.update(deps)

            elif op_type == "group" and "group_by" in operation:
                group_col = operation["group_by"]
                if group_col in available_columns:
                    dependencies.add(group_col)

        return dependencies


class DependencyResolver:
    """Resolve column dependencies and determine execution order."""

    def __init__(self):
        """Initialize the dependency resolver."""
        self.analyzer = DependencyAnalyzer()
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)

    def build_dependency_graph(
        self, column_configs: Dict[str, Dict[str, Any]], input_columns: Set[str]
    ) -> None:
        """Build the dependency graph for all columns."""
        self.dependency_graph.clear()
        self.reverse_graph.clear()

        # All available columns (input + defined columns)
        all_columns = input_columns.copy()
        all_columns.update(column_configs.keys())

        # Analyze dependencies for each column
        for column_name, config in column_configs.items():
            dependencies = set()

            # Check source dependencies
            source = config.get("source", column_name)
            if source != column_name and source in all_columns:
                dependencies.add(source)

            # Check transformation dependencies
            if "transformation" in config:
                transformation_deps = self.analyzer.analyze_expression(
                    config["transformation"], all_columns
                )
                dependencies.update(transformation_deps)

            # Check operations dependencies
            if "operations" in config:
                operations_deps = self.analyzer.analyze_operations(
                    config["operations"], all_columns
                )
                dependencies.update(operations_deps)

            # Filter out self-dependencies and non-column dependencies
            dependencies = {
                dep
                for dep in dependencies
                if dep != column_name
                and (dep in input_columns or dep in column_configs)
            }

            # Build dependency graph
            self.dependency_graph[column_name] = dependencies

            # Build reverse graph (who depends on this column)
            for dep in dependencies:
                self.reverse_graph[dep].add(column_name)

    def resolve_execution_order(
        self, column_configs: Dict[str, Dict[str, Any]], input_columns: Set[str]
    ) -> List[str]:
        """Resolve the execution order using topological sorting."""
        # Build dependency graph
        self.build_dependency_graph(column_configs, input_columns)

        # Topological sort using Kahn's algorithm
        # Only count dependencies on other output columns, not input columns
        in_degree = {
            col: len([dep for dep in deps if dep in column_configs])
            for col, deps in self.dependency_graph.items()
        }
        queue = deque([col for col, degree in in_degree.items() if degree == 0])
        execution_order = []

        while queue:
            current = queue.popleft()
            execution_order.append(current)

            # Update in-degrees of dependent columns (only for output columns)
            for dependent in self.reverse_graph[current]:
                if dependent in column_configs:  # Only process output columns
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # Check for circular dependencies
        if len(execution_order) != len(column_configs):
            remaining = set(column_configs.keys()) - set(execution_order)
            raise ValueError(f"Circular dependency detected in columns: {remaining}")

        return execution_order

    def get_dependency_info(self) -> Dict[str, Any]:
        """Get detailed dependency information for debugging."""
        return {
            "dependency_graph": dict(self.dependency_graph),
            "reverse_graph": dict(self.reverse_graph),
            "total_columns": len(self.dependency_graph),
            "dependency_counts": {
                col: len(deps) for col, deps in self.dependency_graph.items()
            },
        }

    def validate_dependencies(
        self, column_configs: Dict[str, Dict[str, Any]], input_columns: Set[str]
    ) -> List[str]:
        """Validate all dependencies are resolvable."""
        errors = []
        all_columns = input_columns.union(column_configs.keys())

        for column_name, config in column_configs.items():
            # Check source column exists
            source = config.get("source", column_name)
            if source != column_name and source not in all_columns:
                errors.append(f"Column '{column_name}': source '{source}' not found")

            # Check transformation dependencies
            if "transformation" in config:
                deps = self.analyzer.analyze_expression(
                    config["transformation"], all_columns
                )
                for dep in deps:
                    if dep not in all_columns:
                        errors.append(
                            f"Column '{column_name}': transformation references unknown column '{dep}'"
                        )

            # Check operations dependencies
            if "operations" in config:
                deps = self.analyzer.analyze_operations(
                    config["operations"], all_columns
                )
                for dep in deps:
                    if dep not in all_columns:
                        errors.append(
                            f"Column '{column_name}': operations reference unknown column '{dep}'"
                        )

        return errors


class ColumnExecutionEngine:
    """Enhanced transformation engine with dependency resolution."""

    def __init__(self):
        """Initialize the execution engine."""
        self.resolver = DependencyResolver()
        self.interim_columns: Set[str] = set()
        self.final_columns: Set[str] = set()

    def plan_execution(
        self, column_configs: Dict[str, Dict[str, Any]], input_columns: Set[str]
    ) -> Dict[str, Any]:
        """Plan the execution order and categorize columns."""
        # Validate dependencies
        validation_errors = self.resolver.validate_dependencies(
            column_configs, input_columns
        )
        if validation_errors:
            raise ValueError(
                f"Dependency validation failed:\n{chr(10).join(validation_errors)}"
            )

        # Resolve execution order
        execution_order = self.resolver.resolve_execution_order(
            column_configs, input_columns
        )

        # Categorize columns
        self.interim_columns = {
            col
            for col, config in column_configs.items()
            if config.get("interim", False)
        }
        self.final_columns = {
            col for col in column_configs.keys() if col not in self.interim_columns
        }

        # Create execution plan
        execution_plan = {
            "execution_order": execution_order,
            "interim_columns": list(self.interim_columns),
            "final_columns": list(self.final_columns),
            "dependency_info": self.resolver.get_dependency_info(),
            "total_steps": len(execution_order),
        }

        return execution_plan

    def filter_final_columns(self, df, final_columns: List[str]) -> List[str]:
        """Filter to only include final columns that exist in the dataframe."""
        return [col for col in final_columns if col in df.columns]
