"""
Tests for DocumentationConfiguration system.

This module tests the documentation configuration functionality including
template management, validation, and compatibility checking.
"""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, mock_open

from a3.core.models import (
    DocumentationConfiguration, ValidationError
)


class TestDocumentationConfigurationBasic:
    """Test basic DocumentationConfiguration functionality."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = DocumentationConfiguration()
        
        assert config.enable_requirements is True
        assert config.enable_design is True
        assert config.enable_tasks is True
        assert config.requirement_format == "EARS"
        assert config.template_path is None
        assert config.custom_templates == {}
        assert config.validation_level == "strict"
        assert config.template_variables == {}
        assert config.output_format == "markdown"
        assert config.include_metadata is True
        assert config.compatibility_version == "1.0"
    
    def test_custom_configuration(self):
        """Test configuration with custom values."""
        custom_templates = {"requirements": "# Custom Requirements\n{requirements}"}
        custom_variables = {"project_name": "Test Project"}
        
        config = DocumentationConfiguration(
            enable_requirements=False,
            enable_design=True,
            enable_tasks=False,
            requirement_format="user_stories",
            template_path="/custom/templates",
            custom_templates=custom_templates,
            validation_level="lenient",
            template_variables=custom_variables,
            output_format="json",
            include_metadata=False,
            compatibility_version="2.1"
        )
        
        assert config.enable_requirements is False
        assert config.enable_design is True
        assert config.enable_tasks is False
        assert config.requirement_format == "user_stories"
        assert config.template_path == "/custom/templates"
        assert config.custom_templates == custom_templates
        assert config.validation_level == "lenient"
        assert config.template_variables == custom_variables
        assert config.output_format == "json"
        assert config.include_metadata is False
        assert config.compatibility_version == "2.1"


class TestDocumentationConfigurationValidation:
    """Test validation methods of DocumentationConfiguration."""
    
    def test_validate_success(self):
        """Test successful validation."""
        config = DocumentationConfiguration()
        # Should not raise any exception
        config.validate()
    
    def test_validate_invalid_requirement_format(self):
        """Test validation failure for invalid requirement format."""
        config = DocumentationConfiguration(requirement_format="invalid")
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        
        assert "Invalid requirement format 'invalid'" in str(exc_info.value)
        assert "EARS, user_stories, custom" in str(exc_info.value)
    
    def test_validate_invalid_validation_level(self):
        """Test validation failure for invalid validation level."""
        config = DocumentationConfiguration(validation_level="invalid")
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        
        assert "Invalid validation level 'invalid'" in str(exc_info.value)
        assert "strict, moderate, lenient" in str(exc_info.value)
    
    def test_validate_invalid_output_format(self):
        """Test validation failure for invalid output format."""
        config = DocumentationConfiguration(output_format="invalid")
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        
        assert "Invalid output format 'invalid'" in str(exc_info.value)
        assert "markdown, json, html" in str(exc_info.value)
    
    def test_validate_empty_template_document_type(self):
        """Test validation failure for empty template document type."""
        config = DocumentationConfiguration(custom_templates={"": "template content"})
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        
        assert "Custom template document type cannot be empty" in str(exc_info.value)
    
    def test_validate_empty_template_content(self):
        """Test validation failure for empty template content."""
        config = DocumentationConfiguration(custom_templates={"requirements": ""})
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        
        assert "Custom template for 'requirements' cannot be empty" in str(exc_info.value)
    
    def test_validate_empty_template_path(self):
        """Test validation failure for empty template path."""
        config = DocumentationConfiguration(template_path="")
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        
        assert "Template path cannot be empty string" in str(exc_info.value)
    
    def test_validate_invalid_compatibility_version(self):
        """Test validation failure for invalid compatibility version format."""
        config = DocumentationConfiguration(compatibility_version="invalid")
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        
        assert "Invalid compatibility version format 'invalid'" in str(exc_info.value)
        assert "Must be in format 'X.Y' or 'X.Y.Z'" in str(exc_info.value)
    
    def test_validate_compatibility_version_formats(self):
        """Test various valid compatibility version formats."""
        valid_versions = ["1.0", "2.1", "1.0.0", "10.5.3"]
        
        for version in valid_versions:
            config = DocumentationConfiguration(compatibility_version=version)
            config.validate()  # Should not raise exception


class TestTemplateValidation:
    """Test template syntax validation."""
    
    def test_validate_template_syntax_success(self):
        """Test successful template syntax validation."""
        config = DocumentationConfiguration()
        
        # Valid template with required placeholders
        template = "# Requirements\n{introduction}\n{requirements}"
        config._validate_template_syntax(template, "requirements")
    
    def test_validate_template_missing_required_placeholder(self):
        """Test validation failure for missing required placeholder."""
        config = DocumentationConfiguration()
        
        # Template missing required 'requirements' placeholder
        template = "# Requirements\n{introduction}"
        
        with pytest.raises(ValidationError) as exc_info:
            config._validate_template_syntax(template, "requirements")
        
        assert "missing required placeholder '{requirements}'" in str(exc_info.value)
    
    def test_validate_template_invalid_placeholder_name(self):
        """Test validation failure for invalid placeholder name."""
        config = DocumentationConfiguration()
        
        # Template with invalid placeholder name (contains hyphen)
        template = "# Requirements\n{introduction}\n{requirements}\n{invalid-name}"
        
        with pytest.raises(ValidationError) as exc_info:
            config._validate_template_syntax(template, "requirements")
        
        assert "Invalid placeholder name 'invalid-name'" in str(exc_info.value)
        assert "Must be a valid identifier" in str(exc_info.value)
    
    def test_get_required_placeholders(self):
        """Test getting required placeholders for each document type."""
        config = DocumentationConfiguration()
        
        req_placeholders = config._get_required_placeholders("requirements")
        assert "introduction" in req_placeholders
        assert "requirements" in req_placeholders
        
        design_placeholders = config._get_required_placeholders("design")
        assert "overview" in design_placeholders
        assert "architecture" in design_placeholders
        assert "components" in design_placeholders
        
        tasks_placeholders = config._get_required_placeholders("tasks")
        assert "tasks" in tasks_placeholders
        assert "requirement_coverage" in tasks_placeholders
        
        # Unknown document type should return empty list
        unknown_placeholders = config._get_required_placeholders("unknown")
        assert unknown_placeholders == []


class TestDocumentTypeManagement:
    """Test document type management methods."""
    
    def test_is_document_enabled(self):
        """Test checking if document types are enabled."""
        config = DocumentationConfiguration(
            enable_requirements=True,
            enable_design=False,
            enable_tasks=True
        )
        
        assert config.is_document_enabled("requirements") is True
        assert config.is_document_enabled("design") is False
        assert config.is_document_enabled("tasks") is True
        assert config.is_document_enabled("unknown") is False
    
    def test_get_template_custom(self):
        """Test getting custom template."""
        custom_template = "# Custom Requirements\n{introduction}\n{requirements}"
        config = DocumentationConfiguration(
            custom_templates={"requirements": custom_template}
        )
        
        result = config.get_template("requirements")
        assert result == custom_template
    
    def test_get_template_default(self):
        """Test getting default template."""
        config = DocumentationConfiguration()
        
        # Should return default template for requirements
        result = config.get_template("requirements")
        assert result is not None
        assert "# Requirements Document" in result
        assert "{introduction}" in result
        assert "{requirements}" in result
    
    def test_get_template_unknown_type(self):
        """Test getting template for unknown document type."""
        config = DocumentationConfiguration()
        
        result = config.get_template("unknown")
        assert result is None


class TestDefaultTemplates:
    """Test default template generation."""
    
    def test_get_default_requirements_template_ears(self):
        """Test default requirements template for EARS format."""
        config = DocumentationConfiguration(requirement_format="EARS")
        
        template = config._get_default_requirements_template()
        assert "# Requirements Document" in template
        assert "{introduction}" in template
        assert "{requirements}" in template
    
    def test_get_default_requirements_template_user_stories(self):
        """Test default requirements template for user stories format."""
        config = DocumentationConfiguration(requirement_format="user_stories")
        
        template = config._get_default_requirements_template()
        assert "# Requirements Document" in template
        assert "## User Stories" in template
        assert "{introduction}" in template
        assert "{requirements}" in template
    
    def test_get_default_requirements_template_custom(self):
        """Test default requirements template for custom format."""
        config = DocumentationConfiguration(requirement_format="custom")
        
        template = config._get_default_requirements_template()
        assert "# Requirements Document" in template
        assert "{introduction}" in template
        assert "{requirements}" in template
    
    def test_get_default_design_template(self):
        """Test default design template."""
        config = DocumentationConfiguration()
        
        template = config._get_default_design_template()
        assert "# Design Document" in template
        assert "## Overview" in template
        assert "## Architecture" in template
        assert "## Components and Interfaces" in template
        assert "{overview}" in template
        assert "{architecture}" in template
        assert "{components}" in template
    
    def test_get_default_tasks_template(self):
        """Test default tasks template."""
        config = DocumentationConfiguration()
        
        template = config._get_default_tasks_template()
        assert "# Implementation Plan" in template
        assert "## Requirement Coverage" in template
        assert "## Design Coverage" in template
        assert "{tasks}" in template
        assert "{requirement_coverage}" in template


class TestTemplateLoading:
    """Test template loading from file system."""
    
    def test_load_templates_from_path_success(self):
        """Test successful template loading from path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template files
            req_template = "# Custom Requirements\n{introduction}\n{requirements}"
            design_template = "# Custom Design\n{overview}\n{architecture}\n{components}"
            tasks_template = "# Custom Tasks\n{tasks}\n{requirement_coverage}"
            
            with open(os.path.join(temp_dir, "requirements_template.md"), "w") as f:
                f.write(req_template)
            with open(os.path.join(temp_dir, "design_template.md"), "w") as f:
                f.write(design_template)
            with open(os.path.join(temp_dir, "tasks_template.md"), "w") as f:
                f.write(tasks_template)
            
            config = DocumentationConfiguration()
            config.load_templates_from_path(temp_dir)
            
            assert config.template_path == temp_dir
            assert config.custom_templates["requirements"] == req_template
            assert config.custom_templates["design"] == design_template
            assert config.custom_templates["tasks"] == tasks_template
    
    def test_load_templates_from_path_nonexistent(self):
        """Test loading templates from non-existent path."""
        config = DocumentationConfiguration()
        
        with pytest.raises(ValidationError) as exc_info:
            config.load_templates_from_path("/nonexistent/path")
        
        assert "Template path '/nonexistent/path' does not exist" in str(exc_info.value)
    
    def test_load_templates_from_path_not_directory(self):
        """Test loading templates from path that is not a directory."""
        with tempfile.NamedTemporaryFile() as temp_file:
            config = DocumentationConfiguration()
            
            with pytest.raises(ValidationError) as exc_info:
                config.load_templates_from_path(temp_file.name)
            
            assert f"Template path '{temp_file.name}' is not a directory" in str(exc_info.value)
    
    def test_load_templates_partial_files(self):
        """Test loading templates when only some template files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create only requirements template
            req_template = "# Custom Requirements\n{introduction}\n{requirements}"
            with open(os.path.join(temp_dir, "requirements_template.md"), "w") as f:
                f.write(req_template)
            
            config = DocumentationConfiguration()
            config.load_templates_from_path(temp_dir)
            
            assert config.template_path == temp_dir
            assert config.custom_templates["requirements"] == req_template
            assert "design" not in config.custom_templates
            assert "tasks" not in config.custom_templates
    
    def test_load_templates_io_error(self):
        """Test handling of IO errors during template loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a template file
            template_file = os.path.join(temp_dir, "requirements_template.md")
            with open(template_file, "w") as f:
                f.write("test")
            
            config = DocumentationConfiguration()
            
            # Mock the open function to raise IOError when reading the template file
            with patch("builtins.open", side_effect=IOError("Permission denied")):
                with pytest.raises(ValidationError) as exc_info:
                    config.load_templates_from_path(temp_dir)
                
                assert "Failed to load template file" in str(exc_info.value)
                assert "Permission denied" in str(exc_info.value)


