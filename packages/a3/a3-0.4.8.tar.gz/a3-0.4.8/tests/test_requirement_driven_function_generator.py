"""
Unit tests for RequirementDrivenFunctionGenerator.

This module tests the requirement-driven function generation capabilities
including function specification generation, validation logic creation,
requirement-based comments, and coverage validation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from a3.core.requirement_driven_function_generator import (
    RequirementDrivenFunctionGenerator,
    RequirementDrivenFunctionGeneratorInterface
)
from a3.core.models import (
    RequirementsDocument, Requirement, AcceptanceCriterion, RequirementPriority,
    EnhancedFunctionSpec, FunctionSpec, Argument, Module,
    DocumentGenerationError, RequirementValidationError,
    FunctionSpecValidationError
)


class TestRequirementDrivenFunctionGenerator:
    """Test cases for RequirementDrivenFunctionGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create a RequirementDrivenFunctionGenerator instance."""
        return RequirementDrivenFunctionGenerator()
    
    @pytest.fixture
    def sample_requirements_document(self):
        """Create a sample requirements document for testing."""
        acceptance_criteria_1 = [
            AcceptanceCriterion(
                id="ac_1_1",
                when_clause="WHEN user provides valid input data",
                shall_clause="system SHALL validate and process the data",
                requirement_id="req_1"
            ),
            AcceptanceCriterion(
                id="ac_1_2", 
                when_clause="WHEN input data is invalid",
                shall_clause="system SHALL return appropriate error message",
                requirement_id="req_1"
            )
        ]
        
        acceptance_criteria_2 = [
            AcceptanceCriterion(
                id="ac_2_1",
                when_clause="WHEN user requests data retrieval",
                shall_clause="system SHALL return requested data within 2 seconds",
                requirement_id="req_2"
            )
        ]
        
        requirements = [
            Requirement(
                id="req_1",
                user_story="As a user, I want to input data for processing, so that I can get validated results",
                acceptance_criteria=acceptance_criteria_1,
                priority=RequirementPriority.HIGH,
                category="data_processing"
            ),
            Requirement(
                id="req_2", 
                user_story="As a user, I want to retrieve data quickly, so that I can maintain productivity",
                acceptance_criteria=acceptance_criteria_2,
                priority=RequirementPriority.MEDIUM,
                category="data_retrieval"
            )
        ]
        
        return RequirementsDocument(
            introduction="Sample requirements for testing requirement-driven function generation",
            requirements=requirements,
            created_at=datetime.now(),
            version="1.0"
        )
    
    @pytest.fixture
    def sample_modules(self):
        """Create sample modules for testing."""
        functions = [
            FunctionSpec(
                name="process_data",
                module="data_processor",
                docstring="Process input data and return validated results",
                arguments=[
                    Argument(name="data", type_hint="Dict[str, Any]", description="Input data to process"),
                    Argument(name="validate", type_hint="bool", default_value="True", description="Whether to validate data")
                ],
                return_type="Dict[str, Any]"
            ),
            FunctionSpec(
                name="retrieve_data",
                module="data_retriever", 
                docstring="Retrieve data from storage",
                arguments=[
                    Argument(name="query", type_hint="str", description="Query string for data retrieval"),
                    Argument(name="timeout", type_hint="int", default_value="30", description="Timeout in seconds")
                ],
                return_type="List[Dict[str, Any]]"
            )
        ]
        
        modules = [
            Module(
                name="data_processor",
                description="Module for processing data",
                file_path="data_processor.py",
                functions=[functions[0]]
            ),
            Module(
                name="data_retriever",
                description="Module for retrieving data", 
                file_path="data_retriever.py",
                functions=[functions[1]]
            )
        ]
        
        return modules
    
    def test_interface_compliance(self, generator):
        """Test that the generator implements the required interface."""
        assert isinstance(generator, RequirementDrivenFunctionGeneratorInterface)
        
        # Check that all required methods are implemented
        assert hasattr(generator, 'generate_function_specifications')
        assert hasattr(generator, 'generate_validation_logic')
        assert hasattr(generator, 'generate_requirement_comments')
        assert hasattr(generator, 'validate_requirement_coverage')
    
    def test_generate_function_specifications_success(self, generator, sample_requirements_document, sample_modules):
        """Test successful generation of function specifications with requirement references."""
        enhanced_functions = generator.generate_function_specifications(sample_requirements_document, sample_modules)
        
        # Verify we get enhanced function specifications
        assert len(enhanced_functions) == 2
        assert all(isinstance(func, EnhancedFunctionSpec) for func in enhanced_functions)
        
        # Verify requirement references are added
        for func in enhanced_functions:
            assert len(func.requirement_references) > 0
            assert len(func.acceptance_criteria_implementations) >= 0
            
        # Verify specific function mappings
        process_func = next((f for f in enhanced_functions if f.name == "process_data"), None)
        assert process_func is not None
        assert len(process_func.requirement_references) > 0
        
        retrieve_func = next((f for f in enhanced_functions if f.name == "retrieve_data"), None)
        assert retrieve_func is not None
        assert len(retrieve_func.requirement_references) > 0
    
    def test_generate_function_specifications_empty_modules(self, generator, sample_requirements_document):
        """Test function specification generation with empty modules list."""
        enhanced_functions = generator.generate_function_specifications(sample_requirements_document, [])
        assert enhanced_functions == []
    
    def test_generate_validation_logic_success(self, generator):
        """Test successful generation of validation logic from acceptance criteria."""
        acceptance_criteria = [
            AcceptanceCriterion(
                id="ac_test_1",
                when_clause="WHEN user provides input data",
                shall_clause="system SHALL validate the data format",
                requirement_id="req_test"
            ),
            AcceptanceCriterion(
                id="ac_test_2",
                when_clause="WHEN data validation fails", 
                shall_clause="system SHALL return error message",
                requirement_id="req_test"
            )
        ]
        
        validation_logic = generator.generate_validation_logic(acceptance_criteria)
        
        # Verify validation logic is generated
        assert isinstance(validation_logic, str)
        assert len(validation_logic) > 0
        assert "Generated validation logic from requirements" in validation_logic
        assert "ac_test_1" in validation_logic
        assert "ac_test_2" in validation_logic
    
    def test_generate_validation_logic_empty_criteria(self, generator):
        """Test validation logic generation with empty acceptance criteria."""
        validation_logic = generator.generate_validation_logic([])
        assert validation_logic == ""
    
    def test_generate_requirement_comments_success(self, generator, sample_requirements_document):
        """Test successful generation of requirement-based comments."""
        requirement_references = ["req_1", "req_2"]
        
        comments = generator.generate_requirement_comments(requirement_references, sample_requirements_document)
        
        # Verify comments are generated
        assert isinstance(comments, str)
        assert len(comments) > 0
        assert "Requirements Traceability:" in comments
        assert "req_1" in comments
        assert "req_2" in comments
        assert "As a user" in comments  # Part of user stories
    
    def test_generate_requirement_comments_empty_references(self, generator, sample_requirements_document):
        """Test requirement comments generation with empty references."""
        comments = generator.generate_requirement_comments([], sample_requirements_document)
        assert comments == ""
    
    def test_validate_requirement_coverage_success(self, generator, sample_requirements_document):
        """Test successful requirement coverage validation."""
        enhanced_functions = [
            EnhancedFunctionSpec(
                name="test_func_1",
                module="test_module",
                docstring="Test function 1",
                requirement_references=["req_1"],
                acceptance_criteria_implementations=["ac_1_1", "ac_1_2"]
            ),
            EnhancedFunctionSpec(
                name="test_func_2", 
                module="test_module",
                docstring="Test function 2",
                requirement_references=["req_2"],
                acceptance_criteria_implementations=["ac_2_1"]
            )
        ]
        
        coverage_result = generator.validate_requirement_coverage(enhanced_functions, sample_requirements_document)
        
        # Verify coverage analysis results
        assert isinstance(coverage_result, dict)
        assert "covered_requirements" in coverage_result
        assert "uncovered_requirements" in coverage_result
        assert "function_coverage" in coverage_result
        assert "coverage_percentage" in coverage_result
        assert "gaps" in coverage_result
        
        # Verify coverage metrics
        assert len(coverage_result["covered_requirements"]) == 2
        assert len(coverage_result["uncovered_requirements"]) == 0
        assert coverage_result["coverage_percentage"] == 100.0
        assert len(coverage_result["gaps"]) == 0
    
    def test_validate_requirement_coverage_partial_coverage(self, generator, sample_requirements_document):
        """Test requirement coverage validation with partial coverage."""
        enhanced_functions = [
            EnhancedFunctionSpec(
                name="test_func_1",
                module="test_module", 
                docstring="Test function 1",
                requirement_references=["req_1"],  # Only covers req_1, not req_2
                acceptance_criteria_implementations=["ac_1_1"]
            )
        ]
        
        coverage_result = generator.validate_requirement_coverage(enhanced_functions, sample_requirements_document)
        
        # Verify partial coverage
        assert len(coverage_result["covered_requirements"]) == 1
        assert len(coverage_result["uncovered_requirements"]) == 1
        assert coverage_result["coverage_percentage"] == 50.0
        assert len(coverage_result["gaps"]) == 1
        assert coverage_result["gaps"][0]["requirement_id"] == "req_2"
    
    def test_validate_requirement_coverage_no_functions(self, generator, sample_requirements_document):
        """Test requirement coverage validation with no functions."""
        coverage_result = generator.validate_requirement_coverage([], sample_requirements_document)
        
        # Verify no coverage
        assert len(coverage_result["covered_requirements"]) == 0
        assert len(coverage_result["uncovered_requirements"]) == 2
        assert coverage_result["coverage_percentage"] == 0.0
        assert len(coverage_result["gaps"]) == 2
    
    def test_private_method_extract_keywords(self, generator):
        """Test the private method for extracting keywords from text."""
        text = "This is a test function for data processing and validation"
        keywords = generator._extract_keywords(text)
        
        # Verify keyword extraction
        assert isinstance(keywords, set)
        assert "test" in keywords
        assert "function" in keywords
        assert "data" in keywords
        assert "processing" in keywords
        assert "validation" in keywords
        
        # Verify common words are excluded
        assert "this" not in keywords
        assert "is" not in keywords
        assert "a" not in keywords
    
    def test_initialization(self, generator):
        """Test proper initialization of the generator."""
        assert hasattr(generator, 'validation_templates')
        assert hasattr(generator, 'comment_templates')
        assert isinstance(generator.validation_templates, dict)
        assert isinstance(generator.comment_templates, dict)
        
        # Verify templates are populated
        assert len(generator.validation_templates) > 0
        assert len(generator.comment_templates) > 0