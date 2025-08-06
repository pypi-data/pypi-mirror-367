"""
Tests for error handling utilities in the enhanced planning system.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from a3.core.models import (
    DocumentGenerationError, RequirementParsingError, RequirementValidationError,
    DocumentConsistencyError, ValidationWarning, PartialGenerationResult,
    GracefulDegradationConfig, ValidationError
)
from a3.core.error_handling import (
    ErrorHandler, ValidationWarningSystem, safe_document_generation,
    create_fallback_content
)


class TestDocumentGenerationError:
    """Test enhanced DocumentGenerationError functionality."""
    
    def test_basic_error_creation(self):
        """Test basic error creation."""
        error = DocumentGenerationError("Test error")
        assert str(error) == "Test error"
        assert error.document_type is None
        assert error.partial_content == {}
        assert error.recoverable is True
        assert isinstance(error.timestamp, datetime)
    
    def test_error_with_details(self):
        """Test error creation with detailed information."""
        partial_content = {"section1": "content"}
        error = DocumentGenerationError(
            "Generation failed",
            document_type="requirements",
            partial_content=partial_content,
            recoverable=False
        )
        
        assert error.document_type == "requirements"
        assert error.partial_content == partial_content
        assert error.recoverable is False
        assert not error.can_recover()
    
    def test_recoverable_error(self):
        """Test recoverable error functionality."""
        error = DocumentGenerationError("Recoverable error", recoverable=True)
        assert error.can_recover()
        
        error = DocumentGenerationError("Non-recoverable error", recoverable=False)
        assert not error.can_recover()
    
    def test_partial_content_retrieval(self):
        """Test partial content retrieval."""
        partial_content = {"intro": "test", "requirements": []}
        error = DocumentGenerationError("Error", partial_content=partial_content)
        
        retrieved_content = error.get_partial_content()
        assert retrieved_content == partial_content


class TestRequirementParsingError:
    """Test enhanced RequirementParsingError functionality."""
    
    def test_basic_parsing_error(self):
        """Test basic parsing error creation."""
        error = RequirementParsingError("Parsing failed")
        assert str(error) == "Parsing failed"
        assert error.objective_text is None
        assert error.parsed_requirements == []
        assert error.line_number is None
    
    def test_parsing_error_with_context(self):
        """Test parsing error with context information."""
        objective = "Create a web application"
        parsed_reqs = [{"id": "1", "text": "requirement 1"}]
        
        error = RequirementParsingError(
            "Failed at line 5",
            objective_text=objective,
            parsed_requirements=parsed_reqs,
            line_number=5
        )
        
        assert error.objective_text == objective
        assert error.parsed_requirements == parsed_reqs
        assert error.line_number == 5
    
    def test_partial_requirements_retrieval(self):
        """Test partial requirements retrieval."""
        parsed_reqs = [{"id": "1"}, {"id": "2"}]
        error = RequirementParsingError("Error", parsed_requirements=parsed_reqs)
        
        retrieved_reqs = error.get_partial_requirements()
        assert retrieved_reqs == parsed_reqs


class TestRequirementValidationError:
    """Test enhanced RequirementValidationError functionality."""
    
    def test_basic_validation_error(self):
        """Test basic validation error creation."""
        error = RequirementValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert error.requirement_id is None
        assert error.validation_errors == []
        assert error.severity == "error"
        assert not error.is_warning()
    
    def test_validation_warning(self):
        """Test validation error as warning."""
        error = RequirementValidationError(
            "Minor issue",
            requirement_id="REQ-1",
            validation_errors=["Missing WHEN clause"],
            severity="warning"
        )
        
        assert error.requirement_id == "REQ-1"
        assert error.validation_errors == ["Missing WHEN clause"]
        assert error.is_warning()
    
    def test_validation_errors_retrieval(self):
        """Test validation errors retrieval."""
        errors = ["Error 1", "Error 2"]
        error = RequirementValidationError("Failed", validation_errors=errors)
        
        retrieved_errors = error.get_validation_errors()
        assert retrieved_errors == errors


class TestDocumentConsistencyError:
    """Test enhanced DocumentConsistencyError functionality."""
    
    def test_basic_consistency_error(self):
        """Test basic consistency error creation."""
        error = DocumentConsistencyError("Inconsistency detected")
        assert str(error) == "Inconsistency detected"
        assert error.inconsistencies == []
        assert error.affected_documents == []
        assert error.severity == "error"
        assert not error.is_warning()
    
    def test_consistency_error_with_details(self):
        """Test consistency error with detailed information."""
        inconsistencies = [{"type": "missing_ref", "details": "REQ-1 not found"}]
        affected_docs = ["requirements.md", "design.md"]
        
        error = DocumentConsistencyError(
            "Multiple inconsistencies",
            inconsistencies=inconsistencies,
            affected_documents=affected_docs,
            severity="warning"
        )
        
        assert error.inconsistencies == inconsistencies
        assert error.affected_documents == affected_docs
        assert error.is_warning()
    
    def test_inconsistencies_retrieval(self):
        """Test inconsistencies retrieval."""
        inconsistencies = [{"issue": "test"}]
        error = DocumentConsistencyError("Error", inconsistencies=inconsistencies)
        
        retrieved = error.get_inconsistencies()
        assert retrieved == inconsistencies


class TestValidationWarning:
    """Test ValidationWarning data class."""
    
    def test_basic_warning_creation(self):
        """Test basic warning creation."""
        warning = ValidationWarning(
            message="Test warning",
            warning_type="test_type"
        )
        
        assert warning.message == "Test warning"
        assert warning.warning_type == "test_type"
        assert warning.affected_item is None
        assert warning.severity == "warning"
        assert warning.suggestions == []
        assert isinstance(warning.timestamp, datetime)
    
    def test_warning_with_details(self):
        """Test warning creation with all details."""
        suggestions = ["Fix this", "Try that"]
        warning = ValidationWarning(
            message="Detailed warning",
            warning_type="detailed_type",
            affected_item="REQ-1",
            severity="error",
            suggestions=suggestions
        )
        
        assert warning.affected_item == "REQ-1"
        assert warning.severity == "error"
        assert warning.suggestions == suggestions
    
    def test_warning_validation(self):
        """Test warning validation."""
        # Empty message should raise error
        with pytest.raises(ValidationError, match="Warning message cannot be empty"):
            ValidationWarning(message="", warning_type="test")
        
        # Invalid severity should raise error
        with pytest.raises(ValidationError, match="Invalid severity level"):
            ValidationWarning(message="test", warning_type="test", severity="invalid")
        
        # Empty warning type should raise error
        with pytest.raises(ValidationError, match="Warning type cannot be empty"):
            ValidationWarning(message="test", warning_type="")


class TestPartialGenerationResult:
    """Test PartialGenerationResult data class."""
    
    def test_successful_result(self):
        """Test successful generation result."""
        generated_docs = {"requirements": {"content": "test"}}
        result = PartialGenerationResult(
            success=True,
            generated_documents=generated_docs
        )
        
        assert result.success is True
        assert result.generated_documents == generated_docs
        assert result.failed_documents == {}
        assert result.warnings == []
        assert result.errors == []
        assert not result.has_warnings()
        assert not result.has_errors()
        assert result.get_success_rate() == 1.0
        assert not result.is_partial_success()
    
    def test_partial_success_result(self):
        """Test partial success result."""
        generated_docs = {"requirements": {"content": "test"}}
        failed_docs = {"design": "Generation failed"}
        warnings = [ValidationWarning("Warning", "test")]
        
        result = PartialGenerationResult(
            success=False,
            generated_documents=generated_docs,
            failed_documents=failed_docs,
            warnings=warnings
        )
        
        assert result.success is False
        assert result.has_warnings()
        assert result.get_warning_count() == 1
        assert result.get_success_rate() == 0.5
        assert result.is_partial_success()
        assert result.get_generated_document_types() == ["requirements"]
        assert result.get_failed_document_types() == ["design"]
    
    def test_result_validation(self):
        """Test result validation."""
        # Invalid generated_documents type
        with pytest.raises(ValidationError, match="Generated documents must be a dictionary"):
            PartialGenerationResult(success=True, generated_documents="invalid")
        
        # No documents at all
        with pytest.raises(ValidationError, match="must have either generated or failed documents"):
            PartialGenerationResult(success=True)


class TestGracefulDegradationConfig:
    """Test GracefulDegradationConfig data class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = GracefulDegradationConfig()
        
        assert config.allow_partial_generation is True
        assert config.continue_on_warnings is True
        assert config.continue_on_errors is False
        assert config.max_warnings_threshold == 10
        assert config.max_errors_threshold == 3
        assert config.fallback_to_basic_generation is True
        assert config.preserve_partial_content is True
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Negative thresholds should raise error
        with pytest.raises(ValidationError, match="Max warnings threshold cannot be negative"):
            GracefulDegradationConfig(max_warnings_threshold=-1)
        
        with pytest.raises(ValidationError, match="Max errors threshold cannot be negative"):
            GracefulDegradationConfig(max_errors_threshold=-1)
    
    def test_threshold_checks(self):
        """Test threshold checking methods."""
        config = GracefulDegradationConfig(
            max_warnings_threshold=5,
            max_errors_threshold=2,
            continue_on_warnings=True,
            continue_on_errors=True
        )
        
        # Within thresholds
        assert config.should_continue_on_warning(3)
        assert config.should_continue_on_error(1)
        
        # At thresholds
        assert config.should_continue_on_warning(5)
        assert config.should_continue_on_error(2)
        
        # Exceeding thresholds
        assert not config.should_continue_on_warning(6)
        assert not config.should_continue_on_error(3)
        
        # Disabled continuation
        config.continue_on_warnings = False
        config.continue_on_errors = False
        assert not config.should_continue_on_warning(1)
        assert not config.should_continue_on_error(1)


