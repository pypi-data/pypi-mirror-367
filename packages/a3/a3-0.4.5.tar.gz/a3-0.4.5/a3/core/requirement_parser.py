"""
RequirementParser component for parsing objectives into structured requirements.

This module provides functionality to extract and structure requirements from
project objectives, generating WHEN/SHALL statements and user stories.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .models import (
    RequirementsDocument, Requirement, AcceptanceCriterion, RequirementPriority,
    RequirementParsingError, RequirementValidationError
)
from .interfaces import AIClientInterface


@dataclass
class RequirementParsingContext:
    """Context information for requirement parsing."""
    objective: str
    domain: Optional[str] = None
    stakeholders: List[str] = None
    constraints: List[str] = None
    existing_requirements: List[Requirement] = None
    
    def __post_init__(self):
        if self.stakeholders is None:
            self.stakeholders = []
        if self.constraints is None:
            self.constraints = []
        if self.existing_requirements is None:
            self.existing_requirements = []


class RequirementParser:
    """
    Component for parsing objectives into structured requirements with WHEN/SHALL statements.
    
    This class provides capabilities to:
    - Parse natural language objectives into structured requirements
    - Generate WHEN/SHALL statements from functional descriptions
    - Create user stories for major functional areas
    - Validate requirement completeness and consistency
    """
    
    def __init__(self, ai_client: AIClientInterface):
        """Initialize the RequirementParser with an AI client."""
        self.ai_client = ai_client
        self._functional_keywords = [
            "should", "must", "shall", "will", "needs to", "has to", "requires",
            "enables", "allows", "provides", "supports", "implements", "generates"
        ]
        self._condition_keywords = [
            "when", "if", "after", "before", "during", "while", "upon", "once",
            "whenever", "in case", "provided that", "given that"
        ]
    
    def parse_objective(self, context: RequirementParsingContext) -> RequirementsDocument:
        """
        Parse an objective into a structured requirements document.
        
        Args:
            context: The parsing context containing objective and additional information
            
        Returns:
            RequirementsDocument: Structured requirements document
            
        Raises:
            RequirementParsingError: If parsing fails
        """
        try:
            # Validate input
            if not context.objective or not context.objective.strip():
                raise RequirementParsingError("Objective cannot be empty")
            
            # Extract functional requirements from objective
            functional_requirements = self._extract_functional_requirements(context.objective)
            
            # Ensure we have at least one requirement
            if not functional_requirements:
                functional_requirements = [{
                    'description': context.objective,
                    'stakeholder': 'user',
                    'benefit': 'achieve the stated objective',
                    'conditions': [],
                    'priority': 'HIGH',
                    'category': 'Core Functionality'
                }]
            
            # Generate requirements with user stories and acceptance criteria
            requirements = []
            for i, func_req in enumerate(functional_requirements, 1):
                requirement = self._create_requirement_from_functional(
                    func_req, f"REQ-{i:03d}", context
                )
                requirements.append(requirement)
            
            # Generate introduction
            introduction = self._generate_introduction(context.objective, requirements)
            
            # Create requirements document
            doc = RequirementsDocument(
                introduction=introduction,
                requirements=requirements
            )
            
            # Validate the document
            doc.validate()
            
            return doc
            
        except Exception as e:
            raise RequirementParsingError(f"Failed to parse objective: {str(e)}") from e
    
    def _extract_functional_requirements(self, objective: str) -> List[Dict[str, Any]]:
        """Extract functional requirements from the objective text."""
        # Use AI to extract structured functional requirements
        prompt = f"""
        Analyze the following objective and extract distinct functional requirements:
        
        Objective: {objective}
        
        For each functional requirement, provide:
        1. A clear functional description
        2. The primary stakeholder/user role
        3. The main benefit or purpose
        4. Any conditions or triggers
        5. Priority level (HIGH, MEDIUM, LOW)
        6. Category (e.g., "Core Functionality", "User Interface", "Data Management")
        
        Return the analysis in a structured format that clearly separates each requirement.
        Focus on what the system must DO, not how it should be implemented.
        """
        
        try:
            response = self.ai_client.generate_with_retry(prompt, max_retries=2)
            return self._parse_ai_functional_requirements(response)
        except Exception as e:
            # Fallback to rule-based extraction
            return self._rule_based_functional_extraction(objective)
    
    def _parse_ai_functional_requirements(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured functional requirements."""
        requirements = []
        
        # Split response into sections (assuming AI structures the response)
        sections = re.split(r'\n\s*(?:\d+\.|\*|\-)\s*', ai_response)
        
        for section in sections[1:]:  # Skip first empty section
            if not section.strip():
                continue
                
            req_data = self._extract_requirement_data_from_text(section)
            if req_data:
                requirements.append(req_data)
        
        # If no requirements were extracted, fall back to rule-based extraction
        if not requirements:
            return self._rule_based_functional_extraction(ai_response)
        
        return requirements
    
    def _extract_requirement_data_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract requirement data from a text section."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return None
        
        # Look for description line
        description = lines[0]
        for line in lines:
            if line.lower().startswith('description:'):
                description = line.split(':', 1)[1].strip()
                break
        
        req_data = {
            'description': description,
            'stakeholder': 'user',
            'benefit': 'system functionality',
            'conditions': [],
            'priority': 'MEDIUM',
            'category': 'Core Functionality'
        }
        
        # Extract structured information from remaining lines
        for line in lines:
            line_lower = line.lower()
            if line_lower.startswith('description:'):
                req_data['description'] = line.split(':', 1)[1].strip()
            elif line_lower.startswith('stakeholder:'):
                req_data['stakeholder'] = line.split(':', 1)[1].strip()
            elif line_lower.startswith('benefit:'):
                req_data['benefit'] = line.split(':', 1)[1].strip()
            elif line_lower.startswith('conditions:'):
                conditions_text = line.split(':', 1)[1].strip()
                req_data['conditions'] = [c.strip() for c in conditions_text.split(',') if c.strip()]
            elif line_lower.startswith('priority:'):
                req_data['priority'] = line.split(':', 1)[1].strip().upper()
            elif line_lower.startswith('category:'):
                req_data['category'] = line.split(':', 1)[1].strip()
            elif 'stakeholder' in line_lower or 'user' in line_lower or 'role' in line_lower:
                req_data['stakeholder'] = self._extract_stakeholder(line)
            elif 'benefit' in line_lower or 'purpose' in line_lower:
                req_data['benefit'] = self._extract_benefit(line)
            elif 'condition' in line_lower or 'trigger' in line_lower:
                req_data['conditions'].extend(self._extract_conditions(line))
            elif 'priority' in line_lower:
                req_data['priority'] = self._extract_priority(line)
            elif 'category' in line_lower:
                req_data['category'] = self._extract_category(line)
        
        return req_data
    
    def _rule_based_functional_extraction(self, objective: str) -> List[Dict[str, Any]]:
        """Fallback rule-based extraction of functional requirements."""
        requirements = []
        
        # Split objective into sentences
        sentences = re.split(r'[.!?]+', objective)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains functional keywords
            if any(keyword in sentence.lower() for keyword in self._functional_keywords):
                req_data = {
                    'description': sentence,
                    'stakeholder': self._infer_stakeholder(sentence),
                    'benefit': self._infer_benefit(sentence),
                    'conditions': self._extract_conditions_from_sentence(sentence),
                    'priority': self._infer_priority(sentence),
                    'category': self._infer_category(sentence)
                }
                requirements.append(req_data)
        
        # Ensure we have at least one requirement
        if not requirements:
            requirements.append({
                'description': objective,
                'stakeholder': 'user',
                'benefit': 'achieve the stated objective',
                'conditions': [],
                'priority': 'HIGH',
                'category': 'Core Functionality'
            })
        
        return requirements
    
    def _create_requirement_from_functional(
        self, 
        func_req: Dict[str, Any], 
        req_id: str, 
        context: RequirementParsingContext
    ) -> Requirement:
        """Create a Requirement object from functional requirement data."""
        
        # Generate user story
        user_story = self._generate_user_story(
            func_req['stakeholder'],
            func_req['description'],
            func_req['benefit']
        )
        
        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(
            func_req, req_id
        )
        
        # Map priority string to enum
        priority_map = {
            'HIGH': RequirementPriority.HIGH,
            'MEDIUM': RequirementPriority.MEDIUM,
            'LOW': RequirementPriority.LOW
        }
        priority = priority_map.get(func_req['priority'], RequirementPriority.MEDIUM)
        
        return Requirement(
            id=req_id,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            priority=priority,
            category=func_req['category']
        )
    
    def _generate_user_story(self, stakeholder: str, description: str, benefit: str) -> str:
        """Generate a user story in the standard format."""
        # Clean and format stakeholder
        stakeholder = stakeholder.lower().strip()
        if not stakeholder.startswith('a '):
            stakeholder = f"a {stakeholder}"
        
        # Clean description to extract the "want" part
        want_part = description
        if any(keyword in description.lower() for keyword in self._functional_keywords):
            # Extract the action part
            for keyword in self._functional_keywords:
                if keyword in description.lower():
                    parts = description.lower().split(keyword, 1)
                    if len(parts) > 1:
                        want_part = keyword + parts[1]
                    break
        
        # Clean benefit
        benefit = benefit.strip()
        if not benefit.startswith('so that'):
            benefit = f"so that {benefit}"
        
        return f"As {stakeholder}, I want {want_part}, {benefit}"
    
    def _generate_acceptance_criteria(
        self, 
        func_req: Dict[str, Any], 
        req_id: str
    ) -> List[AcceptanceCriterion]:
        """Generate acceptance criteria in EARS format."""
        criteria = []
        
        # Generate primary acceptance criterion
        when_clause, shall_clause = self._convert_to_when_shall(func_req['description'])
        
        primary_criterion = AcceptanceCriterion(
            id=f"{req_id}-AC-001",
            when_clause=when_clause,
            shall_clause=shall_clause,
            requirement_id=req_id
        )
        criteria.append(primary_criterion)
        
        # Generate additional criteria from conditions
        for i, condition in enumerate(func_req['conditions'], 2):
            when_clause, shall_clause = self._convert_condition_to_when_shall(
                condition, func_req['description']
            )
            
            criterion = AcceptanceCriterion(
                id=f"{req_id}-AC-{i:03d}",
                when_clause=when_clause,
                shall_clause=shall_clause,
                requirement_id=req_id
            )
            criteria.append(criterion)
        
        return criteria
    
    def _convert_to_when_shall(self, description: str) -> Tuple[str, str]:
        """Convert a functional description to WHEN/SHALL format."""
        # Look for existing conditions
        when_clause = "WHEN the system is operational"
        shall_clause = f"THEN the system SHALL {description.lower()}"
        
        # Check if description already contains condition keywords
        for keyword in self._condition_keywords:
            if keyword in description.lower():
                parts = description.lower().split(keyword, 1)
                if len(parts) > 1:
                    when_clause = f"WHEN {keyword} {parts[1].strip()}"
                    shall_clause = f"THEN the system SHALL {parts[0].strip()}"
                break
        
        # Clean up the SHALL clause
        shall_clause = self._clean_shall_clause(shall_clause)
        
        return when_clause, shall_clause
    
    def _convert_condition_to_when_shall(self, condition: str, description: str) -> Tuple[str, str]:
        """Convert a condition and description to WHEN/SHALL format."""
        when_clause = f"WHEN {condition.strip()}"
        shall_clause = f"THEN the system SHALL {description.lower()}"
        
        # Clean up clauses
        when_clause = self._clean_when_clause(when_clause)
        shall_clause = self._clean_shall_clause(shall_clause)
        
        return when_clause, shall_clause
    
    def _clean_when_clause(self, when_clause: str) -> str:
        """Clean and standardize WHEN clause."""
        when_clause = when_clause.strip()
        if not when_clause.upper().startswith("WHEN"):
            when_clause = f"WHEN {when_clause}"
        return when_clause
    
    def _clean_shall_clause(self, shall_clause: str) -> str:
        """Clean and standardize SHALL clause."""
        shall_clause = shall_clause.strip()
        if not shall_clause.upper().startswith("THEN"):
            shall_clause = f"THEN {shall_clause}"
        if "SHALL" not in shall_clause.upper():
            # Insert SHALL after "the system" or at the beginning
            if "the system" in shall_clause.lower():
                shall_clause = shall_clause.replace("the system", "the system SHALL", 1)
            else:
                # Insert SHALL after THEN
                shall_clause = shall_clause.replace("THEN", "THEN the system SHALL", 1)
        return shall_clause
    
    def _generate_introduction(self, objective: str, requirements: List[Requirement]) -> str:
        """Generate an introduction for the requirements document."""
        return f"""This requirements document defines the functional and non-functional requirements for the system based on the following objective:

{objective}

The document contains {len(requirements)} requirements organized into the following categories:
{self._get_category_summary(requirements)}

Each requirement includes a user story and acceptance criteria in EARS (Easy Approach to Requirements Syntax) format using WHEN/SHALL statements to ensure clear, testable requirements."""
    
    def _get_category_summary(self, requirements: List[Requirement]) -> str:
        """Generate a summary of requirement categories."""
        categories = {}
        for req in requirements:
            categories[req.category] = categories.get(req.category, 0) + 1
        
        summary_lines = []
        for category, count in sorted(categories.items()):
            summary_lines.append(f"- {category}: {count} requirement{'s' if count != 1 else ''}")
        
        return '\n'.join(summary_lines)
    
    # Helper methods for extraction
    def _extract_stakeholder(self, text: str) -> str:
        """Extract stakeholder from text."""
        # Simple pattern matching for common stakeholder patterns
        patterns = [
            r'(?:stakeholder|user|role):\s*([^,\n]+)',
            r'(?:as\s+a\s+)([^,\n]+)',
            r'([^,\n]+)\s+(?:user|stakeholder)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "user"
    
    def _extract_benefit(self, text: str) -> str:
        """Extract benefit from text."""
        patterns = [
            r'(?:benefit|purpose):\s*([^,\n]+)',
            r'(?:so\s+that\s+)([^,\n]+)',
            r'(?:to\s+)([^,\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "achieve system functionality"
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Extract conditions from text."""
        conditions = []
        for keyword in self._condition_keywords:
            pattern = f'{keyword}\\s+([^,\n]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            conditions.extend([match.strip() for match in matches])
        
        return conditions
    
    def _extract_conditions_from_sentence(self, sentence: str) -> List[str]:
        """Extract conditions from a single sentence."""
        conditions = []
        for keyword in self._condition_keywords:
            if keyword in sentence.lower():
                parts = sentence.lower().split(keyword, 1)
                if len(parts) > 1:
                    condition = parts[1].strip()
                    if condition:
                        conditions.append(condition)
        
        return conditions
    
    def _extract_priority(self, text: str) -> str:
        """Extract priority from text."""
        text_upper = text.upper()
        if 'HIGH' in text_upper or 'CRITICAL' in text_upper:
            return 'HIGH'
        elif 'LOW' in text_upper:
            return 'LOW'
        else:
            return 'MEDIUM'
    
    def _extract_category(self, text: str) -> str:
        """Extract category from text."""
        patterns = [
            r'(?:category):\s*([^,\n]+)',
            r'([^,\n]+)\s+(?:category|type)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Core Functionality"
    
    def _infer_stakeholder(self, sentence: str) -> str:
        """Infer stakeholder from sentence context."""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['admin', 'administrator']):
            return "administrator"
        elif any(word in sentence_lower for word in ['developer', 'programmer']):
            return "developer"
        elif any(word in sentence_lower for word in ['manager', 'supervisor']):
            return "manager"
        else:
            return "user"
    
    def _infer_benefit(self, sentence: str) -> str:
        """Infer benefit from sentence context."""
        sentence_lower = sentence.lower()
        
        if 'efficient' in sentence_lower:
            return "improve efficiency"
        elif 'secure' in sentence_lower:
            return "ensure security"
        elif 'accurate' in sentence_lower:
            return "maintain accuracy"
        else:
            return "achieve the desired functionality"
    
    def _infer_priority(self, sentence: str) -> str:
        """Infer priority from sentence context."""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['must', 'critical', 'essential', 'required']):
            return 'HIGH'
        elif any(word in sentence_lower for word in ['should', 'important']):
            return 'MEDIUM'
        elif any(word in sentence_lower for word in ['could', 'optional', 'nice']):
            return 'LOW'
        else:
            return 'MEDIUM'
    
    def _infer_category(self, sentence: str) -> str:
        """Infer category from sentence context."""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['ui', 'interface', 'display', 'show']):
            return "User Interface"
        elif any(word in sentence_lower for word in ['data', 'database', 'store', 'save']):
            return "Data Management"
        elif any(word in sentence_lower for word in ['security', 'auth', 'login', 'permission']):
            return "Security"
        elif any(word in sentence_lower for word in ['api', 'service', 'endpoint']):
            return "API"
        else:
            return "Core Functionality"
    
    def validate_requirements_consistency(self, requirements: List[Requirement]) -> List[str]:
        """
        Validate consistency across requirements and return any issues found.
        
        Args:
            requirements: List of requirements to validate
            
        Returns:
            List of validation issues (empty if no issues)
        """
        issues = []
        
        # Check for duplicate IDs
        ids = [req.id for req in requirements]
        if len(ids) != len(set(ids)):
            issues.append("Duplicate requirement IDs found")
        
        # Check for overlapping functionality
        descriptions = [req.user_story.lower() for req in requirements]
        for i, desc1 in enumerate(descriptions):
            for j, desc2 in enumerate(descriptions[i+1:], i+1):
                similarity = self._calculate_similarity(desc1, desc2)
                if similarity > 0.8:  # High similarity threshold
                    issues.append(f"Requirements {requirements[i].id} and {requirements[j].id} may have overlapping functionality")
        
        # Check for missing acceptance criteria
        for req in requirements:
            if not req.acceptance_criteria:
                issues.append(f"Requirement {req.id} has no acceptance criteria")
        
        return issues
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0