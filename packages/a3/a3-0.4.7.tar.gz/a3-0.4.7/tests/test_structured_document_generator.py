"""
Tests for StructuredDocumentGenerator component.

This module tests the structured document generation functionality including
requirements, design, and tasks document generation with proper traceability.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from a3.core.structured_document_generator import (
    StructuredDocumentGeneratorInterface, StructuredDocumentGenerator
)
from a3.core.models import (
    RequirementsDocument, Requirement, AcceptanceCriterion, RequirementPriority,
    DesignDocument, DesignComponent, TasksDocument, ImplementationTask,
    Module, FunctionSpec, Argument, DocumentationConfiguration,
    DocumentGenerationError, RequirementParsingError
)
from a3.core.requirement_parser import RequirementParser, RequirementParsingContext


class TestStructuredDocumentGeneratorInterface:
    """Test the abstract interface for structured document generation."""
    
    def test_interface_is_abstract(self):
        """Test that the interface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StructuredDocumentGeneratorInterface()
    
    def test_interface_methods_are_abstract(self):
        """Test that all interface methods are abstract."""
        # Create a concrete class that doesn't implement all methods
        class IncompleteGenerator(StructuredDocumentGeneratorInterface):
            def generate_requirements_document(self, objective, context):
                pass
        
        with pytest.raises(TypeError):
            IncompleteGenerator()


# Shared fixtures
@pytest.fixture
def mock_requirement_parser():
    """Create a mock requirement parser."""
    parser = Mock(spec=RequirementParser)
    return parser

@pytest.fixture
def generator(mock_requirement_parser):
    """Create a StructuredDocumentGenerator instance."""
    return StructuredDocumentGenerator(requirement_parser=mock_requirement_parser)

@pytest.fixture
def sample_requirements_document():
        """Create a sample requirements document for testing."""
        req1 = Requirement(
            id="REQ-1",
            user_story="As a developer, I want to parse requirements, so that I can generate structured documentation",
            acceptance_criteria=[
                AcceptanceCriterion(
                    id="AC-1.1",
                    when_clause="WHEN an objective is provided",
                    shall_clause="the system SHALL parse it into structured requirements",
                    requirement_id="REQ-1"
                )
            ],
            priority=RequirementPriority.HIGH,
            category="parsing"
        )
        
        req2 = Requirement(
            id="REQ-2",
            user_story="As a developer, I want to generate design documents, so that I can trace requirements to implementation",
            acceptance_criteria=[
                AcceptanceCriterion(
                    id="AC-2.1",
                    when_clause="WHEN requirements are available",
                    shall_clause="the system SHALL generate a design document with traceability",
                    requirement_id="REQ-2"
                )
            ],
            priority=RequirementPriority.MEDIUM,
            category="design"
        )
        
        return RequirementsDocument(
            introduction="This document specifies requirements for structured documentation generation.",
            requirements=[req1, req2],
            created_at=datetime.now(),
            version="1.0"
        )
    
@pytest.fixture
def sample_modules():
        """Create sample modules for testing."""
        func1 = FunctionSpec(
            name="parse_requirements",
            module="parser",
            docstring="Parse requirements from objective text",
            arguments=[
                Argument(name="objective", type_hint="str", description="The objective to parse")
            ],
            return_type="RequirementsDocument"
        )
        
        func2 = FunctionSpec(
            name="generate_design",
            module="generator",
            docstring="Generate design document from requirements",
            arguments=[
                Argument(name="requirements", type_hint="RequirementsDocument", description="Requirements to base design on")
            ],
            return_type="DesignDocument"
        )
        
        module1 = Module(
            name="parser",
            description="Module for parsing requirements",
            file_path="src/parser.py",
            functions=[func1]
        )
        
        module2 = Module(
            name="generator",
            description="Module for generating design documents",
            file_path="src/generator.py",
            dependencies=["parser"],
            functions=[func2]
        )
        
        return [module1, module2]
    
@pytest.fixture
def sample_design_document(sample_requirements_document):
        """Create a sample design document for testing."""
        component1 = DesignComponent(
            id="comp_parser",
            name="parser",
            description="Module for parsing requirements",
            responsibilities=["Parse requirements from text"],
            interfaces=["parse_requirements(objective: str) -> RequirementsDocument"],
            requirement_mappings=["REQ-1"]
        )
        
        component2 = DesignComponent(
            id="comp_generator",
            name="generator",
            description="Module for generating design documents",
            responsibilities=["Generate design documents"],
            interfaces=["generate_design(requirements: RequirementsDocument) -> DesignDocument"],
            requirement_mappings=["REQ-2"]
        )
        
        return DesignDocument(
            overview="Design overview for structured documentation system",
            architecture="Modular architecture with parser and generator components",
            components=[component1, component2],
            requirement_mappings={
                "REQ-1": ["comp_parser"],
                "REQ-2": ["comp_generator"]
            },
            created_at=datetime.now()
        )


