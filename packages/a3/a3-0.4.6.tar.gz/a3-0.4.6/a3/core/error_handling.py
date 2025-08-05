"""
Error handling utilities for enhanced planning system.

This module provides utilities for graceful degradation, partial generation,
and validation warning management in the A3 enhanced planning system.
"""

from datetime import datetime

from typing import Dict, List, Optional, Any, Callable, Union
import logging

from .models import (



    DocumentGenerationError, RequirementParsingError, RequirementValidationError,
    DocumentConsistencyError, ValidationWarning, PartialGenerationResult,
    GracefulDegradationConfig
)


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors and warnings during document generation with graceful degradation."""
    
def __init__(self, config: Optional[GracefulDegradationConfig] = None):
        """Initialize the error handler with configuration."""
        self.config = config or GracefulDegradationConfig()
        self.warnings: List[ValidationWarning] = []
        self.errors: List[Exception] = []
        self.partial_content: Dict[str, Any] = {}
    
def add_warning(self, warning: ValidationWarning) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)
        logger.warning(f"Validation warning: {warning.message}")
    
def add_error(self, error: Exception) -> None:
        """Add an error."""
        self.errors.append(error)
        logger.error(f"Error occurred: {str(error)}")
    
def should_continue(self) -> bool:
        """Determine if processing should continue based on current warnings and errors."""
        warning_count = len(self.warnings)
        error_count = len(self.errors)
        
        if not self.config.should_continue_on_warning(warning_count):
            logger.info(f"Stopping due to warning threshold exceeded: {warning_count}")
            return False
        
        if not self.config.should_continue_on_error(error_count):
            logger.info(f"Stopping due to error threshold exceeded: {error_count}")
            return False
        
        return True
    
def create_partial_result(self, generated_docs: Dict[str, Any], 
                            failed_docs: Dict[str, str]) -> PartialGenerationResult:
        """Create a partial generation result."""
        success = len(generated_docs) > 0 and len(failed_docs) == 0
        
        return PartialGenerationResult(
            success=success,
            generated_documents=generated_docs,
            failed_documents=failed_docs,
            warnings=self.warnings.copy(),
            errors=self.errors.copy(),
            timestamp=datetime.now()
        )
    
def reset(self) -> None:
        """Reset the error handler state."""
        self.warnings.clear()
        self.errors.clear()
        self.partial_content.clear()


class ValidationWarningSystem:
    """System for managing validation warnings and requirement coverage analysis."""
    
def __init__(self):
        """Initialize the validation warning system."""
        self.warnings: List[ValidationWarning] = []
    
def check_requirement_coverage(self, requirements: List[Dict[str, Any]], 
                                 tasks: List[Dict[str, Any]]) -> List[ValidationWarning]:
        """Check for incomplete requirement coverage in tasks."""
        warnings = []
        
        # Create mapping of requirement IDs to tasks
        task_requirements = set()
        for task in tasks:
            req_refs = task.get('requirement_references', [])
            task_requirements.update(req_refs)
        
        # Check for uncovered requirements
        for req in requirements:
            req_id = req.get('id', '')
            if req_id and req_id not in task_requirements:
                warning = ValidationWarning(
                    message=f"Requirement '{req_id}' is not covered by any implementation task",
                    warning_type="incomplete_coverage",
                    affected_item=req_id,
                    severity="warning",
                    suggestions=[
                        f"Add implementation task for requirement {req_id}",
                        "Review requirement to ensure it needs implementation"
                    ]
                )
                warnings.append(warning)
        
        return warnings
    
def check_orphaned_tasks(self, requirements: List[Dict[str, Any]], 
                           tasks: List[Dict[str, Any]]) -> List[ValidationWarning]:
        """Check for tasks that don't reference any requirements."""
        warnings = []
        
        # Create set of valid requirement IDs
        valid_req_ids = {req.get('id', '') for req in requirements if req.get('id')}
        
        # Check each task for requirement references
        for task in tasks:
            task_id = task.get('id', 'unknown')
            req_refs = task.get('requirement_references', [])
            
            if not req_refs:
                warning = ValidationWarning(
                    message=f"Task '{task_id}' does not reference any requirements",
                    warning_type="orphaned_task",
                    affected_item=task_id,
                    severity="warning",
                    suggestions=[
                        f"Add requirement references to task {task_id}",
                        "Review if task is necessary for the feature"
                    ]
                )
                warnings.append(warning)
            else:
                # Check for invalid requirement references
                for req_ref in req_refs:
                    if req_ref not in valid_req_ids:
                        warning = ValidationWarning(
                            message=f"Task '{task_id}' references non-existent requirement '{req_ref}'",
                            warning_type="invalid_requirement_reference",
                            affected_item=task_id,
                            severity="error",
                            suggestions=[
                                f"Remove invalid reference '{req_ref}' from task {task_id}",
                                f"Create requirement with ID '{req_ref}' if needed"
                            ]
                        )
                        warnings.append(warning)
        
        return warnings
    
