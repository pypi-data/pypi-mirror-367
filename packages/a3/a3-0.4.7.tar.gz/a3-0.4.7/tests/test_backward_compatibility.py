"""
Tests for backward compatibility and migration support.

This module tests the backward compatibility features and migration utilities
for enhanced planning functionality.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from a3.core.models import (
    ProjectPlan, EnhancedProjectPlan, Module, FunctionSpec, DependencyGraph,
    ImplementationStatus, RequirementsDocument, DesignDocument, TasksDocument,
    DocumentationConfiguration, EnhancedFunctionSpec
)
from a3.engines.planning import PlanningEngine
from a3.managers.state import StateManager
from a3.core.migration import ProjectMigrator, check_project_compatibility, migrate_project_to_enhanced
from a3.core.interfaces import AIClientInterface


class TestBackwardCompatibility:
    """Test backward compatibility features."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        client = Mock(spec=AIClientInterface)
        client.generate_with_retry.return_value = json.dumps({
            "modules": [
                {
                    "name": "test_module",
                    "description": "Test module",
                    "file_path": "test_module.py",
                    "dependencies": [],
                    "functions": [
                        {
                            "name": "test_function",
                            "description": "Test function",
                            "arguments": [],
                            "return_type": "None"
                        }
                    ]
                }
            ]
        })
        return client
    
    @pytest.fixture
    def basic_project_plan(self):
        """Create a basic project plan for testing."""
        module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="test_function",
                    module="test_module",
                    docstring="Test function",
                    arguments=[],
                    return_type="None",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
            ]
        )
        
        return ProjectPlan(
            objective="Test project",
            modules=[module],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=1,
            created_at=datetime.now()
        )
    
    def test_planning_engine_without_ai_client(self, temp_project_dir):
        """Test that PlanningEngine works without AI client (fallback mode)."""
        engine = PlanningEngine(ai_client=None, project_path=temp_project_dir)
        
        # Should not raise an exception
        assert engine.structured_document_generator is None
        assert engine.requirement_driven_function_generator is None
        assert not engine._can_use_enhanced_features()
    
    def test_planning_engine_with_ai_client(self, temp_project_dir, mock_ai_client):
        """Test that PlanningEngine works with AI client."""
        engine = PlanningEngine(ai_client=mock_ai_client, project_path=temp_project_dir)
        engine.initialize()
        
        # Should have enhanced features available
        assert engine.structured_document_generator is not None
        assert engine.requirement_driven_function_generator is not None
        assert engine._can_use_enhanced_features()
    
    def test_generate_plan_fallback_without_ai_client(self, temp_project_dir):
        """Test generate_plan works without AI client."""
        engine = PlanningEngine(ai_client=None, project_path=temp_project_dir)
        
        # Should raise an error since basic generate_plan needs AI client
        with pytest.raises(Exception):
            engine.generate_plan("Test objective")
    
    def test_generate_plan_with_documentation_fallback(self, temp_project_dir, mock_ai_client):
        """Test generate_plan_with_documentation falls back gracefully."""
        engine = PlanningEngine(ai_client=mock_ai_client, project_path=temp_project_dir)
        engine.initialize()
        
        # Mock the structured document generator to fail
        engine.structured_document_generator = None
        
        result = engine.generate_plan_with_documentation("Test objective")
        
        # Should return an EnhancedProjectPlan even without enhanced features
        assert isinstance(result, EnhancedProjectPlan)
        assert result.objective == "Test objective"
        assert result.requirements_document is None
        assert result.design_document is None
        assert result.tasks_document is None
    
    def test_convert_to_enhanced_plan(self, temp_project_dir, basic_project_plan, mock_ai_client):
        """Test conversion of basic plan to enhanced plan."""
        engine = PlanningEngine(ai_client=mock_ai_client, project_path=temp_project_dir)
        
        enhanced_plan = engine._convert_to_enhanced_plan(basic_project_plan)
        
        assert isinstance(enhanced_plan, EnhancedProjectPlan)
        assert enhanced_plan.objective == basic_project_plan.objective
        assert enhanced_plan.modules == basic_project_plan.modules
        assert enhanced_plan.requirements_document is None
        assert enhanced_plan.design_document is None
        assert enhanced_plan.tasks_document is None
        assert enhanced_plan.enhanced_functions == []


