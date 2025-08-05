"""
Tests for integration phase validation in the integration engine.

This module tests that the integration engine properly validates dependencies
at the integration level and catches missing dependencies.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from a3.engines.integration import IntegrationEngine
from a3.managers.dependency import DependencyAnalyzer
from a3.core.models import Module, FunctionSpec, ValidationResult, ValidationLevel


class TestIntegrationValidation:
    """Test integration phase validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_path = "/test/project"
        self.dependency_analyzer = Mock(spec=DependencyAnalyzer)
        self.filesystem_manager = Mock()
        
        self.integration_engine = IntegrationEngine(
            dependency_analyzer=self.dependency_analyzer,
            filesystem_manager=self.filesystem_manager
        )
        # Initialize the engine to avoid runtime errors
        self.integration_engine._initialized = True
        
        # Sample modules for testing
        self.module_a = Module(
            name="module_a",
            file_path="/test/project/module_a.py",
            description="Module A",
            functions=[],
            dependencies=["module_b"]  # Depends on module_b
        )
        
        self.module_b = Module(
            name="module_b", 
            file_path="/test/project/module_b.py",
            description="Module B",
            functions=[],
            dependencies=[]
        )
        
        self.module_c = Module(
            name="module_c",
            file_path="/test/project/module_c.py", 
            description="Module C",
            functions=[],
            dependencies=["missing_module"]  # Depends on non-existent module
        )
    
    def test_integration_validation_uses_integration_level(self):
        """Test that integration validation explicitly uses INTEGRATION validation level."""
        # Setup: Mock successful validation
        self.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=True,
            issues=[],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Execute: Validate modules for integration
        errors = self.integration_engine._validate_modules_for_integration([self.module_a, self.module_b])
        
        # Verify: analyze_dependencies was called with INTEGRATION level
        self.dependency_analyzer.analyze_dependencies.assert_called_once_with(
            [self.module_a, self.module_b],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Should have no errors for valid modules
        assert errors == []
    
    def test_integration_validation_catches_missing_dependencies(self):
        """Test that integration validation catches missing dependencies."""
        # Setup: Mock validation that finds missing dependencies
        self.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=False,
            issues=["Module 'module_c' has missing dependencies: ['missing_module']"],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Execute: Validate modules with missing dependencies
        errors = self.integration_engine._validate_modules_for_integration([self.module_c])
        
        # Verify: Error was caught and properly formatted
        assert len(errors) == 1
        assert "Integration validation failed" in errors[0]
        assert "missing dependencies" in errors[0]
        assert "missing_module" in errors[0]
    
    def test_integration_validation_catches_circular_dependencies(self):
        """Test that integration validation catches circular dependencies."""
        # Setup: Mock validation that finds circular dependencies
        self.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=False,
            issues=["Circular dependency detected: module_a -> module_b -> module_a"],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Execute: Validate modules with circular dependencies
        errors = self.integration_engine._validate_modules_for_integration([self.module_a, self.module_b])
        
        # Verify: Circular dependency error was caught
        assert len(errors) == 1
        assert "Integration validation failed" in errors[0]
        assert "Circular dependency detected" in errors[0]
    
    def test_integration_validation_fallback_without_analyzer(self):
        """Test integration validation fallback when no dependency analyzer is available."""
        # Setup: Integration engine without dependency analyzer
        engine_no_analyzer = IntegrationEngine(
            dependency_analyzer=None,
            filesystem_manager=self.filesystem_manager
        )
        engine_no_analyzer._initialized = True
        
        # Execute: Validate modules without analyzer - module_a depends on module_b but only module_a is provided
        errors = engine_no_analyzer._validate_modules_for_integration([self.module_a])
        
        # Verify: Fallback validation catches missing dependencies
        assert len(errors) == 1
        assert "Integration validation failed" in errors[0]
        assert "depends on missing module" in errors[0]
        assert "module_b" in errors[0]
    
    def test_integration_validation_handles_analyzer_errors(self):
        """Test that integration validation handles dependency analyzer errors gracefully."""
        # Setup: Mock analyzer that raises an exception
        self.dependency_analyzer.analyze_dependencies.side_effect = Exception("Analyzer error")
        
        # Execute: Validate modules when analyzer fails
        errors = self.integration_engine._validate_modules_for_integration([self.module_a])
        
        # Verify: Error was caught and reported
        assert len(errors) == 1
        assert "Failed to perform integration-level dependency validation" in errors[0]
        assert "Analyzer error" in errors[0]
    
    def test_integration_validation_duplicate_module_names(self):
        """Test that integration validation catches duplicate module names."""
        # Setup: Modules with duplicate names
        duplicate_module = Module(
            name="module_a",  # Same name as self.module_a
            file_path="/test/project/duplicate_a.py",
            description="Duplicate Module A",
            functions=[],
            dependencies=[]
        )
        
        self.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=True,
            issues=[],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Execute: Validate modules with duplicate names
        errors = self.integration_engine._validate_modules_for_integration([self.module_a, duplicate_module])
        
        # Verify: Duplicate names were caught
        assert len(errors) == 1
        assert "Duplicate module names found" in errors[0]
        assert "module_a" in errors[0]
    
    def test_integration_validation_invalid_file_paths(self):
        """Test that integration validation catches invalid file paths."""
        # Setup: Module with invalid file path
        invalid_module = Module(
            name="invalid_module",
            file_path="",  # Empty file path
            description="Invalid Module",
            functions=[],
            dependencies=[]
        )
        
        non_python_module = Module(
            name="non_python_module",
            file_path="/test/project/module.txt",  # Not a .py file
            description="Non-Python Module", 
            functions=[],
            dependencies=[]
        )
        
        self.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=True,
            issues=[],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Execute: Validate modules with invalid paths
        errors = self.integration_engine._validate_modules_for_integration([invalid_module, non_python_module])
        
        # Verify: Invalid paths were caught
        assert len(errors) == 2
        assert any("empty file path" in error for error in errors)
        assert any("must end with .py" in error for error in errors)
    
    def test_full_integration_with_missing_dependencies(self):
        """Test full integration process fails appropriately with missing dependencies."""
        # Setup: Mock filesystem operations
        self.filesystem_manager.file_exists.return_value = False
        self.filesystem_manager.write_file.return_value = True
        
        # Mock dependency analyzer to report missing dependencies
        self.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=False,
            issues=["Module 'module_c' has missing dependencies: ['missing_module']"],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Initialize the engine
        self.integration_engine._initialized = True
        
        # Execute: Attempt full integration
        result = self.integration_engine.integrate_modules([self.module_c])
        
        # Verify: Integration failed due to missing dependencies
        assert not result.success
        assert len(result.import_errors) > 0
        assert any("Integration validation failed" in error for error in result.import_errors)
        assert any("missing dependencies" in error for error in result.import_errors)
    
    def test_integration_succeeds_with_valid_dependencies(self):
        """Test that integration succeeds when all dependencies are valid."""
        # Setup: Mock successful validation and file operations
        self.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=True,
            issues=[],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        self.dependency_analyzer.get_build_order.return_value = ["module_b", "module_a"]
        
        self.filesystem_manager.file_exists.return_value = True
        self.filesystem_manager.read_file.return_value = "# Module content"
        
        # Initialize the engine
        self.integration_engine._initialized = True
        
        # Mock import generation
        with patch.object(self.integration_engine, 'generate_imports') as mock_generate:
            mock_generate.return_value = {
                "module_a": ["from .module_b import *"],
                "module_b": []
            }
            
            with patch.object(self.integration_engine, 'verify_integration') as mock_verify:
                mock_verify.return_value = ValidationResult(is_valid=True, issues=[], warnings=[])
                
                # Execute: Integration with valid modules
                result = self.integration_engine.integrate_modules([self.module_a, self.module_b])
        
        # Verify: Integration succeeded
        assert result.success
        assert len(result.import_errors) == 0
        assert "module_a" in result.integrated_modules
        assert "module_b" in result.integrated_modules


if __name__ == "__main__":
    pytest.main([__file__])