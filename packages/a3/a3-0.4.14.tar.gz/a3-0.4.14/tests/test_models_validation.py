"""
Unit tests for data model validation logic.
"""

import pytest
from datetime import datetime
from a3.core.models import (
    Argument, FunctionSpec, Module, DependencyGraph, ProjectPlan, ProjectProgress,
    ValidationError, ProjectPlanValidationError, ModuleValidationError,
    FunctionSpecValidationError, DependencyGraphValidationError,
    ProjectPhase, ImplementationStatus,
    # Enhanced models
    RequirementsDocument, Requirement, AcceptanceCriterion, RequirementPriority,
    DesignDocument, DesignComponent, TasksDocument, ImplementationTask,
    DocumentationConfiguration, EnhancedProjectPlan, EnhancedFunctionSpec,
    # Exception types
    DocumentGenerationError, RequirementParsingError, RequirementValidationError,
    DocumentConsistencyError
)


class TestArgumentValidation:
    """Test validation for Argument class."""
    
    def test_valid_argument(self):
        """Test that valid arguments pass validation."""
        arg = Argument(name="param", type_hint="str", description="A parameter")
        arg.validate()  # Should not raise
    
    def test_empty_name_raises_error(self):
        """Test that empty argument name raises ValidationError."""
        arg = Argument(name="", type_hint="str")
        with pytest.raises(ValidationError, match="Argument name cannot be empty"):
            arg.validate()
    
    def test_invalid_name_raises_error(self):
        """Test that invalid argument name raises ValidationError."""
        arg = Argument(name="123invalid", type_hint="str")
        with pytest.raises(ValidationError, match="Invalid argument name"):
            arg.validate()
    
    def test_empty_type_hint_raises_error(self):
        """Test that empty type hint raises ValidationError."""
        arg = Argument(name="param", type_hint="")
        with pytest.raises(ValidationError, match="Argument type hint cannot be empty"):
            arg.validate()
    
    def test_keyword_name_raises_error(self):
        """Test that Python keyword as name raises ValidationError."""
        arg = Argument(name="def", type_hint="str")
        with pytest.raises(ValidationError, match="is a Python keyword"):
            arg.validate()


class TestFunctionSpecValidation:
    """Test validation for FunctionSpec class."""
    
    def test_valid_function_spec(self):
        """Test that valid function spec passes validation."""
        func = FunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            arguments=[Argument("param", "str")],
            return_type="bool"
        )
        func.validate()  # Should not raise
    
    def test_empty_name_raises_error(self):
        """Test that empty function name raises error."""
        func = FunctionSpec(name="", module="test", docstring="Test")
        with pytest.raises(FunctionSpecValidationError, match="Function name cannot be empty"):
            func.validate()
    
    def test_invalid_name_raises_error(self):
        """Test that invalid function name raises error."""
        func = FunctionSpec(name="123invalid", module="test", docstring="Test")
        with pytest.raises(FunctionSpecValidationError, match="Invalid function name"):
            func.validate()
    
    def test_empty_module_raises_error(self):
        """Test that empty module name raises error."""
        func = FunctionSpec(name="test", module="", docstring="Test")
        with pytest.raises(FunctionSpecValidationError, match="Module name cannot be empty"):
            func.validate()
    
    def test_empty_docstring_raises_error(self):
        """Test that empty docstring raises error."""
        func = FunctionSpec(name="test", module="test", docstring="")
        with pytest.raises(FunctionSpecValidationError, match="Function docstring cannot be empty"):
            func.validate()
    
    def test_duplicate_argument_names_raises_error(self):
        """Test that duplicate argument names raise error."""
        func = FunctionSpec(
            name="test",
            module="test",
            docstring="Test",
            arguments=[
                Argument("param", "str"),
                Argument("param", "int")  # Duplicate name
            ]
        )
        with pytest.raises(FunctionSpecValidationError, match="Duplicate argument name"):
            func.validate()


class TestModuleValidation:
    """Test validation for Module class."""
    
    def test_valid_module(self):
        """Test that valid module passes validation."""
        module = Module(
            name="test_module",
            description="Test module",
            file_path="test_module.py",
            functions=[FunctionSpec("test_func", "test_module", "Test function")]
        )
        module.validate()  # Should not raise
    
    def test_empty_name_raises_error(self):
        """Test that empty module name raises error."""
        module = Module(name="", description="Test", file_path="test.py")
        with pytest.raises(ModuleValidationError, match="Module name cannot be empty"):
            module.validate()
    
    def test_invalid_file_path_raises_error(self):
        """Test that non-Python file path raises error."""
        module = Module(name="test", description="Test", file_path="test.txt")
        with pytest.raises(ModuleValidationError, match="must end with .py"):
            module.validate()
    
    def test_self_dependency_raises_error(self):
        """Test that self-dependency raises error."""
        module = Module(
            name="test",
            description="Test",
            file_path="test.py",
            dependencies=["test"]  # Self-dependency
        )
        with pytest.raises(ModuleValidationError, match="cannot depend on itself"):
            module.validate()
    
    def test_duplicate_function_names_raises_error(self):
        """Test that duplicate function names raise error."""
        module = Module(
            name="test",
            description="Test",
            file_path="test.py",
            functions=[
                FunctionSpec("func", "test", "Test 1"),
                FunctionSpec("func", "test", "Test 2")  # Duplicate name
            ]
        )
        with pytest.raises(ModuleValidationError, match="Duplicate function name"):
            module.validate()