class TestStructuredDocumentGenerator:
    """Test the concrete implementation of structured document generator."""


class TestGenerateRequirementsDocument:
    """Test requirements document generation."""
    
    def test_generate_requirements_document_success(self, generator):
        """Test successful requirements document generation."""
        objective = "Create a system that can parse text and generate structured documentation"
        context = {
            'existing_modules': [],
            'project_type': 'library',
            'constraints': [],
            'stakeholders': ['developer']
        }
        
        # Mock the requirement parser to return a valid document
        with patch.object(generator.requirement_parser, 'parse_objective') as mock_parse:
            mock_requirements = RequirementsDocument(
                introduction="Test introduction",
                requirements=[
                    Requirement(
                        id="REQ-1",
                        user_story="As a user, I want functionality, so that I can achieve goals",
                        acceptance_criteria=[
                            AcceptanceCriterion(
                                id="AC-1.1",
                                when_clause="WHEN condition occurs",
                                shall_clause="the system SHALL respond appropriately",
                                requirement_id="REQ-1"
                            )
                        ],
                        priority=RequirementPriority.HIGH,
                        category="core"
                    )
                ],
                created_at=datetime.now(),
                version="1.0"
            )
            mock_parse.return_value = mock_requirements
            
            result = generator.generate_requirements_document(objective, context)
            
            assert isinstance(result, RequirementsDocument)
            assert result.introduction == "Test introduction"
            assert len(result.requirements) == 1
            assert result.requirements[0].id == "REQ-1"
            
            # Verify the parser was called with correct context
            mock_parse.assert_called_once()
            call_args = mock_parse.call_args[0][0]
            assert isinstance(call_args, RequirementParsingContext)
            assert call_args.objective == objective
    
    def test_generate_requirements_document_parsing_error(self, generator):
        """Test handling of requirement parsing errors."""
        objective = "Invalid objective"
        context = {}
        
        with patch.object(generator.requirement_parser, 'parse_objective') as mock_parse:
            mock_parse.side_effect = RequirementParsingError("Parsing failed")
            
            with pytest.raises(DocumentGenerationError) as exc_info:
                generator.generate_requirements_document(objective, context)
            
            assert "Failed to parse requirements" in str(exc_info.value)
    
    def test_generate_requirements_document_validation_error(self, generator):
        """Test handling of validation errors."""
        objective = "Test objective"
        context = {}
        
        with patch.object(generator.requirement_parser, 'parse_objective') as mock_parse:
            # Return invalid requirements document (empty introduction)
            invalid_doc = RequirementsDocument(
                introduction="",  # Invalid - empty introduction
                requirements=[],
                created_at=datetime.now(),
                version="1.0"
            )
            mock_parse.return_value = invalid_doc
            
            with pytest.raises(DocumentGenerationError) as exc_info:
                generator.generate_requirements_document(objective, context)
            
            assert "must have a non-empty introduction" in str(exc_info.value)


class TestGenerateDesignDocument:
    """Test design document generation."""
    
    def test_generate_design_document_success(self, generator, sample_requirements_document, sample_modules):
        """Test successful design document generation."""
        result = generator.generate_design_document(sample_requirements_document, sample_modules)
        
        assert isinstance(result, DesignDocument)
        assert result.overview
        assert result.architecture
        assert len(result.components) >= len(sample_modules)
        assert result.requirement_mappings
        
        # Check that all requirements are mapped
        req_ids = {req.id for req in sample_requirements_document.requirements}
        mapped_req_ids = set(result.requirement_mappings.keys())
        assert req_ids.issubset(mapped_req_ids)
    
    def test_generate_design_document_empty_modules(self, generator, sample_requirements_document):
        """Test design document generation with empty modules list."""
        result = generator.generate_design_document(sample_requirements_document, [])
        
        assert isinstance(result, DesignDocument)
        assert result.overview
        assert result.architecture
        assert len(result.components) == 0
    
    def test_generate_design_document_validation_error(self, generator, sample_requirements_document, sample_modules):
        """Test validation error handling in design document generation."""
        # Mock the overview generation to return empty string
        with patch.object(generator, '_generate_design_overview', return_value=""):
            with pytest.raises(DocumentGenerationError) as exc_info:
                generator.generate_design_document(sample_requirements_document, sample_modules)
            
            assert "must have a non-empty overview" in str(exc_info.value)


