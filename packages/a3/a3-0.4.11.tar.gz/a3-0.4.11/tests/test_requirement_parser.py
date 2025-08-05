"""
Unit tests for the RequirementParser component.

Tests cover objective parsing, WHEN/SHALL statement conversion,
user story generation, and requirement validation.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from a3.core.requirement_parser import RequirementParser, RequirementParsingContext
from a3.core.models import (
    RequirementsDocument, Requirement, AcceptanceCriterion, RequirementPriority,
    RequirementParsingError, RequirementValidationError
)
from a3.core.interfaces import AIClientInterface


class TestRequirementParser:
    """Test cases for RequirementParser class."""
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client for testing."""
        mock_client = Mock(spec=AIClientInterface)
        return mock_client
    
    @pytest.fixture
    def parser(self, mock_ai_client):
        """Create a RequirementParser instance for testing."""
        return RequirementParser(mock_ai_client)
    
    @pytest.fixture
    def simple_context(self):
        """Create a simple parsing context for testing."""
        return RequirementParsingContext(
            objective="Create a user authentication system that allows users to login and logout securely."
        )
    
    @pytest.fixture
    def complex_context(self):
        """Create a complex parsing context for testing."""
        return RequirementParsingContext(
            objective="Build a task management system that enables users to create, edit, and delete tasks. The system must support user authentication, task categorization, and deadline notifications. When a task is overdue, the system should send email alerts.",
            domain="Task Management",
            stakeholders=["end user", "administrator"],
            constraints=["Must be web-based", "Must support mobile devices"]
        )
    
    def test_init(self, mock_ai_client):
        """Test RequirementParser initialization."""
        parser = RequirementParser(mock_ai_client)
        
        assert parser.ai_client == mock_ai_client
        assert isinstance(parser._functional_keywords, list)
        assert isinstance(parser._condition_keywords, list)
        assert "should" in parser._functional_keywords
        assert "when" in parser._condition_keywords
    
    def test_parse_objective_simple(self, parser, mock_ai_client, simple_context):
        """Test parsing a simple objective."""
        # Mock AI response
        mock_ai_client.generate_with_retry.return_value = """
        1. User Authentication
           Description: Allow users to login with credentials
           Stakeholder: end user
           Benefit: access the system securely
           Priority: HIGH
           Category: Security
        
        2. User Logout
           Description: Allow users to logout from the system
           Stakeholder: end user
           Benefit: secure session termination
           Priority: HIGH
           Category: Security
        """
        
        result = parser.parse_objective(simple_context)
        
        assert isinstance(result, RequirementsDocument)
        assert len(result.requirements) == 2
        assert result.introduction
        assert "authentication system" in result.introduction.lower()
        
        # Check first requirement
        req1 = result.requirements[0]
        assert req1.id == "REQ-001"
        assert "As a end user" in req1.user_story
        assert "login" in req1.user_story.lower()
        assert len(req1.acceptance_criteria) >= 1
        assert req1.priority == RequirementPriority.HIGH
        assert req1.category == "Security"
    
    def test_parse_objective_with_ai_failure(self, parser, mock_ai_client, simple_context):
        """Test parsing when AI client fails, falling back to rule-based extraction."""
        # Mock AI failure
        mock_ai_client.generate_with_retry.side_effect = Exception("AI service unavailable")
        
        result = parser.parse_objective(simple_context)
        
        assert isinstance(result, RequirementsDocument)
        assert len(result.requirements) >= 1
        assert result.introduction
        
        # Should still create valid requirements using rule-based approach
        req = result.requirements[0]
        assert req.id
        assert req.user_story
        assert len(req.acceptance_criteria) >= 1
    
    def test_extract_functional_requirements_ai_success(self, parser, mock_ai_client):
        """Test AI-based functional requirement extraction."""
        objective = "Create a user management system with login and registration features."
        
        mock_ai_client.generate_with_retry.return_value = """
        1. User Login Functionality
           Description: Enable users to authenticate with username and password
           Stakeholder: end user
           Benefit: secure access to the system
           Priority: HIGH
           Category: Authentication
        
        2. User Registration
           Description: Allow new users to create accounts
           Stakeholder: new user
           Benefit: join the system
           Priority: HIGH
           Category: User Management
        """
        
        requirements = parser._extract_functional_requirements(objective)
        
        assert len(requirements) == 2
        assert requirements[0]['description'] == "Enable users to authenticate with username and password"
        assert requirements[0]['stakeholder'] == "end user"
        assert requirements[0]['priority'] == "HIGH"
        assert requirements[1]['category'] == "User Management"
    
    def test_extract_functional_requirements_rule_based(self, parser, mock_ai_client):
        """Test rule-based functional requirement extraction."""
        objective = "The system should allow users to create tasks and must send notifications when tasks are due."
        
        # Mock AI failure to trigger rule-based extraction
        mock_ai_client.generate_with_retry.side_effect = Exception("AI unavailable")
        
        requirements = parser._extract_functional_requirements(objective)
        
        assert len(requirements) >= 1
        # Should extract requirements based on functional keywords
        descriptions = [req['description'] for req in requirements]
        assert any('create tasks' in desc.lower() for desc in descriptions)
    
    def test_generate_user_story(self, parser):
        """Test user story generation."""
        stakeholder = "administrator"
        description = "manage user accounts"
        benefit = "maintain system security"
        
        user_story = parser._generate_user_story(stakeholder, description, benefit)
        
        assert user_story.startswith("As a administrator")
        assert "manage user accounts" in user_story
        assert "so that maintain system security" in user_story
    
    def test_generate_user_story_formatting(self, parser):
        """Test user story formatting with various inputs."""
        # Test with stakeholder already having 'a'
        user_story1 = parser._generate_user_story("a user", "login", "access system")
        assert "As a user" in user_story1
        
        # Test with benefit not starting with 'so that'
        user_story2 = parser._generate_user_story("developer", "debug code", "fix issues")
        assert "so that fix issues" in user_story2
    
    def test_convert_to_when_shall(self, parser):
        """Test conversion of descriptions to WHEN/SHALL format."""
        description = "validate user credentials"
        
        when_clause, shall_clause = parser._convert_to_when_shall(description)
        
        assert when_clause.startswith("WHEN")
        assert "SHALL" in shall_clause.upper()
        assert "validate user credentials" in shall_clause.lower()
    
    def test_convert_to_when_shall_with_condition(self, parser):
        """Test conversion with existing conditions in description."""
        description = "when user submits form validate the input data"
        
        when_clause, shall_clause = parser._convert_to_when_shall(description)
        
        assert "WHEN when user submits form" in when_clause
        assert "SHALL" in shall_clause.upper()
    
    def test_generate_acceptance_criteria(self, parser):
        """Test acceptance criteria generation."""
        func_req = {
            'description': 'authenticate user credentials',
            'conditions': ['user enters invalid password', 'user account is locked'],
            'priority': 'HIGH',
            'category': 'Security'
        }
        req_id = "REQ-001"
        
        criteria = parser._generate_acceptance_criteria(func_req, req_id)
        
        assert len(criteria) == 3  # Primary + 2 conditions
        
        # Check primary criterion
        primary = criteria[0]
        assert primary.id == "REQ-001-AC-001"
        assert primary.requirement_id == req_id
        assert "WHEN" in primary.when_clause.upper()
        assert "SHALL" in primary.shall_clause.upper()
        
        # Check condition-based criteria
        assert criteria[1].id == "REQ-001-AC-002"
        assert criteria[2].id == "REQ-001-AC-003"
    
    def test_create_requirement_from_functional(self, parser):
        """Test creating a Requirement object from functional data."""
        func_req = {
            'description': 'process user login',
            'stakeholder': 'user',
            'benefit': 'access the system',
            'conditions': ['credentials are valid'],
            'priority': 'HIGH',
            'category': 'Authentication'
        }
        req_id = "REQ-001"
        context = RequirementParsingContext(objective="Test objective")
        
        requirement = parser._create_requirement_from_functional(func_req, req_id, context)
        
        assert isinstance(requirement, Requirement)
        assert requirement.id == req_id
        assert "As a user" in requirement.user_story
        assert requirement.priority == RequirementPriority.HIGH
        assert requirement.category == "Authentication"
        assert len(requirement.acceptance_criteria) >= 1
    
    def test_validate_requirements_consistency(self, parser):
        """Test requirement consistency validation."""
        # Create requirements with potential issues
        req1 = Requirement(
            id="REQ-001",
            user_story="As a user, I want to login, so that I can access the system",
            acceptance_criteria=[
                AcceptanceCriterion(
                    id="REQ-001-AC-001",
                    when_clause="WHEN user enters credentials",
                    shall_clause="THEN system SHALL authenticate user",
                    requirement_id="REQ-001"
                )
            ]
        )
        
        req2 = Requirement(
            id="REQ-002",
            user_story="As a user, I want to login to the system, so that I can use features",
            acceptance_criteria=[
                AcceptanceCriterion(
                    id="REQ-002-AC-001",
                    when_clause="WHEN user provides login details",
                    shall_clause="THEN system SHALL verify credentials",
                    requirement_id="REQ-002"
                )
            ]
        )
        
        req3 = Requirement(
            id="REQ-003",
            user_story="As a user, I want to logout, so that I can secure my session",
            acceptance_criteria=[]  # No acceptance criteria - should trigger issue
        )
        
        issues = parser.validate_requirements_consistency([req1, req2, req3])
        
        # Should detect overlapping functionality and missing acceptance criteria
        assert len(issues) >= 1
        assert any("no acceptance criteria" in issue for issue in issues)
    
    def test_validate_requirements_consistency_duplicate_ids(self, parser):
        """Test detection of duplicate requirement IDs."""
        req1 = Requirement(
            id="REQ-001",
            user_story="As a user, I want to login, so that I can access the system",
            acceptance_criteria=[
                AcceptanceCriterion(
                    id="REQ-001-AC-001",
                    when_clause="WHEN user enters credentials",
                    shall_clause="THEN system SHALL authenticate user",
                    requirement_id="REQ-001"
                )
            ]
        )
        
        req2 = Requirement(
            id="REQ-001",  # Duplicate ID
            user_story="As a user, I want to register, so that I can create an account",
            acceptance_criteria=[
                AcceptanceCriterion(
                    id="REQ-001-AC-002",
                    when_clause="WHEN user provides registration data",
                    shall_clause="THEN system SHALL create account",
                    requirement_id="REQ-001"
                )
            ]
        )
        
        issues = parser.validate_requirements_consistency([req1, req2])
        
        assert any("duplicate" in issue.lower() for issue in issues)
    
    def test_inference_methods(self, parser):
        """Test various inference methods for extracting information."""
        # Test stakeholder inference
        assert parser._infer_stakeholder("admin panel functionality") == "administrator"
        assert parser._infer_stakeholder("developer tools") == "developer"
        assert parser._infer_stakeholder("user interface") == "user"
        
        # Test benefit inference
        assert "efficiency" in parser._infer_benefit("make process more efficient")
        assert "security" in parser._infer_benefit("ensure secure access")
        
        # Test priority inference
        assert parser._infer_priority("must implement critical feature") == "HIGH"
        assert parser._infer_priority("should add this feature") == "MEDIUM"
        assert parser._infer_priority("could be nice to have") == "LOW"
        
        # Test category inference
        assert parser._infer_category("display user interface") == "User Interface"
        assert parser._infer_category("store data in database") == "Data Management"
        assert parser._infer_category("secure authentication") == "Security"
    
    def test_extract_conditions_from_sentence(self, parser):
        """Test condition extraction from sentences."""
        sentence = "When user clicks button, if form is valid, the system should save data"
        
        conditions = parser._extract_conditions_from_sentence(sentence)
        
        assert len(conditions) >= 1
        assert any("user clicks button" in condition for condition in conditions)
    
    def test_clean_when_shall_clauses(self, parser):
        """Test cleaning and standardization of WHEN/SHALL clauses."""
        # Test WHEN clause cleaning
        when_clause = parser._clean_when_clause("user submits form")
        assert when_clause.startswith("WHEN")
        
        when_clause2 = parser._clean_when_clause("WHEN user logs in")
        assert when_clause2 == "WHEN user logs in"
        
        # Test SHALL clause cleaning
        shall_clause = parser._clean_shall_clause("system validates input")
        assert "SHALL" in shall_clause.upper()
        assert shall_clause.startswith("THEN")
        
        shall_clause2 = parser._clean_shall_clause("THEN system SHALL process request")
        assert shall_clause2 == "THEN system SHALL process request"
    
    def test_generate_introduction(self, parser):
        """Test requirements document introduction generation."""
        objective = "Create a user management system"
        requirements = [
            Requirement(
                id="REQ-001",
                user_story="As a user, I want to login, so that I can access the system",
                category="Authentication"
            ),
            Requirement(
                id="REQ-002", 
                user_story="As an admin, I want to manage users, so that I can control access",
                category="User Management"
            )
        ]
        
        introduction = parser._generate_introduction(objective, requirements)
        
        assert objective in introduction
        assert "2 requirements" in introduction
        assert "Authentication" in introduction
        assert "User Management" in introduction
        assert "EARS" in introduction
    
    def test_similarity_calculation(self, parser):
        """Test text similarity calculation."""
        text1 = "user login authentication system"
        text2 = "user authentication login system"
        text3 = "task management workflow"
        
        # High similarity
        similarity1 = parser._calculate_similarity(text1, text2)
        assert similarity1 > 0.7
        
        # Low similarity
        similarity2 = parser._calculate_similarity(text1, text3)
        assert similarity2 < 0.3
        
        # Empty text handling
        similarity3 = parser._calculate_similarity("", text1)
        assert similarity3 == 0.0
    
    def test_parsing_error_handling(self, parser, mock_ai_client):
        """Test error handling during parsing."""
        context = RequirementParsingContext(objective="")
        
        # Test with empty objective
        with pytest.raises(RequirementParsingError):
            parser.parse_objective(context)
    
    def test_complex_objective_parsing(self, parser, mock_ai_client, complex_context):
        """Test parsing a complex objective with multiple features."""
        mock_ai_client.generate_with_retry.return_value = """
        1. Task Creation
           Description: Enable users to create new tasks with title and description
           Stakeholder: end user
           Benefit: organize work efficiently
           Priority: HIGH
           Category: Task Management
        
        2. Task Editing
           Description: Allow users to modify existing task details
           Stakeholder: end user
           Benefit: keep tasks up to date
           Priority: MEDIUM
           Category: Task Management
        
        3. User Authentication
           Description: Secure user login and session management
           Stakeholder: end user
           Benefit: protect user data
           Priority: HIGH
           Category: Security
        
        4. Email Notifications
           Description: Send alerts when tasks become overdue
           Stakeholder: end user
           Benefit: stay informed about deadlines
           Conditions: task is overdue
           Priority: MEDIUM
           Category: Notifications
        """
        
        result = parser.parse_objective(complex_context)
        
        assert isinstance(result, RequirementsDocument)
        assert len(result.requirements) == 4
        
        # Check that different categories are represented
        categories = {req.category for req in result.requirements}
        assert "Task Management" in categories
        assert "Security" in categories
        assert "Notifications" in categories
        
        # Check that conditions are properly handled
        notification_req = next(req for req in result.requirements if req.category == "Notifications")
        assert len(notification_req.acceptance_criteria) >= 2  # Primary + condition-based
    
    def test_requirement_parsing_context(self):
        """Test RequirementParsingContext initialization and defaults."""
        # Test with minimal context
        context1 = RequirementParsingContext(objective="Test objective")
        assert context1.objective == "Test objective"
        assert context1.stakeholders == []
        assert context1.constraints == []
        assert context1.existing_requirements == []
        
        # Test with full context
        context2 = RequirementParsingContext(
            objective="Full test",
            domain="Testing",
            stakeholders=["tester"],
            constraints=["time limit"],
            existing_requirements=[]
        )
        assert context2.domain == "Testing"
        assert context2.stakeholders == ["tester"]
        assert context2.constraints == ["time limit"]