class TestErrorHandler:
    """Test ErrorHandler class."""
    
    def test_basic_error_handler(self):
        """Test basic error handler functionality."""
        handler = ErrorHandler()
        
        assert len(handler.warnings) == 0
        assert len(handler.errors) == 0
        assert handler.should_continue()
    
    def test_adding_warnings_and_errors(self):
        """Test adding warnings and errors."""
        handler = ErrorHandler()
        
        warning = ValidationWarning("Test warning", "test")
        error = DocumentGenerationError("Test error")
        
        handler.add_warning(warning)
        handler.add_error(error)
        
        assert len(handler.warnings) == 1
        assert len(handler.errors) == 1
        assert handler.warnings[0] == warning
        assert handler.errors[0] == error
    
    def test_threshold_checking(self):
        """Test threshold-based continuation logic."""
        config = GracefulDegradationConfig(
            max_warnings_threshold=2,
            max_errors_threshold=1
        )
        handler = ErrorHandler(config)
        
        # Should continue initially
        assert handler.should_continue()
        
        # Add warnings up to threshold
        handler.add_warning(ValidationWarning("Warning 1", "test"))
        handler.add_warning(ValidationWarning("Warning 2", "test"))
        assert handler.should_continue()
        
        # Exceed warning threshold
        handler.add_warning(ValidationWarning("Warning 3", "test"))
        assert not handler.should_continue()
    
    def test_partial_result_creation(self):
        """Test partial result creation."""
        handler = ErrorHandler()
        
        warning = ValidationWarning("Test warning", "test")
        error = DocumentGenerationError("Test error")
        handler.add_warning(warning)
        handler.add_error(error)
        
        generated_docs = {"requirements": {"content": "test"}}
        failed_docs = {"design": "Failed"}
        
        result = handler.create_partial_result(generated_docs, failed_docs)
        
        assert result.generated_documents == generated_docs
        assert result.failed_documents == failed_docs
        assert len(result.warnings) == 1
        assert len(result.errors) == 1
        assert not result.success  # Has failed docs
    
    def test_handler_reset(self):
        """Test handler reset functionality."""
        handler = ErrorHandler()
        
        handler.add_warning(ValidationWarning("Warning", "test"))
        handler.add_error(DocumentGenerationError("Error"))
        handler.partial_content["test"] = "content"
        
        assert len(handler.warnings) > 0
        assert len(handler.errors) > 0
        assert len(handler.partial_content) > 0
        
        handler.reset()
        
        assert len(handler.warnings) == 0
        assert len(handler.errors) == 0
        assert len(handler.partial_content) == 0