class TestStateManagerCompatibility:
    """Test state manager backward compatibility."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def basic_project_plan(self):
        """Create a basic project plan for testing."""
        module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="test_function",
                    module="test_module",
                    docstring="Test function",
                    arguments=[],
                    return_type="None",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
            ]
        )
        
        return ProjectPlan(
            objective="Test project",
            modules=[module],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=1,
            created_at=datetime.now()
        )
    
    def test_save_and_load_basic_project_plan(self, temp_project_dir, basic_project_plan):
        """Test saving and loading basic project plan."""
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        
        # Save basic plan
        state_manager.save_project_plan(basic_project_plan)
        
        # Load plan
        loaded_plan = state_manager.load_project_plan()
        
        assert loaded_plan is not None
        assert isinstance(loaded_plan, ProjectPlan)
        assert not isinstance(loaded_plan, EnhancedProjectPlan)
        assert loaded_plan.objective == basic_project_plan.objective
        assert len(loaded_plan.modules) == len(basic_project_plan.modules)
    
    def test_save_and_load_enhanced_project_plan(self, temp_project_dir, basic_project_plan):
        """Test saving and loading enhanced project plan."""
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        
        # Create enhanced plan
        enhanced_plan = EnhancedProjectPlan(
            objective=basic_project_plan.objective,
            modules=basic_project_plan.modules,
            dependency_graph=basic_project_plan.dependency_graph,
            estimated_functions=basic_project_plan.estimated_functions,
            created_at=basic_project_plan.created_at,
            requirements_document=None,
            design_document=None,
            tasks_document=None,
            documentation_config=None,
            enhanced_functions=[]
        )
        
        # Save enhanced plan
        state_manager.save_project_plan(enhanced_plan)
        
        # Load plan
        loaded_plan = state_manager.load_project_plan()
        
        assert loaded_plan is not None
        assert isinstance(loaded_plan, EnhancedProjectPlan)
        assert loaded_plan.objective == enhanced_plan.objective
        assert len(loaded_plan.modules) == len(enhanced_plan.modules)
    
    def test_migrate_to_enhanced_plan(self, temp_project_dir, basic_project_plan):
        """Test migration from basic to enhanced plan."""
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        
        # Save basic plan first
        state_manager.save_project_plan(basic_project_plan)
        
        # Migrate to enhanced
        success = state_manager.migrate_to_enhanced_plan()
        assert success
        
        # Load and verify it's enhanced
        loaded_plan = state_manager.load_project_plan()
        assert isinstance(loaded_plan, EnhancedProjectPlan)
        assert loaded_plan.objective == basic_project_plan.objective
    
    def test_can_use_enhanced_features(self, temp_project_dir, basic_project_plan):
        """Test detection of enhanced features capability."""
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        
        # Initially should return False
        assert not state_manager.can_use_enhanced_features()
        
        # Save basic plan
        state_manager.save_project_plan(basic_project_plan)
        assert not state_manager.can_use_enhanced_features()
        
        # Migrate to enhanced
        state_manager.migrate_to_enhanced_plan()
        assert state_manager.can_use_enhanced_features()


class TestProjectMigrator:
    """Test project migration utilities."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def basic_project_plan(self):
        """Create a basic project plan for testing."""
        module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            dependencies=[],
            functions=[
                FunctionSpec(
                    name="test_function",
                    module="test_module",
                    docstring="Test function",
                    arguments=[],
                    return_type="None",
                    implementation_status=ImplementationStatus.NOT_STARTED
                )
            ]
        )
        
        return ProjectPlan(
            objective="Test project",
            modules=[module],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=1,
            created_at=datetime.now()
        )
    
    def test_check_compatibility_no_plan(self, temp_project_dir):
        """Test compatibility check with no existing plan."""
        migrator = ProjectMigrator(temp_project_dir)
        
        result = migrator.check_compatibility()
        
        assert not result["compatible"]
        assert not result["has_existing_plan"]
        assert not result["is_already_enhanced"]
        assert not result["migration_needed"]
        assert "No existing project plan found" in result["issues"]
    
    def test_check_compatibility_with_basic_plan(self, temp_project_dir, basic_project_plan):
        """Test compatibility check with basic plan."""
        # Set up project with basic plan
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        state_manager.save_project_plan(basic_project_plan)
        
        migrator = ProjectMigrator(temp_project_dir)
        result = migrator.check_compatibility()
        
        assert result["compatible"]
        assert result["has_existing_plan"]
        assert not result["is_already_enhanced"]
        assert result["migration_needed"]
        assert len(result["issues"]) == 0
    
    def test_migrate_project_success(self, temp_project_dir, basic_project_plan):
        """Test successful project migration."""
        # Set up project with basic plan
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        state_manager.save_project_plan(basic_project_plan)
        
        migrator = ProjectMigrator(temp_project_dir)
        result = migrator.migrate_project(backup=True)
        
        assert result["success"]
        assert result["backup_created"]
        assert result["backup_id"] is not None
        
        # Verify migration worked
        loaded_plan = state_manager.load_project_plan()
        assert isinstance(loaded_plan, EnhancedProjectPlan)
    
    def test_migrate_project_no_migration_needed(self, temp_project_dir, basic_project_plan):
        """Test migration when no migration is needed."""
        # Set up project with enhanced plan
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        
        enhanced_plan = EnhancedProjectPlan(
            objective=basic_project_plan.objective,
            modules=basic_project_plan.modules,
            dependency_graph=basic_project_plan.dependency_graph,
            estimated_functions=basic_project_plan.estimated_functions,
            created_at=basic_project_plan.created_at
        )
        state_manager.save_project_plan(enhanced_plan)
        
        migrator = ProjectMigrator(temp_project_dir)
        result = migrator.migrate_project()
        
        assert result["success"]
        assert not result["backup_created"]
        assert "No migration needed" in result["message"]
    
    def test_get_migration_status_no_plan(self, temp_project_dir):
        """Test migration status with no plan."""
        migrator = ProjectMigrator(temp_project_dir)
        
        status = migrator.get_migration_status()
        
        assert status["status"] == "no_plan"
        assert not status["is_enhanced"]
        assert not status["can_migrate"]
    
    def test_get_migration_status_basic_plan(self, temp_project_dir, basic_project_plan):
        """Test migration status with basic plan."""
        # Set up project with basic plan
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        state_manager.save_project_plan(basic_project_plan)
        
        migrator = ProjectMigrator(temp_project_dir)
        status = migrator.get_migration_status()
        
        assert status["status"] == "basic"
        assert not status["is_enhanced"]
        assert status["can_migrate"]
        assert status["modules_count"] == 1
    
    def test_get_migration_status_enhanced_plan(self, temp_project_dir, basic_project_plan):
        """Test migration status with enhanced plan."""
        # Set up project with enhanced plan
        state_manager = StateManager(temp_project_dir)
        state_manager.initialize()
        
        enhanced_plan = EnhancedProjectPlan(
            objective=basic_project_plan.objective,
            modules=basic_project_plan.modules,
            dependency_graph=basic_project_plan.dependency_graph,
            estimated_functions=basic_project_plan.estimated_functions,
            created_at=basic_project_plan.created_at
        )
        state_manager.save_project_plan(enhanced_plan)
        
        migrator = ProjectMigrator(temp_project_dir)
        status = migrator.get_migration_status()
        
        assert status["status"] == "enhanced"
        assert status["is_enhanced"]
        assert not status["can_migrate"]


class TestConvenienceFunctions:
    """Test convenience functions for migration."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_check_project_compatibility_function(self, temp_project_dir):
        """Test the convenience function for checking compatibility."""
        result = check_project_compatibility(temp_project_dir)
        
        assert "compatible" in result
        assert "has_existing_plan" in result
        assert "is_already_enhanced" in result
    
    def test_migrate_project_to_enhanced_function(self, temp_project_dir):
        """Test the convenience function for migration."""
        # This will fail since there's no existing plan, but should not crash
        result = migrate_project_to_enhanced(temp_project_dir, backup=False)
        
        assert "success" in result
        assert not result["success"]  # Should fail due to no existing plan