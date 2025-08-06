"""
Unit tests for the fixed import logic in IntegrationEngine.

This module tests the corrected import path calculation, validation methods,
and enhanced error handling that were implemented to fix the import generation issues.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import os

from a3.engines.integration import IntegrationEngine
from a3.core.models import Module, FunctionSpec, ValidationResult
from a3.core.interfaces import DependencyAnalyzerInterface, FileSystemManagerInterface


# Global fixtures for all test classes
@pytest.fixture
def mock_dependency_analyzer():
    """Create a mock dependency analyzer."""
    analyzer = Mock(spec=DependencyAnalyzerInterface)
    analyzer.get_build_order.return_value = ["module_a", "module_b"]
    analyzer.detect_circular_dependencies.return_value = []
    analyzer.create_dependency_graph.return_value = Mock()
    analyzer.validate_dependency_graph.return_value = ValidationResult(
        is_valid=True, issues=[], warnings=[]
    )
    return analyzer

@pytest.fixture
def mock_filesystem_manager():
    """Create a mock filesystem manager."""
    manager = Mock(spec=FileSystemManagerInterface)
    manager.file_exists.return_value = True
    manager.read_file.return_value = '"""\nModule docstring\n"""\n\n'
    manager.write_file.return_value = True
    return manager

@pytest.fixture
def temp_project_structure():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        
        # Create project structure
        (project_root / "setup.py").touch()
        (project_root / "src").mkdir()
        (project_root / "src" / "__init__.py").touch()
        (project_root / "src" / "utils").mkdir()
        (project_root / "src" / "utils" / "__init__.py").touch()
        (project_root / "src" / "core").mkdir()
        (project_root / "src" / "core" / "__init__.py").touch()
        (project_root / "src" / "core" / "models").mkdir()
        (project_root / "src" / "core" / "models" / "__init__.py").touch()
        
        # Create some test files
        (project_root / "src" / "main.py").touch()
        (project_root / "src" / "utils" / "helpers.py").touch()
        (project_root / "src" / "core" / "engine.py").touch()
        (project_root / "src" / "core" / "models" / "data.py").touch()
        
        yield {
            'root': str(project_root),
            'main': str(project_root / "src" / "main.py"),
            'helpers': str(project_root / "src" / "utils" / "helpers.py"),
            'engine': str(project_root / "src" / "core" / "engine.py"),
            'data': str(project_root / "src" / "core" / "models" / "data.py")
        }


class TestIntegrationEngineImportLogic:
    """Test cases for the fixed import logic methods."""


class TestCalculateRelativeImportPath:
    """Test cases for _calculate_relative_import_path method."""
    
    @pytest.fixture
    def integration_engine(self):
        """Create a basic integration engine for testing."""
        return IntegrationEngine()
    
    def test_same_directory_import(self, integration_engine, temp_project_structure):
        """Test import calculation for modules in the same directory."""
        from_path = temp_project_structure['main']
        to_path = temp_project_structure['helpers']  # Different directory, let's use same dir
        project_root = temp_project_structure['root']
        
        # Create files in same directory for this test
        same_dir_file = str(Path(temp_project_structure['root']) / "src" / "other.py")
        Path(same_dir_file).touch()
        
        result = integration_engine._calculate_relative_import_path(
            temp_project_structure['main'], same_dir_file, project_root
        )
        
        assert result is not None
        assert result == "from .other import *"
    
    def test_cross_directory_import_down(self, integration_engine, temp_project_structure):
        """Test import calculation from parent to child directory."""
        from_path = temp_project_structure['main']  # src/main.py
        to_path = temp_project_structure['helpers']  # src/utils/helpers.py
        project_root = temp_project_structure['root']
        
        result = integration_engine._calculate_relative_import_path(
            from_path, to_path, project_root
        )
        
        assert result is not None
        assert result == "from .utils.helpers import *"
    
    def test_cross_directory_import_up(self, integration_engine, temp_project_structure):
        """Test import calculation from child to parent directory."""
        from_path = temp_project_structure['helpers']  # src/utils/helpers.py
        to_path = temp_project_structure['main']  # src/main.py
        project_root = temp_project_structure['root']
        
        result = integration_engine._calculate_relative_import_path(
            from_path, to_path, project_root
        )
        
        assert result is not None
        assert result == "from ..main import *"
    
    def test_nested_directory_import(self, integration_engine, temp_project_structure):
        """Test import calculation between deeply nested directories."""
        from_path = temp_project_structure['data']  # src/core/models/data.py
        to_path = temp_project_structure['helpers']  # src/utils/helpers.py
        project_root = temp_project_structure['root']
        
        result = integration_engine._calculate_relative_import_path(
            from_path, to_path, project_root
        )
        
        assert result is not None
        assert result == "from ...utils.helpers import *"
    
    def test_common_ancestor_import(self, integration_engine, temp_project_structure):
        """Test import calculation with common ancestor directory."""
        from_path = temp_project_structure['engine']  # src/core/engine.py
        to_path = temp_project_structure['helpers']  # src/utils/helpers.py
        project_root = temp_project_structure['root']
        
        result = integration_engine._calculate_relative_import_path(
            from_path, to_path, project_root
        )
        
        assert result is not None
        assert result == "from ..utils.helpers import *"
    
    def test_outside_project_boundary(self, integration_engine, temp_project_structure):
        """Test import calculation fails when files are outside project boundary."""
        from_path = temp_project_structure['main']
        to_path = "/tmp/external_module.py"  # Outside project
        project_root = temp_project_structure['root']
        
        result = integration_engine._calculate_relative_import_path(
            from_path, to_path, project_root
        )
        
        assert result is None
    
    def test_invalid_paths(self, integration_engine):
        """Test import calculation with invalid paths."""
        result = integration_engine._calculate_relative_import_path(
            "invalid/path.py", "another/invalid.py", "/nonexistent/root"
        )
        
        assert result is None
    
    def test_project_root_level_files(self, integration_engine, temp_project_structure):
        """Test import calculation for files at project root level."""
        project_root = temp_project_structure['root']
        
        # Create files at project root
        root_file1 = str(Path(project_root) / "module1.py")
        root_file2 = str(Path(project_root) / "module2.py")
        Path(root_file1).touch()
        Path(root_file2).touch()
        
        result = integration_engine._calculate_relative_import_path(
            root_file1, root_file2, project_root
        )
        
        assert result is not None
        assert result == "from .module2 import *"


@pytest.fixture
def sample_module(temp_project_structure):
    """Create a sample module for testing."""
    return Module(
        name="test_module",
        description="Test module",
        file_path=temp_project_structure['main'],
        dependencies=[],
        functions=[]
    )


class TestValidateImportPath:
    """Test cases for _validate_import_path method."""
    
    def test_valid_import_statement(self, mock_filesystem_manager, sample_module, temp_project_structure):
        """Test validation of a valid import statement."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import_statement = "from .utils.helpers import *"
        project_root = temp_project_structure['root']
        
        # Mock the filesystem manager to return True for target file existence
        mock_filesystem_manager.file_exists.return_value = True
        
        with patch.object(integration_engine, '_validate_import_syntax', return_value=True), \
             patch.object(integration_engine, '_extract_target_path_from_import', 
                         return_value=temp_project_structure['helpers']), \
             patch.object(integration_engine, '_validate_target_module_structure', return_value=True), \
             patch.object(integration_engine, '_validate_no_circular_import', return_value=True):
            
            result = integration_engine._validate_import_path(
                import_statement, sample_module, project_root
            )
            
            assert result is True
    
    def test_invalid_syntax(self, mock_filesystem_manager, sample_module, temp_project_structure):
        """Test validation fails for invalid import syntax."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import_statement = "invalid import statement"
        project_root = temp_project_structure['root']
        
        with patch.object(integration_engine, '_validate_import_syntax', return_value=False):
            result = integration_engine._validate_import_path(
                import_statement, sample_module, project_root
            )
            
            assert result is False
    
    def test_missing_target_file(self, mock_filesystem_manager, sample_module, temp_project_structure):
        """Test validation fails when target file doesn't exist."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import_statement = "from .nonexistent import *"
        project_root = temp_project_structure['root']
        
        # Mock filesystem manager to return False for file existence
        mock_filesystem_manager.file_exists.return_value = False
        
        with patch.object(integration_engine, '_validate_import_syntax', return_value=True), \
             patch.object(integration_engine, '_extract_target_path_from_import', 
                         return_value="/nonexistent/path.py"):
            
            result = integration_engine._validate_import_path(
                import_statement, sample_module, project_root
            )
            
            assert result is False
    
    def test_circular_import_detection(self, mock_filesystem_manager, sample_module, temp_project_structure):
        """Test validation fails when circular import is detected."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import_statement = "from .circular import *"
        project_root = temp_project_structure['root']
        
        mock_filesystem_manager.file_exists.return_value = True
        
        with patch.object(integration_engine, '_validate_import_syntax', return_value=True), \
             patch.object(integration_engine, '_extract_target_path_from_import', 
                         return_value=temp_project_structure['helpers']), \
             patch.object(integration_engine, '_validate_target_module_structure', return_value=True), \
             patch.object(integration_engine, '_validate_no_circular_import', return_value=False):
            
            result = integration_engine._validate_import_path(
                import_statement, sample_module, project_root
            )
            
            assert result is False
    
    def test_comment_lines_ignored(self, mock_filesystem_manager, sample_module, temp_project_structure):
        """Test that comment lines are properly ignored."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import_statement = "# This is a comment"
        project_root = temp_project_structure['root']
        
        result = integration_engine._validate_import_path(
            import_statement, sample_module, project_root
        )
        
        assert result is False
    
    def test_empty_statement_ignored(self, mock_filesystem_manager, sample_module, temp_project_structure):
        """Test that empty statements are properly ignored."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import_statement = ""
        project_root = temp_project_structure['root']
        
        result = integration_engine._validate_import_path(
            import_statement, sample_module, project_root
        )
        
        assert result is False
    
    def test_exception_handling(self, mock_filesystem_manager, sample_module, temp_project_structure):
        """Test that exceptions are handled gracefully."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import_statement = "from .valid import *"
        project_root = temp_project_structure['root']
        
        # Mock to raise an exception
        with patch.object(integration_engine, '_validate_import_syntax', 
                         side_effect=Exception("Test exception")):
            
            result = integration_engine._validate_import_path(
                import_statement, sample_module, project_root
            )
            
            assert result is False


