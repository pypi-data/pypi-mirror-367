"""
State management implementation for AI Project Builder.

This module provides the StateManager class that handles all project state
persistence, including project plans, progress tracking, and checkpoints.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid

from ..core.interfaces import StateManagerInterface
from ..core.models import (
    ProjectPlan, ProjectProgress, ProjectPhase, ProjectStatus,
    Module, FunctionSpec, DependencyGraph, Argument,
    ImplementationStatus, ValidationResult, ModelConfiguration,
    RequirementsDocument, DesignDocument, TasksDocument,
    EnhancedProjectPlan, DocumentationConfiguration, EnhancedFunctionSpec
)
from .base import BaseStateManager


class StateManagerError(Exception):
    """Base exception for state manager errors."""
    pass


class StateCorruptionError(StateManagerError):
    """Exception raised when state data is corrupted."""
    pass


class CheckpointError(StateManagerError):
    """Exception raised during checkpoint operations."""
    pass


class StateManager(BaseStateManager):
    """
    Manages project state persistence in the .A3 directory.
    
    Handles saving/loading project plans, progress tracking, and checkpoint
    functionality with atomic operations and error recovery.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the state manager.
        
        Args:
            project_path: Path to the project directory
        """
        super().__init__(project_path)
        
        # Define state file paths
        self.plan_file = self.a3_dir / "project_plan.json"
        self.progress_file = self.a3_dir / "progress.json"
        self.status_file = self.a3_dir / "status.json"
        self.model_config_file = self.a3_dir / "model_config.json"
        self.checkpoints_dir = self.a3_dir / "checkpoints"
        
        # Enhanced documentation file paths
        self.requirements_file = self.a3_dir / "requirements_document.json"
        self.design_file = self.a3_dir / "design_document.json"
        self.tasks_file = self.a3_dir / "tasks_document.json"
        self.documentation_config_file = self.a3_dir / "documentation_config.json"
        self.documentation_history_dir = self.a3_dir / "documentation_history"
        
        # Temporary files for atomic operations
        self.plan_temp = self.a3_dir / "project_plan.json.tmp"
        self.progress_temp = self.a3_dir / "progress.json.tmp"
        self.status_temp = self.a3_dir / "status.json.tmp"
        self.model_config_temp = self.a3_dir / "model_config.json.tmp"
        self.requirements_temp = self.a3_dir / "requirements_document.json.tmp"
        self.design_temp = self.a3_dir / "design_document.json.tmp"
        self.tasks_temp = self.a3_dir / "tasks_document.json.tmp"
        self.documentation_config_temp = self.a3_dir / "documentation_config.json.tmp"
    
    def initialize(self) -> None:
        """Initialize the state manager and create necessary directories."""
        super().initialize()
        
        # Create checkpoints directory
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # Create documentation history directory
        self.documentation_history_dir.mkdir(exist_ok=True)
        
        # Enhanced functions file path
        self.enhanced_functions_file = self.a3_dir / "enhanced_functions.json"
        self.enhanced_functions_temp = self.a3_dir / "enhanced_functions.json.tmp"
        
        # Initialize status file if it doesn't exist
        if not self.status_file.exists():
            initial_status = ProjectStatus(
                is_active=False,
                progress=None,
                errors=[],
                can_resume=False,
                next_action=None
            )
            self._save_status(initial_status)
    
    def save_project_plan(self, plan: ProjectPlan) -> None:
        """
        Save project plan to persistent storage with atomic operations.
        
        This method maintains backward compatibility by handling both
        basic ProjectPlan and EnhancedProjectPlan objects.
        
        Args:
            plan: The project plan to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the plan before saving
            plan.validate()
            
            # Handle enhanced project plans
            if isinstance(plan, EnhancedProjectPlan):
                self._save_enhanced_project_plan(plan)
            else:
                # Handle basic project plans (backward compatibility)
                self._save_basic_project_plan(plan)
            
            # Update status
            self._update_status(is_active=True, can_resume=True)
            
        except Exception as e:
            # Clean up temporary files if they exist
            self._cleanup_temp_files()
            raise StateManagerError(f"Failed to save project plan: {e}") from e
    
    def _save_basic_project_plan(self, plan: ProjectPlan) -> None:
        """Save a basic project plan (backward compatibility)."""
        # Convert to dictionary for JSON serialization
        plan_dict = self._project_plan_to_dict(plan)
        
        # Write to temporary file first (atomic operation)
        with open(self.plan_temp, 'w', encoding='utf-8') as f:
            json.dump(plan_dict, f, indent=2, default=str)
        
        # Move temporary file to final location
        shutil.move(str(self.plan_temp), str(self.plan_file))
    
    def _save_enhanced_project_plan(self, plan: EnhancedProjectPlan) -> None:
        """Save an enhanced project plan with structured documentation."""
        # Save the basic plan data
        basic_plan_dict = self._project_plan_to_dict(plan)
        
        # Add enhanced plan marker
        basic_plan_dict["is_enhanced"] = True
        basic_plan_dict["enhanced_functions_count"] = len(plan.enhanced_functions)
        
        # Write basic plan to temporary file first (atomic operation)
        with open(self.plan_temp, 'w', encoding='utf-8') as f:
            json.dump(basic_plan_dict, f, indent=2, default=str)
        
        # Move temporary file to final location
        shutil.move(str(self.plan_temp), str(self.plan_file))
        
        # Save structured documentation components if they exist
        if plan.requirements_document:
            self.save_requirements_document(plan.requirements_document)
        
        if plan.design_document:
            self.save_design_document(plan.design_document)
        
        if plan.tasks_document:
            self.save_tasks_document(plan.tasks_document)
        
        if plan.documentation_config:
            self.save_documentation_configuration(plan.documentation_config)
        
        # Save enhanced functions if they exist
        if plan.enhanced_functions:
            self._save_enhanced_functions(plan.enhanced_functions)
    
    def _cleanup_temp_files(self) -> None:
        """Clean up all temporary files."""
        temp_files = [
            self.plan_temp, self.progress_temp, self.status_temp,
            self.model_config_temp, self.requirements_temp,
            self.design_temp, self.tasks_temp, self.documentation_config_temp
        ]
        
        for temp_file in temp_files:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    # Ignore cleanup errors
                    pass
    
    def load_project_plan(self) -> Optional[ProjectPlan]:
        """
        Load project plan from persistent storage.
        
        This method maintains backward compatibility by detecting and loading
        both basic ProjectPlan and EnhancedProjectPlan objects.
        
        Returns:
            The loaded project plan, or None if no plan exists
            
        Raises:
            StateCorruptionError: If the plan data is corrupted
        """
        self._ensure_initialized()
        
        if not self.plan_file.exists():
            return None
        
        try:
            with open(self.plan_file, 'r', encoding='utf-8') as f:
                plan_dict = json.load(f)
            
            # Check if this is an enhanced project plan
            if plan_dict.get("is_enhanced", False):
                plan = self._load_enhanced_project_plan(plan_dict)
            else:
                # Load as basic project plan (backward compatibility)
                plan = self._dict_to_project_plan(plan_dict)
            
            # Validate the loaded plan
            plan.validate()
            
            return plan
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Project plan file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load project plan: {e}") from e
    
    def _load_enhanced_project_plan(self, plan_dict: Dict[str, Any]) -> EnhancedProjectPlan:
        """
        Load an enhanced project plan with structured documentation.
        
        Args:
            plan_dict: Dictionary containing basic plan data
            
        Returns:
            EnhancedProjectPlan with loaded documentation
        """
        # Load basic plan data
        basic_plan = self._dict_to_project_plan(plan_dict)
        
        # Load structured documentation components
        requirements_doc = self.load_requirements_document()
        design_doc = self.load_design_document()
        tasks_doc = self.load_tasks_document()
        doc_config = self.load_documentation_configuration()
        enhanced_functions = self._load_enhanced_functions()
        
        # Create enhanced project plan
        enhanced_plan = EnhancedProjectPlan(
            objective=basic_plan.objective,
            modules=basic_plan.modules,
            dependency_graph=basic_plan.dependency_graph,
            enhanced_dependency_graph=basic_plan.enhanced_dependency_graph,
            estimated_functions=basic_plan.estimated_functions,
            created_at=basic_plan.created_at,
            requirements_document=requirements_doc,
            design_document=design_doc,
            tasks_document=tasks_doc,
            documentation_config=doc_config,
            enhanced_functions=enhanced_functions or []
        )
        
        return enhanced_plan
    
    def can_use_enhanced_features(self) -> bool:
        """
        Check if the current project can use enhanced planning features.
        
        Returns:
            True if enhanced features are available and compatible
        """
        try:
            # Check if enhanced documentation files exist
            has_enhanced_files = (
                self.requirements_file.exists() or
                self.design_file.exists() or
                self.tasks_file.exists()
            )
            
            # Check if current plan is enhanced
            if self.plan_file.exists():
                with open(self.plan_file, 'r', encoding='utf-8') as f:
                    plan_dict = json.load(f)
                    is_enhanced = plan_dict.get("is_enhanced", False)
                    return is_enhanced or has_enhanced_files
            
            return has_enhanced_files
            
        except Exception:
            return False
    
    def migrate_to_enhanced_plan(self) -> bool:
        """
        Migrate an existing basic project plan to enhanced format.
        
        Returns:
            True if migration was successful, False otherwise
        """
        try:
            # Load existing plan
            existing_plan = self.load_project_plan()
            if not existing_plan:
                return False
            
            # If already enhanced, no migration needed
            if isinstance(existing_plan, EnhancedProjectPlan):
                return True
            
            # Convert to enhanced plan
            enhanced_plan = EnhancedProjectPlan(
                objective=existing_plan.objective,
                modules=existing_plan.modules,
                dependency_graph=existing_plan.dependency_graph,
                enhanced_dependency_graph=existing_plan.enhanced_dependency_graph,
                estimated_functions=existing_plan.estimated_functions,
                created_at=existing_plan.created_at,
                requirements_document=None,
                design_document=None,
                tasks_document=None,
                documentation_config=None,
                enhanced_functions=[]
            )
            
            # Save as enhanced plan
            self.save_project_plan(enhanced_plan)
            
            return True
            
        except Exception:
            return False
    
    def save_progress(self, phase: ProjectPhase, data: Dict[str, Any]) -> None:
        """
        Save progress information for a specific phase.
        
        Args:
            phase: The current project phase
            data: Additional data to save with the progress
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Ensure directories exist
            self.a3_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing progress or create new
            current_progress = self.get_current_progress()
            if current_progress is None:
                current_progress = ProjectProgress(
                    current_phase=phase,
                    completed_phases=[],
                    total_functions=0,
                    implemented_functions=0,
                    failed_functions=[],
                    last_updated=datetime.now()
                )
            
            # Update progress
            current_progress.current_phase = phase
            current_progress.last_updated = datetime.now()
            
            # Add to completed phases if not already there
            if phase not in current_progress.completed_phases:
                # Only add if we're moving forward
                phase_order = [ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION, 
                              ProjectPhase.IMPLEMENTATION, ProjectPhase.INTEGRATION, 
                              ProjectPhase.COMPLETED]
                
                current_index = phase_order.index(phase)
                for i, completed_phase in enumerate(current_progress.completed_phases):
                    completed_index = phase_order.index(completed_phase)
                    if completed_index >= current_index:
                        break
                else:
                    # Add previous phases as completed if they're not already
                    for prev_phase in phase_order[:current_index]:
                        if prev_phase not in current_progress.completed_phases:
                            current_progress.completed_phases.append(prev_phase)
            
            # Update with additional data
            if 'total_functions' in data:
                current_progress.total_functions = data['total_functions']
            if 'implemented_functions' in data:
                current_progress.implemented_functions = data['implemented_functions']
            if 'failed_functions' in data:
                current_progress.failed_functions = data['failed_functions']
            
            # Validate before saving
            current_progress.validate()
            
            # Convert to dictionary and save atomically
            progress_dict = self._progress_to_dict(current_progress)
            
            with open(self.progress_temp, 'w', encoding='utf-8') as f:
                json.dump(progress_dict, f, indent=2, default=str)
            
            shutil.move(str(self.progress_temp), str(self.progress_file))
            
            # Update status with better error handling
            try:
                next_action = self._determine_next_action(current_progress)
                self._update_status(
                    is_active=True,
                    can_resume=True,
                    next_action=next_action
                )
            except Exception as status_error:
                # Log but don't fail the progress save
                print(f"Warning: Failed to update status: {status_error}")
                pass
            
        except Exception as e:
            if self.progress_temp.exists():
                self.progress_temp.unlink()
            raise StateManagerError(f"Failed to save progress: {e}") from e
    
    def get_current_progress(self) -> Optional[ProjectProgress]:
        """
        Get current project progress information.
        
        Returns:
            Current progress, or None if no progress exists
            
        Raises:
            StateCorruptionError: If progress data is corrupted
        """
        self._ensure_initialized()
        
        if not self.progress_file.exists():
            return None
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress_dict = json.load(f)
            
            progress = self._dict_to_progress(progress_dict)
            progress.validate()
            
            return progress
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Progress file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load progress: {e}") from e
    
    def create_checkpoint(self) -> str:
        """
        Create a checkpoint of current project state.
        
        Returns:
            Checkpoint ID for later restoration
            
        Raises:
            CheckpointError: If checkpoint creation fails
        """
        self._ensure_initialized()
        
        try:
            # Generate unique checkpoint ID
            checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            checkpoint_dir = self.checkpoints_dir / checkpoint_id
            
            # Create checkpoint directory
            checkpoint_dir.mkdir(exist_ok=True)
            
            # Copy all state files to checkpoint
            state_files = [
                (self.plan_file, "project_plan.json"),
                (self.progress_file, "progress.json"),
                (self.status_file, "status.json"),
                (self.model_config_file, "model_config.json"),
                (self.requirements_file, "requirements_document.json"),
                (self.design_file, "design_document.json"),
                (self.tasks_file, "tasks_document.json"),
                (self.documentation_config_file, "documentation_config.json")
            ]
            
            for source_file, target_name in state_files:
                if source_file.exists():
                    target_file = checkpoint_dir / target_name
                    shutil.copy2(str(source_file), str(target_file))
            
            # Save checkpoint metadata
            metadata = {
                "checkpoint_id": checkpoint_id,
                "created_at": datetime.now().isoformat(),
                "project_path": str(self.project_path),
                "files_saved": [name for _, name in state_files if (self.a3_dir / name).exists()]
            }
            
            metadata_file = checkpoint_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return checkpoint_id
            
        except Exception as e:
            # Clean up partial checkpoint
            if 'checkpoint_dir' in locals() and checkpoint_dir.exists():
                shutil.rmtree(str(checkpoint_dir), ignore_errors=True)
            raise CheckpointError(f"Failed to create checkpoint: {e}") from e
    
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restore project state from a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to restore
            
        Returns:
            True if restoration was successful, False otherwise
            
        Raises:
            CheckpointError: If restoration fails
        """
        self._ensure_initialized()
        
        checkpoint_dir = self.checkpoints_dir / checkpoint_id
        
        if not checkpoint_dir.exists():
            raise CheckpointError(f"Checkpoint {checkpoint_id} does not exist")
        
        try:
            # Load checkpoint metadata
            metadata_file = checkpoint_dir / "metadata.json"
            if not metadata_file.exists():
                raise CheckpointError(f"Checkpoint {checkpoint_id} is missing metadata")
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verify checkpoint integrity
            expected_files = metadata.get("files_saved", [])
            for filename in expected_files:
                checkpoint_file = checkpoint_dir / filename
                if not checkpoint_file.exists():
                    raise CheckpointError(f"Checkpoint {checkpoint_id} is missing file: {filename}")
            
            # Create backup of current state
            backup_id = self.create_checkpoint()
            
            try:
                # Restore files from checkpoint
                state_files = [
                    ("project_plan.json", self.plan_file),
                    ("progress.json", self.progress_file),
                    ("status.json", self.status_file),
                    ("model_config.json", self.model_config_file),
                    ("requirements_document.json", self.requirements_file),
                    ("design_document.json", self.design_file),
                    ("tasks_document.json", self.tasks_file),
                    ("documentation_config.json", self.documentation_config_file)
                ]
                
                for source_name, target_file in state_files:
                    source_file = checkpoint_dir / source_name
                    if source_file.exists():
                        # Use atomic operation
                        temp_file = target_file.with_suffix('.tmp')
                        shutil.copy2(str(source_file), str(temp_file))
                        shutil.move(str(temp_file), str(target_file))
                
                return True
                
            except Exception as restore_error:
                # Attempt to restore from backup
                try:
                    self.restore_checkpoint(backup_id)
                except Exception:
                    pass  # Best effort recovery
                raise restore_error
            
        except Exception as e:
            raise CheckpointError(f"Failed to restore checkpoint {checkpoint_id}: {e}") from e
    
    def cleanup_state(self) -> None:
        """Clean up temporary state files and old checkpoints."""
        self._ensure_initialized()
        
        # Clean up temporary files
        temp_files = [
            self.plan_temp, self.progress_temp, self.status_temp, self.model_config_temp,
            self.requirements_temp, self.design_temp, self.tasks_temp, self.documentation_config_temp
        ]
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()
        
        # Clean up old checkpoints (keep last 10)
        if self.checkpoints_dir.exists():
            checkpoints = sorted(
                [d for d in self.checkpoints_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove old checkpoints beyond the limit
            for old_checkpoint in checkpoints[10:]:
                shutil.rmtree(str(old_checkpoint), ignore_errors=True)
    
    def _save_enhanced_functions(self, enhanced_functions: List[EnhancedFunctionSpec]) -> None:
        """Save enhanced function specifications."""
        try:
            functions_data = [self._enhanced_function_spec_to_dict(func) for func in enhanced_functions]
            
            with open(self.enhanced_functions_temp, 'w', encoding='utf-8') as f:
                json.dump(functions_data, f, indent=2, default=str)
            
            shutil.move(str(self.enhanced_functions_temp), str(self.enhanced_functions_file))
            
        except Exception as e:
            if self.enhanced_functions_temp.exists():
                self.enhanced_functions_temp.unlink()
            raise StateManagerError(f"Failed to save enhanced functions: {e}") from e
    
    def _load_enhanced_functions(self) -> Optional[List[EnhancedFunctionSpec]]:
        """Load enhanced function specifications."""
        if not self.enhanced_functions_file.exists():
            return None
        
        try:
            with open(self.enhanced_functions_file, 'r', encoding='utf-8') as f:
                functions_data = json.load(f)
            
            return [self._dict_to_enhanced_function_spec(func_data) for func_data in functions_data]
            
        except Exception:
            return None
    
    def _enhanced_function_spec_to_dict(self, func: EnhancedFunctionSpec) -> Dict[str, Any]:
        """Convert EnhancedFunctionSpec to dictionary."""
        base_dict = self._function_spec_to_dict(func)
        base_dict.update({
            "requirement_references": func.requirement_references,
            "acceptance_criteria_implementations": func.acceptance_criteria_implementations,
            "validation_logic": func.validation_logic
        })
        return base_dict
    
    def _dict_to_enhanced_function_spec(self, data: Dict[str, Any]) -> EnhancedFunctionSpec:
        """Convert dictionary to EnhancedFunctionSpec."""
        base_func = self._dict_to_function_spec(data)
        
        return EnhancedFunctionSpec(
            name=base_func.name,
            module=base_func.module,
            docstring=base_func.docstring,
            arguments=base_func.arguments,
            return_type=base_func.return_type,
            implementation_status=base_func.implementation_status,
            requirement_references=data.get("requirement_references", []),
            acceptance_criteria_implementations=data.get("acceptance_criteria_implementations", []),
            validation_logic=data.get("validation_logic")
        )

    def get_project_status(self) -> ProjectStatus:
        """
        Get current project status.
        
        Returns:
            Current project status
        """
        self._ensure_initialized()
        
        if not self.status_file.exists():
            return ProjectStatus()
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                status_dict = json.load(f)
            
            return self._dict_to_status(status_dict)
            
        except Exception:
            # Return default status if file is corrupted
            return ProjectStatus()
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint information dictionaries
        """
        self._ensure_initialized()
        
        checkpoints = []
        
        if not self.checkpoints_dir.exists():
            return checkpoints
        
        for checkpoint_dir in self.checkpoints_dir.iterdir():
            if not checkpoint_dir.is_dir():
                continue
            
            metadata_file = checkpoint_dir / "metadata.json"
            if not metadata_file.exists():
                continue
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                checkpoints.append(metadata)
            except Exception:
                continue  # Skip corrupted checkpoints
        
        # Sort by creation time (newest first)
        checkpoints.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return checkpoints
    
    def save_model_configuration(self, config: ModelConfiguration) -> None:
        """
        Save model configuration to persistent storage with atomic operations.
        
        Args:
            config: The model configuration to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the configuration before saving
            config.validate()
            
            # Convert to dictionary for JSON serialization
            config_dict = self._model_config_to_dict(config)
            
            # Write to temporary file first (atomic operation)
            with open(self.model_config_temp, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            # Move temporary file to final location
            shutil.move(str(self.model_config_temp), str(self.model_config_file))
            
        except Exception as e:
            # Clean up temporary file if it exists
            if self.model_config_temp.exists():
                self.model_config_temp.unlink()
            raise StateManagerError(f"Failed to save model configuration: {e}") from e
    
    def load_model_configuration(self) -> Optional[ModelConfiguration]:
        """
        Load model configuration from persistent storage.
        
        Returns:
            The loaded model configuration, or None if no configuration exists
            
        Raises:
            StateCorruptionError: If the configuration data is corrupted
        """
        self._ensure_initialized()
        
        if not self.model_config_file.exists():
            return None
        
        try:
            with open(self.model_config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Convert from dictionary to ModelConfiguration object
            config = self._dict_to_model_config(config_dict)
            
            # Validate the loaded configuration
            config.validate()
            
            return config
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Model configuration file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load model configuration: {e}") from e
    
    def get_or_create_model_configuration(self, default_model: str = "qwen/qwen-2.5-72b-instruct:free") -> ModelConfiguration:
        """
        Get existing model configuration or create a default one.
        
        Args:
            default_model: Default model to use if no configuration exists
            
        Returns:
            Model configuration (existing or newly created)
        """
        config = self.load_model_configuration()
        
        if config is None:
            # Create default configuration for projects without model config (migration logic)
            config = ModelConfiguration(
                current_model=default_model,
                available_models=[default_model],
                fallback_models=[default_model],
                preferences={
                    "auto_fallback": True,
                    "model_validation": True
                }
            )
            
            # Save the default configuration
            try:
                self.save_model_configuration(config)
            except Exception as e:
                # Log warning but don't fail - return the config anyway
                print(f"Warning: Failed to save default model configuration: {e}")
        
        return config
    
    def update_model_configuration(self, **kwargs) -> None:
        """
        Update model configuration with given parameters.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Raises:
            StateManagerError: If update fails
        """
        config = self.get_or_create_model_configuration()
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Update timestamp
        config.last_updated = datetime.now()
        
        # Save updated configuration
        self.save_model_configuration(config)

    # Private helper methods for serialization/deserialization
    
    def _project_plan_to_dict(self, plan: ProjectPlan) -> Dict[str, Any]:
        """Convert ProjectPlan to dictionary for JSON serialization."""
        return {
            "objective": plan.objective,
            "modules": [self._module_to_dict(module) for module in plan.modules],
            "dependency_graph": self._dependency_graph_to_dict(plan.dependency_graph),
            "estimated_functions": plan.estimated_functions,
            "created_at": plan.created_at.isoformat()
        }
    
    def _dict_to_project_plan(self, data: Dict[str, Any]) -> ProjectPlan:
        """Convert dictionary to ProjectPlan object."""
        modules = [self._dict_to_module(module_data) for module_data in data.get("modules", [])]
        dependency_graph = self._dict_to_dependency_graph(data.get("dependency_graph", {}))
        
        return ProjectPlan(
            objective=data["objective"],
            modules=modules,
            dependency_graph=dependency_graph,
            estimated_functions=data.get("estimated_functions", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )
    
    def _module_to_dict(self, module: Module) -> Dict[str, Any]:
        """Convert Module to dictionary for JSON serialization."""
        return {
            "name": module.name,
            "description": module.description,
            "file_path": module.file_path,
            "dependencies": module.dependencies,
            "functions": [self._function_spec_to_dict(func) for func in module.functions]
        }
    
    def _dict_to_module(self, data: Dict[str, Any]) -> Module:
        """Convert dictionary to Module object."""
        functions = [self._dict_to_function_spec(func_data) for func_data in data.get("functions", [])]
        
        return Module(
            name=data["name"],
            description=data["description"],
            file_path=data["file_path"],
            dependencies=data.get("dependencies", []),
            functions=functions
        )
    
    def _function_spec_to_dict(self, func: FunctionSpec) -> Dict[str, Any]:
        """Convert FunctionSpec to dictionary for JSON serialization."""
        return {
            "name": func.name,
            "module": func.module,
            "docstring": func.docstring,
            "arguments": [self._argument_to_dict(arg) for arg in func.arguments],
            "return_type": func.return_type,
            "implementation_status": func.implementation_status.value
        }
    
    def _dict_to_function_spec(self, data: Dict[str, Any]) -> FunctionSpec:
        """Convert dictionary to FunctionSpec object."""
        arguments = [self._dict_to_argument(arg_data) for arg_data in data.get("arguments", [])]
        
        return FunctionSpec(
            name=data["name"],
            module=data["module"],
            docstring=data["docstring"],
            arguments=arguments,
            return_type=data.get("return_type", "None"),
            implementation_status=ImplementationStatus(data.get("implementation_status", "not_started"))
        )
    
    def _argument_to_dict(self, arg: Argument) -> Dict[str, Any]:
        """Convert Argument to dictionary for JSON serialization."""
        return {
            "name": arg.name,
            "type_hint": arg.type_hint,
            "default_value": arg.default_value,
            "description": arg.description
        }
    
    def _dict_to_argument(self, data: Dict[str, Any]) -> Argument:
        """Convert dictionary to Argument object."""
        return Argument(
            name=data["name"],
            type_hint=data["type_hint"],
            default_value=data.get("default_value"),
            description=data.get("description", "")
        )
    
    def _dependency_graph_to_dict(self, graph: DependencyGraph) -> Dict[str, Any]:
        """Convert DependencyGraph to dictionary for JSON serialization."""
        return {
            "nodes": graph.nodes,
            "edges": graph.edges
        }
    
    def _dict_to_dependency_graph(self, data: Dict[str, Any]) -> DependencyGraph:
        """Convert dictionary to DependencyGraph object."""
        return DependencyGraph(
            nodes=data.get("nodes", []),
            edges=[tuple(edge) for edge in data.get("edges", [])]
        )
    
    def _progress_to_dict(self, progress: ProjectProgress) -> Dict[str, Any]:
        """Convert ProjectProgress to dictionary for JSON serialization."""
        return {
            "current_phase": progress.current_phase.value,
            "completed_phases": [phase.value for phase in progress.completed_phases],
            "total_functions": progress.total_functions,
            "implemented_functions": progress.implemented_functions,
            "failed_functions": progress.failed_functions,
            "last_updated": progress.last_updated.isoformat()
        }
    
    def _dict_to_progress(self, data: Dict[str, Any]) -> ProjectProgress:
        """Convert dictionary to ProjectProgress object."""
        return ProjectProgress(
            current_phase=ProjectPhase(data.get("current_phase", "planning")),
            completed_phases=[ProjectPhase(phase) for phase in data.get("completed_phases", [])],
            total_functions=data.get("total_functions", 0),
            implemented_functions=data.get("implemented_functions", 0),
            failed_functions=data.get("failed_functions", []),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
    
    def _status_to_dict(self, status: ProjectStatus) -> Dict[str, Any]:
        """Convert ProjectStatus to dictionary for JSON serialization."""
        return {
            "is_active": status.is_active,
            "progress": self._progress_to_dict(status.progress) if status.progress else None,
            "errors": status.errors,
            "can_resume": status.can_resume,
            "next_action": status.next_action
        }
    
    def _dict_to_status(self, data: Dict[str, Any]) -> ProjectStatus:
        """Convert dictionary to ProjectStatus object."""
        progress_data = data.get("progress")
        progress = self._dict_to_progress(progress_data) if progress_data else None
        
        return ProjectStatus(
            is_active=data.get("is_active", False),
            progress=progress,
            errors=data.get("errors", []),
            can_resume=data.get("can_resume", False),
            next_action=data.get("next_action")
        )
    
    def _save_status(self, status: ProjectStatus) -> None:
        """Save project status atomically."""
        try:
            status_dict = self._status_to_dict(status)
            
            with open(self.status_temp, 'w', encoding='utf-8') as f:
                json.dump(status_dict, f, indent=2, default=str)
            
            shutil.move(str(self.status_temp), str(self.status_file))
            
        except Exception as e:
            if self.status_temp.exists():
                self.status_temp.unlink()
            raise StateManagerError(f"Failed to save status: {e}") from e
    
    def _update_status(self, **kwargs) -> None:
        """Update project status with given parameters."""
        current_status = self.get_project_status()
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(current_status, key):
                setattr(current_status, key, value)
        
        self._save_status(current_status)
    
    def _determine_next_action(self, progress: ProjectProgress) -> Optional[str]:
        """Determine the next action based on current progress."""
        phase_actions = {
            ProjectPhase.PLANNING: "Generate specifications",
            ProjectPhase.SPECIFICATION: "Implement functions",
            ProjectPhase.IMPLEMENTATION: "Integrate modules",
            ProjectPhase.INTEGRATION: "Project complete",
            ProjectPhase.COMPLETED: None
        }
        
        return phase_actions.get(progress.current_phase)
    
    def _model_config_to_dict(self, config: ModelConfiguration) -> Dict[str, Any]:
        """Convert ModelConfiguration to dictionary for JSON serialization."""
        return {
            "current_model": config.current_model,
            "available_models": config.available_models,
            "fallback_models": config.fallback_models,
            "preferences": config.preferences,
            "last_updated": config.last_updated.isoformat()
        }
    
    def _dict_to_model_config(self, data: Dict[str, Any]) -> ModelConfiguration:
        """Convert dictionary to ModelConfiguration object."""
        return ModelConfiguration(
            current_model=data["current_model"],
            available_models=data.get("available_models", []),
            fallback_models=data.get("fallback_models", []),
            preferences=data.get("preferences", {}),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
    
    # Enhanced documentation persistence methods
    
    def save_requirements_document(self, requirements: RequirementsDocument) -> None:
        """
        Save requirements document to persistent storage with atomic operations.
        
        Args:
            requirements: The requirements document to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the requirements before saving
            requirements.validate()
            
            # Create version history entry (don't fail if this fails)
            try:
                self._create_documentation_version("requirements", requirements)
            except Exception as e:
                # Log warning but don't fail the main operation
                print(f"Warning: Failed to create version for requirements: {e}")
            
            # Convert to dictionary for JSON serialization
            requirements_dict = self._requirements_document_to_dict(requirements)
            
            # Write to temporary file first (atomic operation)
            with open(self.requirements_temp, 'w', encoding='utf-8') as f:
                json.dump(requirements_dict, f, indent=2, default=str)
            
            # Move temporary file to final location
            shutil.move(str(self.requirements_temp), str(self.requirements_file))
            
        except Exception as e:
            # Clean up temporary file if it exists
            if self.requirements_temp.exists():
                self.requirements_temp.unlink()
            raise StateManagerError(f"Failed to save requirements document: {e}") from e
    
    def load_requirements_document(self) -> Optional[RequirementsDocument]:
        """
        Load requirements document from persistent storage.
        
        Returns:
            The loaded requirements document, or None if no document exists
            
        Raises:
            StateCorruptionError: If the document data is corrupted
        """
        self._ensure_initialized()
        
        if not self.requirements_file.exists():
            return None
        
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                requirements_dict = json.load(f)
            
            # Convert from dictionary to RequirementsDocument object
            requirements = self._dict_to_requirements_document(requirements_dict)
            
            # Validate the loaded document
            requirements.validate()
            
            return requirements
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Requirements document file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load requirements document: {e}") from e
    
    def save_design_document(self, design: DesignDocument) -> None:
        """
        Save design document to persistent storage with atomic operations.
        
        Args:
            design: The design document to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the design before saving
            design.validate()
            
            # Create version history entry (don't fail if this fails)
            try:
                self._create_documentation_version("design", design)
            except Exception as e:
                # Log warning but don't fail the main operation
                print(f"Warning: Failed to create version for design: {e}")
            
            # Convert to dictionary for JSON serialization
            design_dict = self._design_document_to_dict(design)
            
            # Write to temporary file first (atomic operation)
            with open(self.design_temp, 'w', encoding='utf-8') as f:
                json.dump(design_dict, f, indent=2, default=str)
            
            # Move temporary file to final location
            shutil.move(str(self.design_temp), str(self.design_file))
            
        except Exception as e:
            # Clean up temporary file if it exists
            if self.design_temp.exists():
                self.design_temp.unlink()
            raise StateManagerError(f"Failed to save design document: {e}") from e
    
    def load_design_document(self) -> Optional[DesignDocument]:
        """
        Load design document from persistent storage.
        
        Returns:
            The loaded design document, or None if no document exists
            
        Raises:
            StateCorruptionError: If the document data is corrupted
        """
        self._ensure_initialized()
        
        if not self.design_file.exists():
            return None
        
        try:
            with open(self.design_file, 'r', encoding='utf-8') as f:
                design_dict = json.load(f)
            
            # Convert from dictionary to DesignDocument object
            design = self._dict_to_design_document(design_dict)
            
            # Validate the loaded document
            design.validate()
            
            return design
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Design document file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load design document: {e}") from e
    
    def save_tasks_document(self, tasks: TasksDocument) -> None:
        """
        Save tasks document to persistent storage with atomic operations.
        
        Args:
            tasks: The tasks document to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the tasks before saving
            tasks.validate()
            
            # Create version history entry (don't fail if this fails)
            try:
                self._create_documentation_version("tasks", tasks)
            except Exception as e:
                # Log warning but don't fail the main operation
                print(f"Warning: Failed to create version for tasks: {e}")
            
            # Convert to dictionary for JSON serialization
            tasks_dict = self._tasks_document_to_dict(tasks)
            
            # Write to temporary file first (atomic operation)
            with open(self.tasks_temp, 'w', encoding='utf-8') as f:
                json.dump(tasks_dict, f, indent=2, default=str)
            
            # Move temporary file to final location
            shutil.move(str(self.tasks_temp), str(self.tasks_file))
            
        except Exception as e:
            # Clean up temporary file if it exists
            if self.tasks_temp.exists():
                self.tasks_temp.unlink()
            raise StateManagerError(f"Failed to save tasks document: {e}") from e
    
    def load_tasks_document(self) -> Optional[TasksDocument]:
        """
        Load tasks document from persistent storage.
        
        Returns:
            The loaded tasks document, or None if no document exists
            
        Raises:
            StateCorruptionError: If the document data is corrupted
        """
        self._ensure_initialized()
        
        if not self.tasks_file.exists():
            return None
        
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks_dict = json.load(f)
            
            # Convert from dictionary to TasksDocument object
            tasks = self._dict_to_tasks_document(tasks_dict)
            
            # Validate the loaded document
            tasks.validate()
            
            return tasks
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Tasks document file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load tasks document: {e}") from e
    
    def save_enhanced_project_plan(self, plan: EnhancedProjectPlan) -> None:
        """
        Save enhanced project plan with documentation components to persistent storage.
        
        Args:
            plan: The enhanced project plan to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the plan before saving
            plan.validate()
            
            # Save the base project plan
            self.save_project_plan(plan)
            
            # Save documentation components if they exist
            if plan.requirements_document:
                self.save_requirements_document(plan.requirements_document)
            
            if plan.design_document:
                self.save_design_document(plan.design_document)
            
            if plan.tasks_document:
                self.save_tasks_document(plan.tasks_document)
            
            if plan.documentation_config:
                self.save_documentation_configuration(plan.documentation_config)
            
        except Exception as e:
            raise StateManagerError(f"Failed to save enhanced project plan: {e}") from e
    
    def load_enhanced_project_plan(self) -> Optional[EnhancedProjectPlan]:
        """
        Load enhanced project plan with documentation components from persistent storage.
        
        Returns:
            The loaded enhanced project plan, or None if no plan exists
            
        Raises:
            StateCorruptionError: If the plan data is corrupted
        """
        self._ensure_initialized()
        
        # Load base project plan
        base_plan = self.load_project_plan()
        if not base_plan:
            return None
        
        try:
            # Create enhanced plan from base plan
            enhanced_plan = EnhancedProjectPlan(
                objective=base_plan.objective,
                modules=base_plan.modules,
                dependency_graph=base_plan.dependency_graph,
                estimated_functions=base_plan.estimated_functions,
                created_at=base_plan.created_at
            )
            
            # Load documentation components
            enhanced_plan.requirements_document = self.load_requirements_document()
            enhanced_plan.design_document = self.load_design_document()
            enhanced_plan.tasks_document = self.load_tasks_document()
            enhanced_plan.documentation_config = self.load_documentation_configuration()
            
            return enhanced_plan
            
        except Exception as e:
            raise StateCorruptionError(f"Failed to load enhanced project plan: {e}") from e
    
    def save_documentation_configuration(self, config: DocumentationConfiguration) -> None:
        """
        Save documentation configuration to persistent storage with atomic operations.
        
        Args:
            config: The documentation configuration to save
            
        Raises:
            StateManagerError: If saving fails
        """
        self._ensure_initialized()
        
        try:
            # Validate the configuration before saving
            config.validate()
            
            # Convert to dictionary for JSON serialization
            config_dict = self._documentation_config_to_dict(config)
            
            # Write to temporary file first (atomic operation)
            with open(self.documentation_config_temp, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            # Move temporary file to final location
            shutil.move(str(self.documentation_config_temp), str(self.documentation_config_file))
            
        except Exception as e:
            # Clean up temporary file if it exists
            if self.documentation_config_temp.exists():
                self.documentation_config_temp.unlink()
            raise StateManagerError(f"Failed to save documentation configuration: {e}") from e
    
    def load_documentation_configuration(self) -> Optional[DocumentationConfiguration]:
        """
        Load documentation configuration from persistent storage.
        
        Returns:
            The loaded documentation configuration, or None if no configuration exists
            
        Raises:
            StateCorruptionError: If the configuration data is corrupted
        """
        self._ensure_initialized()
        
        if not self.documentation_config_file.exists():
            return None
        
        try:
            with open(self.documentation_config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Convert from dictionary to DocumentationConfiguration object
            config = self._dict_to_documentation_config(config_dict)
            
            # Validate the loaded configuration
            config.validate()
            
            return config
            
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Documentation configuration file is corrupted: {e}") from e
        except Exception as e:
            raise StateCorruptionError(f"Failed to load documentation configuration: {e}") from e
    
    def get_documentation_history(self, doc_type: str) -> List[Dict[str, Any]]:
        """
        Get version history for a specific documentation type.
        
        Args:
            doc_type: Type of documentation ('requirements', 'design', 'tasks')
            
        Returns:
            List of version history entries, sorted by timestamp (newest first)
        """
        self._ensure_initialized()
        
        history_file = self.documentation_history_dir / f"{doc_type}_history.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Sort by timestamp (newest first)
            history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return history
            
        except Exception:
            return []  # Return empty list if history is corrupted
    
    def restore_documentation_version(self, doc_type: str, version_id: str) -> bool:
        """
        Restore a specific version of documentation.
        
        Args:
            doc_type: Type of documentation ('requirements', 'design', 'tasks')
            version_id: ID of the version to restore
            
        Returns:
            True if restoration was successful, False otherwise
            
        Raises:
            StateManagerError: If restoration fails
        """
        self._ensure_initialized()
        
        try:
            # Check for valid document type first
            valid_doc_types = ["requirements", "design", "tasks"]
            if doc_type not in valid_doc_types:
                raise StateManagerError(f"Unknown document type: {doc_type}")
            
            # Get version history
            history = self.get_documentation_history(doc_type)
            
            # Find the specific version
            version_entry = None
            for entry in history:
                if entry.get("version_id") == version_id:
                    version_entry = entry
                    break
            
            if not version_entry:
                raise StateManagerError(f"Version {version_id} not found for {doc_type}")
            
            # Get the version file path
            version_file = self.documentation_history_dir / f"{doc_type}_{version_id}.json"
            
            if not version_file.exists():
                raise StateManagerError(f"Version file not found: {version_file}")
            
            # Load the version data
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
            
            # Restore based on document type
            if doc_type == "requirements":
                requirements = self._dict_to_requirements_document(version_data)
                self.save_requirements_document(requirements)
            elif doc_type == "design":
                design = self._dict_to_design_document(version_data)
                self.save_design_document(design)
            elif doc_type == "tasks":
                tasks = self._dict_to_tasks_document(version_data)
                self.save_tasks_document(tasks)
            
            return True
            
        except Exception as e:
            raise StateManagerError(f"Failed to restore {doc_type} version {version_id}: {e}") from e
    
    def _create_documentation_version(self, doc_type: str, document: Any) -> str:
        """
        Create a version history entry for a document.
        
        Args:
            doc_type: Type of documentation ('requirements', 'design', 'tasks')
            document: The document to version
            
        Returns:
            Version ID of the created version
        """
        try:
            # Generate version ID
            timestamp = datetime.now()
            version_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Convert document to dictionary
            if doc_type == "requirements":
                doc_dict = self._requirements_document_to_dict(document)
            elif doc_type == "design":
                doc_dict = self._design_document_to_dict(document)
            elif doc_type == "tasks":
                doc_dict = self._tasks_document_to_dict(document)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")
            
            # Save version file
            version_file = self.documentation_history_dir / f"{doc_type}_{version_id}.json"
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(doc_dict, f, indent=2, default=str)
            
            # Update history file
            history_file = self.documentation_history_dir / f"{doc_type}_history.json"
            
            # Load existing history
            history = []
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except Exception:
                    history = []  # Start fresh if corrupted
            
            # Add new version entry
            version_entry = {
                "version_id": version_id,
                "timestamp": timestamp.isoformat(),
                "doc_type": doc_type,
                "file_path": str(version_file)
            }
            
            history.append(version_entry)
            
            # Keep only last 20 versions
            history = history[-20:]
            
            # Save updated history
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, default=str)
            
            return version_id
            
        except Exception as e:
            # Don't fail the main operation if versioning fails
            print(f"Warning: Failed to create version for {doc_type}: {e}")
            return ""
    
    # Serialization methods for enhanced documentation models
    
    def _requirements_document_to_dict(self, requirements: RequirementsDocument) -> Dict[str, Any]:
        """Convert RequirementsDocument to dictionary for JSON serialization."""
        return {
            "introduction": requirements.introduction,
            "requirements": [self._requirement_to_dict(req) for req in requirements.requirements],
            "created_at": requirements.created_at.isoformat(),
            "version": requirements.version
        }
    
    def _dict_to_requirements_document(self, data: Dict[str, Any]) -> RequirementsDocument:
        """Convert dictionary to RequirementsDocument object."""
        from ..core.models import Requirement
        
        requirements = [self._dict_to_requirement(req_data) for req_data in data.get("requirements", [])]
        
        return RequirementsDocument(
            introduction=data["introduction"],
            requirements=requirements,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            version=data.get("version", "1.0")
        )
    
    def _requirement_to_dict(self, requirement) -> Dict[str, Any]:
        """Convert Requirement to dictionary for JSON serialization."""
        return {
            "id": requirement.id,
            "user_story": requirement.user_story,
            "acceptance_criteria": [self._acceptance_criterion_to_dict(ac) for ac in requirement.acceptance_criteria],
            "priority": requirement.priority.value,
            "category": requirement.category
        }
    
    def _dict_to_requirement(self, data: Dict[str, Any]):
        """Convert dictionary to Requirement object."""
        from ..core.models import Requirement, AcceptanceCriterion, RequirementPriority
        
        acceptance_criteria = [self._dict_to_acceptance_criterion(ac_data) for ac_data in data.get("acceptance_criteria", [])]
        
        return Requirement(
            id=data["id"],
            user_story=data["user_story"],
            acceptance_criteria=acceptance_criteria,
            priority=RequirementPriority(data.get("priority", "medium")),
            category=data.get("category", "")
        )
    
    def _acceptance_criterion_to_dict(self, criterion) -> Dict[str, Any]:
        """Convert AcceptanceCriterion to dictionary for JSON serialization."""
        return {
            "id": criterion.id,
            "when_clause": criterion.when_clause,
            "shall_clause": criterion.shall_clause,
            "requirement_id": criterion.requirement_id
        }
    
    def _dict_to_acceptance_criterion(self, data: Dict[str, Any]):
        """Convert dictionary to AcceptanceCriterion object."""
        from ..core.models import AcceptanceCriterion
        
        return AcceptanceCriterion(
            id=data["id"],
            when_clause=data["when_clause"],
            shall_clause=data["shall_clause"],
            requirement_id=data["requirement_id"]
        )
    
    def _design_document_to_dict(self, design: DesignDocument) -> Dict[str, Any]:
        """Convert DesignDocument to dictionary for JSON serialization."""
        return {
            "overview": design.overview,
            "architecture": design.architecture,
            "components": [self._design_component_to_dict(comp) for comp in design.components],
            "requirement_mappings": design.requirement_mappings,
            "created_at": design.created_at.isoformat()
        }
    
    def _dict_to_design_document(self, data: Dict[str, Any]) -> DesignDocument:
        """Convert dictionary to DesignDocument object."""
        from ..core.models import DesignComponent
        
        components = [self._dict_to_design_component(comp_data) for comp_data in data.get("components", [])]
        
        return DesignDocument(
            overview=data["overview"],
            architecture=data["architecture"],
            components=components,
            requirement_mappings=data.get("requirement_mappings", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )
    
    def _design_component_to_dict(self, component) -> Dict[str, Any]:
        """Convert DesignComponent to dictionary for JSON serialization."""
        return {
            "id": component.id,
            "name": component.name,
            "description": component.description,
            "responsibilities": component.responsibilities,
            "interfaces": component.interfaces,
            "requirement_mappings": component.requirement_mappings
        }
    
    def _dict_to_design_component(self, data: Dict[str, Any]):
        """Convert dictionary to DesignComponent object."""
        from ..core.models import DesignComponent
        
        return DesignComponent(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            responsibilities=data.get("responsibilities", []),
            interfaces=data.get("interfaces", []),
            requirement_mappings=data.get("requirement_mappings", [])
        )
    
    def _tasks_document_to_dict(self, tasks: TasksDocument) -> Dict[str, Any]:
        """Convert TasksDocument to dictionary for JSON serialization."""
        return {
            "tasks": [self._implementation_task_to_dict(task) for task in tasks.tasks],
            "requirement_coverage": tasks.requirement_coverage,
            "design_coverage": tasks.design_coverage,
            "created_at": tasks.created_at.isoformat()
        }
    
    def _dict_to_tasks_document(self, data: Dict[str, Any]) -> TasksDocument:
        """Convert dictionary to TasksDocument object."""
        from ..core.models import ImplementationTask
        
        tasks = [self._dict_to_implementation_task(task_data) for task_data in data.get("tasks", [])]
        
        return TasksDocument(
            tasks=tasks,
            requirement_coverage=data.get("requirement_coverage", {}),
            design_coverage=data.get("design_coverage", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )
    
    def _implementation_task_to_dict(self, task) -> Dict[str, Any]:
        """Convert ImplementationTask to dictionary for JSON serialization."""
        return {
            "id": task.id,
            "description": task.description,
            "requirement_references": task.requirement_references,
            "design_references": task.design_references,
            "dependencies": task.dependencies,
            "estimated_effort": task.estimated_effort,
            "priority": task.priority.value
        }
    
    def _dict_to_implementation_task(self, data: Dict[str, Any]):
        """Convert dictionary to ImplementationTask object."""
        from ..core.models import ImplementationTask, RequirementPriority
        
        return ImplementationTask(
            id=data["id"],
            description=data["description"],
            requirement_references=data.get("requirement_references", []),
            design_references=data.get("design_references", []),
            dependencies=data.get("dependencies", []),
            estimated_effort=data.get("estimated_effort"),
            priority=RequirementPriority(data.get("priority", "medium"))
        )
    
    def _documentation_config_to_dict(self, config: DocumentationConfiguration) -> Dict[str, Any]:
        """Convert DocumentationConfiguration to dictionary for JSON serialization."""
        return {
            "enable_requirements": config.enable_requirements,
            "enable_design": config.enable_design,
            "enable_tasks": config.enable_tasks,
            "requirement_format": config.requirement_format,
            "template_requirements": config.template_requirements,
            "template_design": config.template_design,
            "template_tasks": config.template_tasks,
            "include_traceability": config.include_traceability,
            "validation_level": config.validation_level
        }
    
    def _dict_to_documentation_config(self, data: Dict[str, Any]) -> DocumentationConfiguration:
        """Convert dictionary to DocumentationConfiguration object."""
        return DocumentationConfiguration(
            enable_requirements=data.get("enable_requirements", True),
            enable_design=data.get("enable_design", True),
            enable_tasks=data.get("enable_tasks", True),
            requirement_format=data.get("requirement_format", "ears"),
            template_requirements=data.get("template_requirements"),
            template_design=data.get("template_design"),
            template_tasks=data.get("template_tasks"),
            include_traceability=data.get("include_traceability", True),
            validation_level=data.get("validation_level", "strict")
        )