class TestCustomTemplateManagement:
    """Test custom template management methods."""
    
    def test_set_custom_template_success(self):
        """Test successful custom template setting."""
        config = DocumentationConfiguration()
        template = "# Custom Requirements\n{introduction}\n{requirements}"
        
        config.set_custom_template("requirements", template)
        
        assert config.custom_templates["requirements"] == template
    
    def test_set_custom_template_invalid_document_type(self):
        """Test setting custom template with invalid document type."""
        config = DocumentationConfiguration()
        
        with pytest.raises(ValidationError) as exc_info:
            config.set_custom_template("invalid", "template content")
        
        assert "Invalid document type 'invalid'" in str(exc_info.value)
        assert "requirements, design, tasks" in str(exc_info.value)
    
    def test_set_custom_template_empty_content(self):
        """Test setting custom template with empty content."""
        config = DocumentationConfiguration()
        
        with pytest.raises(ValidationError) as exc_info:
            config.set_custom_template("requirements", "")
        
        assert "Template content for 'requirements' cannot be empty" in str(exc_info.value)
    
    def test_set_custom_template_invalid_syntax(self):
        """Test setting custom template with invalid syntax."""
        config = DocumentationConfiguration()
        
        # Template missing required placeholder
        template = "# Requirements\n{introduction}"
        
        with pytest.raises(ValidationError) as exc_info:
            config.set_custom_template("requirements", template)
        
        assert "missing required placeholder '{requirements}'" in str(exc_info.value)
    
    def test_remove_custom_template(self):
        """Test removing custom template."""
        config = DocumentationConfiguration(
            custom_templates={"requirements": "custom template"}
        )
        
        assert "requirements" in config.custom_templates
        
        config.remove_custom_template("requirements")
        
        assert "requirements" not in config.custom_templates
    
    def test_remove_custom_template_nonexistent(self):
        """Test removing non-existent custom template."""
        config = DocumentationConfiguration()
        
        # Should not raise exception
        config.remove_custom_template("requirements")