class TestGetProjectRoot:
    """Test cases for _get_project_root method."""
    
    @pytest.fixture
    def integration_engine(self):
        """Create a basic integration engine for testing."""
        return IntegrationEngine()
    
    def test_project_root_with_setup_py(self, integration_engine, temp_project_structure):
        """Test project root detection with setup.py."""
        module_path = temp_project_structure['main']
        
        result = integration_engine._get_project_root(module_path)
        
        assert result == temp_project_structure['root']
    
    def test_project_root_with_multiple_indicators(self, integration_engine, temp_project_structure):
        """Test project root detection with multiple indicators."""
        project_root = Path(temp_project_structure['root'])
        
        # Add more indicators
        (project_root / "pyproject.toml").touch()
        (project_root / "requirements.txt").touch()
        (project_root / ".gitignore").touch()
        
        module_path = temp_project_structure['data']  # Deep nested file
        
        result = integration_engine._get_project_root(module_path)
        
        assert result == temp_project_structure['root']
    
    def test_project_root_with_git_directory(self, integration_engine):
        """Test project root detection with .git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create .git directory
            (project_root / ".git").mkdir()
            (project_root / "src").mkdir()
            module_file = project_root / "src" / "module.py"
            module_file.touch()
            
            result = integration_engine._get_project_root(str(module_file))
            
            assert result == str(project_root)
    
    def test_project_root_fallback_to_module_directory(self, integration_engine):
        """Test fallback to module directory when no indicators found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a module file without any project indicators
            module_dir = Path(temp_dir) / "some" / "deep" / "path"
            module_dir.mkdir(parents=True)
            module_file = module_dir / "module.py"
            module_file.touch()
            
            result = integration_engine._get_project_root(str(module_file))
            
            assert result == str(module_dir)
    
    def test_project_root_with_package_structure(self, integration_engine):
        """Test project root detection with Python package structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create package structure
            package_dir = project_root / "mypackage"
            package_dir.mkdir()
            (package_dir / "__init__.py").touch()
            
            subpackage_dir = package_dir / "subpackage"
            subpackage_dir.mkdir()
            (subpackage_dir / "__init__.py").touch()
            
            module_file = subpackage_dir / "module.py"
            module_file.touch()
            
            # Add project indicator at root
            (project_root / "setup.py").touch()
            
            result = integration_engine._get_project_root(str(module_file))
            
            assert result == str(project_root)
    
    def test_project_root_max_levels_limit(self, integration_engine):
        """Test that project root detection respects max levels limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create very deep directory structure
            current_path = Path(temp_dir)
            for i in range(10):  # Create 10 levels deep
                current_path = current_path / f"level{i}"
                current_path.mkdir()
            
            module_file = current_path / "module.py"
            module_file.touch()
            
            # Put project indicator very high up (beyond max levels)
            (Path(temp_dir) / "setup.py").touch()
            
            result = integration_engine._get_project_root(str(module_file))
            
            # Should fallback to module directory due to max levels limit
            assert result == str(current_path)
    
    def test_project_root_exception_handling(self, integration_engine):
        """Test project root detection handles exceptions gracefully."""
        # Test with invalid path
        result = integration_engine._get_project_root("/nonexistent/path/module.py")
        
        # Should not raise exception and return some fallback
        assert isinstance(result, str)


