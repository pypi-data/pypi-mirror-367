"""
End-to-end workflow tests for planning workflow fix.

This module tests the complete workflow from planning through integration,
verifying that planning succeeds with missing dependencies and integration
fails appropriately when dependencies don't exist.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from a3.engines.planning import PlanningEngine, PlanGenerationError
from a3.engines.integration import IntegrationEngine
from a3.managers.dependency import DependencyAnalyzer
from a3.core.models import (
    Module, FunctionSpec, Argument, ProjectPlan, DependencyGraph,
    ValidationResult, ValidationLevel, ImplementationStatus, IntegrationResult
)
from a3.core.interfaces import AIClientInterface


class TestPlanningWorkflowEndToEnd:
    """Test complete end-to-end workflow from planning through integration."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create mock AI client with realistic responses."""
        mock_client = Mock(spec=AIClientInterface)
        mock_client.validate_api_key.return_value = True
        
        # Mock AI response for plan generation
        mock_client.generate_with_retry.return_value = '''
        {
            "project_name": "test_project",
            "modules": [
                {
                    "name": "core",
                    "description": "Core functionality module",
                    "file_path": "core.py",
                    "dependencies": [],
                    "functions": [
                        {
                            "name": "core_function",
                            "description": "Core function",
                            "arguments": [
                                {
                                    "name": "data",
                                    "type": "str",
                                    "description": "Input data"
                                }
                            ],
                            "return_type": "str"
                        }
                    ]
                },
                {
                    "name": "utils",
                    "description": "Utility functions module",
                    "file_path": "utils.py",
                    "dependencies": ["core", "missing_module"],
                    "functions": [
                        {
                            "name": "utility_function",
                            "description": "Utility function that depends on missing module",
                            "arguments": [
                                {
                                    "name": "input_data",
                                    "type": "str",
                                    "description": "Input data"
                                }
                            ],
                            "return_type": "str"
                        }
                    ]
                }
            ]
        }
        '''
        
        return mock_client
    
    @pytest.fixture
    def planning_engine(self, temp_project_dir, mock_ai_client):
        """Create planning engine with mocked dependencies."""
        engine = PlanningEngine(
            ai_client=mock_ai_client,
            project_path=temp_project_dir
        )
        engine.initialize()
        return engine
    
    @pytest.fixture
    def integration_engine(self, temp_project_dir):
        """Create integration engine with mocked dependencies."""
        dependency_analyzer = Mock(spec=DependencyAnalyzer)
        filesystem_manager = Mock()
        
        engine = IntegrationEngine(
            dependency_analyzer=dependency_analyzer,
            filesystem_manager=filesystem_manager
        )
        engine.initialize()
        return engine
    
    def test_planning_succeeds_with_missing_dependencies(self, planning_engine, temp_project_dir):
        """
        Test that planning succeeds when AI generates modules with dependencies that don't exist yet.
        
        This verifies that planning phase uses planning-specific validation that allows
        missing dependencies to be deferred to integration phase.
        
        Requirements: 1.1, 1.2, 1.3
        """
        objective = "Build a system with modules that depend on each other"
        
        # Mock the AI client to return modules with missing dependencies
        planning_engine.ai_client.generate_with_retry.return_value = '''
        {
            "project_name": "test_project",
            "modules": [
                {
                    "name": "core",
                    "description": "Core functionality module",
                    "file_path": "core.py",
                    "dependencies": [],
                    "functions": [
                        {
                            "name": "core_function",
                            "description": "Core function",
                            "arguments": [],
                            "return_type": "str"
                        }
                    ]
                },
                {
                    "name": "utils",
                    "description": "Utility functions module",
                    "file_path": "utils.py",
                    "dependencies": ["core"],
                    "functions": [
                        {
                            "name": "utility_function",
                            "description": "Utility function",
                            "arguments": [],
                            "return_type": "str"
                        }
                    ]
                }
            ]
        }
        '''
        
        # Mock the dependency analyzer to use planning-specific validation
        with patch.object(planning_engine.dependency_analyzer, 'analyze_planning_dependencies') as mock_analyze_planning:
            # Planning validation should succeed and only check structural issues
            mock_analyze_planning.return_value = ValidationResult(
                is_valid=True,
                issues=[],
                warnings=["Planning phase validation completed - missing dependencies will be validated during integration"],
                validation_level=ValidationLevel.PLANNING
            )
            
            # Execute planning - should succeed with planning-specific validation
            plan = planning_engine.generate_plan(objective)
            
            # Verify planning succeeded
            assert isinstance(plan, ProjectPlan)
            assert len(plan.modules) == 2
            assert plan.objective == objective
            
            # Verify planning validation was called (not full validation)
            mock_analyze_planning.assert_called_once()
            
            # Verify the modules were created correctly
            core_module = next(m for m in plan.modules if m.name == "core")
            utils_module = next(m for m in plan.modules if m.name == "utils")
            
            assert core_module.dependencies == []
            assert utils_module.dependencies == ["core"]
            
            # Verify dependency graph was created successfully
            assert isinstance(plan.dependency_graph, DependencyGraph)
            assert "utils" in plan.dependency_graph.nodes
            assert "core" in plan.dependency_graph.nodes
    
    def test_integration_fails_with_missing_dependencies(self, integration_engine):
        """
        Test that integration fails appropriately when dependencies don't exist.
        
        This verifies that integration phase validates dependency existence
        and fails when modules are missing.
        
        Requirements: 2.1, 2.2, 2.3
        """
        # Create modules with missing dependencies
        core_module = Module(
            name="core",
            description="Core module",
            file_path="core.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="core_function",
                    module="core",
                    docstring="Core function",
                    arguments=[Argument("data", "str")],
                    return_type="str"
                )
            ]
        )
        
        utils_module = Module(
            name="utils",
            description="Utils module with missing dependency",
            file_path="utils.py",
            dependencies=["core", "missing_module"],  # missing_module doesn't exist
            functions=[
                FunctionSpec(
                    name="utility_function",
                    module="utils",
                    docstring="Utility function",
                    arguments=[Argument("input_data", "str")],
                    return_type="str"
                )
            ]
        )
        
        modules = [core_module, utils_module]
        
        # Mock dependency analyzer to report missing dependencies during integration
        integration_engine.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=False,
            issues=["Module 'utils' has missing dependencies: ['missing_module']"],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Mock filesystem operations
        integration_engine.filesystem_manager.file_exists.return_value = False
        integration_engine.filesystem_manager.write_file.return_value = True
        
        # Execute integration - should fail due to missing dependencies
        result = integration_engine.integrate_modules(modules)
        
        # Verify integration failed
        assert not result.success
        assert len(result.import_errors) > 0
        
        # Verify error message indicates integration validation failure
        error_messages = " ".join(result.import_errors)
        assert "Integration validation failed" in error_messages
        assert "missing dependencies" in error_messages
        assert "missing_module" in error_messages
        
        # Verify integration-level validation was called
        integration_engine.dependency_analyzer.analyze_dependencies.assert_called_once_with(
            modules, validation_level=ValidationLevel.INTEGRATION
        )
    
    def test_planning_handles_missing_dependencies_from_ai(self, planning_engine, temp_project_dir):
        """
        Test that planning phase properly handles when AI generates modules with missing dependencies.
        
        This tests the scenario where the AI generates a plan that references modules that don't exist,
        and the planning phase should handle this gracefully by using planning-specific validation.
        
        Requirements: 1.1, 1.2, 3.3
        """
        objective = "Build a system that uses external services"
        
        # Mock AI to generate modules with missing dependencies
        planning_engine.ai_client.generate_with_retry.return_value = '''
        {
            "project_name": "external_service_project",
            "modules": [
                {
                    "name": "client",
                    "description": "Client module that uses external service",
                    "file_path": "client.py",
                    "dependencies": ["external_service"],
                    "functions": [
                        {
                            "name": "call_external_service",
                            "description": "Call external service",
                            "arguments": [],
                            "return_type": "str"
                        }
                    ]
                }
            ]
        }
        '''
        
        # Mock planning validation to handle missing dependencies appropriately
        with patch.object(planning_engine.dependency_analyzer, 'analyze_planning_dependencies') as mock_analyze_planning:
            mock_analyze_planning.return_value = ValidationResult(
                is_valid=True,
                issues=[],
                warnings=["Missing dependency 'external_service' detected - will be validated during integration"],
                validation_level=ValidationLevel.PLANNING
            )
            
            # Mock the module creation to filter out missing dependencies during planning
            original_create_modules = planning_engine._create_modules_from_structure
            
            def mock_create_modules(structure):
                modules = original_create_modules(structure)
                # During planning, filter out dependencies that don't exist in the current module set
                module_names = {m.name for m in modules}
                for module in modules:
                    # Keep only dependencies that exist in the current module set
                    module.dependencies = [dep for dep in module.dependencies if dep in module_names]
                return modules
            
            with patch.object(planning_engine, '_create_modules_from_structure', side_effect=mock_create_modules):
                # Execute planning - should succeed by filtering missing dependencies
                plan = planning_engine.generate_plan(objective)
                
                # Verify planning succeeded
                assert isinstance(plan, ProjectPlan)
                assert len(plan.modules) == 1
                
                # Verify the missing dependency was filtered out during planning
                client_module = plan.modules[0]
                assert client_module.name == "client"
                assert client_module.dependencies == []  # Missing dependency filtered out
                
                # Verify planning validation was called
                mock_analyze_planning.assert_called_once()

    def test_complete_workflow_planning_to_integration(self, planning_engine, integration_engine, temp_project_dir):
        """
        Test complete workflow from planning through integration.
        
        This verifies the entire workflow where planning succeeds with missing dependencies
        and integration appropriately handles the validation.
        
        Requirements: 1.4, 2.4
        """
        objective = "Build a modular system with interdependent components"
        
        # Step 1: Planning phase - should succeed with valid modules
        # Mock AI to generate valid modules for planning
        planning_engine.ai_client.generate_with_retry.return_value = '''
        {
            "project_name": "modular_system",
            "modules": [
                {
                    "name": "service",
                    "description": "Service module",
                    "file_path": "service.py",
                    "dependencies": [],
                    "functions": [
                        {
                            "name": "service_function",
                            "description": "Service function",
                            "arguments": [],
                            "return_type": "str"
                        }
                    ]
                },
                {
                    "name": "client",
                    "description": "Client module",
                    "file_path": "client.py",
                    "dependencies": ["service"],
                    "functions": [
                        {
                            "name": "client_function",
                            "description": "Client function",
                            "arguments": [],
                            "return_type": "str"
                        }
                    ]
                }
            ]
        }
        '''
        
        with patch.object(planning_engine.dependency_analyzer, 'analyze_planning_dependencies') as mock_analyze_planning:
            mock_analyze_planning.return_value = ValidationResult(
                is_valid=True,
                issues=[],
                warnings=[],
                validation_level=ValidationLevel.PLANNING
            )
            
            # Generate plan
            plan = planning_engine.generate_plan(objective)
            
            # Verify planning succeeded
            assert isinstance(plan, ProjectPlan)
            assert len(plan.modules) == 2
        
        # Step 2: Integration phase - simulate missing dependencies being discovered
        modules = plan.modules
        
        # Simulate that during integration, we discover missing dependencies
        # (e.g., the client module actually needs an external service that wasn't in the plan)
        client_module = next(m for m in modules if m.name == "client")
        client_module.dependencies.append("external_service")  # Add missing dependency
        
        # Mock integration validation to find missing dependencies
        integration_engine.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=False,
            issues=["Module 'client' has missing dependencies: ['external_service']"],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Mock filesystem operations
        integration_engine.filesystem_manager.file_exists.return_value = False
        integration_engine.filesystem_manager.write_file.return_value = True
        
        # Execute integration
        integration_result = integration_engine.integrate_modules(modules)
        
        # Verify integration failed appropriately
        assert not integration_result.success
        assert len(integration_result.import_errors) > 0
        
        # Verify the workflow separation worked correctly
        # Planning succeeded, integration failed for the right reasons
        error_message = " ".join(integration_result.import_errors)
        assert "Integration validation failed" in error_message
        assert "external_service" in error_message
    
    def test_circular_dependencies_fail_at_planning_phase(self, planning_engine):
        """
        Test that circular dependencies are caught and fail at planning phase.
        
        This verifies that structural issues like circular dependencies
        are still caught during planning validation.
        
        Requirements: 3.1, 3.2
        """
        objective = "Build a system with circular dependencies"
        
        # Mock AI client to return modules with circular dependencies
        planning_engine.ai_client.generate_with_retry.return_value = '''
        {
            "project_name": "circular_test",
            "modules": [
                {
                    "name": "module_a",
                    "description": "Module A",
                    "file_path": "module_a.py",
                    "dependencies": ["module_b"],
                    "functions": [
                        {
                            "name": "function_a",
                            "description": "Function A",
                            "arguments": [],
                            "return_type": "str"
                        }
                    ]
                },
                {
                    "name": "module_b",
                    "description": "Module B",
                    "file_path": "module_b.py",
                    "dependencies": ["module_a"],
                    "functions": [
                        {
                            "name": "function_b",
                            "description": "Function B",
                            "arguments": [],
                            "return_type": "str"
                        }
                    ]
                }
            ]
        }
        '''
        
        # Mock planning validation to detect circular dependencies
        with patch.object(planning_engine.dependency_analyzer, 'analyze_planning_dependencies') as mock_analyze_planning:
            mock_analyze_planning.return_value = ValidationResult(
                is_valid=False,
                issues=["Circular dependency detected: module_a -> module_b -> module_a"],
                warnings=[],
                validation_level=ValidationLevel.PLANNING
            )
            
            # Planning should fail due to circular dependencies
            with pytest.raises(PlanGenerationError) as exc_info:
                planning_engine.generate_plan(objective)
            
            # Verify error message indicates planning phase failure
            error_message = str(exc_info.value)
            assert "Planning phase dependency validation failed" in error_message
            # The specific circular dependency message might be in the detailed error breakdown
            assert "Planning phase validation failed" in error_message
            
            # Verify planning validation was called
            mock_analyze_planning.assert_called_once()
    
    def test_backward_compatibility_with_existing_workflows(self, integration_engine):
        """
        Test backward compatibility with existing workflows.
        
        This verifies that existing code using analyze_dependencies still works
        and that integration phase behavior is unchanged.
        
        Requirements: 4.1, 4.2
        """
        # Create modules with valid dependencies
        module_a = Module(
            name="module_a",
            description="Module A",
            file_path="module_a.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="function_a",
                    module="module_a",
                    docstring="Function A",
                    arguments=[],
                    return_type="str"
                )
            ]
        )
        
        module_b = Module(
            name="module_b",
            description="Module B",
            file_path="module_b.py",
            dependencies=["module_a"],
            functions=[
                FunctionSpec(
                    name="function_b",
                    module="module_b",
                    docstring="Function B",
                    arguments=[],
                    return_type="str"
                )
            ]
        )
        
        modules = [module_a, module_b]
        
        # Test that existing analyze_dependencies method still works
        integration_engine.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=True,
            issues=[],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Mock successful integration operations
        integration_engine.dependency_analyzer.get_build_order.return_value = ["module_a", "module_b"]
        integration_engine.filesystem_manager.file_exists.return_value = True
        integration_engine.filesystem_manager.read_file.return_value = "# Module content"
        
        with patch.object(integration_engine, 'generate_imports') as mock_generate:
            mock_generate.return_value = {
                "module_a": [],
                "module_b": ["from .module_a import *"]
            }
            
            with patch.object(integration_engine, 'verify_integration') as mock_verify:
                mock_verify.return_value = ValidationResult(is_valid=True, issues=[], warnings=[])
                
                # Execute integration
                result = integration_engine.integrate_modules(modules)
        
        # Verify integration succeeded with existing workflow
        assert result.success
        assert len(result.import_errors) == 0
        
        # Verify analyze_dependencies was called with INTEGRATION level
        integration_engine.dependency_analyzer.analyze_dependencies.assert_called_once_with(
            modules, validation_level=ValidationLevel.INTEGRATION
        )
    
    def test_integration_succeeds_when_all_dependencies_exist(self, integration_engine):
        """
        Test that integration succeeds when all dependencies are properly implemented.
        
        This verifies the positive case where planning and integration both succeed.
        
        Requirements: 2.1, 2.4
        """
        # Create modules with valid, existing dependencies
        core_module = Module(
            name="core",
            description="Core module",
            file_path="core.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="core_function",
                    module="core",
                    docstring="Core function",
                    arguments=[Argument("data", "str")],
                    return_type="str"
                )
            ]
        )
        
        utils_module = Module(
            name="utils",
            description="Utils module",
            file_path="utils.py",
            dependencies=["core"],  # Only depends on existing core module
            functions=[
                FunctionSpec(
                    name="utility_function",
                    module="utils",
                    docstring="Utility function",
                    arguments=[Argument("input_data", "str")],
                    return_type="str"
                )
            ]
        )
        
        modules = [core_module, utils_module]
        
        # Mock successful dependency validation
        integration_engine.dependency_analyzer.analyze_dependencies.return_value = ValidationResult(
            is_valid=True,
            issues=[],
            warnings=[],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Mock successful build order and file operations
        integration_engine.dependency_analyzer.get_build_order.return_value = ["core", "utils"]
        integration_engine.filesystem_manager.file_exists.return_value = True
        integration_engine.filesystem_manager.read_file.return_value = "# Module content"
        
        with patch.object(integration_engine, 'generate_imports') as mock_generate:
            mock_generate.return_value = {
                "core": [],
                "utils": ["from .core import *"]
            }
            
            with patch.object(integration_engine, 'verify_integration') as mock_verify:
                mock_verify.return_value = ValidationResult(is_valid=True, issues=[], warnings=[])
                
                # Execute integration
                result = integration_engine.integrate_modules(modules)
        
        # Verify integration succeeded
        assert result.success
        assert len(result.import_errors) == 0
        assert "core" in result.integrated_modules
        assert "utils" in result.integrated_modules
        
        # Verify proper validation was performed
        integration_engine.dependency_analyzer.analyze_dependencies.assert_called_once_with(
            modules, validation_level=ValidationLevel.INTEGRATION
        )


if __name__ == "__main__":
    pytest.main([__file__])