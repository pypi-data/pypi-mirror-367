"""
Unit tests for ValidationLevel enum and ValidationResult enhancement.

Tests the new ValidationLevel enum and the updated ValidationResult class
with validation_level field support.
"""

from a3.core.models import ValidationLevel, ValidationResult

import pytest




class TestValidationLevel:
    """Test cases for the ValidationLevel enum."""
    
def test_validation_level_enum_values(self):
        """Test that ValidationLevel enum has correct values."""
        assert ValidationLevel.PLANNING.value == "planning"
        assert ValidationLevel.INTEGRATION.value == "integration"
    
def test_validation_level_enum_members(self):
        """Test that ValidationLevel enum has expected members."""
        expected_members = {"PLANNING", "INTEGRATION"}
        actual_members = {member.name for member in ValidationLevel}
        assert actual_members == expected_members
    
def test_validation_level_enum_comparison(self):
        """Test ValidationLevel enum comparison operations."""
        assert ValidationLevel.PLANNING == ValidationLevel.PLANNING
        assert ValidationLevel.INTEGRATION == ValidationLevel.INTEGRATION
        assert ValidationLevel.PLANNING != ValidationLevel.INTEGRATION
    
def test_validation_level_enum_string_representation(self):
        """Test string representation of ValidationLevel enum."""
        assert str(ValidationLevel.PLANNING) == "ValidationLevel.PLANNING"
        assert str(ValidationLevel.INTEGRATION) == "ValidationLevel.INTEGRATION"


class TestValidationResultEnhancement:
    """Test cases for ValidationResult with validation_level field."""
    
def test_validation_result_with_validation_level(self):
        """Test ValidationResult initialization with validation_level."""
        result = ValidationResult(
            is_valid=True,
            validation_level=ValidationLevel.PLANNING
        )
        
        assert result.is_valid is True
        assert result.validation_level == ValidationLevel.PLANNING
        assert result.errors == []
        assert result.warnings == []
        assert result.fixed_imports == []
    
def test_validation_result_without_validation_level(self):
        """Test ValidationResult initialization without validation_level (backward compatibility)."""
        result = ValidationResult(is_valid=False, errors=["test error"])
        
        assert result.is_valid is False
        assert result.validation_level is None
        assert result.errors == ["test error"]
    
def test_validation_result_with_all_fields(self):
        """Test ValidationResult with all fields including validation_level."""
        result = ValidationResult(
            is_valid=False,
            errors=["error1", "error2"],
            warnings=["warning1"],
            fixed_imports=["import1"],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        assert result.is_valid is False
        assert result.errors == ["error1", "error2"]
        assert result.warnings == ["warning1"]
        assert result.fixed_imports == ["import1"]
        assert result.validation_level == ValidationLevel.INTEGRATION
    
def test_validation_result_backward_compatibility_issues(self):
        """Test backward compatibility with 'issues' parameter."""
        result = ValidationResult(
            is_valid=False,
            issues=["issue1", "issue2"],
            validation_level=ValidationLevel.PLANNING
        )
        
        assert result.is_valid is False
        assert result.errors == ["issue1", "issue2"]
        assert result.issues == ["issue1", "issue2"]  # Backward compatibility property
        assert result.validation_level == ValidationLevel.PLANNING
    
def test_validation_result_issues_property_getter(self):
        """Test the issues property getter for backward compatibility."""
        result = ValidationResult(
            is_valid=False,
            errors=["error1", "error2"],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        # Issues property should return the same as errors
        assert result.issues == result.errors
        assert result.issues == ["error1", "error2"]
    
def test_validation_result_issues_property_setter(self):
        """Test the issues property setter for backward compatibility."""
        result = ValidationResult(is_valid=True, validation_level=ValidationLevel.PLANNING)
        
        # Setting issues should update errors
        result.issues = ["new_issue1", "new_issue2"]
        
        assert result.errors == ["new_issue1", "new_issue2"]
        assert result.issues == ["new_issue1", "new_issue2"]
    
def test_validation_result_both_issues_and_errors_raises_error(self):
        """Test that providing both 'issues' and 'errors' raises ValueError."""
        with pytest.raises(ValueError, match="Cannot specify both 'issues' and 'errors' parameters"):
            ValidationResult(
                is_valid=False,
                errors=["error1"],
                issues=["issue1"],
                validation_level=ValidationLevel.PLANNING
            )
    
def test_validation_result_planning_level_example(self):
        """Test ValidationResult with PLANNING validation level example."""
        result = ValidationResult(
            is_valid=False,
            errors=["Circular dependency detected: module_a -> module_b -> module_a"],
            warnings=["Self-dependency found in module_c"],
            validation_level=ValidationLevel.PLANNING
        )
        
        assert result.validation_level == ValidationLevel.PLANNING
        assert not result.is_valid
        assert "Circular dependency" in result.errors[0]
        assert "Self-dependency" in result.warnings[0]
    
def test_validation_result_integration_level_example(self):
        """Test ValidationResult with INTEGRATION validation level example."""
        result = ValidationResult(
            is_valid=False,
            errors=["Module 'missing_module' not found"],
            warnings=["Redundant dependency detected"],
            validation_level=ValidationLevel.INTEGRATION
        )
        
        assert result.validation_level == ValidationLevel.INTEGRATION
        assert not result.is_valid
        assert "not found" in result.errors[0]
        assert "Redundant dependency" in result.warnings[0]
    
def test_validation_result_none_validation_level(self):
        """Test ValidationResult with None validation_level (default)."""
        result = ValidationResult(is_valid=True)
        
        assert result.validation_level is None
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.fixed_imports == []


if __name__ == "__main__":
    pytest.main([__file__])