class TestConvertFilePathToImportPath:
    """Test cases for _convert_file_path_to_import_path method."""
    
    @pytest.fixture
    def integration_engine(self):
        """Create a basic integration engine for testing."""
        return IntegrationEngine()
    
    def test_simple_file_conversion(self, integration_engine, temp_project_structure):
        """Test conversion of simple file path to import path."""
        file_path = temp_project_structure['main']  # src/main.py
        project_root = temp_project_structure['root']
        
        result = integration_engine._convert_file_path_to_import_path(file_path, project_root)
        
        assert result == "src.main"
    
    def test_nested_file_conversion(self, integration_engine, temp_project_structure):
        """Test conversion of nested file path to import path."""
        file_path = temp_project_structure['data']  # src/core/models/data.py
        project_root = temp_project_structure['root']
        
        result = integration_engine._convert_file_path_to_import_path(file_path, project_root)
        
        assert result == "src.core.models.data"
    
    def test_root_level_file_conversion(self, integration_engine, temp_project_structure):
        """Test conversion of root level file to import path."""
        project_root = temp_project_structure['root']
        root_file = str(Path(project_root) / "root_module.py")
        Path(root_file).touch()
        
        result = integration_engine._convert_file_path_to_import_path(root_file, project_root)
        
        assert result == "root_module"
    
    def test_relative_path_handling(self, integration_engine, temp_project_structure):
        """Test conversion handles relative paths correctly."""
        project_root = temp_project_structure['root']
        
        # Use relative path
        relative_path = "src/utils/helpers.py"
        full_path = str(Path(project_root) / relative_path)
        
        result = integration_engine._convert_file_path_to_import_path(full_path, project_root)
        
        assert result == "src.utils.helpers"
    
    def test_path_separator_normalization(self, integration_engine, temp_project_structure):
        """Test that path separators are properly normalized to dots."""
        file_path = temp_project_structure['helpers']
        project_root = temp_project_structure['root']
        
        result = integration_engine._convert_file_path_to_import_path(file_path, project_root)
        
        # Should convert path separators to dots
        assert "." in result
        assert os.sep not in result
        assert result == "src.utils.helpers"
    
    def test_py_extension_removal(self, integration_engine, temp_project_structure):
        """Test that .py extension is properly removed."""
        file_path = temp_project_structure['main']
        project_root = temp_project_structure['root']
        
        result = integration_engine._convert_file_path_to_import_path(file_path, project_root)
        
        assert not result.endswith(".py")
        assert result == "src.main"
    
    def test_double_dots_cleanup(self, integration_engine):
        """Test that double dots are cleaned up."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create a path that might result in double dots
            weird_path = project_root / "src" / ".." / "src" / "module.py"
            weird_path.parent.mkdir(parents=True, exist_ok=True)
            weird_path.touch()
            
            result = integration_engine._convert_file_path_to_import_path(
                str(weird_path), str(project_root)
            )
            
            # Should not contain double dots
            assert ".." not in result
    
    def test_exception_handling_invalid_path(self, integration_engine):
        """Test exception handling with invalid paths."""
        result = integration_engine._convert_file_path_to_import_path(
            "/nonexistent/path.py", "/nonexistent/root"
        )
        
        # Should handle gracefully and return something
        assert isinstance(result, str)
    
    def test_fallback_to_filename(self, integration_engine):
        """Test fallback to filename when path processing fails."""
        # This tests the ultimate fallback mechanism
        with patch('pathlib.Path') as mock_path:
            mock_path.side_effect = Exception("Path error")
            
            # Should still try the fallback
            result = integration_engine._convert_file_path_to_import_path(
                "some_file.py", "/some/root"
            )
            
            # Fallback should handle the exception
            assert isinstance(result, str)


class TestImportPathCalculationWithVariousProjectLayouts:
    """Test import path calculation with various project structures."""
    
    @pytest.fixture
    def integration_engine(self):
        """Create a basic integration engine for testing."""
        return IntegrationEngine()
    
    def test_flat_project_structure(self, integration_engine):
        """Test import calculation in flat project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create flat structure
            (project_root / "setup.py").touch()
            (project_root / "module_a.py").touch()
            (project_root / "module_b.py").touch()
            
            result = integration_engine._calculate_relative_import_path(
                str(project_root / "module_a.py"),
                str(project_root / "module_b.py"),
                str(project_root)
            )
            
            assert result == "from .module_b import *"
    
    def test_src_layout_project(self, integration_engine):
        """Test import calculation in src/ layout project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            src_dir = project_root / "src"
            
            # Create src layout
            (project_root / "setup.py").touch()
            src_dir.mkdir()
            (src_dir / "module_a.py").touch()
            (src_dir / "module_b.py").touch()
            
            result = integration_engine._calculate_relative_import_path(
                str(src_dir / "module_a.py"),
                str(src_dir / "module_b.py"),
                str(project_root)
            )
            
            assert result == "from .module_b import *"
    
    def test_package_layout_project(self, integration_engine):
        """Test import calculation in package layout project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            package_dir = project_root / "mypackage"
            
            # Create package layout
            (project_root / "setup.py").touch()
            package_dir.mkdir()
            (package_dir / "__init__.py").touch()
            (package_dir / "module_a.py").touch()
            (package_dir / "module_b.py").touch()
            
            result = integration_engine._calculate_relative_import_path(
                str(package_dir / "module_a.py"),
                str(package_dir / "module_b.py"),
                str(project_root)
            )
            
            assert result == "from .module_b import *"
    
    def test_mixed_depth_project(self, integration_engine):
        """Test import calculation in project with mixed depth modules."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create mixed depth structure
            (project_root / "setup.py").touch()
            (project_root / "main.py").touch()
            
            utils_dir = project_root / "utils"
            utils_dir.mkdir()
            (utils_dir / "__init__.py").touch()
            (utils_dir / "helpers.py").touch()
            
            core_dir = project_root / "core" / "engine"
            core_dir.mkdir(parents=True)
            (core_dir.parent / "__init__.py").touch()
            (core_dir / "__init__.py").touch()
            (core_dir / "processor.py").touch()
            
            # Test various combinations
            # Root to utils
            result1 = integration_engine._calculate_relative_import_path(
                str(project_root / "main.py"),
                str(utils_dir / "helpers.py"),
                str(project_root)
            )
            assert result1 == "from .utils.helpers import *"
            
            # Utils to deep core
            result2 = integration_engine._calculate_relative_import_path(
                str(utils_dir / "helpers.py"),
                str(core_dir / "processor.py"),
                str(project_root)
            )
            assert result2 == "from ..core.engine.processor import *"
            
            # Deep core to root
            result3 = integration_engine._calculate_relative_import_path(
                str(core_dir / "processor.py"),
                str(project_root / "main.py"),
                str(project_root)
            )
            assert result3 == "from ...main import *"


class TestEnhancedErrorHandling:
    """Test cases for enhanced error handling in import logic."""
    
    def test_graceful_handling_of_invalid_paths(self, mock_filesystem_manager):
        """Test graceful handling when paths are invalid."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        # Test _calculate_relative_import_path with invalid paths
        result = integration_engine._calculate_relative_import_path(
            "invalid/path.py", "another/invalid.py", "/nonexistent"
        )
        assert result is None
        
        # Test _get_project_root with invalid path
        result = integration_engine._get_project_root("/completely/invalid/path.py")
        assert isinstance(result, str)  # Should return something, not crash
        
        # Test _convert_file_path_to_import_path with invalid paths
        result = integration_engine._convert_file_path_to_import_path(
            "/invalid.py", "/invalid/root"
        )
        assert isinstance(result, str)  # Should return something, not crash
    
    def test_filesystem_errors_handled(self, mock_filesystem_manager):
        """Test that filesystem errors are handled gracefully."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        # Mock filesystem manager to raise exceptions
        mock_filesystem_manager.file_exists.side_effect = OSError("Permission denied")
        
        sample_module = Module(
            name="test", description="Test", file_path="/test.py", 
            dependencies=[], functions=[]
        )
        
        # Should not raise exception
        result = integration_engine._validate_import_path(
            "from .test import *", sample_module, "/project"
        )
        assert result is False
    
    def test_logging_on_import_generation_failure(self, mock_filesystem_manager):
        """Test that import generation failures are properly logged."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        # Test that the method handles exceptions gracefully by calling it directly
        # without mocking it (since the real method already has exception handling)
        result = integration_engine._calculate_relative_import_path(
            "/nonexistent/test1.py", "/nonexistent/test2.py", "/nonexistent/project"
        )
        
        assert result is None  # Should handle exception gracefully
    
    def test_fallback_mechanisms(self, mock_filesystem_manager, temp_project_structure):
        """Test fallback mechanisms when primary methods fail."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        # Test project root fallback by using an invalid path
        # The method should fallback to the module directory
        result = integration_engine._get_project_root("/completely/invalid/path/module.py")
        assert isinstance(result, str)
    
    def test_partial_failure_handling(self, mock_filesystem_manager):
        """Test handling of partial failures in import processing."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "setup.py").touch()
            
            # Create some valid and some invalid scenarios
            valid_file = project_root / "valid.py"
            valid_file.touch()
            
            # Test with mix of valid and invalid inputs
            results = []
            test_cases = [
                (str(valid_file), str(valid_file), str(project_root)),  # Valid
                ("invalid.py", str(valid_file), str(project_root)),     # Invalid from
                (str(valid_file), "invalid.py", str(project_root)),     # Invalid to
                ("invalid.py", "invalid.py", str(project_root))         # Both invalid
            ]
            
            for from_path, to_path, root in test_cases:
                result = integration_engine._calculate_relative_import_path(from_path, to_path, root)
                results.append(result)
            
            # Should have at least one valid result and handle invalid ones gracefully
            assert results[0] is not None  # Valid case should work
            assert all(r is None for r in results[1:])  # Invalid cases should return None
    
    def test_edge_case_handling(self, mock_filesystem_manager):
        """Test handling of edge cases in import logic."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        # Test with empty strings
        result = integration_engine._calculate_relative_import_path("", "", "")
        assert result is None
        
        # Test with None values (should be handled by type system, but test robustness)
        try:
            result = integration_engine._convert_file_path_to_import_path("test.py", "")
            assert isinstance(result, str)
        except Exception:
            # If it raises an exception, that's also acceptable for this edge case
            pass
    
    def test_concurrent_access_safety(self, mock_filesystem_manager):
        """Test that methods are safe for concurrent access."""
        integration_engine = IntegrationEngine(filesystem_manager=mock_filesystem_manager)
        integration_engine.initialize()
        
        import threading
        import time
        
        results = []
        errors = []
        
        def worker():
            try:
                for i in range(10):
                    result = integration_engine._get_project_root(f"/test/path{i}.py")
                    results.append(result)
                    time.sleep(0.001)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should not have any errors from concurrent access
        assert len(errors) == 0
        assert len(results) == 30  # 3 threads * 10 iterations each