class TestTemplateVariables:
    """Test template variable management."""
    
    def test_get_template_variables_default(self):
        """Test getting default template variables."""
        config = DocumentationConfiguration()
        
        variables = config.get_template_variables()
        
        assert "project_name" in variables
        assert "version" in variables
        assert "author" in variables
        assert "date" in variables
        assert "timestamp" in variables
        
        assert variables["project_name"] == "Project"
        assert variables["version"] == "1.0"
        assert variables["author"] == "Developer"
    
    def test_get_template_variables_custom(self):
        """Test getting template variables with custom values."""
        custom_vars = {"project_name": "My Project", "custom_var": "custom_value"}
        config = DocumentationConfiguration(template_variables=custom_vars)
        
        variables = config.get_template_variables()
        
        # Custom variables should override defaults
        assert variables["project_name"] == "My Project"
        assert variables["custom_var"] == "custom_value"
        
        # Default variables should still be present
        assert "version" in variables
        assert "author" in variables
    
    def test_set_template_variable_success(self):
        """Test successful template variable setting."""
        config = DocumentationConfiguration()
        
        config.set_template_variable("project_name", "Test Project")
        config.set_template_variable("version", "2.0")
        
        assert config.template_variables["project_name"] == "Test Project"
        assert config.template_variables["version"] == "2.0"
    
    def test_set_template_variable_empty_name(self):
        """Test setting template variable with empty name."""
        config = DocumentationConfiguration()
        
        with pytest.raises(ValidationError) as exc_info:
            config.set_template_variable("", "value")
        
        assert "Template variable name cannot be empty" in str(exc_info.value)
    
    def test_set_template_variable_invalid_name(self):
        """Test setting template variable with invalid name."""
        config = DocumentationConfiguration()
        
        with pytest.raises(ValidationError) as exc_info:
            config.set_template_variable("invalid-name", "value")
        
        assert "Invalid template variable name 'invalid-name'" in str(exc_info.value)
        assert "Must be a valid identifier" in str(exc_info.value)


