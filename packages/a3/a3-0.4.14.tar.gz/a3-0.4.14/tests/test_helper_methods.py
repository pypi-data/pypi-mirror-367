"""
Unit tests for the helper methods for project structure analysis.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from a3.engines.integration import IntegrationEngine
from a3.core.models import Module, FunctionSpec, Argument


class TestHelperMethods(unittest.TestCase):
    """Test cases for the helper methods added for project structure analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = IntegrationEngine()
        
    def test_get_project_root_with_git(self):
        """Test _get_project_root method with .git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock project structure
            project_root = Path(temp_dir) / "project"
            project_root.mkdir()
            
            # Create .git directory
            (project_root / ".git").mkdir()
            
            # Create a subdirectory with a module
            subdir = project_root / "src"
            subdir.mkdir()
            module_path = subdir / "test_module.py"
            module_path.write_text("# test module")
            
            # Test that it finds the project root
            result = self.engine._get_project_root(str(module_path))
            self.assertEqual(result, str(project_root))
    
    def test_get_project_root_with_setup_py(self):
        """Test _get_project_root method with setup.py file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock project structure
            project_root = Path(temp_dir) / "project"
            project_root.mkdir()
            
            # Create setup.py file
            (project_root / "setup.py").write_text("# setup file")
            
            # Create a subdirectory with a module
            subdir = project_root / "src"
            subdir.mkdir()
            module_path = subdir / "test_module.py"
            module_path.write_text("# test module")
            
            # Test that it finds the project root
            result = self.engine._get_project_root(str(module_path))
            self.assertEqual(result, str(project_root))
    
    def test_get_project_root_fallback(self):
        """Test _get_project_root method fallback behavior."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a module without project indicators
            module_path = Path(temp_dir) / "test_module.py"
            module_path.write_text("# test module")
            
            # Test that it falls back to module directory
            result = self.engine._get_project_root(str(module_path))
            self.assertEqual(result, str(module_path.parent))
    
    def test_convert_file_path_to_import_path_simple(self):
        """Test _convert_file_path_to_import_path with simple paths."""
        project_root = "/project"
        file_path = "/project/module.py"
        
        result = self.engine._convert_file_path_to_import_path(file_path, project_root)
        self.assertEqual(result, "module")
    
    def test_convert_file_path_to_import_path_nested(self):
        """Test _convert_file_path_to_import_path with nested paths."""
        project_root = "/project"
        file_path = "/project/src/utils/helper.py"
        
        result = self.engine._convert_file_path_to_import_path(file_path, project_root)
        self.assertEqual(result, "src.utils.helper")
    
    def test_convert_file_path_to_import_path_windows(self):
        """Test _convert_file_path_to_import_path with Windows paths."""
        if os.name == 'nt':  # Only run on Windows
            project_root = "C:\\project"
            file_path = "C:\\project\\src\\utils\\helper.py"
            
            result = self.engine._convert_file_path_to_import_path(file_path, project_root)
            self.assertEqual(result, "src.utils.helper")
    
    def test_convert_file_path_to_import_path_fallback(self):
        """Test _convert_file_path_to_import_path fallback behavior."""
        # Test with invalid paths that should trigger exception handling
        result = self.engine._convert_file_path_to_import_path("invalid", "invalid")
        self.assertEqual(result, "")  # Should fallback to empty string for completely invalid paths
    
    def test_analyze_project_structure_empty_modules(self):
        """Test _analyze_project_structure with empty module list."""
        result = self.engine._analyze_project_structure([])
        
        expected = {
            'project_root': '',
            'module_paths': {},
            'package_hierarchy': {},
            'directory_structure': {},
            'import_relationships': {}
        }
        self.assertEqual(result, expected)
    
    def test_analyze_project_structure_single_module(self):
        """Test _analyze_project_structure with single module."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_root = Path(temp_dir)
            (project_root / "README.md").write_text("# Test Project")
            
            module_path = project_root / "test_module.py"
            module = Module(
                name="test_module",
                file_path=str(module_path),
                description="Test module",
                functions=[],
                dependencies=[]
            )
            
            result = self.engine._analyze_project_structure([module])
            
            self.assertEqual(result['project_root'], str(project_root))
            self.assertEqual(result['module_paths'], {'test_module': str(module_path)})
            self.assertEqual(result['package_hierarchy'], {'': ['test_module']})
            self.assertEqual(result['directory_structure'], {'.': ['test_module']})
            self.assertEqual(result['import_relationships'], {'test_module': []})
    
    def test_analyze_project_structure_multiple_modules(self):
        """Test _analyze_project_structure with multiple modules and dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_root = Path(temp_dir)
            (project_root / "README.md").write_text("# Test Project")
            
            # Create subdirectory
            subdir = project_root / "utils"
            subdir.mkdir()
            
            # Create modules
            module1_path = project_root / "main.py"
            module2_path = subdir / "helper.py"
            
            modules = [
                Module(
                    name="main",
                    file_path=str(module1_path),
                    description="Main module",
                    functions=[],
                    dependencies=["helper"]
                ),
                Module(
                    name="helper",
                    file_path=str(module2_path),
                    description="Helper module",
                    functions=[],
                    dependencies=[]
                )
            ]
            
            result = self.engine._analyze_project_structure(modules)
            
            self.assertEqual(result['project_root'], str(project_root))
            self.assertEqual(result['module_paths'], {
                'main': str(module1_path),
                'helper': str(module2_path)
            })
            self.assertEqual(result['package_hierarchy'], {
                '': ['main'],
                'utils': ['helper']
            })
            self.assertEqual(result['directory_structure'], {
                '.': ['main'],
                'utils': ['helper']
            })
            self.assertEqual(result['import_relationships'], {
                'main': ['helper'],
                'helper': []
            })
    
    def test_analyze_project_structure_error_handling(self):
        """Test _analyze_project_structure error handling."""
        # Create a module with an invalid path that might cause issues
        module = Module(
            name="test_module",
            file_path="",  # Invalid empty path
            description="Test module",
            functions=[],
            dependencies=[]
        )
        
        # Should not raise exception, should return minimal structure
        result = self.engine._analyze_project_structure([module])
        
        # Should have basic structure even with error
        self.assertIn('project_root', result)
        self.assertIn('module_paths', result)
        self.assertIn('package_hierarchy', result)
        self.assertIn('directory_structure', result)
        self.assertIn('import_relationships', result)
    
    def test_helper_methods_integration(self):
        """Test that all helper methods work together correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a realistic project structure
            project_root = Path(temp_dir)
            (project_root / "pyproject.toml").write_text("[tool.poetry]")
            
            # Create package structure
            src_dir = project_root / "src"
            src_dir.mkdir()
            utils_dir = src_dir / "utils"
            utils_dir.mkdir()
            
            # Create module files
            main_path = src_dir / "main.py"
            utils_path = utils_dir / "helpers.py"
            
            # Test _get_project_root
            detected_root = self.engine._get_project_root(str(main_path))
            self.assertEqual(detected_root, str(project_root))
            
            # Test _convert_file_path_to_import_path
            main_import = self.engine._convert_file_path_to_import_path(str(main_path), detected_root)
            utils_import = self.engine._convert_file_path_to_import_path(str(utils_path), detected_root)
            
            self.assertEqual(main_import, "src.main")
            self.assertEqual(utils_import, "src.utils.helpers")
            
            # Test _analyze_project_structure
            modules = [
                Module(
                    name="main",
                    file_path=str(main_path),
                    description="Main module",
                    functions=[],
                    dependencies=["helpers"]
                ),
                Module(
                    name="helpers",
                    file_path=str(utils_path),
                    description="Helper utilities",
                    functions=[],
                    dependencies=[]
                )
            ]
            
            structure = self.engine._analyze_project_structure(modules)
            
            # Verify the structure analysis used the correct project root
            self.assertEqual(structure['project_root'], detected_root)
            self.assertEqual(structure['package_hierarchy'], {
                'src': ['main'],
                'src.utils': ['helpers']
            })


if __name__ == '__main__':
    unittest.main()