class TestDependencyGraphValidation:
    """Test validation for DependencyGraph class."""
    
    def test_valid_dependency_graph(self):
        """Test that valid dependency graph passes validation."""
        graph = DependencyGraph(
            nodes=["module_a", "module_b"],
            edges=[("module_a", "module_b")]
        )
        graph.validate()  # Should not raise
    
    def test_duplicate_nodes_raises_error(self):
        """Test that duplicate nodes raise error."""
        graph = DependencyGraph(nodes=["module_a", "module_a"])
        with pytest.raises(DependencyGraphValidationError, match="duplicate nodes"):
            graph.validate()
    
    def test_invalid_node_name_raises_error(self):
        """Test that invalid node name raises error."""
        graph = DependencyGraph(nodes=["123invalid"])
        with pytest.raises(DependencyGraphValidationError, match="Invalid node name"):
            graph.validate()
    
    def test_edge_to_nonexistent_node_raises_error(self):
        """Test that edge to non-existent node raises error."""
        graph = DependencyGraph(
            nodes=["module_a"],
            edges=[("module_a", "nonexistent")]
        )
        with pytest.raises(DependencyGraphValidationError, match="non-existent node"):
            graph.validate()
    
    def test_self_dependency_raises_error(self):
        """Test that self-dependency raises error."""
        graph = DependencyGraph(
            nodes=["module_a"],
            edges=[("module_a", "module_a")]
        )
        with pytest.raises(DependencyGraphValidationError, match="Self-dependency detected"):
            graph.validate()
    
    def test_circular_dependency_raises_error(self):
        """Test that circular dependencies raise error."""
        graph = DependencyGraph(
            nodes=["module_a", "module_b"],
            edges=[("module_a", "module_b"), ("module_b", "module_a")]
        )
        with pytest.raises(DependencyGraphValidationError, match="circular dependencies"):
            graph.validate()


class TestProjectPlanValidation:
    """Test validation for ProjectPlan class."""
    
    def test_valid_project_plan(self):
        """Test that valid project plan passes validation."""
        module = Module("test_module", "Test", "test.py")
        graph = DependencyGraph(nodes=["test_module"])
        plan = ProjectPlan(
            objective="Test project",
            modules=[module],
            dependency_graph=graph,
            estimated_functions=0
        )
        plan.validate()  # Should not raise
    
    def test_empty_objective_raises_error(self):
        """Test that empty objective raises error."""
        plan = ProjectPlan(objective="")
        with pytest.raises(ProjectPlanValidationError, match="Project objective cannot be empty"):
            plan.validate()
    
    def test_negative_estimated_functions_raises_error(self):
        """Test that negative estimated functions raises error."""
        plan = ProjectPlan(objective="Test", estimated_functions=-1)
        with pytest.raises(ProjectPlanValidationError, match="cannot be negative"):
            plan.validate()
    
    def test_mismatched_graph_nodes_raises_error(self):
        """Test that mismatched graph nodes and modules raise error."""
        module = Module("test_module", "Test", "test.py")
        graph = DependencyGraph(nodes=["different_module"])
        plan = ProjectPlan(
            objective="Test",
            modules=[module],
            dependency_graph=graph
        )
        with pytest.raises(ProjectPlanValidationError, match="don't match module names"):
            plan.validate()


class TestProjectProgressValidation:
    """Test validation for ProjectProgress class."""
    
    def test_valid_project_progress(self):
        """Test that valid project progress passes validation."""
        progress = ProjectProgress(
            current_phase=ProjectPhase.IMPLEMENTATION,
            completed_phases=[ProjectPhase.PLANNING, ProjectPhase.SPECIFICATION],
            total_functions=10,
            implemented_functions=5
        )
        progress.validate()  # Should not raise
    
    def test_negative_total_functions_raises_error(self):
        """Test that negative total functions raises error."""
        progress = ProjectProgress(total_functions=-1)
        with pytest.raises(ValidationError, match="Total functions count cannot be negative"):
            progress.validate()
    
    def test_implemented_exceeds_total_raises_error(self):
        """Test that implemented > total raises error."""
        progress = ProjectProgress(total_functions=5, implemented_functions=10)
        with pytest.raises(ValidationError, match="cannot exceed total functions"):
            progress.validate()
    
    def test_invalid_phase_progression_raises_error(self):
        """Test that invalid phase progression raises error."""
        progress = ProjectProgress(
            current_phase=ProjectPhase.PLANNING,
            completed_phases=[ProjectPhase.IMPLEMENTATION]  # Future phase marked complete
        )
        with pytest.raises(ValidationError, match="cannot be ahead of current phase"):
            progress.validate()