class TestGenerateTasksDocument:
    """Test tasks document generation."""
    
    def test_generate_tasks_document_success(self, generator, sample_requirements_document, sample_design_document):
        """Test successful tasks document generation."""
        result = generator.generate_tasks_document(sample_requirements_document, sample_design_document)
        
        assert isinstance(result, TasksDocument)
        assert len(result.tasks) > 0
        assert result.requirement_coverage
        assert result.design_coverage
        
        # Check requirement coverage
        req_ids = {req.id for req in sample_requirements_document.requirements}
        covered_req_ids = set(result.requirement_coverage.keys())
        assert req_ids == covered_req_ids
        
        # Check design coverage
        component_ids = {comp.id for comp in sample_design_document.components}
        covered_component_ids = set(result.design_coverage.keys())
        assert component_ids == covered_component_ids
    
    def test_generate_tasks_document_validation_error(self, generator, sample_requirements_document, sample_design_document):
        """Test validation error handling in tasks document generation."""
        # Mock task generation to return empty list
        with patch.object(generator, '_generate_implementation_tasks', return_value=[]):
            with pytest.raises(DocumentGenerationError) as exc_info:
                generator.generate_tasks_document(sample_requirements_document, sample_design_document)
            
            assert "must have at least one task" in str(exc_info.value)


class TestHelperMethods:
    """Test helper methods of StructuredDocumentGenerator."""
    
    def test_extract_keywords(self, generator):
        """Test keyword extraction from text."""
        text = "This is a test function that processes data and generates reports"
        keywords = generator._extract_keywords(text)
        
        assert "test" in keywords
        assert "function" in keywords
        assert "processes" in keywords
        assert "data" in keywords
        assert "generates" in keywords
        assert "reports" in keywords
        
        # Common words should be filtered out
        assert "this" not in keywords
        assert "and" not in keywords
        assert "that" not in keywords
    
    def test_is_major_function(self, generator):
        """Test major function detection."""
        # Simple function - not major
        simple_func = FunctionSpec(
            name="simple",
            module="test",
            docstring="Simple function",
            arguments=[Argument(name="x", type_hint="int")],
            return_type="str"
        )
        assert not generator._is_major_function(simple_func)
        
        # Complex function with many arguments - major
        complex_func = FunctionSpec(
            name="complex",
            module="test",
            docstring="Complex function",
            arguments=[
                Argument(name="a", type_hint="int"),
                Argument(name="b", type_hint="str"),
                Argument(name="c", type_hint="bool"),
                Argument(name="d", type_hint="float")
            ],
            return_type="dict"
        )
        assert generator._is_major_function(complex_func)
        
        # Function with long docstring - major
        long_docstring_func = FunctionSpec(
            name="documented",
            module="test",
            docstring="This is a very long docstring that describes the function in great detail and explains all the nuances of its implementation and usage patterns",
            arguments=[],
            return_type="None"
        )
        assert generator._is_major_function(long_docstring_func)
    
    def test_create_function_interface(self, generator):
        """Test function interface creation."""
        func = FunctionSpec(
            name="test_func",
            module="test",
            docstring="Test function",
            arguments=[
                Argument(name="param1", type_hint="str"),
                Argument(name="param2", type_hint="int", default_value="0")
            ],
            return_type="bool"
        )
        
        interface = generator._create_function_interface(func)
        expected = "test_func(param1: str, param2: int) -> bool"
        assert interface == expected


class TestValidationMethods:
    """Test validation methods of StructuredDocumentGenerator."""
    
    def test_validate_requirements_document_success(self, generator):
        """Test successful requirements document validation."""
        valid_doc = RequirementsDocument(
            introduction="Valid introduction",
            requirements=[
                Requirement(
                    id="REQ-1",
                    user_story="Valid user story",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            id="AC-1.1",
                            when_clause="WHEN something happens",
                            shall_clause="the system SHALL respond",
                            requirement_id="REQ-1"
                        )
                    ],
                    priority=RequirementPriority.HIGH,
                    category="test"
                )
            ],
            created_at=datetime.now(),
            version="1.0"
        )
        
        # Should not raise any exception
        generator._validate_requirements_document(valid_doc)
    
    def test_validate_requirements_document_empty_introduction(self, generator):
        """Test validation failure for empty introduction."""
        invalid_doc = RequirementsDocument(
            introduction="",
            requirements=[],
            created_at=datetime.now(),
            version="1.0"
        )
        
        with pytest.raises(DocumentGenerationError) as exc_info:
            generator._validate_requirements_document(invalid_doc)
        
        assert "must have a non-empty introduction" in str(exc_info.value)
    
    def test_validate_requirements_document_no_requirements(self, generator):
        """Test validation failure for no requirements."""
        invalid_doc = RequirementsDocument(
            introduction="Valid introduction",
            requirements=[],
            created_at=datetime.now(),
            version="1.0"
        )
        
        with pytest.raises(DocumentGenerationError) as exc_info:
            generator._validate_requirements_document(invalid_doc)
        
        assert "must have at least one requirement" in str(exc_info.value)
    
    def test_validate_requirements_document_missing_acceptance_criteria(self, generator):
        """Test validation failure for missing acceptance criteria."""
        invalid_doc = RequirementsDocument(
            introduction="Valid introduction",
            requirements=[
                Requirement(
                    id="REQ-1",
                    user_story="Valid user story",
                    acceptance_criteria=[],  # Empty acceptance criteria
                    priority=RequirementPriority.HIGH,
                    category="test"
                )
            ],
            created_at=datetime.now(),
            version="1.0"
        )
        
        with pytest.raises(DocumentGenerationError) as exc_info:
            generator._validate_requirements_document(invalid_doc)
        
        assert "must have acceptance criteria" in str(exc_info.value)


