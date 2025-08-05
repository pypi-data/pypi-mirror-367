"""
Requirement-Driven Function Generator for A3 Planning Engine.

This module provides components for generating function specifications that are
directly informed by structured requirements documents, including WHEN/SHALL
statements and requirement traceability.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import re
from datetime import datetime

from .models import (
    RequirementsDocument, Requirement, AcceptanceCriterion,
    EnhancedFunctionSpec, FunctionSpec, Argument, Module,
    DocumentGenerationError, RequirementValidationError,
    FunctionSpecValidationError
)


class RequirementDrivenFunctionGeneratorInterface(ABC):
    """Abstract interface for requirement-driven function generation."""
    
    @abstractmethod
    def generate_function_specifications(self, requirements: RequirementsDocument, modules: List[Module]) -> List[EnhancedFunctionSpec]:
        """
        Generate function specifications with requirement references.
        
        Args:
            requirements: The requirements document to base functions on
            modules: List of modules that need function implementations
            
        Returns:
            List of EnhancedFunctionSpec with requirement traceability
            
        Raises:
            DocumentGenerationError: If function generation fails
        """
        pass
    
    @abstractmethod
    def generate_validation_logic(self, acceptance_criteria: List[AcceptanceCriterion]) -> str:
        """
        Generate validation logic from WHEN/SHALL statements.
        
        Args:
            acceptance_criteria: List of acceptance criteria with WHEN/SHALL statements
            
        Returns:
            Generated validation logic as code string
            
        Raises:
            RequirementValidationError: If validation logic generation fails
        """
        pass
    
    @abstractmethod
    def generate_requirement_comments(self, requirement_references: List[str], requirements: RequirementsDocument) -> str:
        """
        Generate requirement-based comments and documentation.
        
        Args:
            requirement_references: List of requirement IDs to reference
            requirements: The requirements document containing the requirements
            
        Returns:
            Generated comments and documentation as string
            
        Raises:
            DocumentGenerationError: If comment generation fails
        """
        pass
    
    @abstractmethod
    def validate_requirement_coverage(self, functions: List[EnhancedFunctionSpec], requirements: RequirementsDocument) -> Dict[str, Any]:
        """
        Validate requirement coverage for function implementations.
        
        Args:
            functions: List of enhanced function specifications
            requirements: The requirements document to validate against
            
        Returns:
            Dictionary containing coverage analysis results
            
        Raises:
            RequirementValidationError: If coverage validation fails
        """
        pass


class RequirementDrivenFunctionGenerator(RequirementDrivenFunctionGeneratorInterface):
    """Concrete implementation of requirement-driven function generator."""
    
    def __init__(self):
        """Initialize the requirement-driven function generator."""
        self.validation_templates = self._initialize_validation_templates()
        self.comment_templates = self._initialize_comment_templates()
    
    def generate_function_specifications(self, requirements: RequirementsDocument, modules: List[Module]) -> List[EnhancedFunctionSpec]:
        """
        Generate function specifications with requirement references.
        
        This method enhances existing function specifications by:
        - Adding requirement references to function docstrings
        - Mapping functions to relevant requirements based on content analysis
        - Including acceptance criteria implementations
        - Generating validation logic from WHEN/SHALL statements
        
        Args:
            requirements: The requirements document to base functions on
            modules: List of modules that need function implementations
            
        Returns:
            List of EnhancedFunctionSpec with requirement traceability
            
        Raises:
            DocumentGenerationError: If function generation fails
        """
        try:
            enhanced_functions = []
            
            for module in modules:
                for func in module.functions:
                    # Map function to relevant requirements
                    relevant_requirements = self._map_function_to_requirements(func, requirements)
                    
                    # Get acceptance criteria for relevant requirements
                    acceptance_criteria = self._get_acceptance_criteria_for_requirements(relevant_requirements, requirements)
                    
                    # Generate validation logic
                    validation_logic = None
                    if acceptance_criteria:
                        try:
                            validation_logic = self.generate_validation_logic(acceptance_criteria)
                        except RequirementValidationError:
                            # Continue without validation logic if generation fails
                            validation_logic = None
                    
                    # Generate requirement-based comments
                    requirement_comments = self.generate_requirement_comments(
                        [req.id for req in relevant_requirements], 
                        requirements
                    )
                    
                    # Create enhanced function specification
                    enhanced_func = EnhancedFunctionSpec(
                        name=func.name,
                        module=func.module,
                        docstring=self._enhance_docstring(func.docstring, requirement_comments),
                        arguments=func.arguments.copy(),
                        return_type=func.return_type,
                        implementation_status=func.implementation_status,
                        requirement_references=[req.id for req in relevant_requirements],
                        acceptance_criteria_implementations=[ac.id for req in relevant_requirements for ac in req.acceptance_criteria],
                        validation_logic=validation_logic
                    )
                    
                    # Validate the enhanced function specification
                    enhanced_func.validate()
                    enhanced_functions.append(enhanced_func)
            
            return enhanced_functions
            
        except Exception as e:
            raise DocumentGenerationError(f"Failed to generate function specifications: {str(e)}")
    
    def generate_validation_logic(self, acceptance_criteria: List[AcceptanceCriterion]) -> str:
        """
        Generate validation logic from WHEN/SHALL statements.
        
        This method analyzes WHEN/SHALL statements and generates corresponding
        validation logic that can be incorporated into function implementations.
        
        Args:
            acceptance_criteria: List of acceptance criteria with WHEN/SHALL statements
            
        Returns:
            Generated validation logic as code string
            
        Raises:
            RequirementValidationError: If validation logic generation fails
        """
        try:
            if not acceptance_criteria:
                return ""
            
            validation_parts = []
            validation_parts.append("# Generated validation logic from requirements")
            validation_parts.append("")
            
            for criterion in acceptance_criteria:
                # Parse WHEN clause to extract conditions
                when_conditions = self._parse_when_clause(criterion.when_clause)
                
                # Parse SHALL clause to extract expected behavior
                shall_behavior = self._parse_shall_clause(criterion.shall_clause)
                
                # Generate validation code
                validation_code = self._generate_validation_code(when_conditions, shall_behavior, criterion.id)
                
                if validation_code:
                    validation_parts.append(f"# Validation for {criterion.id}")
                    validation_parts.append(validation_code)
                    validation_parts.append("")
            
            return "\n".join(validation_parts)
            
        except Exception as e:
            raise RequirementValidationError(f"Failed to generate validation logic: {str(e)}")
    
    def generate_requirement_comments(self, requirement_references: List[str], requirements: RequirementsDocument) -> str:
        """
        Generate requirement-based comments and documentation.
        
        This method creates comprehensive comments that reference specific
        requirements and their acceptance criteria, providing clear traceability
        from implementation back to requirements.
        
        Args:
            requirement_references: List of requirement IDs to reference
            requirements: The requirements document containing the requirements
            
        Returns:
            Generated comments and documentation as string
            
        Raises:
            DocumentGenerationError: If comment generation fails
        """
        try:
            if not requirement_references:
                return ""
            
            comment_parts = []
            comment_parts.append("Requirements Traceability:")
            comment_parts.append("")
            
            for req_id in requirement_references:
                requirement = requirements.get_requirement_by_id(req_id)
                if requirement:
                    comment_parts.append(f"- {req_id}: {requirement.user_story}")
                    
                    # Add acceptance criteria references
                    if requirement.acceptance_criteria:
                        comment_parts.append("  Acceptance Criteria:")
                        for criterion in requirement.acceptance_criteria:
                            comment_parts.append(f"    - {criterion.id}: {criterion.when_clause} THEN {criterion.shall_clause}")
                    
                    comment_parts.append("")
            
            return "\n".join(comment_parts)
            
        except Exception as e:
            raise DocumentGenerationError(f"Failed to generate requirement comments: {str(e)}")
    
    def validate_requirement_coverage(self, functions: List[EnhancedFunctionSpec], requirements: RequirementsDocument) -> Dict[str, Any]:
        """
        Validate requirement coverage for function implementations.
        
        This method analyzes the mapping between requirements and functions to ensure
        complete coverage and identify any gaps or overlaps in implementation.
        
        Args:
            functions: List of enhanced function specifications
            requirements: The requirements document to validate against
            
        Returns:
            Dictionary containing coverage analysis results including:
            - covered_requirements: List of requirement IDs covered by functions
            - uncovered_requirements: List of requirement IDs not covered
            - function_coverage: Mapping of functions to their requirement coverage
            - coverage_percentage: Overall coverage percentage
            - gaps: List of identified coverage gaps
            
        Raises:
            RequirementValidationError: If coverage validation fails
        """
        try:
            all_requirement_ids = {req.id for req in requirements.requirements}
            covered_requirement_ids = set()
            function_coverage = {}
            
            # Analyze coverage for each function
            for func in functions:
                function_coverage[f"{func.module}.{func.name}"] = {
                    "requirement_references": func.requirement_references.copy(),
                    "acceptance_criteria_count": len(func.acceptance_criteria_implementations),
                    "has_validation_logic": func.has_validation_logic()
                }
                
                # Add to covered requirements
                covered_requirement_ids.update(func.requirement_references)
            
            # Calculate uncovered requirements
            uncovered_requirement_ids = all_requirement_ids - covered_requirement_ids
            
            # Calculate coverage percentage
            coverage_percentage = (len(covered_requirement_ids) / len(all_requirement_ids)) * 100 if all_requirement_ids else 100
            
            # Identify gaps
            gaps = []
            for req_id in uncovered_requirement_ids:
                requirement = requirements.get_requirement_by_id(req_id)
                if requirement:
                    gaps.append({
                        "requirement_id": req_id,
                        "user_story": requirement.user_story,
                        "priority": requirement.priority.value if requirement.priority else "unknown",
                        "acceptance_criteria_count": len(requirement.acceptance_criteria)
                    })
            
            # Analyze requirement distribution
            requirement_distribution = {}
            for func in functions:
                for req_id in func.requirement_references:
                    if req_id not in requirement_distribution:
                        requirement_distribution[req_id] = []
                    requirement_distribution[req_id].append(f"{func.module}.{func.name}")
            
            return {
                "covered_requirements": list(covered_requirement_ids),
                "uncovered_requirements": list(uncovered_requirement_ids),
                "function_coverage": function_coverage,
                "coverage_percentage": coverage_percentage,
                "gaps": gaps,
                "requirement_distribution": requirement_distribution,
                "total_requirements": len(all_requirement_ids),
                "total_functions": len(functions),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise RequirementValidationError(f"Failed to validate requirement coverage: {str(e)}")
    
    def _map_function_to_requirements(self, func: FunctionSpec, requirements: RequirementsDocument) -> List[Requirement]:
        """Map a function to relevant requirements based on content analysis."""
        relevant_requirements = []
        
        # Extract keywords from function
        func_keywords = self._extract_keywords(func.name + " " + func.docstring)
        
        # Score each requirement based on keyword overlap
        requirement_scores = []
        for req in requirements.requirements:
            req_keywords = self._extract_keywords(req.user_story + " " + req.category)
            
            # Calculate similarity score
            common_keywords = func_keywords & req_keywords
            score = len(common_keywords) / max(len(func_keywords), len(req_keywords), 1)
            
            # Boost score for exact name matches
            if func.name.lower() in req.user_story.lower() or req.category.lower() in func.name.lower():
                score += 0.5
            
            # Boost score for function arguments matching requirement terms
            for arg in func.arguments:
                if arg.name.lower() in req.user_story.lower():
                    score += 0.2
            
            requirement_scores.append((req, score))
        
        # Sort by score and take top matches
        requirement_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Include requirements with score > 0.1 or at least the top requirement
        for req, score in requirement_scores:
            if score > 0.1 or (not relevant_requirements and requirement_scores):
                relevant_requirements.append(req)
            elif len(relevant_requirements) >= 3:  # Limit to top 3 requirements per function
                break
        
        # Ensure at least one requirement is mapped if any exist
        if not relevant_requirements and requirements.requirements:
            relevant_requirements.append(requirements.requirements[0])
        
        return relevant_requirements
    
    def _get_acceptance_criteria_for_requirements(self, requirements: List[Requirement], requirements_doc: RequirementsDocument) -> List[AcceptanceCriterion]:
        """Get all acceptance criteria for a list of requirements."""
        acceptance_criteria = []
        for req in requirements:
            acceptance_criteria.extend(req.acceptance_criteria)
        return acceptance_criteria
    
    def _enhance_docstring(self, original_docstring: str, requirement_comments: str) -> str:
        """Enhance function docstring with requirement information."""
        if not requirement_comments:
            return original_docstring
        
        enhanced_parts = [original_docstring]
        
        if requirement_comments:
            enhanced_parts.append("")
            enhanced_parts.append(requirement_comments)
        
        return "\n".join(enhanced_parts)
    
    def _parse_when_clause(self, when_clause: str) -> Dict[str, Any]:
        """Parse WHEN clause to extract conditions."""
        conditions = {
            "triggers": [],
            "preconditions": [],
            "parameters": []
        }
        
        # Simple parsing - could be enhanced with NLP
        when_lower = when_clause.lower()
        
        # Extract trigger events
        trigger_patterns = [
            r'when\s+(\w+)\s+(?:is|are)\s+(\w+)',
            r'when\s+(\w+)\s+(\w+)',
            r'when\s+(.+?)\s+(?:occurs|happens)'
        ]
        
        for pattern in trigger_patterns:
            matches = re.findall(pattern, when_lower)
            for match in matches:
                if isinstance(match, tuple):
                    conditions["triggers"].extend(match)
                else:
                    conditions["triggers"].append(match)
        
        # Extract parameters mentioned
        param_pattern = r'\b([a-zA-Z_]\w*)\b'
        potential_params = re.findall(param_pattern, when_clause)
        conditions["parameters"] = [p for p in potential_params if p not in ['when', 'then', 'shall', 'the', 'a', 'an', 'is', 'are']]
        
        return conditions
    
    def _parse_shall_clause(self, shall_clause: str) -> Dict[str, Any]:
        """Parse SHALL clause to extract expected behavior."""
        behavior = {
            "actions": [],
            "constraints": [],
            "outputs": []
        }
        
        # Simple parsing - could be enhanced with NLP
        shall_lower = shall_clause.lower()
        
        # Extract actions
        action_patterns = [
            r'shall\s+(\w+)',
            r'must\s+(\w+)',
            r'should\s+(\w+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, shall_lower)
            behavior["actions"].extend(matches)
        
        # Extract constraints
        if 'not' in shall_lower or 'cannot' in shall_lower or 'must not' in shall_lower:
            behavior["constraints"].append("negative_constraint")
        
        if 'within' in shall_lower or 'before' in shall_lower or 'after' in shall_lower:
            behavior["constraints"].append("temporal_constraint")
        
        return behavior
    
    def _generate_validation_code(self, when_conditions: Dict[str, Any], shall_behavior: Dict[str, Any], criterion_id: str) -> str:
        """Generate validation code from parsed conditions and behavior."""
        code_parts = []
        
        # Generate condition checks
        if when_conditions.get("parameters"):
            params = when_conditions["parameters"][:3]  # Limit to first 3 parameters
            for param in params:
                code_parts.append(f"if {param} is None:")
                code_parts.append(f"    raise ValueError(f'Parameter {param} is required for {criterion_id}')")
        
        # Generate behavior validation
        if shall_behavior.get("actions"):
            actions = shall_behavior["actions"][:2]  # Limit to first 2 actions
            for action in actions:
                if action in ['return', 'provide', 'generate']:
                    code_parts.append(f"# Ensure {action} behavior is implemented")
                elif action in ['validate', 'check', 'verify']:
                    code_parts.append(f"# Implement {action} logic")
        
        # Add constraint validation
        if "negative_constraint" in shall_behavior.get("constraints", []):
            code_parts.append("# Implement negative constraint validation")
        
        if "temporal_constraint" in shall_behavior.get("constraints", []):
            code_parts.append("# Implement temporal constraint validation")
        
        return "\n".join(code_parts) if code_parts else ""
    
    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text."""
        # Common words to exclude
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'them', 'their', 'when', 'then', 'if', 'else', 'as'
        }
        
        # Extract words and filter
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = {word for word in words if len(word) > 2 and word not in common_words}
        
        return keywords
    
    def _initialize_validation_templates(self) -> Dict[str, str]:
        """Initialize validation code templates."""
        return {
            "parameter_check": "if {param} is None:\n    raise ValueError('Parameter {param} is required')",
            "type_check": "if not isinstance({param}, {type}):\n    raise TypeError('Parameter {param} must be of type {type}')",
            "range_check": "if not ({min} <= {param} <= {max}):\n    raise ValueError('Parameter {param} must be between {min} and {max}')",
            "not_empty_check": "if not {param}:\n    raise ValueError('Parameter {param} cannot be empty')"
        }
    
    def _initialize_comment_templates(self) -> Dict[str, str]:
        """Initialize comment generation templates."""
        return {
            "requirement_header": "Requirements Traceability:",
            "requirement_item": "- {req_id}: {user_story}",
            "acceptance_criteria_header": "  Acceptance Criteria:",
            "acceptance_criteria_item": "    - {ac_id}: {when_clause} THEN {shall_clause}"
        }