class TestCompatibilityValidation:
    """Test configuration compatibility validation."""
    
    def test_validate_compatibility_no_existing_config(self):
        """Test compatibility validation with no existing configuration."""
        config = DocumentationConfiguration()
        
        warnings = config.validate_compatibility(None)
        
        assert warnings == []
    
    def test_validate_compatibility_same_config(self):
        """Test compatibility validation with identical configuration."""
        config1 = DocumentationConfiguration()
        config2 = DocumentationConfiguration()
        
        warnings = config1.validate_compatibility(config2)
        
        assert warnings == []
    
    def test_validate_compatibility_major_version_change(self):
        """Test compatibility validation with major version change."""
        config1 = DocumentationConfiguration(compatibility_version="2.0")
        config2 = DocumentationConfiguration(compatibility_version="1.0")
        
        warnings = config1.validate_compatibility(config2)
        
        assert len(warnings) == 1
        assert "Major version change from 1.0 to 2.0" in warnings[0]
    
    def test_validate_compatibility_document_generation_changes(self):
        """Test compatibility validation with document generation changes."""
        config1 = DocumentationConfiguration(
            enable_requirements=False,
            enable_design=True,
            enable_tasks=False
        )
        config2 = DocumentationConfiguration(
            enable_requirements=True,
            enable_design=False,
            enable_tasks=True
        )
        
        warnings = config1.validate_compatibility(config2)
        
        assert len(warnings) == 3
        assert any("Requirements generation changed from True to False" in w for w in warnings)
        assert any("Design generation changed from False to True" in w for w in warnings)
        assert any("Tasks generation changed from True to False" in w for w in warnings)
    
    def test_validate_compatibility_format_changes(self):
        """Test compatibility validation with format changes."""
        config1 = DocumentationConfiguration(
            requirement_format="user_stories",
            output_format="json",
            validation_level="lenient"
        )
        config2 = DocumentationConfiguration(
            requirement_format="EARS",
            output_format="markdown",
            validation_level="strict"
        )
        
        warnings = config1.validate_compatibility(config2)
        
        assert len(warnings) == 3
        assert any("Requirement format changed from 'EARS' to 'user_stories'" in w for w in warnings)
        assert any("Output format changed from 'markdown' to 'json'" in w for w in warnings)
        assert any("Validation level changed from 'strict' to 'lenient'" in w for w in warnings)
    
    def test_is_compatible_with_compatible(self):
        """Test compatibility check with compatible configurations."""
        config1 = DocumentationConfiguration(requirement_format="user_stories")
        config2 = DocumentationConfiguration(requirement_format="EARS")
        
        # Format changes are not breaking
        assert config1.is_compatible_with(config2) is True
    
    def test_is_compatible_with_incompatible_major_version(self):
        """Test compatibility check with incompatible major version."""
        config1 = DocumentationConfiguration(compatibility_version="2.0")
        config2 = DocumentationConfiguration(compatibility_version="1.0")
        
        assert config1.is_compatible_with(config2) is False
    
    def test_is_compatible_with_incompatible_breaking_change(self):
        """Test compatibility check with breaking changes."""
        config1 = DocumentationConfiguration(enable_requirements=False)
        config2 = DocumentationConfiguration(enable_requirements=True)
        
        # Disabling generation is considered breaking
        assert config1.is_compatible_with(config2) is False