class TestIntegration:
    """Integration tests for the complete document generation workflow."""
    
    def test_complete_workflow(self):
        """Test the complete workflow from objective to all documents."""
        mock_parser = Mock(spec=RequirementParser)
        generator = StructuredDocumentGenerator(requirement_parser=mock_parser)
        
        objective = "Create a system for managing user authentication and authorization"
        context = {
            'existing_modules': [],
            'project_type': 'web_application',
            'constraints': ['security', 'scalability'],
            'stakeholders': ['developer', 'end_user', 'admin']
        }
        
        # Mock the requirement parser for predictable results
        with patch.object(mock_parser, 'parse_objective') as mock_parse:
            mock_requirements = RequirementsDocument(
                introduction="Authentication and authorization system requirements",
                requirements=[
                    Requirement(
                        id="REQ-1",
                        user_story="As a user, I want to authenticate, so that I can access the system",
                        acceptance_criteria=[
                            AcceptanceCriterion(
                                id="AC-1.1",
                                when_clause="WHEN a user provides valid credentials",
                                shall_clause="the system SHALL authenticate the user",
                                requirement_id="REQ-1"
                            )
                        ],
                        priority=RequirementPriority.HIGH,
                        category="authentication"
                    ),
                    Requirement(
                        id="REQ-2",
                        user_story="As an admin, I want to manage user permissions, so that I can control access",
                        acceptance_criteria=[
                            AcceptanceCriterion(
                                id="AC-2.1",
                                when_clause="WHEN an admin modifies permissions",
                                shall_clause="the system SHALL update user access rights",
                                requirement_id="REQ-2"
                            )
                        ],
                        priority=RequirementPriority.MEDIUM,
                        category="authorization"
                    )
                ],
                created_at=datetime.now(),
                version="1.0"
            )
            mock_parse.return_value = mock_requirements
            
            # Generate requirements document
            requirements_doc = generator.generate_requirements_document(objective, context)
            assert isinstance(requirements_doc, RequirementsDocument)
            assert len(requirements_doc.requirements) == 2
            
            # Create sample modules for design generation
            modules = [
                Module(
                    name="auth",
                    description="Authentication module",
                    file_path="src/auth.py",
                    functions=[
                        FunctionSpec(
                            name="authenticate_user",
                            module="auth",
                            docstring="Authenticate user credentials",
                            arguments=[
                                Argument(name="username", type_hint="str"),
                                Argument(name="password", type_hint="str")
                            ],
                            return_type="bool"
                        )
                    ]
                ),
                Module(
                    name="permissions",
                    description="Permission management module",
                    file_path="src/permissions.py",
                    dependencies=["auth"],
                    functions=[
                        FunctionSpec(
                            name="update_permissions",
                            module="permissions",
                            docstring="Update user permissions",
                            arguments=[
                                Argument(name="user_id", type_hint="str"),
                                Argument(name="permissions", type_hint="List[str]")
                            ],
                            return_type="None"
                        )
                    ]
                )
            ]
            
            # Generate design document
            design_doc = generator.generate_design_document(requirements_doc, modules)
            assert isinstance(design_doc, DesignDocument)
            assert len(design_doc.components) >= len(modules)
            assert all(req_id in design_doc.requirement_mappings for req_id in ["REQ-1", "REQ-2"])
            
            # Generate tasks document
            tasks_doc = generator.generate_tasks_document(requirements_doc, design_doc)
            assert isinstance(tasks_doc, TasksDocument)
            assert len(tasks_doc.tasks) > 0
            assert all(req_id in tasks_doc.requirement_coverage for req_id in ["REQ-1", "REQ-2"])
            assert all(comp.id in tasks_doc.design_coverage for comp in design_doc.components)
            
            # Verify traceability
            for req in requirements_doc.requirements:
                # Each requirement should be mapped in design
                assert req.id in design_doc.requirement_mappings
                assert len(design_doc.requirement_mappings[req.id]) > 0
                
                # Each requirement should be covered by tasks
                assert req.id in tasks_doc.requirement_coverage
                assert len(tasks_doc.requirement_coverage[req.id]) > 0