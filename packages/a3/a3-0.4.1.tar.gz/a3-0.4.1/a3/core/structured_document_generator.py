"""
Structured Document Generator for A3 Planning Engine.

This module provides components for generating structured documentation files
(requirements.md, design.md, tasks.md) that inform function generation with
formal requirements specifications.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

from .models import (
    RequirementsDocument, Requirement, AcceptanceCriterion, RequirementPriority,
    DesignDocument, DesignComponent, TasksDocument, ImplementationTask,
    Module, FunctionSpec, DocumentationConfiguration,
    DocumentGenerationError, RequirementParsingError
)
from .requirement_parser import RequirementParser, RequirementParsingContext


class StructuredDocumentGeneratorInterface(ABC):
    """Abstract interface for structured document generation."""
    
    @abstractmethod
    def generate_requirements_document(self, objective: str, context: Dict[str, Any]) -> RequirementsDocument:
        """
        Generate structured requirements document from objective.
        
        Args:
            objective: The project objective or description
            context: Additional context information
            
        Returns:
            RequirementsDocument: Structured requirements with EARS format
            
        Raises:
            DocumentGenerationError: If document generation fails
        """
        pass
    
    @abstractmethod
    def generate_design_document(self, requirements: RequirementsDocument, modules: List[Module]) -> DesignDocument:
        """
        Generate design document with requirement traceability.
        
        Args:
            requirements: The requirements document to base design on
            modules: List of modules in the project
            
        Returns:
            DesignDocument: Design document with requirement mappings
            
        Raises:
            DocumentGenerationError: If document generation fails
        """
        pass
    
    @abstractmethod
    def generate_tasks_document(self, requirements: RequirementsDocument, design: DesignDocument) -> TasksDocument:
        """
        Generate implementation tasks with requirement mappings.
        
        Args:
            requirements: The requirements document
            design: The design document
            
        Returns:
            TasksDocument: Tasks document with requirement and design mappings
            
        Raises:
            DocumentGenerationError: If document generation fails
        """
        pass


class StructuredDocumentGenerator(StructuredDocumentGeneratorInterface):
    """Concrete implementation of structured document generator."""
    
    def __init__(self, requirement_parser: Optional[RequirementParser] = None):
        """
        Initialize the structured document generator.
        
        Args:
            requirement_parser: Optional requirement parser instance
        """
        self.requirement_parser = requirement_parser
    
    def generate_requirements_document(self, objective: str, context: Dict[str, Any]) -> RequirementsDocument:
        """
        Generate structured requirements document from objective.
        
        This method creates a comprehensive requirements document with:
        - Clear introduction summarizing the feature
        - Hierarchical numbered requirements with user stories
        - EARS format acceptance criteria (WHEN/SHALL statements)
        - Proper requirement validation
        
        Args:
            objective: The project objective or description
            context: Additional context information including:
                - existing_modules: List of existing modules
                - project_type: Type of project (web, cli, library, etc.)
                - constraints: Any technical constraints
                - stakeholders: Target users or stakeholders
                
        Returns:
            RequirementsDocument: Structured requirements with EARS format
            
        Raises:
            DocumentGenerationError: If document generation fails
        """
        try:
            # Create parsing context
            parsing_context = RequirementParsingContext(
                objective=objective,
                domain=context.get('project_type', 'general'),
                constraints=context.get('constraints', []),
                stakeholders=context.get('stakeholders', ['developer'])
            )
            
            # Use requirement parser to generate structured requirements
            if self.requirement_parser is None:
                raise DocumentGenerationError("RequirementParser is required but not provided")
            
            requirements_doc = self.requirement_parser.parse_objective(parsing_context)
            
            # Validate the generated document
            self._validate_requirements_document(requirements_doc)
            
            return requirements_doc
            
        except RequirementParsingError as e:
            raise DocumentGenerationError(f"Failed to parse requirements: {str(e)}")
        except Exception as e:
            raise DocumentGenerationError(f"Failed to generate requirements document: {str(e)}")
    
    def generate_design_document(self, requirements: RequirementsDocument, modules: List[Module]) -> DesignDocument:
        """
        Generate design document with requirement traceability.
        
        This method creates a comprehensive design document that:
        - References specific requirements using requirement IDs
        - Includes architectural decisions that satisfy WHEN/SHALL requirements
        - Specifies how each module addresses particular requirements
        - Ensures all requirements have corresponding design elements
        
        Args:
            requirements: The requirements document to base design on
            modules: List of modules in the project
            
        Returns:
            DesignDocument: Design document with requirement mappings
            
        Raises:
            DocumentGenerationError: If document generation fails
        """
        try:
            # Generate overview section
            overview = self._generate_design_overview(requirements, modules)
            
            # Generate architecture section
            architecture = self._generate_architecture_section(requirements, modules)
            
            # Generate design components with requirement traceability
            components = self._generate_design_components(requirements, modules)
            
            # Create requirement mappings
            requirement_mappings = self._create_requirement_mappings(requirements, components)
            
            # Create design document
            design_doc = DesignDocument(
                overview=overview,
                architecture=architecture,
                components=components,
                requirement_mappings=requirement_mappings,
                created_at=datetime.now()
            )
            
            # Validate the design document
            self._validate_design_document(design_doc, requirements)
            
            return design_doc
            
        except Exception as e:
            raise DocumentGenerationError(f"Failed to generate design document: {str(e)}")
    
    def generate_tasks_document(self, requirements: RequirementsDocument, design: DesignDocument) -> TasksDocument:
        """
        Generate implementation tasks with requirement mappings.
        
        This method creates a comprehensive tasks document that:
        - References both requirements and design elements for each task
        - Includes requirement IDs that each task satisfies
        - Specifies which WHEN/SHALL statements functions must implement
        - Ensures complete coverage of all requirements and design elements
        
        Args:
            requirements: The requirements document
            design: The design document
            
        Returns:
            TasksDocument: Tasks document with requirement and design mappings
            
        Raises:
            DocumentGenerationError: If document generation fails
        """
        try:
            # Generate implementation tasks
            tasks = self._generate_implementation_tasks(requirements, design)
            
            # Create requirement coverage mapping
            requirement_coverage = self._create_requirement_coverage(requirements, tasks)
            
            # Create design coverage mapping
            design_coverage = self._create_design_coverage(design, tasks)
            
            # Create tasks document
            tasks_doc = TasksDocument(
                tasks=tasks,
                requirement_coverage=requirement_coverage,
                design_coverage=design_coverage,
                created_at=datetime.now()
            )
            
            # Validate the tasks document
            self._validate_tasks_document(tasks_doc, requirements, design)
            
            return tasks_doc
            
        except Exception as e:
            raise DocumentGenerationError(f"Failed to generate tasks document: {str(e)}")
    
    def _validate_requirements_document(self, doc: RequirementsDocument) -> None:
        """Validate requirements document structure and content."""
        if not doc.introduction or not doc.introduction.strip():
            raise DocumentGenerationError("Requirements document must have a non-empty introduction")
        
        if not doc.requirements:
            raise DocumentGenerationError("Requirements document must have at least one requirement")
        
        # Validate each requirement has proper WHEN/SHALL statements
        for req in doc.requirements:
            if not req.acceptance_criteria:
                raise DocumentGenerationError(f"Requirement {req.id} must have acceptance criteria")
            
            for criterion in req.acceptance_criteria:
                if not criterion.when_clause or not criterion.shall_clause:
                    raise DocumentGenerationError(
                        f"Acceptance criterion {criterion.id} must have both WHEN and SHALL clauses"
                    )
    
    def _validate_design_document(self, doc: DesignDocument, requirements: RequirementsDocument) -> None:
        """Validate design document has proper requirement traceability."""
        if not doc.overview or not doc.overview.strip():
            raise DocumentGenerationError("Design document must have a non-empty overview")
        
        if not doc.architecture or not doc.architecture.strip():
            raise DocumentGenerationError("Design document must have a non-empty architecture section")
        
        # Check that all requirements are mapped to design components
        req_ids = {req.id for req in requirements.requirements}
        mapped_req_ids = set(doc.requirement_mappings.keys())
        
        unmapped_requirements = req_ids - mapped_req_ids
        if unmapped_requirements:
            raise DocumentGenerationError(
                f"Requirements not mapped to design components: {unmapped_requirements}"
            )
    
    def _validate_tasks_document(self, doc: TasksDocument, requirements: RequirementsDocument, design: DesignDocument) -> None:
        """Validate tasks document has complete coverage."""
        if not doc.tasks:
            raise DocumentGenerationError("Tasks document must have at least one task")
        
        # Check requirement coverage
        req_ids = {req.id for req in requirements.requirements}
        covered_req_ids = set(doc.requirement_coverage.keys())
        
        uncovered_requirements = req_ids - covered_req_ids
        if uncovered_requirements:
            raise DocumentGenerationError(
                f"Requirements not covered by tasks: {uncovered_requirements}"
            )
        
        # Check design coverage
        component_ids = {comp.id for comp in design.components}
        covered_component_ids = set(doc.design_coverage.keys())
        
        uncovered_components = component_ids - covered_component_ids
        if uncovered_components:
            raise DocumentGenerationError(
                f"Design components not covered by tasks: {uncovered_components}"
            )   
 
    def _generate_design_overview(self, requirements: RequirementsDocument, modules: List[Module]) -> str:
        """Generate the overview section of the design document."""
        overview_parts = [
            "# Design Overview\n",
            f"This design document addresses the requirements outlined in the requirements specification. ",
            f"The system will be implemented across {len(modules)} modules to satisfy {len(requirements.requirements)} requirements.\n\n",
            "## Key Design Principles\n",
            "- Requirement traceability: Each design component maps to specific requirements\n",
            "- Modular architecture: Clear separation of concerns across modules\n",
            "- WHEN/SHALL compliance: Design elements directly address acceptance criteria\n",
            "- Maintainability: Clear interfaces and well-defined responsibilities\n\n"
        ]
        
        # Add requirement summary
        overview_parts.append("## Requirements Summary\n")
        for req in requirements.requirements:
            overview_parts.append(f"- **{req.id}**: {req.user_story}\n")
        
        return "".join(overview_parts)
    
    def _generate_architecture_section(self, requirements: RequirementsDocument, modules: List[Module]) -> str:
        """Generate the architecture section of the design document."""
        arch_parts = [
            "# System Architecture\n\n",
            "## Module Structure\n",
            "The system is organized into the following modules:\n\n"
        ]
        
        for module in modules:
            arch_parts.append(f"### {module.name}\n")
            arch_parts.append(f"**Purpose**: {module.description}\n")
            arch_parts.append(f"**Location**: {module.file_path}\n")
            
            if module.dependencies:
                arch_parts.append(f"**Dependencies**: {', '.join(module.dependencies)}\n")
            
            if module.functions:
                arch_parts.append(f"**Functions**: {len(module.functions)} functions\n")
            
            arch_parts.append("\n")
        
        # Add dependency flow
        arch_parts.append("## Dependency Flow\n")
        arch_parts.append("The modules are organized to minimize circular dependencies and ensure clear data flow:\n\n")
        
        for module in modules:
            if module.dependencies:
                arch_parts.append(f"- {module.name} depends on: {', '.join(module.dependencies)}\n")
        
        return "".join(arch_parts)
    
    def _generate_design_components(self, requirements: RequirementsDocument, modules: List[Module]) -> List[DesignComponent]:
        """Generate design components with requirement traceability."""
        components = []
        
        for module in modules:
            # Create a design component for each module
            component = DesignComponent(
                id=f"component_{module.name}",
                name=module.name,
                description=module.description,
                responsibilities=self._extract_responsibilities(module),
                interfaces=self._extract_interfaces(module),
                requirement_mappings=self._map_module_to_requirements(module, requirements)
            )
            components.append(component)
            
            # Create components for major functions if they warrant separate design consideration
            for func in module.functions:
                if self._is_major_function(func):
                    func_component = DesignComponent(
                        id=f"component_{module.name}_{func.name}",
                        name=f"{module.name}.{func.name}",
                        description=func.docstring,
                        responsibilities=[f"Implement {func.name} functionality"],
                        interfaces=[self._create_function_interface(func)],
                        requirement_mappings=self._map_function_to_requirements(func, requirements)
                    )
                    components.append(func_component)
        
        return components
    
    def _extract_responsibilities(self, module: Module) -> List[str]:
        """Extract responsibilities from module description and functions."""
        responsibilities = [module.description]
        
        # Add function-based responsibilities
        for func in module.functions:
            if func.docstring:
                # Extract first sentence as responsibility
                first_sentence = func.docstring.split('.')[0].strip()
                if first_sentence and first_sentence not in responsibilities:
                    responsibilities.append(f"Provide {first_sentence.lower()}")
        
        return responsibilities
    
    def _extract_interfaces(self, module: Module) -> List[str]:
        """Extract interface definitions from module functions."""
        interfaces = []
        
        for func in module.functions:
            interface = self._create_function_interface(func)
            interfaces.append(interface)
        
        return interfaces
    
    def _create_function_interface(self, func: FunctionSpec) -> str:
        """Create interface definition for a function."""
        args_str = ", ".join([f"{arg.name}: {arg.type_hint}" for arg in func.arguments])
        return f"{func.name}({args_str}) -> {func.return_type}"
    
    def _map_module_to_requirements(self, module: Module, requirements: RequirementsDocument) -> List[str]:
        """Map module to relevant requirements based on content analysis."""
        relevant_reqs = []
        
        # Simple keyword matching for now - could be enhanced with NLP
        module_keywords = self._extract_keywords(module.description + " " + module.name)
        
        for req in requirements.requirements:
            req_keywords = self._extract_keywords(req.user_story + " " + req.category)
            
            # If there's keyword overlap, consider it relevant
            if module_keywords & req_keywords:
                relevant_reqs.append(req.id)
            # Also check if module name is related to requirement category
            elif module.name.lower() in req.category.lower() or req.category.lower() in module.name.lower():
                relevant_reqs.append(req.id)
            # Check if any function names relate to requirements
            elif any(self._extract_keywords(func.name + " " + func.docstring) & req_keywords for func in module.functions):
                relevant_reqs.append(req.id)
        
        # If no matches found, assign to first requirement as fallback
        if not relevant_reqs and requirements.requirements:
            relevant_reqs.append(requirements.requirements[0].id)
        
        return relevant_reqs
    
    def _map_function_to_requirements(self, func: FunctionSpec, requirements: RequirementsDocument) -> List[str]:
        """Map function to relevant requirements based on content analysis."""
        relevant_reqs = []
        
        func_keywords = self._extract_keywords(func.docstring + " " + func.name)
        
        for req in requirements.requirements:
            req_keywords = self._extract_keywords(req.user_story + " " + req.category)
            
            if func_keywords & req_keywords:
                relevant_reqs.append(req.id)
            # Check if function name relates to requirement category
            elif func.name.lower() in req.category.lower() or req.category.lower() in func.name.lower():
                relevant_reqs.append(req.id)
        
        # If no matches found, assign to first requirement as fallback
        if not relevant_reqs and requirements.requirements:
            relevant_reqs.append(requirements.requirements[0].id)
        
        return relevant_reqs
    
    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction - remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their'}
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = {word for word in words if len(word) > 2 and word not in common_words}
        
        return keywords
    
    def _is_major_function(self, func: FunctionSpec) -> bool:
        """Determine if a function warrants its own design component."""
        # Consider functions major if they have complex signatures or long docstrings
        return len(func.arguments) > 3 or len(func.docstring) > 100
    
    def _create_requirement_mappings(self, requirements: RequirementsDocument, components: List[DesignComponent]) -> Dict[str, List[str]]:
        """Create mapping from requirements to design components."""
        mappings = {}
        
        for req in requirements.requirements:
            mappings[req.id] = []
            
            for component in components:
                if req.id in component.requirement_mappings:
                    mappings[req.id].append(component.id)
        
        return mappings
    
    def _generate_implementation_tasks(self, requirements: RequirementsDocument, design: DesignDocument) -> List[ImplementationTask]:
        """Generate implementation tasks based on requirements and design."""
        tasks = []
        task_counter = 1
        
        # Create tasks for each design component
        for component in design.components:
            # Main implementation task for the component
            main_task = ImplementationTask(
                id=f"task_{task_counter}",
                description=f"Implement {component.name} component according to design specifications",
                requirement_references=component.requirement_mappings,
                design_references=[component.id],
                estimated_effort="medium",
                dependencies=[]
            )
            tasks.append(main_task)
            task_counter += 1
            
            # Create sub-tasks for complex components
            if len(component.interfaces) > 2:
                for interface in component.interfaces:
                    sub_task = ImplementationTask(
                        id=f"task_{task_counter}",
                        description=f"Implement the {interface} interface",
                        requirement_references=component.requirement_mappings,
                        design_references=[component.id],
                        estimated_effort="small",
                        dependencies=[main_task.id]
                    )
                    tasks.append(sub_task)
                    task_counter += 1
        
        # Create integration tasks
        integration_task = ImplementationTask(
            id=f"task_{task_counter}",
            description="Integrate all components and perform end-to-end testing",
            requirement_references=[req.id for req in requirements.requirements],
            design_references=[comp.id for comp in design.components],
            estimated_effort="large",
            dependencies=[task.id for task in tasks]
        )
        tasks.append(integration_task)
        
        return tasks
    

    
    def _create_requirement_coverage(self, requirements: RequirementsDocument, tasks: List[ImplementationTask]) -> Dict[str, List[str]]:
        """Create mapping from requirements to tasks that cover them."""
        coverage = {}
        
        for req in requirements.requirements:
            coverage[req.id] = []
            
            for task in tasks:
                if req.id in task.requirement_references:
                    coverage[req.id].append(task.id)
        
        return coverage
    
    def _create_design_coverage(self, design: DesignDocument, tasks: List[ImplementationTask]) -> Dict[str, List[str]]:
        """Create mapping from design components to tasks that implement them."""
        coverage = {}
        
        for component in design.components:
            coverage[component.id] = []
            
            for task in tasks:
                if component.id in task.design_references:
                    coverage[component.id].append(task.id)
        
        return coverage