class TestConfigurationMerging:
    """Test configuration merging functionality."""
    
    def test_merge_with_basic(self):
        """Test basic configuration merging."""
        config1 = DocumentationConfiguration(
            enable_requirements=False,
            requirement_format="user_stories",
            custom_templates={"requirements": "template1"},
            template_variables={"var1": "value1"}
        )
        
        config2 = DocumentationConfiguration(
            enable_design=False,
            validation_level="lenient",
            custom_templates={"design": "template2"},
            template_variables={"var2": "value2"}
        )
        
        merged = config1.merge_with(config2)
        
        # config1 values should take precedence
        assert merged.enable_requirements is False
        assert merged.requirement_format == "user_stories"
        
        # config2 values should be used where config1 uses defaults, but config1 takes precedence
        assert merged.enable_design is True  # config1 uses default True, so it takes precedence
        assert merged.validation_level == "strict"  # config1 uses default strict, so it takes precedence
        
        # Templates and variables should be merged
        assert merged.custom_templates["requirements"] == "template1"
        assert merged.custom_templates["design"] == "template2"
        assert merged.template_variables["var1"] == "value1"
        assert merged.template_variables["var2"] == "value2"
    
    def test_merge_with_overlapping_templates(self):
        """Test merging with overlapping custom templates."""
        config1 = DocumentationConfiguration(
            custom_templates={"requirements": "template1", "design": "template1_design"}
        )
        
        config2 = DocumentationConfiguration(
            custom_templates={"requirements": "template2", "tasks": "template2_tasks"}
        )
        
        merged = config1.merge_with(config2)
        
        # config1 should take precedence for overlapping keys
        assert merged.custom_templates["requirements"] == "template1"
        assert merged.custom_templates["design"] == "template1_design"
        assert merged.custom_templates["tasks"] == "template2_tasks"
    
    def test_merge_with_template_path_precedence(self):
        """Test template path precedence in merging."""
        config1 = DocumentationConfiguration(template_path="/path1")
        config2 = DocumentationConfiguration(template_path="/path2")
        
        merged = config1.merge_with(config2)
        assert merged.template_path == "/path1"
        
        # Test with None in config1
        config1_none = DocumentationConfiguration(template_path=None)
        merged_none = config1_none.merge_with(config2)
        assert merged_none.template_path == "/path2"