class TestDependencyGraphAlgorithms:
    """Test dependency graph cycle detection and topological sort."""
    
    def test_has_cycles_detects_simple_cycle(self):
        """Test that has_cycles detects a simple cycle."""
        graph = DependencyGraph(
            nodes=["a", "b"],
            edges=[("a", "b"), ("b", "a")]
        )
        assert graph.has_cycles() is True
    
    def test_has_cycles_detects_complex_cycle(self):
        """Test that has_cycles detects a complex cycle."""
        graph = DependencyGraph(
            nodes=["a", "b", "c"],
            edges=[("a", "b"), ("b", "c"), ("c", "a")]
        )
        assert graph.has_cycles() is True
    
    def test_has_cycles_returns_false_for_acyclic_graph(self):
        """Test that has_cycles returns False for acyclic graph."""
        graph = DependencyGraph(
            nodes=["a", "b", "c"],
            edges=[("a", "b"), ("a", "c")]
        )
        assert graph.has_cycles() is False
    
    def test_topological_sort_orders_correctly(self):
        """Test that topological sort orders nodes correctly."""
        graph = DependencyGraph(
            nodes=["a", "b", "c"],
            edges=[("a", "b"), ("a", "c"), ("b", "c")]
        )
        result = graph.topological_sort()
        
        # 'a' should come before 'b' and 'c'
        # 'b' should come before 'c'
        assert result.index("a") < result.index("b")
        assert result.index("a") < result.index("c")
        assert result.index("b") < result.index("c")
    
    def test_topological_sort_handles_cycle(self):
        """Test that topological sort handles cycles gracefully."""
        graph = DependencyGraph(
            nodes=["a", "b"],
            edges=[("a", "b"), ("b", "a")]
        )
        result = graph.topological_sort()
        # Should return original order when cycle exists
        assert result == ["a", "b"]


# Enhanced Models Tests