class TestValidationWarningSystem:
    """Test ValidationWarningSystem class."""
    
    def test_requirement_coverage_check(self):
        """Test requirement coverage checking."""
        system = ValidationWarningSystem()
        
        requirements = [
            {"id": "REQ-1", "text": "Requirement 1"},
            {"id": "REQ-2", "text": "Requirement 2"},
            {"id": "REQ-3", "text": "Requirement 3"}
        ]
        
        tasks = [
            {"id": "TASK-1", "requirement_references": ["REQ-1", "REQ-2"]},
            {"id": "TASK-2", "requirement_references": ["REQ-1"]}
        ]
        
        warnings = system.check_requirement_coverage(requirements, tasks)
        
        # REQ-3 should be uncovered
        assert len(warnings) == 1
        assert warnings[0].affected_item == "REQ-3"
        assert warnings[0].warning_type == "incomplete_coverage"
    
    def test_orphaned_tasks_check(self):
        """Test orphaned tasks checking."""
        system = ValidationWarningSystem()
        
        requirements = [
            {"id": "REQ-1", "text": "Requirement 1"}
        ]
        
        tasks = [
            {"id": "TASK-1", "requirement_references": ["REQ-1"]},
            {"id": "TASK-2", "requirement_references": []},  # Orphaned
            {"id": "TASK-3", "requirement_references": ["REQ-999"]}  # Invalid ref
        ]
        
        warnings = system.check_orphaned_tasks(requirements, tasks)
        
        assert len(warnings) == 2
        
        # Check for orphaned task
        orphaned_warning = next(w for w in warnings if w.warning_type == "orphaned_task")
        assert orphaned_warning.affected_item == "TASK-2"
        
        # Check for invalid reference
        invalid_warning = next(w for w in warnings if w.warning_type == "invalid_requirement_reference")
        assert invalid_warning.affected_item == "TASK-3"
        assert invalid_warning.severity == "error"
    
    def test_design_consistency_check(self):
        """Test design consistency checking."""
        system = ValidationWarningSystem()
        
        requirements = [
            {"id": "REQ-1", "text": "Requirement 1"},
            {"id": "REQ-2", "text": "Requirement 2"}
        ]
        
        design_components = [
            {"id": "COMP-1", "requirement_references": ["REQ-1"]}
        ]
        
        warnings = system.check_design_consistency(requirements, design_components)
        
        # REQ-2 should not be addressed in design
        assert len(warnings) == 1
        assert warnings[0].affected_item == "REQ-2"
        assert warnings[0].warning_type == "missing_design_coverage"
    
    def test_when_shall_validation(self):
        """Test WHEN/SHALL statement validation."""
        system = ValidationWarningSystem()
        
        requirements = [
            {
                "id": "REQ-1",
                "acceptance_criteria": [
                    "WHEN user clicks button THEN system SHALL respond",
                    "Invalid format without proper structure",
                    "IF condition is met THEN system SHALL act"
                ]
            }
        ]
        
        warnings = system.validate_when_shall_statements(requirements)
        
        # Only the middle criterion should generate a warning
        assert len(warnings) == 1
        assert warnings[0].warning_type == "invalid_ears_format"
        assert warnings[0].affected_item == "REQ-1"
    
    def test_when_shall_format_detection(self):
        """Test WHEN/SHALL format detection."""
        system = ValidationWarningSystem()
        
        # Valid formats
        assert system._has_when_shall_format("WHEN user acts THEN system SHALL respond")
        assert system._has_when_shall_format("IF condition THEN system SHALL act")
        assert system._has_when_shall_format("when something happens then it shall work")
        
        # Invalid formats
        assert not system._has_when_shall_format("System should do something")
        assert not system._has_when_shall_format("WHEN something happens")
        assert not system._has_when_shall_format("System SHALL respond")