class TestSerialization:
    """Test configuration serialization and deserialization."""
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = DocumentationConfiguration(
            enable_requirements=False,
            requirement_format="user_stories",
            custom_templates={"requirements": "template"},
            template_variables={"var": "value"},
            compatibility_version="1.5"
        )
        
        data = config.to_dict()
        
        assert data["enable_requirements"] is False
        assert data["requirement_format"] == "user_stories"
        assert data["custom_templates"] == {"requirements": "template"}
        assert data["template_variables"] == {"var": "value"}
        assert data["compatibility_version"] == "1.5"
        
        # Check all expected keys are present
        expected_keys = {
            "enable_requirements", "enable_design", "enable_tasks",
            "requirement_format", "template_path", "custom_templates",
            "validation_level", "template_variables", "output_format",
            "include_metadata", "compatibility_version"
        }
        assert set(data.keys()) == expected_keys
    
    def test_from_dict(self):
        """Test creating configuration from dictionary."""
        data = {
            "enable_requirements": False,
            "enable_design": True,
            "enable_tasks": False,
            "requirement_format": "user_stories",
            "template_path": "/templates",
            "custom_templates": {"requirements": "template"},
            "validation_level": "lenient",
            "template_variables": {"var": "value"},
            "output_format": "json",
            "include_metadata": False,
            "compatibility_version": "2.0"
        }
        
        config = DocumentationConfiguration.from_dict(data)
        
        assert config.enable_requirements is False
        assert config.enable_design is True
        assert config.enable_tasks is False
        assert config.requirement_format == "user_stories"
        assert config.template_path == "/templates"
        assert config.custom_templates == {"requirements": "template"}
        assert config.validation_level == "lenient"
        assert config.template_variables == {"var": "value"}
        assert config.output_format == "json"
        assert config.include_metadata is False
        assert config.compatibility_version == "2.0"
    
    def test_serialization_roundtrip(self):
        """Test serialization roundtrip (to_dict -> from_dict)."""
        original = DocumentationConfiguration(
            enable_requirements=False,
            requirement_format="user_stories",
            custom_templates={"requirements": "template", "design": "design_template"},
            template_variables={"project": "Test", "version": "2.0"},
            validation_level="moderate",
            output_format="html",
            compatibility_version="1.2.3"
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = DocumentationConfiguration.from_dict(data)
        
        # Should be identical
        assert restored.enable_requirements == original.enable_requirements
        assert restored.requirement_format == original.requirement_format
        assert restored.custom_templates == original.custom_templates
        assert restored.template_variables == original.template_variables
        assert restored.validation_level == original.validation_level
        assert restored.output_format == original.output_format
        assert restored.compatibility_version == original.compatibility_version


class TestIntegration:
    """Integration tests for DocumentationConfiguration."""
    
    def test_complete_workflow(self):
        """Test complete configuration workflow."""
        # Create initial configuration
        config = DocumentationConfiguration()
        
        # Load templates from path
        with tempfile.TemporaryDirectory() as temp_dir:
            req_template = "# Custom Requirements\n{introduction}\n{requirements}"
            with open(os.path.join(temp_dir, "requirements_template.md"), "w") as f:
                f.write(req_template)
            
            config.load_templates_from_path(temp_dir)
        
        # Set custom template variables
        config.set_template_variable("project_name", "Integration Test")
        config.set_template_variable("version", "1.0.0")
        
        # Modify configuration
        config.requirement_format = "user_stories"
        config.validation_level = "moderate"
        
        # Validate configuration
        config.validate()
        
        # Test template retrieval
        template = config.get_template("requirements")
        assert template == req_template
        
        # Test variable retrieval
        variables = config.get_template_variables()
        assert variables["project_name"] == "Integration Test"
        assert variables["version"] == "1.0.0"
        
        # Test serialization
        data = config.to_dict()
        restored_config = DocumentationConfiguration.from_dict(data)
        
        # Test compatibility
        warnings = restored_config.validate_compatibility(config)
        assert len(warnings) == 0
        
        assert restored_config.is_compatible_with(config)
    
    def test_error_recovery_workflow(self):
        """Test error recovery in configuration workflow."""
        config = DocumentationConfiguration()
        
        # Test invalid template setting with recovery
        try:
            config.set_custom_template("requirements", "invalid template")
        except ValidationError:
            # Recover by setting valid template
            config.set_custom_template("requirements", "# Valid\n{introduction}\n{requirements}")
        
        # Test invalid variable setting with recovery
        try:
            config.set_template_variable("invalid-name", "value")
        except ValidationError:
            # Recover by setting valid variable
            config.set_template_variable("valid_name", "value")
        
        # Configuration should be valid after recovery
        config.validate()
        
        assert config.get_template("requirements") == "# Valid\n{introduction}\n{requirements}"
        assert config.template_variables["valid_name"] == "value"