class TestAcceptanceCriterionValidation:
    """Test validation for AcceptanceCriterion class."""
    
    def test_valid_acceptance_criterion(self):
        """Test that valid acceptance criterion passes validation."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks button",
            shall_clause="system SHALL display message",
            requirement_id="REQ1"
        )
        criterion.validate()  # Should not raise
    
    def test_empty_id_raises_error(self):
        """Test that empty ID raises error."""
        criterion = AcceptanceCriterion(
            id="",
            when_clause="WHEN user clicks",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        with pytest.raises(RequirementValidationError, match="Acceptance criterion ID cannot be empty"):
            criterion.validate()
    
    def test_empty_when_clause_raises_error(self):
        """Test that empty WHEN clause raises error."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        with pytest.raises(RequirementValidationError, match="WHEN clause cannot be empty"):
            criterion.validate()
    
    def test_empty_shall_clause_raises_error(self):
        """Test that empty SHALL clause raises error."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="",
            requirement_id="REQ1"
        )
        with pytest.raises(RequirementValidationError, match="SHALL clause cannot be empty"):
            criterion.validate()
    
    def test_invalid_when_format_raises_error(self):
        """Test that invalid WHEN format raises error."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="IF user clicks",  # Should start with WHEN
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        with pytest.raises(RequirementValidationError, match="WHEN clause must start with 'WHEN'"):
            criterion.validate()
    
    def test_missing_shall_in_clause_raises_error(self):
        """Test that missing SHALL in clause raises error."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="system will respond",  # Missing SHALL
            requirement_id="REQ1"
        )
        with pytest.raises(RequirementValidationError, match="SHALL clause must contain 'SHALL'"):
            criterion.validate()


class TestRequirementValidation:
    """Test validation for Requirement class."""
    
    def test_valid_requirement(self):
        """Test that valid requirement passes validation."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks button",
            shall_clause="system SHALL display message",
            requirement_id="REQ1"
        )
        requirement = Requirement(
            id="REQ1",
            user_story="As a user, I want to click buttons, so that I can interact with the system",
            acceptance_criteria=[criterion],
            priority=RequirementPriority.HIGH
        )
        requirement.validate()  # Should not raise
    
    def test_empty_id_raises_error(self):
        """Test that empty requirement ID raises error."""
        requirement = Requirement(
            id="",
            user_story="As a user, I want something, so that I can achieve goals"
        )
        with pytest.raises(RequirementValidationError, match="Requirement ID cannot be empty"):
            requirement.validate()
    
    def test_empty_user_story_raises_error(self):
        """Test that empty user story raises error."""
        requirement = Requirement(
            id="REQ1",
            user_story=""
        )
        with pytest.raises(RequirementValidationError, match="User story cannot be empty"):
            requirement.validate()
    
    def test_invalid_user_story_format_raises_error(self):
        """Test that invalid user story format raises error."""
        requirement = Requirement(
            id="REQ1",
            user_story="I want something"  # Missing proper format
        )
        with pytest.raises(RequirementValidationError, match="User story must follow"):
            requirement.validate()
    
    def test_no_acceptance_criteria_raises_error(self):
        """Test that requirement without acceptance criteria raises error."""
        requirement = Requirement(
            id="REQ1",
            user_story="As a user, I want something, so that I can achieve goals",
            acceptance_criteria=[]
        )
        with pytest.raises(RequirementValidationError, match="must have at least one acceptance criterion"):
            requirement.validate()
    
    def test_duplicate_criterion_ids_raises_error(self):
        """Test that duplicate acceptance criterion IDs raise error."""
        criterion1 = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        criterion2 = AcceptanceCriterion(
            id="AC1",  # Duplicate ID
            when_clause="WHEN user types",
            shall_clause="system SHALL process",
            requirement_id="REQ1"
        )
        requirement = Requirement(
            id="REQ1",
            user_story="As a user, I want something, so that I can achieve goals",
            acceptance_criteria=[criterion1, criterion2]
        )
        with pytest.raises(RequirementValidationError, match="Duplicate acceptance criterion ID"):
            requirement.validate()
    
    def test_mismatched_requirement_id_raises_error(self):
        """Test that mismatched requirement ID in criterion raises error."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="system SHALL respond",
            requirement_id="REQ2"  # Different from requirement ID
        )
        requirement = Requirement(
            id="REQ1",
            user_story="As a user, I want something, so that I can achieve goals",
            acceptance_criteria=[criterion]
        )
        with pytest.raises(RequirementValidationError, match="mismatched requirement ID"):
            requirement.validate()


class TestRequirementsDocumentValidation:
    """Test validation for RequirementsDocument class."""
    
    def test_valid_requirements_document(self):
        """Test that valid requirements document passes validation."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks button",
            shall_clause="system SHALL display message",
            requirement_id="REQ1"
        )
        requirement = Requirement(
            id="REQ1",
            user_story="As a user, I want to click buttons, so that I can interact",
            acceptance_criteria=[criterion]
        )
        doc = RequirementsDocument(
            introduction="This document describes requirements",
            requirements=[requirement]
        )
        doc.validate()  # Should not raise
    
    def test_empty_introduction_raises_error(self):
        """Test that empty introduction raises error."""
        doc = RequirementsDocument(
            introduction="",
            requirements=[]
        )
        with pytest.raises(RequirementValidationError, match="introduction cannot be empty"):
            doc.validate()
    
    def test_empty_version_raises_error(self):
        """Test that empty version raises error."""
        doc = RequirementsDocument(
            introduction="Test intro",
            requirements=[],
            version=""
        )
        with pytest.raises(RequirementValidationError, match="version cannot be empty"):
            doc.validate()
    
    def test_no_requirements_raises_error(self):
        """Test that document without requirements raises error."""
        doc = RequirementsDocument(
            introduction="Test intro",
            requirements=[]
        )
        with pytest.raises(RequirementValidationError, match="must have at least one requirement"):
            doc.validate()
    
    def test_duplicate_requirement_ids_raises_error(self):
        """Test that duplicate requirement IDs raise error."""
        criterion1 = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        criterion2 = AcceptanceCriterion(
            id="AC2",
            when_clause="WHEN user types",
            shall_clause="system SHALL process",
            requirement_id="REQ1"
        )
        req1 = Requirement(
            id="REQ1",
            user_story="As a user, I want something, so that I can achieve goals",
            acceptance_criteria=[criterion1]
        )
        req2 = Requirement(
            id="REQ1",  # Duplicate ID
            user_story="As a user, I want something else, so that I can achieve other goals",
            acceptance_criteria=[criterion2]
        )
        doc = RequirementsDocument(
            introduction="Test intro",
            requirements=[req1, req2]
        )
        with pytest.raises(RequirementValidationError, match="Duplicate requirement ID"):
            doc.validate()
    
    def test_get_requirement_by_id(self):
        """Test getting requirement by ID."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        requirement = Requirement(
            id="REQ1",
            user_story="As a user, I want something, so that I can achieve goals",
            acceptance_criteria=[criterion]
        )
        doc = RequirementsDocument(
            introduction="Test intro",
            requirements=[requirement]
        )
        
        found = doc.get_requirement_by_id("REQ1")
        assert found == requirement
        
        not_found = doc.get_requirement_by_id("REQ2")
        assert not_found is None
    
    def test_get_requirements_by_priority(self):
        """Test getting requirements by priority."""
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        high_req = Requirement(
            id="REQ1",
            user_story="As a user, I want something, so that I can achieve goals",
            acceptance_criteria=[criterion],
            priority=RequirementPriority.HIGH
        )
        low_req = Requirement(
            id="REQ2",
            user_story="As a user, I want something else, so that I can achieve other goals",
            acceptance_criteria=[AcceptanceCriterion(
                id="AC2",
                when_clause="WHEN user types",
                shall_clause="system SHALL process",
                requirement_id="REQ2"
            )],
            priority=RequirementPriority.LOW
        )
        doc = RequirementsDocument(
            introduction="Test intro",
            requirements=[high_req, low_req]
        )
        
        high_reqs = doc.get_requirements_by_priority(RequirementPriority.HIGH)
        assert len(high_reqs) == 1
        assert high_reqs[0] == high_req


class TestDesignComponentValidation:
    """Test validation for DesignComponent class."""
    
    def test_valid_design_component(self):
        """Test that valid design component passes validation."""
        component = DesignComponent(
            id="COMP1",
            name="User Interface",
            description="Handles user interactions",
            responsibilities=["Handle clicks", "Display messages"],
            requirement_mappings=["REQ1", "REQ2"]
        )
        component.validate()  # Should not raise
    
    def test_empty_id_raises_error(self):
        """Test that empty component ID raises error."""
        component = DesignComponent(
            id="",
            name="Test Component",
            description="Test description"
        )
        with pytest.raises(ValidationError, match="Design component ID cannot be empty"):
            component.validate()
    
    def test_empty_name_raises_error(self):
        """Test that empty component name raises error."""
        component = DesignComponent(
            id="COMP1",
            name="",
            description="Test description"
        )
        with pytest.raises(ValidationError, match="Design component name cannot be empty"):
            component.validate()
    
    def test_empty_description_raises_error(self):
        """Test that empty component description raises error."""
        component = DesignComponent(
            id="COMP1",
            name="Test Component",
            description=""
        )
        with pytest.raises(ValidationError, match="Design component description cannot be empty"):
            component.validate()
    
    def test_empty_requirement_mapping_raises_error(self):
        """Test that empty requirement mapping raises error."""
        component = DesignComponent(
            id="COMP1",
            name="Test Component",
            description="Test description",
            requirement_mappings=["REQ1", ""]  # Empty mapping
        )
        with pytest.raises(ValidationError, match="Requirement mapping IDs cannot be empty"):
            component.validate()


class TestDesignDocumentValidation:
    """Test validation for DesignDocument class."""
    
    def test_valid_design_document(self):
        """Test that valid design document passes validation."""
        component = DesignComponent(
            id="COMP1",
            name="User Interface",
            description="Handles user interactions"
        )
        doc = DesignDocument(
            overview="System overview",
            architecture="Modular architecture",
            components=[component],
            requirement_mappings={"REQ1": ["COMP1"]}
        )
        doc.validate()  # Should not raise
    
    def test_empty_overview_raises_error(self):
        """Test that empty overview raises error."""
        doc = DesignDocument(
            overview="",
            architecture="Test architecture"
        )
        with pytest.raises(ValidationError, match="Design document overview cannot be empty"):
            doc.validate()
    
    def test_empty_architecture_raises_error(self):
        """Test that empty architecture raises error."""
        doc = DesignDocument(
            overview="Test overview",
            architecture=""
        )
        with pytest.raises(ValidationError, match="Design document architecture cannot be empty"):
            doc.validate()
    
    def test_duplicate_component_ids_raises_error(self):
        """Test that duplicate component IDs raise error."""
        comp1 = DesignComponent(
            id="COMP1",
            name="Component 1",
            description="First component"
        )
        comp2 = DesignComponent(
            id="COMP1",  # Duplicate ID
            name="Component 2",
            description="Second component"
        )
        doc = DesignDocument(
            overview="Test overview",
            architecture="Test architecture",
            components=[comp1, comp2]
        )
        with pytest.raises(ValidationError, match="Duplicate component ID"):
            doc.validate()
    
    def test_invalid_requirement_mapping_raises_error(self):
        """Test that invalid requirement mapping raises error."""
        component = DesignComponent(
            id="COMP1",
            name="Component 1",
            description="First component"
        )
        doc = DesignDocument(
            overview="Test overview",
            architecture="Test architecture",
            components=[component],
            requirement_mappings={"REQ1": ["COMP2"]}  # Non-existent component
        )
        with pytest.raises(ValidationError, match="references non-existent component"):
            doc.validate()
    
    def test_get_component_by_id(self):
        """Test getting component by ID."""
        component = DesignComponent(
            id="COMP1",
            name="Component 1",
            description="First component"
        )
        doc = DesignDocument(
            overview="Test overview",
            architecture="Test architecture",
            components=[component]
        )
        
        found = doc.get_component_by_id("COMP1")
        assert found == component
        
        not_found = doc.get_component_by_id("COMP2")
        assert not_found is None


class TestImplementationTaskValidation:
    """Test validation for ImplementationTask class."""
    
    def test_valid_implementation_task(self):
        """Test that valid implementation task passes validation."""
        task = ImplementationTask(
            id="TASK1",
            description="Implement user interface",
            requirement_references=["REQ1", "REQ2"],
            design_references=["COMP1"],
            dependencies=["TASK0"]
        )
        task.validate()  # Should not raise
    
    def test_empty_id_raises_error(self):
        """Test that empty task ID raises error."""
        task = ImplementationTask(
            id="",
            description="Test task"
        )
        with pytest.raises(ValidationError, match="Implementation task ID cannot be empty"):
            task.validate()
    
    def test_empty_description_raises_error(self):
        """Test that empty task description raises error."""
        task = ImplementationTask(
            id="TASK1",
            description=""
        )
        with pytest.raises(ValidationError, match="Implementation task description cannot be empty"):
            task.validate()
    
    def test_empty_requirement_reference_raises_error(self):
        """Test that empty requirement reference raises error."""
        task = ImplementationTask(
            id="TASK1",
            description="Test task",
            requirement_references=["REQ1", ""]  # Empty reference
        )
        with pytest.raises(ValidationError, match="Requirement reference IDs cannot be empty"):
            task.validate()
    
    def test_empty_design_reference_raises_error(self):
        """Test that empty design reference raises error."""
        task = ImplementationTask(
            id="TASK1",
            description="Test task",
            design_references=["COMP1", ""]  # Empty reference
        )
        with pytest.raises(ValidationError, match="Design reference IDs cannot be empty"):
            task.validate()
    
    def test_empty_dependency_raises_error(self):
        """Test that empty dependency raises error."""
        task = ImplementationTask(
            id="TASK1",
            description="Test task",
            dependencies=["TASK0", ""]  # Empty dependency
        )
        with pytest.raises(ValidationError, match="Task dependency IDs cannot be empty"):
            task.validate()


class TestTasksDocumentValidation:
    """Test validation for TasksDocument class."""
    
    def test_valid_tasks_document(self):
        """Test that valid tasks document passes validation."""
        task = ImplementationTask(
            id="TASK1",
            description="Implement feature",
            requirement_references=["REQ1"]
        )
        doc = TasksDocument(
            tasks=[task],
            requirement_coverage={"REQ1": ["TASK1"]},
            design_coverage={"COMP1": ["TASK1"]}
        )
        doc.validate()  # Should not raise
    
    def test_empty_version_raises_error(self):
        """Test that empty version raises error."""
        doc = TasksDocument(
            tasks=[],
            version=""
        )
        with pytest.raises(ValidationError, match="Tasks document version cannot be empty"):
            doc.validate()
    
    def test_no_tasks_raises_error(self):
        """Test that document without tasks raises error."""
        doc = TasksDocument(tasks=[])
        with pytest.raises(ValidationError, match="must have at least one task"):
            doc.validate()
    
    def test_duplicate_task_ids_raises_error(self):
        """Test that duplicate task IDs raise error."""
        task1 = ImplementationTask(
            id="TASK1",
            description="First task"
        )
        task2 = ImplementationTask(
            id="TASK1",  # Duplicate ID
            description="Second task"
        )
        doc = TasksDocument(tasks=[task1, task2])
        with pytest.raises(ValidationError, match="Duplicate task ID"):
            doc.validate()
    
    def test_invalid_task_dependency_raises_error(self):
        """Test that invalid task dependency raises error."""
        task = ImplementationTask(
            id="TASK1",
            description="Test task",
            dependencies=["TASK2"]  # Non-existent task
        )
        doc = TasksDocument(tasks=[task])
        with pytest.raises(ValidationError, match="depends on non-existent task"):
            doc.validate()
    
    def test_invalid_requirement_coverage_raises_error(self):
        """Test that invalid requirement coverage raises error."""
        task = ImplementationTask(
            id="TASK1",
            description="Test task"
        )
        doc = TasksDocument(
            tasks=[task],
            requirement_coverage={"REQ1": ["TASK2"]}  # Non-existent task
        )
        with pytest.raises(ValidationError, match="Requirement coverage references non-existent task"):
            doc.validate()
    
    def test_get_dependency_order(self):
        """Test getting tasks in dependency order."""
        task1 = ImplementationTask(
            id="TASK1",
            description="First task"
        )
        task2 = ImplementationTask(
            id="TASK2",
            description="Second task",
            dependencies=["TASK1"]
        )
        task3 = ImplementationTask(
            id="TASK3",
            description="Third task",
            dependencies=["TASK1", "TASK2"]
        )
        doc = TasksDocument(tasks=[task3, task1, task2])  # Unordered
        
        order = doc.get_dependency_order()
        assert order.index("TASK1") < order.index("TASK2")
        assert order.index("TASK2") < order.index("TASK3")


class TestDocumentationConfigurationValidation:
    """Test validation for DocumentationConfiguration class."""
    
    def test_valid_documentation_configuration(self):
        """Test that valid documentation configuration passes validation."""
        config = DocumentationConfiguration(
            enable_requirements=True,
            requirement_format="ears",
            validation_level="strict"
        )
        config.validate()  # Should not raise
    
    def test_invalid_requirement_format_raises_error(self):
        """Test that invalid requirement format raises error."""
        config = DocumentationConfiguration(
            requirement_format="invalid_format"
        )
        with pytest.raises(ValidationError, match="Invalid requirement format"):
            config.validate()
    
    def test_invalid_validation_level_raises_error(self):
        """Test that invalid validation level raises error."""
        config = DocumentationConfiguration(
            validation_level="invalid_level"
        )
        with pytest.raises(ValidationError, match="Invalid validation level"):
            config.validate()


class TestEnhancedFunctionSpecValidation:
    """Test validation for EnhancedFunctionSpec class."""
    
    def test_valid_enhanced_function_spec(self):
        """Test that valid enhanced function spec passes validation."""
        func = EnhancedFunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            requirement_references=["REQ1", "REQ2"],
            acceptance_criteria_implementations=["AC1", "AC2"],
            validation_logic="if param is None: raise ValueError"
        )
        func.validate()  # Should not raise
    
    def test_empty_requirement_reference_raises_error(self):
        """Test that empty requirement reference raises error."""
        func = EnhancedFunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            requirement_references=["REQ1", ""]  # Empty reference
        )
        with pytest.raises(ValidationError, match="Requirement reference cannot be empty"):
            func.validate()
    
    def test_empty_acceptance_criteria_implementation_raises_error(self):
        """Test that empty acceptance criteria implementation raises error."""
        func = EnhancedFunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function",
            acceptance_criteria_implementations=["AC1", ""]  # Empty implementation
        )
        with pytest.raises(ValidationError, match="Acceptance criteria implementation cannot be empty"):
            func.validate()


class TestEnhancedProjectPlanValidation:
    """Test validation for EnhancedProjectPlan class."""
    
    def test_valid_enhanced_project_plan(self):
        """Test that valid enhanced project plan passes validation."""
        # Create valid requirements document
        criterion = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user clicks",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        requirement = Requirement(
            id="REQ1",
            user_story="As a user, I want something, so that I can achieve goals",
            acceptance_criteria=[criterion]
        )
        req_doc = RequirementsDocument(
            introduction="Test requirements",
            requirements=[requirement]
        )
        
        # Create valid design document
        component = DesignComponent(
            id="COMP1",
            name="Test Component",
            description="Test component description"
        )
        design_doc = DesignDocument(
            overview="Test design",
            architecture="Test architecture",
            components=[component]
        )
        
        # Create valid tasks document
        task = ImplementationTask(
            id="TASK1",
            description="Test task"
        )
        tasks_doc = TasksDocument(tasks=[task])
        
        # Create valid configuration
        config = DocumentationConfiguration()
        
        # Create enhanced function
        enhanced_func = EnhancedFunctionSpec(
            name="test_func",
            module="test_module",
            docstring="Test function"
        )
        
        # Create basic module and graph for parent validation
        module = Module("test_module", "Test module", "test.py")
        graph = DependencyGraph(nodes=["test_module"])
        
        plan = EnhancedProjectPlan(
            objective="Test project",
            modules=[module],
            dependency_graph=graph,
            requirements_document=req_doc,
            design_document=design_doc,
            tasks_document=tasks_doc,
            documentation_config=config,
            enhanced_functions=[enhanced_func]
        )
        plan.validate()  # Should not raise
    
    def test_invalid_requirements_document_raises_error(self):
        """Test that invalid requirements document raises error."""
        # Create invalid requirements document (empty requirements)
        req_doc = RequirementsDocument(
            introduction="Test requirements",
            requirements=[]  # Invalid - no requirements
        )
        
        module = Module("test_module", "Test module", "test.py")
        graph = DependencyGraph(nodes=["test_module"])
        
        plan = EnhancedProjectPlan(
            objective="Test project",
            modules=[module],
            dependency_graph=graph,
            requirements_document=req_doc
        )
        with pytest.raises(RequirementValidationError):
            plan.validate()


# Performance and Edge Case Tests

class TestLargeDocumentProcessing:
    """Test performance with large documents containing many requirements/components."""
    
    def test_large_requirements_document_validation(self):
        """Test validation performance with many requirements."""
        requirements = []
        for i in range(100):  # Create 100 requirements
            criterion = AcceptanceCriterion(
                id=f"AC{i}",
                when_clause=f"WHEN condition {i} occurs",
                shall_clause=f"system SHALL perform action {i}",
                requirement_id=f"REQ{i}"
            )
            requirement = Requirement(
                id=f"REQ{i}",
                user_story=f"As a user, I want feature {i}, so that I can achieve goal {i}",
                acceptance_criteria=[criterion]
            )
            requirements.append(requirement)
        
        doc = RequirementsDocument(
            introduction="Large requirements document",
            requirements=requirements
        )
        
        # Should validate without issues
        doc.validate()
        assert len(doc.requirements) == 100
    
    def test_large_design_document_validation(self):
        """Test validation performance with many design components."""
        components = []
        requirement_mappings = {}
        
        for i in range(50):  # Create 50 components
            component = DesignComponent(
                id=f"COMP{i}",
                name=f"Component {i}",
                description=f"Description for component {i}",
                requirement_mappings=[f"REQ{i}"]
            )
            components.append(component)
            requirement_mappings[f"REQ{i}"] = [f"COMP{i}"]
        
        doc = DesignDocument(
            overview="Large design document",
            architecture="Complex modular architecture",
            components=components,
            requirement_mappings=requirement_mappings
        )
        
        # Should validate without issues
        doc.validate()
        assert len(doc.components) == 50
    
    def test_large_tasks_document_validation(self):
        """Test validation performance with many implementation tasks."""
        tasks = []
        requirement_coverage = {}
        
        for i in range(200):  # Create 200 tasks
            task = ImplementationTask(
                id=f"TASK{i}",
                description=f"Implement feature {i}",
                requirement_references=[f"REQ{i % 50}"],  # Cycle through requirements
                dependencies=[f"TASK{i-1}"] if i > 0 else []
            )
            tasks.append(task)
            
            req_id = f"REQ{i % 50}"
            if req_id not in requirement_coverage:
                requirement_coverage[req_id] = []
            requirement_coverage[req_id].append(f"TASK{i}")
        
        doc = TasksDocument(
            tasks=tasks,
            requirement_coverage=requirement_coverage
        )
        
        # Should validate without issues
        doc.validate()
        assert len(doc.tasks) == 200
        
        # Test dependency ordering with large task set
        order = doc.get_dependency_order()
        assert len(order) == 200
        # First task should have no dependencies
        assert order[0] == "TASK0"


class TestComplexRequirementTraceability:
    """Test complex requirement traceability scenarios including circular references."""
    
    def test_circular_task_dependencies_detection(self):
        """Test detection of circular dependencies in tasks."""
        task1 = ImplementationTask(
            id="TASK1",
            description="First task",
            dependencies=["TASK2"]
        )
        task2 = ImplementationTask(
            id="TASK2",
            description="Second task",
            dependencies=["TASK1"]  # Circular dependency
        )
        
        doc = TasksDocument(tasks=[task1, task2])
        
        # Should validate (circular dependencies are handled in dependency ordering)
        doc.validate()
        
        # But dependency order should handle the cycle
        order = doc.get_dependency_order()
        assert len(order) == 2
        assert "TASK1" in order
        assert "TASK2" in order
    
    def test_complex_requirement_mappings(self):
        """Test complex requirement to component mappings."""
        # Create components that map to multiple requirements
        comp1 = DesignComponent(
            id="COMP1",
            name="Multi-requirement component",
            description="Handles multiple requirements",
            requirement_mappings=["REQ1", "REQ2", "REQ3"]
        )
        comp2 = DesignComponent(
            id="COMP2",
            name="Single-requirement component",
            description="Handles one requirement",
            requirement_mappings=["REQ2"]
        )
        
        # Create requirement mappings where requirements map to multiple components
        requirement_mappings = {
            "REQ1": ["COMP1"],
            "REQ2": ["COMP1", "COMP2"],  # Multiple components
            "REQ3": ["COMP1"]
        }
        
        doc = DesignDocument(
            overview="Complex mapping design",
            architecture="Multi-layered architecture",
            components=[comp1, comp2],
            requirement_mappings=requirement_mappings
        )
        
        doc.validate()
        
        # Test retrieval methods
        req2_components = doc.get_components_for_requirement("REQ2")
        assert len(req2_components) == 2
        assert comp1 in req2_components
        assert comp2 in req2_components
    
    def test_orphaned_requirements_and_tasks(self):
        """Test scenarios with orphaned requirements and tasks."""
        # Create requirements
        criterion1 = AcceptanceCriterion(
            id="AC1",
            when_clause="WHEN user performs action",
            shall_clause="system SHALL respond",
            requirement_id="REQ1"
        )
        req1 = Requirement(
            id="REQ1",
            user_story="As a user, I want action, so that I get response",
            acceptance_criteria=[criterion1]
        )
        
        criterion2 = AcceptanceCriterion(
            id="AC2",
            when_clause="WHEN user performs other action",
            shall_clause="system SHALL process",
            requirement_id="REQ2"
        )
        req2 = Requirement(
            id="REQ2",
            user_story="As a user, I want other action, so that I get processing",
            acceptance_criteria=[criterion2]
        )
        
        # Create tasks that don't cover all requirements
        task1 = ImplementationTask(
            id="TASK1",
            description="Implement first feature",
            requirement_references=["REQ1"]  # REQ2 is orphaned
        )
        task2 = ImplementationTask(
            id="TASK2",
            description="Implement unrelated feature",
            requirement_references=[]  # Orphaned task
        )
        
        req_doc = RequirementsDocument(
            introduction="Test requirements",
            requirements=[req1, req2]
        )
        
        tasks_doc = TasksDocument(
            tasks=[task1, task2],
            requirement_coverage={"REQ1": ["TASK1"]}  # REQ2 not covered
        )
        
        # Documents should validate individually
        req_doc.validate()
        tasks_doc.validate()
        
        # But traceability analysis would detect issues
        # (This would be caught by the ValidationWarningSystem in error_handling.py)


# Error Handling Tests

class TestDocumentGenerationErrorHandling:
    """Test error handling scenarios for document generation exceptions."""
    
    def test_document_generation_error_creation(self):
        """Test DocumentGenerationError creation and properties."""
        error = DocumentGenerationError(
            message="Failed to generate requirements",
            document_type="requirements",
            recoverable=True,
            partial_content={"partial": "data"}
        )
        
        assert str(error) == "Failed to generate requirements"
        assert error.document_type == "requirements"
        assert error.can_recover() is True
        assert error.get_partial_content() == {"partial": "data"}
    
    def test_requirement_parsing_error_creation(self):
        """Test RequirementParsingError creation and properties."""
        error = RequirementParsingError(
            message="Failed to parse objective",
            objective_text="Build a web app",
            parsed_requirements=[{"id": "REQ1", "text": "Partial requirement"}]
        )
        
        assert str(error) == "Failed to parse objective"
        assert error.objective_text == "Build a web app"
        assert len(error.get_partial_requirements()) == 1
    
    def test_requirement_validation_error_creation(self):
        """Test RequirementValidationError creation and properties."""
        error = RequirementValidationError(
            message="Invalid requirement format",
            requirement_id="REQ1",
            severity="warning"
        )
        
        assert str(error) == "Invalid requirement format"
        assert error.requirement_id == "REQ1"
        assert error.is_warning() is True
    
    def test_document_consistency_error_creation(self):
        """Test DocumentConsistencyError creation and properties."""
        error = DocumentConsistencyError(
            message="Requirements and design are inconsistent",
            affected_documents=["requirements.md", "design.md"],
            inconsistencies=[{"type": "missing_mapping", "details": "Missing requirement mapping"}],
            severity="error"
        )
        
        assert str(error) == "Requirements and design are inconsistent"
        assert "requirements.md" in error.affected_documents
        assert len(error.get_inconsistencies()) == 1
        assert error.is_warning() is False