def check_design_consistency(self, requirements: List[Dict[str, Any]], 
                               design_components: List[Dict[str, Any]]) -> List[ValidationWarning]:
        """Check consistency between requirements and design components."""
        warnings = []
        
        # Create mapping of requirements to design components
        design_req_refs = set()
        for component in design_components:
            req_refs = component.get('requirement_references', [])
            design_req_refs.update(req_refs)
        
        # Check for requirements not addressed in design
        valid_req_ids = {req.get('id', '') for req in requirements if req.get('id')}
        
        for req_id in valid_req_ids:
            if req_id not in design_req_refs:
                warning = ValidationWarning(
                    message=f"Requirement '{req_id}' is not addressed in any design component",
                    warning_type="missing_design_coverage",
                    affected_item=req_id,
                    severity="warning",
                    suggestions=[
                        f"Add design component addressing requirement {req_id}",
                        "Review if requirement needs design consideration"
                    ]
                )
                warnings.append(warning)
        
        return warnings
    
def validate_when_shall_statements(self, requirements: List[Dict[str, Any]]) -> List[ValidationWarning]:
        """Validate WHEN/SHALL statement format in requirements."""
        warnings = []
        
        for req in requirements:
            req_id = req.get('id', 'unknown')
            acceptance_criteria = req.get('acceptance_criteria', [])
            
            for i, criterion in enumerate(acceptance_criteria):
                criterion_text = criterion.get('text', '') if isinstance(criterion, dict) else str(criterion)
                
                # Check for WHEN/SHALL format
                if not self._has_when_shall_format(criterion_text):
                    warning = ValidationWarning(
                        message=f"Acceptance criterion {i+1} in requirement '{req_id}' does not follow WHEN/SHALL format",
                        warning_type="invalid_ears_format",
                        affected_item=req_id,
                        severity="warning",
                        suggestions=[
                            "Rewrite criterion using WHEN [condition] THEN [system] SHALL [response] format",
                            "Use IF [precondition] THEN [system] SHALL [response] for conditional requirements"
                        ]
                    )
                    warnings.append(warning)
        
        # Add warnings to the instance collection
        self.warnings.extend(warnings)
        return warnings
    
def _has_when_shall_format(self, text: str) -> bool:
        """Check if text follows WHEN/SHALL or IF/SHALL format."""
        text_upper = text.upper()
        
        # Check for WHEN...SHALL pattern
        when_shall = 'WHEN' in text_upper and 'SHALL' in text_upper
        
        # Check for IF...SHALL pattern
        if_shall = 'IF' in text_upper and 'SHALL' in text_upper
        
        return when_shall or if_shall
    
def get_all_warnings(self) -> List[ValidationWarning]:
        """Get all collected warnings."""
        return self.warnings.copy()
    
def clear_warnings(self) -> None:
        """Clear all warnings."""
        self.warnings.clear()


def safe_document_generation(generation_func: Callable[[], Any], 
                           document_type: str,
                           error_handler: ErrorHandler) -> Optional[Any]:
    """Safely execute document generation with error handling."""
    try:
        return generation_func()
    except DocumentGenerationError as e:
        error_handler.add_error(e)
        if e.can_recover() and error_handler.config.preserve_partial_content:
            return e.get_partial_content()
        return None
    except RequirementParsingError as e:
        error_handler.add_error(e)
        if error_handler.config.preserve_partial_content:
            return {"partial_requirements": e.get_partial_requirements()}
        return None
    except RequirementValidationError as e:
        if e.is_warning():
            warning = ValidationWarning(
                message=str(e),
                warning_type="requirement_validation",
                affected_item=e.requirement_id,
                severity="warning"
            )
            error_handler.add_warning(warning)
        else:
            error_handler.add_error(e)
        return None
    except DocumentConsistencyError as e:
        if e.is_warning():
            warning = ValidationWarning(
                message=str(e),
                warning_type="document_consistency",
                severity="warning"
            )
            error_handler.add_warning(warning)
        else:
            error_handler.add_error(e)
        return None
    except Exception as e:
        # Wrap unexpected exceptions
        wrapped_error = DocumentGenerationError(
            f"Unexpected error during {document_type} generation: {str(e)}",
            document_type=document_type,
            recoverable=False
        )
        error_handler.add_error(wrapped_error)
        return None


def create_fallback_content(document_type: str, objective: str) -> Dict[str, Any]:
    """Create basic fallback content when enhanced generation fails."""
    timestamp = datetime.now().isoformat()
    
    if document_type == "requirements":
        return {
            "introduction": f"Basic requirements for: {objective}",
            "requirements": [
                {
                    "id": "1",
                    "user_story": f"As a user, I want {objective}, so that I can achieve my goals",
                    "acceptance_criteria": [
                        "WHEN the system is implemented THEN it SHALL meet the basic objective"
                    ]
                }
            ],
            "generated_at": timestamp,
            "fallback": True
        }
    
    elif document_type == "design":
        return {
            "overview": f"Basic design for: {objective}",
            "architecture": "Standard modular architecture",
            "components": [
                {
                    "name": "main_component",
                    "description": "Primary component implementing the objective",
                    "requirement_references": ["1"]
                }
            ],
            "generated_at": timestamp,
            "fallback": True
        }
    
    elif document_type == "tasks":
        return {
            "tasks": [
                {
                    "id": "1",
                    "description": f"Implement basic functionality for {objective}",
                    "requirement_references": ["1"]
                }
            ],
            "generated_at": timestamp,
            "fallback": True
        }
    
    else:
        return {
            "content": f"Basic {document_type} content for: {objective}",
            "generated_at": timestamp,
            "fallback": True
        }