class TestSafeDocumentGeneration:
    """Test safe document generation utility."""
    
    def test_successful_generation(self):
        """Test successful document generation."""
        def mock_generation():
            return {"content": "generated successfully"}
        
        handler = ErrorHandler()
        result = safe_document_generation(mock_generation, "test", handler)
        
        assert result == {"content": "generated successfully"}
        assert len(handler.errors) == 0
        assert len(handler.warnings) == 0
    
    def test_document_generation_error_handling(self):
        """Test handling of DocumentGenerationError."""
        partial_content = {"partial": "content"}
        
        def mock_generation():
            raise DocumentGenerationError(
                "Generation failed",
                partial_content=partial_content,
                recoverable=True
            )
        
        handler = ErrorHandler()
        result = safe_document_generation(mock_generation, "test", handler)
        
        assert result == partial_content
        assert len(handler.errors) == 1
        assert isinstance(handler.errors[0], DocumentGenerationError)
    
    def test_requirement_parsing_error_handling(self):
        """Test handling of RequirementParsingError."""
        partial_reqs = [{"id": "1", "text": "partial"}]
        
        def mock_generation():
            raise RequirementParsingError(
                "Parsing failed",
                parsed_requirements=partial_reqs
            )
        
        handler = ErrorHandler()
        result = safe_document_generation(mock_generation, "test", handler)
        
        assert result == {"partial_requirements": partial_reqs}
        assert len(handler.errors) == 1
    
    def test_validation_error_as_warning(self):
        """Test handling of validation error as warning."""
        def mock_generation():
            raise RequirementValidationError(
                "Minor validation issue",
                requirement_id="REQ-1",
                severity="warning"
            )
        
        handler = ErrorHandler()
        result = safe_document_generation(mock_generation, "test", handler)
        
        assert result is None
        assert len(handler.errors) == 0
        assert len(handler.warnings) == 1
        assert handler.warnings[0].warning_type == "requirement_validation"
    
    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors."""
        def mock_generation():
            raise ValueError("Unexpected error")
        
        handler = ErrorHandler()
        result = safe_document_generation(mock_generation, "test", handler)
        
        assert result is None
        assert len(handler.errors) == 1
        assert isinstance(handler.errors[0], DocumentGenerationError)
        assert "Unexpected error" in str(handler.errors[0])


class TestCreateFallbackContent:
    """Test fallback content creation."""
    
    def test_requirements_fallback(self):
        """Test requirements fallback content creation."""
        objective = "Create a web app"
        content = create_fallback_content("requirements", objective)
        
        assert "introduction" in content
        assert "requirements" in content
        assert content["fallback"] is True
        assert objective in content["introduction"]
        assert len(content["requirements"]) == 1
        assert content["requirements"][0]["id"] == "1"
    
    def test_design_fallback(self):
        """Test design fallback content creation."""
        objective = "Build API"
        content = create_fallback_content("design", objective)
        
        assert "overview" in content
        assert "architecture" in content
        assert "components" in content
        assert content["fallback"] is True
        assert objective in content["overview"]
        assert len(content["components"]) == 1
    
    def test_tasks_fallback(self):
        """Test tasks fallback content creation."""
        objective = "Implement feature"
        content = create_fallback_content("tasks", objective)
        
        assert "tasks" in content
        assert content["fallback"] is True
        assert len(content["tasks"]) == 1
        assert objective in content["tasks"][0]["description"]
    
    def test_generic_fallback(self):
        """Test generic fallback content creation."""
        objective = "Do something"
        content = create_fallback_content("unknown", objective)
        
        assert "content" in content
        assert content["fallback"] is True
        assert objective in content["content"]


if __name__ == "__main__":
    pytest.main([__file__])