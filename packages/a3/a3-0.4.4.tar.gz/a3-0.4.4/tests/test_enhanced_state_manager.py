"""
Tests for enhanced StateManager functionality.

This module contains unit tests for the enhanced state management functionality,
including structured documentation persistence, versioning, and history tracking.
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from a3.managers.state import StateManager, StateManagerError, StateCorruptionError
from a3.core.models import (
    RequirementsDocument, DesignDocument, TasksDocument, EnhancedProjectPlan,
    DocumentationConfiguration, Requirement, AcceptanceCriterion, DesignComponent,
    ImplementationTask, RequirementPriority, ImplementationStatus,
    ProjectPlan, Module, FunctionSpec, DependencyGraph, Argument
)


class TestEnhancedStateManager:
    """Test cases for enhanced StateManager functionality."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def state_manager(self, temp_project_dir):
        """Create a StateManager instance for testing."""
        manager = StateManager(temp_project_dir)
        manager.initialize()
        return manager
    
    @pytest.fixture
    def sample_requirements_document(self):
        """Create a sample requirements document for testing."""
        acceptance_criterion = AcceptanceCriterion(
            id="ac1",
            when_clause="WHEN the user submits valid data",
            shall_clause="THEN the system SHALL process the request",
            requirement_id="req1"
        )
        
        requirement = Requirement(
            id="req1",
            user_story="As a user, I want to submit data, so that it can be processed",
            acceptance_criteria=[acceptance_criterion],
            priority=RequirementPriority.HIGH,
            category="functional"
        )
        
        return RequirementsDocument(
            introduction="Test requirements document",
            requirements=[requirement],
            created_at=datetime.now(),
            version="1.0"
        )
    
    @pytest.fixture
    def sample_design_document(self):
        """Create a sample design document for testing."""
        component = DesignComponent(
            id="comp1",
            name="Data Processor",
            description="Processes user data",
            responsibilities=["Process data", "Validate input"],
            interfaces=["IDataProcessor"],
            requirement_mappings=["req1"]
        )
        
        return DesignDocument(
            overview="Test design document",
            architecture="Layered architecture",
            components=[component],
            requirement_mappings={"req1": ["comp1"]},
            created_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_tasks_document(self):
        """Create a sample tasks document for testing."""
        task = ImplementationTask(
            id="task1",
            description="Implement data processor",
            requirement_references=["req1"],
            design_references=["comp1"],
            dependencies=[],
            estimated_effort="medium",
            priority=RequirementPriority.MEDIUM
        )
        
        return TasksDocument(
            tasks=[task],
            requirement_coverage={"req1": ["task1"]},
            design_coverage={"comp1": ["task1"]},
            created_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_documentation_config(self):
        """Create a sample documentation configuration for testing."""
        return DocumentationConfiguration(
            enable_requirements=True,
            enable_design=True,
            enable_tasks=True,
            requirement_format="ears",
            template_requirements=None,
            template_design=None,
            template_tasks=None,
            include_traceability=True,
            validation_level="strict"
        )
    
    @pytest.fixture
    def sample_enhanced_project_plan(self, sample_requirements_document, 
                                   sample_design_document, sample_tasks_document,
                                   sample_documentation_config):
        """Create a sample enhanced project plan for testing."""
        # Create base project plan components
        arg = Argument(name="data", type_hint="str", description="Input data")
        func = FunctionSpec(
            name="process_data",
            module="processor",
            docstring="Process input data",
            arguments=[arg],
            return_type="bool"
        )
        module = Module(
            name="processor",
            description="Data processing module",
            file_path="processor.py",
            dependencies=[],
            functions=[func]
        )
        dependency_graph = DependencyGraph(nodes=["processor"], edges=[])
        
        return EnhancedProjectPlan(
            objective="Create a data processing system",
            modules=[module],
            dependency_graph=dependency_graph,
            estimated_functions=1,
            created_at=datetime.now(),
            requirements_document=sample_requirements_document,
            design_document=sample_design_document,
            tasks_document=sample_tasks_document,
            documentation_config=sample_documentation_config
        )

    def test_save_and_load_requirements_document(self, state_manager, sample_requirements_document):
        """Test saving and loading requirements document."""
        # Save requirements document
        state_manager.save_requirements_document(sample_requirements_document)
        
        # Verify file exists
        assert state_manager.requirements_file.exists()
        
        # Load requirements document
        loaded_requirements = state_manager.load_requirements_document()
        
        # Verify loaded document matches original
        assert loaded_requirements is not None
        assert loaded_requirements.introduction == sample_requirements_document.introduction
        assert len(loaded_requirements.requirements) == len(sample_requirements_document.requirements)
        assert loaded_requirements.requirements[0].id == sample_requirements_document.requirements[0].id
        assert loaded_requirements.version == sample_requirements_document.version
    
    def test_save_and_load_design_document(self, state_manager, sample_design_document):
        """Test saving and loading design document."""
        # Save design document
        state_manager.save_design_document(sample_design_document)
        
        # Verify file exists
        assert state_manager.design_file.exists()
        
        # Load design document
        loaded_design = state_manager.load_design_document()
        
        # Verify loaded document matches original
        assert loaded_design is not None
        assert loaded_design.overview == sample_design_document.overview
        assert loaded_design.architecture == sample_design_document.architecture
        assert len(loaded_design.components) == len(sample_design_document.components)
        assert loaded_design.components[0].id == sample_design_document.components[0].id
    
    def test_save_and_load_tasks_document(self, state_manager, sample_tasks_document):
        """Test saving and loading tasks document."""
        # Save tasks document
        state_manager.save_tasks_document(sample_tasks_document)
        
        # Verify file exists
        assert state_manager.tasks_file.exists()
        
        # Load tasks document
        loaded_tasks = state_manager.load_tasks_document()
        
        # Verify loaded document matches original
        assert loaded_tasks is not None
        assert len(loaded_tasks.tasks) == len(sample_tasks_document.tasks)
        assert loaded_tasks.tasks[0].id == sample_tasks_document.tasks[0].id
        assert loaded_tasks.requirement_coverage == sample_tasks_document.requirement_coverage
        assert loaded_tasks.design_coverage == sample_tasks_document.design_coverage
    
    def test_save_and_load_documentation_configuration(self, state_manager, sample_documentation_config):
        """Test saving and loading documentation configuration."""
        # Save documentation configuration
        state_manager.save_documentation_configuration(sample_documentation_config)
        
        # Verify file exists
        assert state_manager.documentation_config_file.exists()
        
        # Load documentation configuration
        loaded_config = state_manager.load_documentation_configuration()
        
        # Verify loaded configuration matches original
        assert loaded_config is not None
        assert loaded_config.enable_requirements == sample_documentation_config.enable_requirements
        assert loaded_config.enable_design == sample_documentation_config.enable_design
        assert loaded_config.enable_tasks == sample_documentation_config.enable_tasks
        assert loaded_config.requirement_format == sample_documentation_config.requirement_format
    
    def test_save_and_load_enhanced_project_plan(self, state_manager, sample_enhanced_project_plan):
        """Test saving and loading enhanced project plan."""
        # Save enhanced project plan
        state_manager.save_enhanced_project_plan(sample_enhanced_project_plan)
        
        # Verify all files exist
        assert state_manager.plan_file.exists()
        assert state_manager.requirements_file.exists()
        assert state_manager.design_file.exists()
        assert state_manager.tasks_file.exists()
        assert state_manager.documentation_config_file.exists()
        
        # Load enhanced project plan
        loaded_plan = state_manager.load_enhanced_project_plan()
        
        # Verify loaded plan matches original
        assert loaded_plan is not None
        assert loaded_plan.objective == sample_enhanced_project_plan.objective
        assert len(loaded_plan.modules) == len(sample_enhanced_project_plan.modules)
        assert loaded_plan.requirements_document is not None
        assert loaded_plan.design_document is not None
        assert loaded_plan.tasks_document is not None
        assert loaded_plan.documentation_config is not None
    
    def test_load_nonexistent_documents(self, state_manager):
        """Test loading documents that don't exist."""
        # Test loading nonexistent documents returns None
        assert state_manager.load_requirements_document() is None
        assert state_manager.load_design_document() is None
        assert state_manager.load_tasks_document() is None
        assert state_manager.load_documentation_configuration() is None
        assert state_manager.load_enhanced_project_plan() is None
    
    def test_documentation_versioning(self, state_manager, sample_requirements_document):
        """Test documentation versioning functionality."""
        # Save initial version
        state_manager.save_requirements_document(sample_requirements_document)
        
        # Modify and save again
        sample_requirements_document.introduction = "Updated introduction"
        state_manager.save_requirements_document(sample_requirements_document)
        
        # Check version history
        history = state_manager.get_documentation_history("requirements")
        assert len(history) >= 2  # Should have at least 2 versions
        
        # Verify history entries have required fields
        for entry in history:
            assert "version_id" in entry
            assert "timestamp" in entry
            assert "doc_type" in entry
            assert entry["doc_type"] == "requirements"
    
    def test_restore_documentation_version(self, state_manager, sample_requirements_document):
        """Test restoring a specific version of documentation."""
        # Save initial version
        original_intro = sample_requirements_document.introduction
        state_manager.save_requirements_document(sample_requirements_document)
        
        # Get the version ID of the first save
        history = state_manager.get_documentation_history("requirements")
        first_version_id = history[0]["version_id"]
        
        # Modify and save again
        sample_requirements_document.introduction = "Updated introduction"
        state_manager.save_requirements_document(sample_requirements_document)
        
        # Verify the change
        loaded = state_manager.load_requirements_document()
        assert loaded.introduction == "Updated introduction"
        
        # Restore the first version
        success = state_manager.restore_documentation_version("requirements", first_version_id)
        assert success
        
        # Verify restoration
        restored = state_manager.load_requirements_document()
        assert restored.introduction == original_intro
    
    def test_atomic_operations(self, state_manager, sample_requirements_document):
        """Test that save operations are atomic."""
        # Mock file operations to simulate failure
        with patch('shutil.move', side_effect=Exception("Simulated failure")):
            with pytest.raises(StateManagerError):
                state_manager.save_requirements_document(sample_requirements_document)
        
        # Verify that no partial state was saved
        assert not state_manager.requirements_file.exists()
        assert not state_manager.requirements_temp.exists()
    
    def test_corrupted_file_handling(self, state_manager):
        """Test handling of corrupted documentation files."""
        # Create corrupted requirements file
        state_manager.requirements_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_manager.requirements_file, 'w') as f:
            f.write("invalid json content")
        
        # Test that loading corrupted file raises appropriate exception
        with pytest.raises(StateCorruptionError):
            state_manager.load_requirements_document()
    
    def test_validation_errors(self, state_manager):
        """Test handling of validation errors."""
        # Create invalid requirements document
        invalid_requirements = RequirementsDocument(
            introduction="",  # Empty introduction should fail validation
            requirements=[],
            created_at=datetime.now(),
            version="1.0"
        )
        
        # Mock validation to raise error
        with patch.object(invalid_requirements, 'validate', side_effect=Exception("Validation failed")):
            with pytest.raises(StateManagerError):
                state_manager.save_requirements_document(invalid_requirements)
    
    def test_checkpoint_includes_documentation(self, state_manager, sample_enhanced_project_plan):
        """Test that checkpoints include documentation files."""
        # Save enhanced project plan
        state_manager.save_enhanced_project_plan(sample_enhanced_project_plan)
        
        # Create checkpoint
        checkpoint_id = state_manager.create_checkpoint()
        
        # Verify checkpoint includes documentation files
        checkpoint_dir = state_manager.checkpoints_dir / checkpoint_id
        assert (checkpoint_dir / "requirements_document.json").exists()
        assert (checkpoint_dir / "design_document.json").exists()
        assert (checkpoint_dir / "tasks_document.json").exists()
        assert (checkpoint_dir / "documentation_config.json").exists()
    
    def test_cleanup_includes_documentation_temps(self, state_manager):
        """Test that cleanup removes documentation temporary files."""
        # Create temporary files
        temp_files = [
            state_manager.requirements_temp,
            state_manager.design_temp,
            state_manager.tasks_temp,
            state_manager.documentation_config_temp
        ]
        
        for temp_file in temp_files:
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file.touch()
            assert temp_file.exists()
        
        # Run cleanup
        state_manager.cleanup_state()
        
        # Verify temporary files are removed
        for temp_file in temp_files:
            assert not temp_file.exists()
    
    def test_documentation_history_limit(self, state_manager, sample_requirements_document):
        """Test that documentation history is limited to prevent unbounded growth."""
        # Save multiple versions (more than the limit of 20)
        for i in range(25):
            sample_requirements_document.introduction = f"Version {i}"
            state_manager.save_requirements_document(sample_requirements_document)
        
        # Check that history is limited
        history = state_manager.get_documentation_history("requirements")
        assert len(history) <= 20
    
    def test_enhanced_plan_without_documentation(self, state_manager):
        """Test loading enhanced plan when base plan exists but documentation doesn't."""
        # Create and save a basic project plan
        from a3.core.models import ProjectPlan, Module, DependencyGraph
        
        module = Module(
            name="test_module",
            description="Test module",
            file_path="test.py",
            dependencies=[],
            functions=[]
        )
        
        basic_plan = ProjectPlan(
            objective="Test objective",
            modules=[module],
            dependency_graph=DependencyGraph(nodes=["test_module"], edges=[]),
            estimated_functions=0,
            created_at=datetime.now()
        )
        
        state_manager.save_project_plan(basic_plan)
        
        # Load as enhanced plan
        enhanced_plan = state_manager.load_enhanced_project_plan()
        
        # Verify enhanced plan is created with None documentation components
        assert enhanced_plan is not None
        assert enhanced_plan.objective == basic_plan.objective
        assert enhanced_plan.requirements_document is None
        assert enhanced_plan.design_document is None
        assert enhanced_plan.tasks_document is None
        assert enhanced_plan.documentation_config is None
    
    def test_restore_nonexistent_version(self, state_manager):
        """Test restoring a version that doesn't exist."""
        with pytest.raises(StateManagerError, match="Version nonexistent not found"):
            state_manager.restore_documentation_version("requirements", "nonexistent")
    
    def test_restore_unknown_document_type(self, state_manager, sample_requirements_document):
        """Test restoring with unknown document type."""
        # First save a requirements document to create a version
        state_manager.save_requirements_document(sample_requirements_document)
        history = state_manager.get_documentation_history("requirements")
        version_id = history[0]["version_id"]
        
        # Now try to restore with unknown document type but valid version
        with pytest.raises(StateManagerError, match="Unknown document type"):
            state_manager.restore_documentation_version("unknown", version_id)
    
    def test_get_empty_documentation_history(self, state_manager):
        """Test getting history for document type with no history."""
        history = state_manager.get_documentation_history("requirements")
        assert history == []
    
    def test_corrupted_history_file(self, state_manager):
        """Test handling corrupted history file."""
        # Create corrupted history file
        history_file = state_manager.documentation_history_dir / "requirements_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, 'w') as f:
            f.write("invalid json")
        
        # Should return empty list for corrupted history
        history = state_manager.get_documentation_history("requirements")
        assert history == []
    
    def test_version_creation_failure_handling(self, state_manager, sample_requirements_document):
        """Test that version creation failure doesn't prevent document saving."""
        # Mock version creation to fail
        with patch.object(state_manager, '_create_documentation_version', side_effect=Exception("Version failed")):
            # Should still save the document successfully
            state_manager.save_requirements_document(sample_requirements_document)
            
            # Verify document was saved
            loaded = state_manager.load_requirements_document()
            assert loaded is not None
            assert loaded.introduction == sample_requirements_document.introduction