class TestRequirementParsingEdgeCases:
    """Test edge cases and error conditions for RequirementParser."""
    
    @pytest.fixture
    def parser(self):
        """Create a RequirementParser with mock AI client."""
        mock_client = Mock(spec=AIClientInterface)
        return RequirementParser(mock_client)
    
    def test_empty_objective(self, parser):
        """Test handling of empty objective."""
        context = RequirementParsingContext(objective="")
        
        with pytest.raises(RequirementParsingError):
            parser.parse_objective(context)
    
    def test_malformed_ai_response(self, parser):
        """Test handling of malformed AI responses."""
        context = RequirementParsingContext(objective="Create a system")
        
        # Mock malformed AI response
        parser.ai_client.generate_with_retry.return_value = "Invalid response format"
        
        # Should fall back to rule-based extraction
        result = parser.parse_objective(context)
        assert isinstance(result, RequirementsDocument)
        assert len(result.requirements) >= 1
    
    def test_extract_requirement_data_empty_text(self, parser):
        """Test extraction from empty or whitespace-only text."""
        result = parser._extract_requirement_data_from_text("")
        assert result is None
        
        result2 = parser._extract_requirement_data_from_text("   \n  \t  ")
        assert result2 is None
    
    def test_convert_when_shall_edge_cases(self, parser):
        """Test WHEN/SHALL conversion with edge cases."""
        # Empty description
        when_clause, shall_clause = parser._convert_to_when_shall("")
        assert "WHEN" in when_clause
        assert "SHALL" in shall_clause
        
        # Description with multiple condition keywords
        description = "when user logs in and if session is valid then process request"
        when_clause, shall_clause = parser._convert_to_when_shall(description)
        assert "WHEN" in when_clause
        assert "SHALL" in shall_clause
    
    def test_generate_user_story_edge_cases(self, parser):
        """Test user story generation with edge cases."""
        # Empty inputs
        user_story = parser._generate_user_story("", "", "")
        assert "As a " in user_story
        assert "I want" in user_story
        assert "so that" in user_story
        
        # Very long inputs
        long_stakeholder = "a very long stakeholder description that goes on and on"
        long_description = "perform a very complex operation that involves multiple steps and processes"
        long_benefit = "achieve a comprehensive set of benefits that span multiple domains"
        
        user_story = parser._generate_user_story(long_stakeholder, long_description, long_benefit)
        assert len(user_story) > 0
        assert "As a very long stakeholder" in user_story