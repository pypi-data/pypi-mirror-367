"""
Migration utilities for A3 enhanced planning features.

This module provides utilities for migrating existing A3 projects to use
enhanced planning features while maintaining backward compatibility.
"""

from datetime import datetime
from pathlib import Path
import json

from typing import Optional, Dict, Any, List
import logging

from ..managers.state import StateManager
from .interfaces import StateManagerInterface
from .models import ProjectPlan, EnhancedProjectPlan, DocumentationConfiguration





class MigrationError(Exception):
    """Exception raised during migration operations."""
    pass


class ProjectMigrator:
    """
    Handles migration of existing A3 projects to enhanced planning format.
    
    This class provides utilities to upgrade existing projects to use
    enhanced planning features without breaking existing workflows.
    """
    
def __init__(self, project_path: str):
        """
        Initialize the project migrator.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path)
        self.state_manager = StateManager(str(project_path))
        self.logger = logging.getLogger(__name__)
    
def check_compatibility(self) -> Dict[str, Any]:
        """
        Check if the current project can use enhanced planning features.
        
        Returns:
            Dictionary containing compatibility information
        """
        try:
            self.state_manager.initialize()
            
            # Check if project has existing plan
            existing_plan = self.state_manager.load_project_plan()
            has_existing_plan = existing_plan is not None
            
            # Check if already enhanced
            is_already_enhanced = isinstance(existing_plan, EnhancedProjectPlan)
            
            # Check if enhanced features are available
            can_use_enhanced = self.state_manager.can_use_enhanced_features()
            
            # Check for potential issues
            issues = []
            warnings = []
            
            if has_existing_plan and not is_already_enhanced:
                warnings.append("Project has existing basic plan that can be migrated")
            
            if not has_existing_plan:
                issues.append("No existing project plan found")
            
            # Check for corrupted state
            try:
                if existing_plan:
                    existing_plan.validate()
            except Exception as e:
                issues.append(f"Existing plan validation failed: {str(e)}")
            
            return {
                "compatible": len(issues) == 0,
                "has_existing_plan": has_existing_plan,
                "is_already_enhanced": is_already_enhanced,
                "can_use_enhanced_features": can_use_enhanced,
                "issues": issues,
                "warnings": warnings,
                "migration_needed": has_existing_plan and not is_already_enhanced,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "compatible": False,
                "has_existing_plan": False,
                "is_already_enhanced": False,
                "can_use_enhanced_features": False,
                "issues": [f"Compatibility check failed: {str(e)}"],
                "warnings": [],
                "migration_needed": False,
                "checked_at": datetime.now().isoformat()
            }
    
def migrate_project(self, backup: bool = True) -> Dict[str, Any]:
        """
        Migrate an existing project to enhanced planning format.
        
        Args:
            backup: Whether to create a backup before migration
            
        Returns:
            Dictionary containing migration results
        """
        try:
            self.state_manager.initialize()
            
            # Check compatibility first
            compatibility = self.check_compatibility()
            if not compatibility["compatible"]:
                raise MigrationError(f"Project is not compatible for migration: {compatibility['issues']}")
            
            if not compatibility["migration_needed"]:
                return {
                    "success": True,
                    "message": "No migration needed - project is already enhanced or has no existing plan",
                    "backup_created": False,
                    "migrated_at": datetime.now().isoformat()
                }
            
            # Create backup if requested
            backup_id = None
            if backup:
                backup_id = self.state_manager.create_checkpoint()
            
            # Perform migration
            migration_success = self.state_manager.migrate_to_enhanced_plan()
            
            if not migration_success:
                raise MigrationError("Failed to migrate project plan to enhanced format")
            
            return {
                "success": True,
                "message": "Project successfully migrated to enhanced planning format",
                "backup_created": backup,
                "backup_id": backup_id,
                "migrated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            return {
                "success": False,
                "message": f"Migration failed: {str(e)}",
                "backup_created": False,
                "backup_id": None,
                "migrated_at": datetime.now().isoformat()
            }
    
def rollback_migration(self, backup_id: str) -> Dict[str, Any]:
        """
        Rollback a migration using a backup checkpoint.
        
        Args:
            backup_id: ID of the backup checkpoint to restore
            
        Returns:
            Dictionary containing rollback results
        """
        try:
            self.state_manager.initialize()
            
            # Restore from backup
            self.state_manager.restore_checkpoint(backup_id)
            
            return {
                "success": True,
                "message": f"Successfully rolled back migration using backup {backup_id}",
                "rolled_back_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return {
                "success": False,
                "message": f"Rollback failed: {str(e)}",
                "rolled_back_at": datetime.now().isoformat()
            }
    
def get_migration_status(self) -> Dict[str, Any]:
        """
        Get the current migration status of the project.
        
        Returns:
            Dictionary containing migration status information
        """
        try:
            self.state_manager.initialize()
            
            # Load current plan
            current_plan = self.state_manager.load_project_plan()
            
            if not current_plan:
                return {
                    "status": "no_plan",
                    "message": "No project plan found",
                    "is_enhanced": False,
                    "can_migrate": False
                }
            
            is_enhanced = isinstance(current_plan, EnhancedProjectPlan)
            
            if is_enhanced:
                enhanced_plan = current_plan
                return {
                    "status": "enhanced",
                    "message": "Project is using enhanced planning features",
                    "is_enhanced": True,
                    "can_migrate": False,
                    "has_requirements": enhanced_plan.requirements_document is not None,
                    "has_design": enhanced_plan.design_document is not None,
                    "has_tasks": enhanced_plan.tasks_document is not None,
                    "enhanced_functions_count": len(enhanced_plan.enhanced_functions)
                }
            else:
                return {
                    "status": "basic",
                    "message": "Project is using basic planning features",
                    "is_enhanced": False,
                    "can_migrate": True,
                    "modules_count": len(current_plan.modules),
                    "estimated_functions": current_plan.estimated_functions
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get migration status: {str(e)}",
                "is_enhanced": False,
                "can_migrate": False
            }


def check_project_compatibility(project_path: str) -> Dict[str, Any]:
    """
    Convenience function to check project compatibility.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Dictionary containing compatibility information
    """
    migrator = ProjectMigrator(project_path)
    return migrator.check_compatibility()


def migrate_project_to_enhanced(project_path: str, backup: bool = True) -> Dict[str, Any]:
    """
    Convenience function to migrate a project to enhanced planning.
    
    Args:
        project_path: Path to the project directory
        backup: Whether to create a backup before migration
        
    Returns:
        Dictionary containing migration results
    """
    migrator = ProjectMigrator(project_path)
    return migrator.migrate_project(backup=backup)