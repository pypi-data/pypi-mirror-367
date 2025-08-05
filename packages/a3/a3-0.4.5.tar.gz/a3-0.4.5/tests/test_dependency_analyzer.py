"""
Unit tests for the DependencyAnalyzer class.

This module tests dependency analysis functionality including cycle detection,
build order determination, and dependency validation.
"""

import pytest
from typing import List
import tempfile
import os

from a3.managers.dependency import DependencyAnalyzer, CircularDependencyError
from a3.core.models import Module, FunctionSpec, DependencyGraph, ValidationResult, ValidationLevel


class TestDependencyAnalyzer:
    """Test cases for DependencyAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = DependencyAnalyzer(self.temp_dir)
        # Initialize the analyzer to avoid package manager initialization errors
        self.analyzer.initialize()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_modules(self) -> List[Module]:
        """Create test modules with various dependency patterns."""
        modules = [
            Module(
                name="core",
                description="Core module",
                file_path="core.py",
                dependencies=[],
                functions=[FunctionSpec(name="core_func", module="core", docstring="Core function")]
            ),
            Module(
                name="utils",
                description="Utilities module",
                file_path="utils.py",
                dependencies=["core"],
                functions=[FunctionSpec(name="util_func", module="utils", docstring="Utility function")]
            ),
            Module(
                name="service",
                description="Service module",
                file_path="service.py",
                dependencies=["core", "utils"],
                functions=[FunctionSpec(name="service_func", module="service", docstring="Service function")]
            ),
            Module(
                name="api",
                description="API module",
                file_path="api.py",
                dependencies=["service"],
                functions=[FunctionSpec(name="api_func", module="api", docstring="API function")]
            )
        ]
        return modules
    
    def create_circular_modules(self) -> List[Module]:
        """Create test modules with circular dependencies."""
        modules = [
            Module(
                name="module_a",
                description="Module A",
                file_path="module_a.py",
                dependencies=["module_b"],
                functions=[FunctionSpec(name="func_a", module="module_a", docstring="Function A")]
            ),
            Module(
                name="module_b",
                description="Module B",
                file_path="module_b.py",
                dependencies=["module_c"],
                functions=[FunctionSpec(name="func_b", module="module_b", docstring="Function B")]
            ),
            Module(
                name="module_c",
                description="Module C",
                file_path="module_c.py",
                dependencies=["module_a"],
                functions=[FunctionSpec(name="func_c", module="module_c", docstring="Function C")]
            )
        ]
        return modules
    
    def test_analyze_dependencies_valid(self):
        """Test dependency analysis with valid modules."""
        modules = self.create_test_modules()
        result = self.analyzer.analyze_dependencies(modules)
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_analyze_dependencies_empty_list(self):
        """Test dependency analysis with empty module list."""
        result = self.analyzer.analyze_dependencies([])
        
        assert result.is_valid
        assert len(result.warnings) == 1
        assert "No modules provided" in result.warnings[0]
    
    def test_analyze_dependencies_missing_dependency(self):
        """Test dependency analysis with missing dependencies."""
        modules = [
            Module(
                name="test_module",
                description="Test module",
                file_path="test.py",
                dependencies=["nonexistent_module"],
                functions=[]
            )
        ]
        
        result = self.analyzer.analyze_dependencies(modules)
        
        assert not result.is_valid
        assert len(result.issues) == 1
        assert "missing dependencies" in result.issues[0]
        assert "nonexistent_module" in result.issues[0] 
   
    def test_analyze_dependencies_self_dependency(self):
        """Test dependency analysis with self-dependencies."""
        modules = [
            Module(
                name="self_dep_module",
                description="Self-dependent module",
                file_path="self_dep.py",
                dependencies=["self_dep_module"],
                functions=[]
            )
        ]
        
        result = self.analyzer.analyze_dependencies(modules)
        
        assert not result.is_valid
        assert len(result.issues) == 1
        assert "depends on itself" in result.issues[0]
    
    def test_detect_circular_dependencies_none(self):
        """Test circular dependency detection with no cycles."""
        modules = self.create_test_modules()
        cycles = self.analyzer.detect_circular_dependencies(modules)
        
        assert len(cycles) == 0
    
    def test_detect_circular_dependencies_present(self):
        """Test circular dependency detection with cycles present."""
        modules = self.create_circular_modules()
        cycles = self.analyzer.detect_circular_dependencies(modules)
        
        assert len(cycles) == 1
        assert len(cycles[0]) == 3  # Three modules in the cycle
        cycle_names = set(cycles[0])
        expected_names = {"module_a", "module_b", "module_c"}
        assert cycle_names == expected_names
    
    def test_detect_circular_dependencies_empty_list(self):
        """Test circular dependency detection with empty module list."""
        cycles = self.analyzer.detect_circular_dependencies([])
        assert len(cycles) == 0
    
    def test_get_build_order_valid(self):
        """Test build order generation with valid dependencies."""
        modules = self.create_test_modules()
        build_order = self.analyzer.get_build_order(modules)
        
        assert len(build_order) == 4
        
        # Core should come first (no dependencies)
        assert build_order[0] == "core"
        
        # Utils should come before service (service depends on utils)
        utils_index = build_order.index("utils")
        service_index = build_order.index("service")
        assert utils_index < service_index
        
        # Service should come before api (api depends on service)
        api_index = build_order.index("api")
        assert service_index < api_index
    
    def test_get_build_order_circular_dependencies(self):
        """Test build order generation with circular dependencies."""
        modules = self.create_circular_modules()
        
        with pytest.raises(CircularDependencyError) as exc_info:
            self.analyzer.get_build_order(modules)
        
        assert "circular dependencies" in str(exc_info.value)
        assert len(exc_info.value.cycles) == 1
    
    def test_get_build_order_empty_list(self):
        """Test build order generation with empty module list."""
        build_order = self.analyzer.get_build_order([])
        assert len(build_order) == 0
    
    def test_get_dependency_map(self):
        """Test dependency map generation."""
        modules = self.create_test_modules()
        dep_map = self.analyzer.get_dependency_map(modules)
        
        assert len(dep_map) == 4
        assert dep_map["core"] == set()
        assert dep_map["utils"] == {"core"}
        assert dep_map["service"] == {"core", "utils"}
        assert dep_map["api"] == {"service"}
    
    def test_get_reverse_dependency_map(self):
        """Test reverse dependency map generation."""
        modules = self.create_test_modules()
        reverse_map = self.analyzer.get_reverse_dependency_map(modules)
        
        assert len(reverse_map) == 4
        assert reverse_map["core"] == {"utils", "service"}
        assert reverse_map["utils"] == {"service"}
        assert reverse_map["service"] == {"api"}
        assert reverse_map["api"] == set()
    
    def test_get_transitive_dependencies(self):
        """Test transitive dependency calculation."""
        modules = self.create_test_modules()
        
        # API transitively depends on service, utils, and core
        transitive_deps = self.analyzer.get_transitive_dependencies("api", modules)
        expected_deps = {"service", "utils", "core"}
        assert transitive_deps == expected_deps
        
        # Core has no transitive dependencies
        core_deps = self.analyzer.get_transitive_dependencies("core", modules)
        assert core_deps == set()
    
    def test_create_dependency_graph(self):
        """Test dependency graph creation."""
        modules = self.create_test_modules()
        graph = self.analyzer.create_dependency_graph(modules)
        
        assert isinstance(graph, DependencyGraph)
        assert len(graph.nodes) == 4
        assert set(graph.nodes) == {"core", "utils", "service", "api"}
        
        # Check edges
        expected_edges = {
            ("utils", "core"),
            ("service", "core"),
            ("service", "utils"),
            ("api", "service")
        }
        assert set(graph.edges) == expected_edges
    
    def test_validate_dependency_graph_valid(self):
        """Test dependency graph validation with valid graph."""
        modules = self.create_test_modules()
        graph = self.analyzer.create_dependency_graph(modules)
        result = self.analyzer.validate_dependency_graph(graph)
        
        assert result.is_valid
        assert len(result.issues) == 0
    
    def test_validate_dependency_graph_invalid(self):
        """Test dependency graph validation with invalid graph."""
        # Create invalid graph with circular dependency
        invalid_graph = DependencyGraph(
            nodes=["a", "b"],
            edges=[("a", "b"), ("b", "a")]
        )
        
        result = self.analyzer.validate_dependency_graph(invalid_graph)
        
        assert not result.is_valid
        assert len(result.issues) > 0
    
    def test_analyze_dependencies_nested_structure(self):
        """Test dependency analysis with nested module structure (dotted names)."""
        modules = [
            Module(
                name="scraper.core",
                description="Core scraping engine",
                file_path="src/scraper/core.py",
                dependencies=["parsers.html_parser", "parsers.json_parser", "storage.database"],
                functions=[]
            ),
            Module(
                name="parsers.html_parser",
                description="HTML parsing functionality", 
                file_path="src/scraper/parsers/html_parser.py",
                dependencies=["bs4", "requests"],
                functions=[]
            ),
            Module(
                name="parsers.json_parser",
                description="JSON parsing functionality",
                file_path="src/scraper/parsers/json_parser.py", 
                dependencies=["json", "os"],
                functions=[]
            ),
            Module(
                name="storage.database",
                description="Database storage functionality",
                file_path="src/scraper/storage/database.py",
                dependencies=["sqlite3", "typing"],
                functions=[]
            )
        ]
        
        result = self.analyzer.analyze_dependencies(modules)
        
        # Should be valid - all nested dependencies exist within the module set
        assert result.is_valid
        assert len(result.issues) == 0
        
        # Should be able to determine build order
        build_order = self.analyzer.get_build_order(modules)
        assert len(build_order) == 4
        # Core should come last since it depends on others
        assert build_order[-1] == "scraper.core"
    
    def test_analyze_dependencies_mixed_valid_invalid_nested(self):
        """Test dependency analysis with both valid nested deps and truly missing ones."""
        modules = [
            Module(
                name="scraper.core",
                description="Core scraping engine",
                file_path="src/scraper/core.py",
                dependencies=[
                    "parsers.html_parser",  # Valid - exists in module set
                    "nonexistent.module",   # Invalid - truly missing
                    "requests"              # Valid - third party
                ],
                functions=[]
            ),
            Module(
                name="parsers.html_parser",
                description="HTML parsing functionality", 
                file_path="src/scraper/parsers/html_parser.py",
                dependencies=["bs4"],
                functions=[]
            )
        ]
        
        result = self.analyzer.analyze_dependencies(modules)
        
        # Should be invalid due to truly missing dependency
        assert not result.is_valid
        assert len(result.issues) == 1
        assert "nonexistent.module" in result.issues[0]
        assert "scraper.core" in result.issues[0]
    
    def test_analyze_planning_dependencies_valid(self):
        """Test planning-specific dependency analysis with valid modules."""
        modules = self.create_test_modules()
        result = self.analyzer.analyze_planning_dependencies(modules)
        
        assert result.is_valid
        assert len(result.issues) == 0
        assert result.validation_level.value == "planning"
    
    def test_analyze_planning_dependencies_empty_list(self):
        """Test planning dependency analysis with empty module list."""
        result = self.analyzer.analyze_planning_dependencies([])
        
        assert result.is_valid
        assert len(result.warnings) == 1
        assert "No modules provided" in result.warnings[0]
        assert result.validation_level.value == "planning"
    
    def test_analyze_planning_dependencies_missing_dependency_allowed(self):
        """Test that planning analysis allows missing dependencies."""
        modules = [
            Module(
                name="test_module",
                description="Test module",
                file_path="test.py",
                dependencies=["nonexistent_module"],
                functions=[]
            )
        ]
        
        result = self.analyzer.analyze_planning_dependencies(modules)
        
        # Should be valid - missing dependencies are allowed in planning phase
        assert result.is_valid
        assert len(result.issues) == 0
        assert result.validation_level.value == "planning"
    
    def test_analyze_planning_dependencies_self_dependency(self):
        """Test that planning analysis catches self-dependencies."""
        modules = [
            Module(
                name="self_dep_module",
                description="Self-dependent module",
                file_path="self_dep.py",
                dependencies=["self_dep_module"],
                functions=[]
            )
        ]
        
        result = self.analyzer.analyze_planning_dependencies(modules)
        
        assert not result.is_valid
        assert len(result.issues) == 1
        assert "depends on itself" in result.issues[0]
        assert result.validation_level.value == "planning"
    
    def test_analyze_planning_dependencies_circular_dependency(self):
        """Test that planning analysis catches circular dependencies."""
        modules = self.create_circular_modules()
        result = self.analyzer.analyze_planning_dependencies(modules)
        
        assert not result.is_valid
        assert len(result.issues) == 1
        assert "Circular dependency detected" in result.issues[0]
        assert result.validation_level.value == "planning"
    
    def test_analyze_planning_dependencies_vs_full_analysis(self):
        """Test that planning analysis is more permissive than full analysis."""
        modules = [
            Module(
                name="module_with_missing_deps",
                description="Module with missing dependencies",
                file_path="test.py",
                dependencies=["nonexistent_module", "another_missing"],
                functions=[]
            )
        ]
        
        # Planning analysis should pass (doesn't check for missing dependencies)
        planning_result = self.analyzer.analyze_planning_dependencies(modules)
        assert planning_result.is_valid
        assert planning_result.validation_level.value == "planning"
        
        # For comparison, test that the same modules would fail with missing dependency check
        # We can test this by directly calling the _find_missing_dependencies method
        missing_deps = self.analyzer._find_missing_dependencies(modules)
        assert len(missing_deps) > 0  # Should find missing dependencies
        assert "module_with_missing_deps" in missing_deps
        assert "nonexistent_module" in missing_deps["module_with_missing_deps"]
    
    def test_analyze_planning_dependencies_complex_valid_structure(self):
        """Test planning analysis with complex but structurally valid dependencies."""
        modules = [
            Module(
                name="frontend.components.button",
                description="Button component",
                file_path="src/frontend/components/button.py",
                dependencies=["frontend.utils.styling", "backend.api.user_service"],
                functions=[]
            ),
            Module(
                name="frontend.utils.styling",
                description="Styling utilities",
                file_path="src/frontend/utils/styling.py",
                dependencies=["external_css_lib"],  # External dependency
                functions=[]
            ),
            Module(
                name="backend.api.user_service",
                description="User service API",
                file_path="src/backend/api/user_service.py",
                dependencies=["backend.models.user", "database_orm"],  # Mixed internal/external
                functions=[]
            ),
            Module(
                name="backend.models.user",
                description="User model",
                file_path="src/backend/models/user.py",
                dependencies=["typing", "datetime"],  # Standard library
                functions=[]
            )
        ]
        
        result = self.analyzer.analyze_planning_dependencies(modules)
        
        # Should be valid - no circular or self dependencies
        assert result.is_valid
        assert len(result.issues) == 0
        assert result.validation_level.value == "planning"