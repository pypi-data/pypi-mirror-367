"""
Main API class for the AI Project Builder.

This module provides the primary user interface for interacting with
the AI Project Builder system.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path

from .models import (
    ProjectPlan, ProjectStatus, SpecificationSet, ImplementationResult, 
    IntegrationResult, ProjectResult, ProjectPhase, ProjectStructure,
    ProjectDocumentation, ExecutionResult, TestResult, DebugContext,
    CodeRevision, TracebackAnalysis, FunctionSpec, EnhancedDependencyGraph,
    TestGenerationResult
)
from .interfaces import ProjectManagerInterface, StateManagerInterface
from ..managers.state import StateManager


# Custom exceptions for API errors
class A3Error(Exception):
    """Base exception for A3 API errors."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None, error_code: Optional[str] = None):
        """
        Initialize A3 error with user-friendly information.
        
        Args:
            message: Error message
            suggestion: Suggested solution for the user
            error_code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message with suggestions."""
        msg = f"Error: {self.message}"
        if self.suggestion:
            msg += f"\n\nSuggestion: {self.suggestion}"
        if self.error_code:
            msg += f"\n\nError Code: {self.error_code}"
        return msg


class ConfigurationError(A3Error):
    """Exception raised for configuration issues."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Check your configuration and try again.",
            error_code="CONFIG_ERROR"
        )


class ProjectStateError(A3Error):
    """Exception raised for project state issues."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Check your project directory and ensure previous steps completed successfully.",
            error_code="STATE_ERROR"
        )


class OperationError(A3Error):
    """Exception raised for operation failures."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Try the operation again. If the problem persists, check your API key and network connection.",
            error_code="OPERATION_ERROR"
        )


class ValidationError(A3Error):
    """Exception raised for validation failures."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(
            message=message,
            suggestion=suggestion or "Review the input parameters and ensure they meet the requirements.",
            error_code="VALIDATION_ERROR"
        )


class A3:
    """
    Main API class for AI Project Builder.
    
    This class provides the primary interface for users to interact with
    the AI Project Builder system, orchestrating project creation from
    high-level objectives to complete implementations.
    """
    
    def __init__(self, project_path: str = "."):
        """
        Initialize the A3 instance.
        
        Args:
            project_path: Path to the project directory (default: current directory)
        """
        self.project_path = Path(project_path).resolve()
        self._api_key: Optional[str] = None
        self._project_manager: Optional[ProjectManagerInterface] = None
        self._state_manager: Optional[StateManagerInterface] = None
        self._logger = logging.getLogger(__name__)
        
        # Initialize state manager immediately
        self._state_manager = StateManager(str(self.project_path))
        self._state_manager.initialize()
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key for AI service authentication.
        
        Args:
            api_key: The API key for OpenRouter or other AI services
            
        Raises:
            ConfigurationError: If the API key is invalid or empty
        """
        try:
            if not api_key or not api_key.strip():
                raise ConfigurationError(
                    "API key cannot be empty",
                    "Please provide a valid OpenRouter API key. You can get one from https://openrouter.ai/"
                )
            
            self._api_key = api_key.strip()
            
            # Validate API key by creating a client and testing it
            try:
                from ..clients.openrouter import OpenRouterClient
                client = OpenRouterClient(self._api_key)
                if not client.validate_api_key():
                    raise ConfigurationError(
                        "Invalid API key provided",
                        "Please check your API key and ensure it's active. You can verify it at https://openrouter.ai/keys"
                    )
            except Exception as e:
                if isinstance(e, ConfigurationError):
                    raise
                raise ConfigurationError(
                    f"Failed to validate API key: {e}",
                    "Check your internet connection and API key. If the problem persists, the API service may be temporarily unavailable."
                ) from e
            
            self._logger.info("API key set and validated successfully")
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            self._handle_unexpected_error("setting API key", e)
    
    def set_model(self, model: str) -> None:
        """
        Set the AI model to use for OpenRouter requests.
        
        Args:
            model: The model identifier (e.g., "anthropic/claude-3-sonnet", "openai/gpt-4")
            
        Raises:
            ConfigurationError: If the model is invalid or unavailable
            ValidationError: If the model name format is invalid
        """
        try:
            if not model or not model.strip():
                raise ValidationError(
                    "Model name cannot be empty",
                    "Please provide a valid model identifier. Use get_available_models() to see available options."
                )
            
            model = model.strip()
            
            # Validate model name format
            import re
            if not re.match(r'^[a-zA-Z0-9_:/.,-]+$', model):
                raise ValidationError(
                    f"Invalid model name format: {model}",
                    "Model names must contain only alphanumeric characters, hyphens, underscores, colons, slashes, dots, and commas."
                )
            
            # Initialize state manager if needed (without requiring API key)
            if not self._state_manager:
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Validate model availability if API key is set
            if self._api_key:
                try:
                    from ..clients.openrouter import OpenRouterClient
                    client = OpenRouterClient(self._api_key)
                    available_models = client.get_available_models()
                    
                    if model not in available_models:
                        # Check if it's a partial match or suggest alternatives
                        suggestions = [m for m in available_models if model.lower() in m.lower()][:3]
                        suggestion_text = f"Did you mean: {', '.join(suggestions)}" if suggestions else "Use get_available_models() to see all available models."
                        
                        raise ConfigurationError(
                            f"Model '{model}' is not available",
                            suggestion_text
                        )
                        
                except Exception as e:
                    if isinstance(e, ConfigurationError):
                        raise
                    # If we can't validate availability, log warning but continue
                    self._logger.warning(f"Could not validate model availability: {e}")
            else:
                # No API key set, just warn that we can't validate availability
                self._logger.info(f"Setting model to '{model}' (availability not validated - no API key set)")
            
            # Update model configuration
            try:
                # Get current configuration to preserve available models
                config = self._state_manager.get_or_create_model_configuration()
                
                # Add the new model to available models if not already there
                if model not in config.available_models:
                    config.available_models.append(model)
                
                # Update the current model and save
                self._state_manager.update_model_configuration(
                    current_model=model,
                    available_models=config.available_models
                )
                
                # Also update the A3Config to keep them in sync
                from ..config import A3Config
                a3_config = A3Config.load()
                a3_config.model = model
                
                # Save to project config
                config_path = self.project_path / '.a3config.json'
                a3_config.save(str(config_path))
                
                self._logger.info(f"Model set to: {model}")
                
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to save model configuration: {e}",
                    "Check that the project directory is writable and try again."
                ) from e
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, ValidationError)):
                raise
            # Don't call _handle_unexpected_error as it might cause issues
            self._logger.error(f"Unexpected error setting model: {e}")
            raise ConfigurationError(f"Failed to set model: {e}") from e
    
    def set_max_retries(self, max_retries: int) -> None:
        """
        Set the maximum number of retries for API requests.
        
        Args:
            max_retries: Maximum number of retry attempts (1-10)
            
        Raises:
            ValidationError: If max_retries is out of valid range
        """
        try:
            if not isinstance(max_retries, int) or max_retries < 1 or max_retries > 10:
                raise ValidationError(
                    "Max retries must be an integer between 1 and 10",
                    "Choose a reasonable number of retry attempts to balance reliability and performance."
                )
            
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.max_retries = max_retries
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Max retries set to: {max_retries}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self._handle_unexpected_error("setting max retries", e)
    
    def set_generate_tests(self, generate_tests: bool) -> None:
        """
        Set whether to automatically generate tests during integration.
        
        Args:
            generate_tests: True to enable test generation, False to disable
        """
        try:
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.generate_tests = generate_tests
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Test generation {'enabled' if generate_tests else 'disabled'}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            self._handle_unexpected_error("setting test generation", e)
    
    def set_test_framework(self, framework: str) -> None:
        """
        Set the test framework to use for generated tests.
        
        Args:
            framework: Test framework name (e.g., "pytest", "unittest")
            
        Raises:
            ValidationError: If framework name is invalid
        """
        try:
            if not framework or not framework.strip():
                raise ValidationError(
                    "Test framework name cannot be empty",
                    "Please provide a valid test framework name like 'pytest' or 'unittest'."
                )
            
            framework = framework.strip().lower()
            valid_frameworks = ["pytest", "unittest", "nose2", "testify"]
            
            if framework not in valid_frameworks:
                raise ValidationError(
                    f"Unsupported test framework: {framework}",
                    f"Supported frameworks: {', '.join(valid_frameworks)}"
                )
            
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.test_framework = framework
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Test framework set to: {framework}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self._handle_unexpected_error("setting test framework", e)
    
    def set_code_style(self, style: str) -> None:
        """
        Set the code style/formatter to use.
        
        Args:
            style: Code style name (e.g., "black", "autopep8", "yapf")
            
        Raises:
            ValidationError: If style name is invalid
        """
        try:
            if not style or not style.strip():
                raise ValidationError(
                    "Code style name cannot be empty",
                    "Please provide a valid code style name like 'black', 'autopep8', or 'yapf'."
                )
            
            style = style.strip().lower()
            valid_styles = ["black", "autopep8", "yapf", "blue"]
            
            if style not in valid_styles:
                raise ValidationError(
                    f"Unsupported code style: {style}",
                    f"Supported styles: {', '.join(valid_styles)}"
                )
            
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.code_style = style
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Code style set to: {style}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self._handle_unexpected_error("setting code style", e)
    
    def get_current_model(self) -> str:
        """
        Get the currently configured AI model.
        
        Returns:
            str: The current model identifier
        """
        try:
            # Initialize state manager if needed (without requiring API key)
            if not self._state_manager:
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Get model configuration
            config = self._state_manager.load_model_configuration()
            if config and config.current_model:
                return config.current_model
            
            # Fallback to default model
            default_model = "qwen/qwen-2.5-72b-instruct:free"
            self._logger.info(f"No model configured, using default: {default_model}")
            return default_model
            
        except Exception as e:
            # Return default model if there's any error
            default_model = "qwen/qwen-2.5-72b-instruct:free"
            self._logger.warning(f"Error getting current model, using default: {e}")
            return default_model
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration settings.
        
        Returns:
            Dict containing current configuration values
        """
        try:
            from ..config import A3Config
            
            # Load config
            config = A3Config.load()
            
            # Get model configuration
            current_model = "Not configured"
            try:
                current_model = self.get_current_model()
            except Exception:
                pass
            
            return {
                "api_key_set": bool(self._api_key),
                "current_model": current_model,
                "max_retries": config.max_retries,
                "generate_tests": config.generate_tests,
                "test_framework": config.test_framework,
                "code_style": config.code_style,
                "line_length": config.line_length,
                "type_checking": config.type_checking,
                "auto_install_deps": config.auto_install_deps,
                "use_fallback_models": config.use_fallback_models,
                "project_path": str(self.project_path)
            }
            
        except Exception as e:
            self._logger.error(f"Error getting config summary: {e}")
            return {"error": str(e)}
    
    def set_line_length(self, length: int) -> None:
        """
        Set the maximum line length for code formatting.
        
        Args:
            length: Maximum line length (typically 79, 88, or 120)
            
        Raises:
            ValidationError: If length is out of reasonable range
        """
        try:
            if not isinstance(length, int) or length < 60 or length > 200:
                raise ValidationError(
                    "Line length must be an integer between 60 and 200",
                    "Common values are 79 (PEP 8), 88 (Black default), or 120 (modern standard)."
                )
            
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.line_length = length
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Line length set to: {length}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self._handle_unexpected_error("setting line length", e)
    
    def set_auto_install_deps(self, auto_install: bool) -> None:
        """
        Set whether to automatically install dependencies during project creation.
        
        Args:
            auto_install: True to enable automatic dependency installation
        """
        try:
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.auto_install_deps = auto_install
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Auto install dependencies {'enabled' if auto_install else 'disabled'}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            self._handle_unexpected_error("setting auto install dependencies", e)
    
    def set_type_checking(self, level: str) -> None:
        """
        Set the type checking strictness level.
        
        Args:
            level: Type checking level ("strict", "normal", "basic", "none")
            
        Raises:
            ValidationError: If level is invalid
        """
        try:
            if not level or not level.strip():
                raise ValidationError(
                    "Type checking level cannot be empty",
                    "Please provide a valid level: 'strict', 'normal', 'basic', or 'none'."
                )
            
            level = level.strip().lower()
            valid_levels = ["strict", "normal", "basic", "none"]
            
            if level not in valid_levels:
                raise ValidationError(
                    f"Invalid type checking level: {level}",
                    f"Valid levels: {', '.join(valid_levels)}"
                )
            
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.type_checking = level
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Type checking level set to: {level}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self._handle_unexpected_error("setting type checking level", e)
    
    def set_use_fallback_models(self, use_fallbacks: bool) -> None:
        """
        Set whether to use fallback models when the primary model fails.
        
        Args:
            use_fallbacks: True to enable fallback models, False to error on primary model failure
        """
        try:
            # Load and update config
            from ..config import A3Config
            config = A3Config.load()
            config.use_fallback_models = use_fallbacks
            
            # Save to project config if in a project directory
            try:
                config_path = self.project_path / '.a3config.json'
                config.save(str(config_path))
                self._logger.info(f"Fallback models {'enabled' if use_fallbacks else 'disabled'}")
            except Exception as e:
                self._logger.warning(f"Could not save config to project directory: {e}")
                
        except Exception as e:
            self._handle_unexpected_error("setting fallback model behavior", e)
    
    def plan(self, objective: str, project_path: str = ".") -> ProjectPlan:
        """
        Generate a comprehensive project plan from a high-level objective.
        
        Args:
            objective: High-level description of what the project should accomplish
            project_path: Path where the project should be created
            
        Returns:
            ProjectPlan: Complete project plan with modules and dependencies
            
        Raises:
            ConfigurationError: If API key is not set
            OperationError: If planning fails
            ValidationError: If objective is empty or invalid
        """
        try:
            # Validate input
            if not objective or not objective.strip():
                raise ValidationError(
                    "Project objective cannot be empty",
                    "Please provide a clear description of what you want to build. For example: 'A web scraper for news articles' or 'A REST API for user management'"
                )
            
            if len(objective.strip()) < 10:
                raise ValidationError(
                    "Project objective is too short",
                    "Please provide a more detailed description (at least 10 characters) to generate a meaningful project plan."
                )
            
            self._ensure_initialized()
            
            # Validate and update project path
            try:
                if project_path != ".":
                    new_path = Path(project_path).resolve()
                    if not new_path.parent.exists():
                        raise ValidationError(
                            f"Parent directory does not exist: {new_path.parent}",
                            "Create the parent directory first or choose an existing location."
                        )
                    self.project_path = new_path
                    self._state_manager = StateManager(str(self.project_path))
                    self._state_manager.initialize()
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(
                    f"Invalid project path: {e}",
                    "Ensure the path is valid and you have write permissions to the directory."
                ) from e
            
            # Check if project already exists
            existing_status = self.status(project_path)
            if existing_status.is_active:
                raise ProjectStateError(
                    "A project already exists in this directory",
                    "Use resume() to continue the existing project, or choose a different directory for a new project."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info(f"Starting project planning for objective: {objective}")
            
            # Execute only the planning phase
            try:
                result = self._project_manager._execute_planning_phase(objective)
            except Exception as e:
                raise OperationError(
                    f"Planning engine failed: {e}",
                    "This could be due to API rate limits, network issues, or an unclear objective. Try again with a more specific objective."
                ) from e
            
            if not result.success:
                error_details = f"Planning failed: {result.message}"
                if result.errors:
                    error_details += f". Details: {'; '.join(result.errors)}"
                
                suggestion = "Try rephrasing your objective more clearly, check your API key, or try again later if there are service issues."
                raise OperationError(error_details, suggestion)
            
            # Load and validate the generated plan
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise OperationError(
                    "Planning completed but no plan was saved",
                    "This indicates a system error. Try running the plan() method again."
                )
            
            self._logger.info(f"Project planning completed successfully. Generated {len(plan.modules)} modules with {plan.estimated_functions} functions.")
            
            # Create checkpoint after successful planning
            try:
                checkpoint_id = self._state_manager.create_checkpoint()
                self._logger.info(f"Created checkpoint after planning: {checkpoint_id}")
            except Exception as e:
                self._logger.warning(f"Failed to create checkpoint after planning: {e}")
            
            return plan
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, OperationError, ValidationError, ProjectStateError)):
                raise
            self._handle_unexpected_error("planning", e)
    
    def generate_specs(self, project_path: str = ".") -> SpecificationSet:
        """
        Generate detailed function specifications from the project plan.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            SpecificationSet: Complete set of function specifications
            
        Raises:
            ProjectStateError: If no project plan exists
            OperationError: If specification generation fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if project plan exists
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            # Start progress tracking for specification generation
            from ..core.user_feedback import start_operation_progress, update_operation_progress, complete_operation_progress
            
            total_functions = sum(len(module.functions) for module in plan.modules)
            progress_indicator = start_operation_progress(
                "spec_generation",
                "Specification Generation", 
                total_functions,
                show_percentage=True,
                show_eta=True
            )
            
            # Get current progress to determine if we need to generate specs
            progress = self._state_manager.get_current_progress()
            if progress:
                current_phase_value = self._get_phase_value(progress.current_phase)
                if current_phase_value in ['specification', 'implementation', 'integration', 'completed']:
                    self._logger.info("Specifications already generated, loading existing specs")
                    # Load existing specifications from state
                    # For now, create from current plan
                    specs = SpecificationSet(
                        functions=[func for module in plan.modules for func in module.functions],
                        modules=plan.modules
                    )
                    
                    # Complete progress tracking
                    complete_operation_progress(
                        "spec_generation",
                        success=True,
                        final_message=f"Loaded existing specifications for {len(specs.functions)} functions"
                    )
                    
                    return specs
            
            # Generate specifications using the specification generator
            from ..clients.openrouter import OpenRouterClient
            from ..engines.specification import SpecificationGenerator
            
            client = OpenRouterClient(self._api_key)
            spec_generator = SpecificationGenerator(client)
            spec_generator.initialize()
            
            # Extract all functions from the plan
            all_functions = []
            for module in plan.modules:
                all_functions.extend(module.functions)
            
            specs = spec_generator.generate_specifications(all_functions)
            # Add modules to specs so CodeGenerator can find file paths
            specs.modules = plan.modules
            
            # Save progress - ensure we're at SPECIFICATION phase
            self._state_manager.save_progress(
                ProjectPhase.SPECIFICATION,
                {
                    'total_functions': len(specs.functions),
                    'implemented_functions': 0,
                    'failed_functions': []
                }
            )
            
            # Complete progress tracking
            complete_operation_progress(
                "spec_generation",
                success=True,
                final_message=f"Generated specifications for {len(specs.functions)} functions"
            )
            
            # Final safety check: ensure we're at SPECIFICATION phase
            final_progress = self._state_manager.get_current_progress()
            if final_progress and self._get_phase_value(final_progress.current_phase) == 'planning':
                self._logger.warning("Project still in PLANNING phase after generate_specs, forcing update to SPECIFICATION")
                self._state_manager.save_progress(
                    ProjectPhase.SPECIFICATION,
                    {
                        'total_functions': len(specs.functions),
                        'implemented_functions': 0,
                        'failed_functions': []
                    }
                )
            
            return specs
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, OperationError)):
                raise
            self._handle_unexpected_error("specification generation", e)
    
    def implement(self, project_path: str = ".") -> ImplementationResult:
        """
        Implement all functions based on their specifications.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ImplementationResult: Results of the implementation process
            
        Raises:
            ProjectStateError: If specifications don't exist
            OperationError: If implementation fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if project plan and specifications exist
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            progress = self._state_manager.get_current_progress()
            if not progress or progress.current_phase == ProjectPhase.PLANNING:
                raise ProjectStateError(
                    "No specifications found. Run generate_specs() first to create function specifications."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            # Start progress tracking for implementation
            from ..core.user_feedback import start_operation_progress, update_operation_progress, complete_operation_progress
            
            total_functions = sum(len(module.functions) for module in plan.modules)
            progress_indicator = start_operation_progress(
                "implementation",
                "Function Implementation",
                total_functions,
                show_percentage=True,
                show_eta=True
            )
            
            # Get current project progress to check if implementation is already complete
            progress = self._state_manager.get_current_progress()
            if progress:
                current_phase_value = self._get_phase_value(progress.current_phase)
                if current_phase_value in ['implementation', 'integration', 'completed']:
                    if current_phase_value in ['integration', 'completed']:
                        self._logger.info("Implementation already completed")
                    return ImplementationResult(
                        implemented_functions=[func.name for module in plan.modules for func in module.functions],
                        failed_functions=progress.failed_functions,
                        success_rate=1.0 - (len(progress.failed_functions) / max(progress.total_functions, 1))
                    )
            
            # Generate implementations using the code generator
            from ..clients.openrouter import OpenRouterClient
            from ..engines.code_generator import CodeGenerator
            
            client = OpenRouterClient(self._api_key)
            code_generator = CodeGenerator(client, self._state_manager, str(self.project_path))
            code_generator.initialize()
            
            # Create specification set from plan
            specs = SpecificationSet(
                functions=[func for module in plan.modules for func in module.functions],
                modules=plan.modules
            )
            
            result = code_generator.implement_all(specs)
            
            # Save progress
            self._state_manager.save_progress(
                ProjectPhase.IMPLEMENTATION,
                {
                    'total_functions': len(specs.functions),
                    'implemented_functions': len(result.implemented_functions),
                    'failed_functions': result.failed_functions
                }
            )
            
            # Complete progress tracking
            complete_operation_progress(
                "implementation",
                success=result.success_rate > 0.5,  # Consider >50% success rate as successful
                final_message=f"Implemented {len(result.implemented_functions)} functions ({result.success_rate:.1%} success rate)"
            )
            
            # Create checkpoint after successful implementation
            if result.success_rate > 0.5:  # Only create checkpoint if implementation was mostly successful
                try:
                    checkpoint_id = self._state_manager.create_checkpoint()
                    self._logger.info(f"Created checkpoint after implementation: {checkpoint_id}")
                except Exception as e:
                    self._logger.warning(f"Failed to create checkpoint after implementation: {e}")
            
            return result
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, OperationError)):
                raise
            self._handle_unexpected_error("implementation", e)
    
    def integrate(self, project_path: str = ".", generate_tests: bool = False) -> IntegrationResult:
        """
        Integrate all modules and handle imports automatically.
        
        Args:
            project_path: Path to the project directory
            generate_tests: Whether to generate unit tests during integration
            
        Returns:
            IntegrationResult: Results of the integration process
            
        Raises:
            ProjectStateError: If implementations don't exist
            OperationError: If integration fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if project plan and implementations exist
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            progress = self._state_manager.get_current_progress()
            if not progress:
                current_phase_value = None
            else:
                current_phase_value = self._get_phase_value(progress.current_phase)
            
            if not progress or current_phase_value in ['planning', 'specification']:
                raise ProjectStateError(
                    "No implementations found. Run implement() first to generate function implementations."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info("Starting module integration")
            
            # Check if integration is already complete
            if progress.current_phase == ProjectPhase.COMPLETED:
                self._logger.info("Integration already completed")
                return IntegrationResult(
                    integrated_modules=[module.name for module in plan.modules],
                    import_errors=[],
                    success=True
                )
            
            # Perform integration using the integration engine
            from ..clients.openrouter import OpenRouterClient
            from ..engines.integration import IntegrationEngine
            from ..managers.dependency import DependencyAnalyzer
            from ..managers.filesystem import FileSystemManager
            
            client = OpenRouterClient(self._api_key)
            dependency_analyzer = DependencyAnalyzer(str(self.project_path))
            filesystem_manager = FileSystemManager(str(self.project_path))
            integration_engine = IntegrationEngine(dependency_analyzer, filesystem_manager, client, self._state_manager)
            integration_engine.initialize()
            
            result = integration_engine.integrate_modules(plan.modules, generate_tests=generate_tests)
            
            # Enhanced result reporting
            if generate_tests and result.test_result:
                if result.test_result.success:
                    self._logger.info(f"Test generation completed successfully. Generated {len(result.test_result.generated_tests)} tests.")
                else:
                    self._logger.warning(f"Test generation encountered errors: {'; '.join(result.test_result.errors)}")
            
            # Enhanced error reporting
            if result.import_errors:
                self._logger.warning(f"Integration completed with import errors: {'; '.join(result.import_errors)}")
            
            if hasattr(result, 'warnings') and result.warnings:
                for warning in result.warnings:
                    self._logger.warning(f"Integration warning: {warning}")
            
            # Save progress
            if result.success:
                progress_data = {
                    'total_functions': progress.total_functions if progress else 0,
                    'implemented_functions': progress.implemented_functions if progress else 0,
                    'failed_functions': progress.failed_functions if progress else []
                }
                
                # Add test generation info to progress if applicable
                if generate_tests and result.test_result:
                    progress_data['test_generation'] = {
                        'enabled': True,
                        'success': result.test_result.success,
                        'tests_generated': len(result.test_result.generated_tests) if result.test_result.generated_tests else 0,
                        'test_files_created': len(result.test_result.test_files_created) if result.test_result.test_files_created else 0
                    }
                
                self._state_manager.save_progress(ProjectPhase.COMPLETED, progress_data)
            else:
                # Log detailed failure information
                error_msg = "Integration failed"
                if result.import_errors:
                    error_msg += f" with import errors: {'; '.join(result.import_errors)}"
                if generate_tests and result.test_result and not result.test_result.success:
                    error_msg += f" and test generation errors: {'; '.join(result.test_result.errors)}"
                
                raise OperationError(
                    error_msg,
                    "Check the error details above and ensure all dependencies are properly installed and accessible."
                )
            
            self._logger.info(f"Integration completed successfully. Integrated {len(result.integrated_modules)} modules.")
            
            # Create checkpoint after successful integration
            try:
                checkpoint_id = self._state_manager.create_checkpoint()
                self._logger.info(f"Created checkpoint after integration: {checkpoint_id}")
            except Exception as e:
                self._logger.warning(f"Failed to create checkpoint after integration: {e}")
            
            return result
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, OperationError)):
                raise
            self._handle_unexpected_error("integration", e)
    
    def status(self, project_path: str = ".") -> ProjectStatus:
        """
        Get the current status of the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectStatus: Current project status and progress information
        """
        try:
            # Validate and update project path
            try:
                if project_path != ".":
                    new_path = Path(project_path).resolve()
                    if not new_path.exists():
                        return ProjectStatus(
                            is_active=False,
                            progress=None,
                            errors=[f"Project directory does not exist: {new_path}"],
                            can_resume=False,
                            next_action="Create the project directory or run plan() to start a new project"
                        )
                    self.project_path = new_path
                    # Create temporary state manager for status check
                    temp_state_manager = StateManager(str(self.project_path))
                    temp_state_manager.initialize()
                    status = temp_state_manager.get_project_status()
                else:
                    # Use existing state manager if available
                    if self._state_manager:
                        status = self._state_manager.get_project_status()
                    else:
                        # Create state manager if none exists
                        self._state_manager = StateManager(str(self.project_path))
                        self._state_manager.initialize()
                        status = self._state_manager.get_project_status()
                
                # Enhance status with user-friendly information
                status = self._enhance_status_with_guidance(status)
                return status
                
            except Exception as e:
                self._logger.error(f"Error accessing project directory: {e}")
                return ProjectStatus(
                    is_active=False,
                    progress=None,
                    errors=[f"Cannot access project directory: {e}"],
                    can_resume=False,
                    next_action="Check directory permissions and ensure the path is correct"
                )
            
        except Exception as e:
            self._logger.error(f"Unexpected error getting project status: {e}")
            return ProjectStatus(
                is_active=False,
                progress=None,
                errors=[f"Status check failed: {e}"],
                can_resume=False,
                next_action="Check project directory and try again"
            )
    
    def resume(self, project_path: str = ".") -> ProjectResult:
        """
        Resume an interrupted project from the last completed stage.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectResult: Result of the resumption operation
            
        Raises:
            ProjectStateError: If no resumable project state exists
            ConfigurationError: If API key is not set
            OperationError: If resumption fails
        """
        self._ensure_initialized()
        
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if there's a resumable project
            status = self._state_manager.get_project_status()
            if not status.can_resume:
                raise ProjectStateError(
                    "No resumable project found. Either no project exists or the project is already complete."
                )
            
            # Check if project plan exists
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "Project state is corrupted: no project plan found despite resumable status."
                )
            
            # Initialize project manager if needed
            if not self._project_manager:
                self._initialize_project_manager()
            
            self._logger.info("Resuming interrupted project")
            
            # Resume the pipeline
            result = self._project_manager.resume_pipeline()
            
            if result.success:
                self._logger.info("Project resumed successfully")
            else:
                self._logger.error(f"Project resumption failed: {result.message}")
            
            return result
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, ConfigurationError, OperationError)):
                raise
            self._handle_unexpected_error("project resumption", e)
    
    def analyze_project(self, project_path: str = ".", database_connection: Optional[str] = None) -> ProjectStructure:
        """
        Analyze an existing project and generate comprehensive documentation.
        
        Args:
            project_path: Path to the project directory to analyze
            database_connection: Optional PostgreSQL connection string for database analysis
            
        Returns:
            ProjectStructure: Complete analysis of the project structure including data sources and database metadata
            
        Raises:
            ValidationError: If project path is invalid or inaccessible
            OperationError: If analysis fails
        """
        try:
            # Validate project path
            project_root = Path(project_path).resolve()
            if not project_root.exists():
                raise ValidationError(
                    f"Project directory does not exist: {project_root}",
                    "Ensure the path is correct and the directory exists."
                )
            
            if not project_root.is_dir():
                raise ValidationError(
                    f"Path is not a directory: {project_root}",
                    "Provide a path to a directory, not a file."
                )
            
            self._logger.info(f"Starting project analysis for: {project_root}")
            
            # Initialize project analyzer and enhanced components
            try:
                from ..clients.openrouter import OpenRouterClient
                from ..engines.project_analyzer import ProjectAnalyzer
                from ..engines.database_analyzer import DatabaseAnalyzer
                from ..managers.dependency import DependencyAnalyzer
                from ..managers.filesystem import FileSystemManager
                from ..managers.data_source_manager import DataSourceManager
                
                # Create components (API key not required for basic analysis)
                client = None
                if self._api_key:
                    client = OpenRouterClient(self._api_key)
                
                dependency_analyzer = DependencyAnalyzer(str(project_root))
                filesystem_manager = FileSystemManager(str(project_root))
                data_source_manager = DataSourceManager(str(project_root))
                
                analyzer = ProjectAnalyzer(
                    ai_client=client,
                    dependency_analyzer=dependency_analyzer,
                    filesystem_manager=filesystem_manager
                )
                analyzer.initialize()
                
                # Initialize database analyzer if connection string provided
                database_analyzer = None
                if database_connection:
                    try:
                        database_analyzer = DatabaseAnalyzer(ai_client=client, state_manager=self._state_manager)
                        database_analyzer.initialize()
                        self._logger.info("Database analyzer initialized for PostgreSQL analysis")
                    except Exception as e:
                        self._logger.warning(f"Failed to initialize database analyzer: {e}")
                        # Continue without database analysis
                
            except Exception as e:
                raise OperationError(
                    f"Failed to initialize project analyzer: {e}",
                    "Check your installation and try again."
                ) from e
            
            # Perform enhanced project analysis
            try:
                # Basic project structure analysis
                project_structure = analyzer.scan_project_folder(str(project_root))
                
                # Enhanced data source analysis
                try:
                    self._logger.info("Scanning for data sources...")
                    data_source_analysis = data_source_manager.scan_project_data_sources(str(project_root))
                    
                    project_structure.data_source_analysis = data_source_analysis
                    
                    if data_source_analysis.unified_metadata:
                        self._logger.info(f"Found {len(data_source_analysis.unified_metadata)} data sources: "
                                        f"{', '.join([ds.file_type for ds in data_source_analysis.unified_metadata])}")
                    else:
                        self._logger.info("No data sources found in project")
                        
                except Exception as e:
                    self._logger.warning(f"Data source analysis failed: {e}")
                    # Continue without data source analysis
                
                # Enhanced database analysis
                if database_connection and database_analyzer:
                    try:
                        self._logger.info("Analyzing database schema...")
                        database_connection_obj = database_analyzer.connect_to_database(database_connection)
                        database_schema = database_analyzer.analyze_database_schema(database_connection_obj)
                        
                        # Store database metadata in project structure
                        project_structure.database_analysis = database_schema
                        
                        self._logger.info(f"Database analysis completed. Found {len(database_schema.tables)} tables.")
                        
                        # Close database connection
                        if hasattr(database_connection_obj, 'close'):
                            database_connection_obj.close()
                            
                    except Exception as e:
                        self._logger.warning(f"Database analysis failed: {e}")
                        # Continue without database analysis
                
                # Generate enhanced documentation if AI client is available
                if client:
                    try:
                        documentation = analyzer.generate_project_documentation(project_structure)
                        project_structure.documentation = documentation
                        self._logger.info("Generated AI-powered project documentation")
                    except Exception as e:
                        self._logger.warning(f"Failed to generate AI documentation: {e}")
                        # Continue without AI documentation
                
                # Log comprehensive analysis results
                analysis_summary = f"Project analysis completed. Found {len(project_structure.source_files)} source files"
                if project_structure.data_source_analysis and project_structure.data_source_analysis.unified_metadata:
                    analysis_summary += f", {len(project_structure.data_source_analysis.unified_metadata)} data sources"
                if project_structure.database_analysis and project_structure.database_analysis.tables:
                    analysis_summary += f", database with {len(project_structure.database_analysis.tables)} tables"
                analysis_summary += "."
                
                self._logger.info(analysis_summary)
                return project_structure
                
            except Exception as e:
                raise OperationError(
                    f"Project analysis failed: {e}",
                    "Ensure the project directory contains valid Python files and you have read permissions."
                ) from e
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("project analysis", e)
    
    def analyze_dependencies(self, project_path: str = ".") -> Dict[str, Any]:
        """
        Analyze project dependencies at both module and function level.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary with comprehensive dependency analysis
            
        Raises:
            ValidationError: If project path is invalid
            OperationError: If analysis fails
        """
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Load project plan
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ValidationError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            # Initialize dependency analyzer
            from ..managers.dependency import DependencyAnalyzer
            dependency_analyzer = DependencyAnalyzer(str(self.project_path))
            
            # Get implementation strategy
            strategy = dependency_analyzer.get_implementation_strategy(plan.modules)
            
            return strategy
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("dependency analysis", e)
    
    def get_implementation_strategy(self, project_path: str = ".") -> Dict[str, Any]:
        """
        Get optimal implementation strategy based on enhanced dependency analysis.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary with implementation strategy details
            
        Raises:
            ValidationError: If project path is invalid
            OperationError: If analysis fails
        """
        try:
            # This is essentially the same as analyze_dependencies but with a clearer name
            return self.analyze_dependencies(project_path)
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("implementation strategy analysis", e)
    
    def get_enhanced_dependency_graph(self, project_path: str = ".") -> EnhancedDependencyGraph:
        """
        Get the enhanced dependency graph for the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            EnhancedDependencyGraph with function-level dependencies
            
        Raises:
            ValidationError: If project path is invalid
            OperationError: If analysis fails
        """
        try:
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Load project plan
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ValidationError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            # Return enhanced dependency graph if available
            if plan.enhanced_dependency_graph:
                return plan.enhanced_dependency_graph
            
            # Create enhanced dependency graph if not available
            from ..managers.dependency import DependencyAnalyzer
            dependency_analyzer = DependencyAnalyzer(str(self.project_path))
            enhanced_graph = dependency_analyzer.build_enhanced_dependency_graph(plan.modules)
            
            # Update the plan with the enhanced graph
            plan.enhanced_dependency_graph = enhanced_graph
            self._state_manager.save_project_plan(plan)
            
            return enhanced_graph
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("enhanced dependency graph retrieval", e)
    
    def debug_and_revise(self, error: Exception, function_spec: FunctionSpec, 
                        module_path: str, max_iterations: int = 3) -> List[CodeRevision]:
        """
        Debug a failed function implementation and generate revision suggestions.
        
        Args:
            error: The exception that occurred during execution
            function_spec: Specification of the function that failed
            module_path: Path to the module containing the function
            max_iterations: Maximum number of revision iterations
            
        Returns:
            List[CodeRevision]: List of code revision suggestions
            
        Raises:
            ConfigurationError: If API key is not set
            ValidationError: If inputs are invalid
            OperationError: If debugging fails
        """
        self._ensure_initialized()
        
        try:
            # Validate inputs
            if not isinstance(error, Exception):
                raise ValidationError(
                    "Error parameter must be an Exception instance",
                    "Pass the actual exception object that was caught."
                )
            
            if not function_spec or not function_spec.name:
                raise ValidationError(
                    "Function specification is required and must have a name",
                    "Provide a valid FunctionSpec object with at least the function name."
                )
            
            module_path_obj = Path(module_path)
            if not module_path_obj.exists():
                raise ValidationError(
                    f"Module file does not exist: {module_path}",
                    "Ensure the module file exists and the path is correct."
                )
            
            if max_iterations < 1 or max_iterations > 10:
                raise ValidationError(
                    "Max iterations must be between 1 and 10",
                    "Choose a reasonable number of revision attempts."
                )
            
            self._logger.info(f"Starting debug analysis for function: {function_spec.name}")
            
            # Initialize debug analyzer
            try:
                from ..clients.openrouter import OpenRouterClient
                from ..engines.debug_analyzer import DebugAnalyzer
                
                client = OpenRouterClient(self._api_key)
                debug_analyzer = DebugAnalyzer(
                    ai_client=client,
                    project_path=str(self.project_path)
                )
                debug_analyzer.initialize()
                
            except Exception as e:
                raise OperationError(
                    f"Failed to initialize debug analyzer: {e}",
                    "Check your API key and network connection."
                ) from e
            
            # Perform debug analysis and revision
            try:
                revisions = debug_analyzer.debug_and_revise_loop(
                    error=error,
                    function_spec=function_spec,
                    module_path=module_path,
                    max_iterations=max_iterations
                )
                
                self._logger.info(f"Debug analysis completed. Generated {len(revisions)} revision suggestions.")
                return revisions
                
            except Exception as e:
                raise OperationError(
                    f"Debug analysis failed: {e}",
                    "The error may be too complex to analyze automatically. Try simplifying the function or checking the error manually."
                ) from e
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("debug and revision", e)
    
    def execute_and_test(self, function_spec: FunctionSpec, module_path: Optional[str] = None, 
                        test_files: Optional[List[str]] = None) -> Tuple[ExecutionResult, Optional[TestResult]]:
        """
        Execute a function implementation and run associated tests.
        
        Args:
            function_spec: Specification of the function to execute
            module_path: Optional path to the module containing the function (inferred if not provided)
            test_files: Optional list of test files to run
            
        Returns:
            Tuple[ExecutionResult, Optional[TestResult]]: Execution and test results
            
        Raises:
            ValidationError: If inputs are invalid
            OperationError: If execution fails
        """
        try:
            # Validate inputs
            if not function_spec or not function_spec.name:
                raise ValidationError(
                    "Function specification is required and must have a name",
                    "Provide a valid FunctionSpec object with at least the function name."
                )
            
            # Infer module path if not provided
            if module_path is None:
                module_path = self._infer_module_path(function_spec)
                if module_path is None:
                    raise ValidationError(
                        f"Could not infer module path for function {function_spec.name} in module {function_spec.module}",
                        "Either provide module_path explicitly or ensure the project has been properly implemented."
                    )
            
            module_path_obj = Path(module_path)
            if not module_path_obj.exists():
                raise ValidationError(
                    f"Module file does not exist: {module_path}",
                    "Ensure the module file exists and the path is correct."
                )
            
            # Validate test files if provided
            if test_files:
                for test_file in test_files:
                    test_path = Path(test_file)
                    if not test_path.exists():
                        raise ValidationError(
                            f"Test file does not exist: {test_file}",
                            "Ensure all test files exist and paths are correct."
                        )
            
            self._logger.info(f"Starting execution and testing for function: {function_spec.name}")
            
            # Initialize code executor
            try:
                from ..engines.code_executor import CodeExecutor
                from ..managers.filesystem import FileSystemManager
                
                filesystem_manager = FileSystemManager(str(self.project_path))
                code_executor = CodeExecutor(
                    project_path=str(self.project_path),
                    file_manager=filesystem_manager
                )
                code_executor.initialize()
                
            except Exception as e:
                raise OperationError(
                    f"Failed to initialize code executor: {e}",
                    "Check your project setup and try again."
                ) from e
            
            # Execute the function
            try:
                execution_result = code_executor.execute_function(function_spec, module_path)
                self._logger.info(f"Function execution completed. Success: {execution_result.success}")
                
            except Exception as e:
                # Create failed execution result
                execution_result = ExecutionResult(
                    success=False,
                    output=None,
                    error=e,
                    execution_time=0.0,
                    memory_usage=None
                )
                self._logger.warning(f"Function execution failed: {e}")
            
            # Run tests if provided
            test_result = None
            if test_files:
                try:
                    test_result = code_executor.run_tests(test_files)
                    self._logger.info(f"Test execution completed. Passed: {test_result.passed_tests}/{test_result.total_tests}")
                    
                except Exception as e:
                    self._logger.warning(f"Test execution failed: {e}")
                    # Create failed test result
                    from ..core.models import TestResult, TestDetail
                    test_result = TestResult(
                        total_tests=0,
                        passed_tests=0,
                        failed_tests=0,
                        test_details=[],
                        coverage_report=None
                    )
            
            return execution_result, test_result
            
        except Exception as e:
            if isinstance(e, (ValidationError, OperationError)):
                raise
            self._handle_unexpected_error("execution and testing", e)
    
    def _ensure_initialized(self) -> None:
        """Ensure that all required components are initialized."""
        if not self._api_key:
            raise ConfigurationError("API key must be set before performing operations. Call set_api_key() first.")
        
        if not self._state_manager:
            self._state_manager = StateManager(str(self.project_path))
            self._state_manager.initialize()
    
    def _initialize_project_manager(self) -> None:
        """Initialize the project manager with all required components."""
        if not self._api_key:
            raise ConfigurationError("API key must be set before initializing project manager")
        
        if not self._state_manager:
            self._state_manager = StateManager(str(self.project_path))
            self._state_manager.initialize()
        
        try:
            # Import components lazily to avoid circular imports
            from ..clients.openrouter import OpenRouterClient
            from ..engines.planning import PlanningEngine
            from ..engines.specification import SpecificationGenerator
            from ..engines.code_generator import CodeGenerator
            from ..engines.integration import IntegrationEngine
            from ..managers.project import ProjectManager
            
            # Create OpenRouter client with fallback configuration
            from ..config import A3Config
            config = A3Config.load()
            
            client = OpenRouterClient(self._api_key)
            
            # Set the model from configuration
            if hasattr(self, '_state_manager') and self._state_manager:
                model_config = self._state_manager.load_model_configuration()
                if model_config and model_config.current_model:
                    client.set_default_model(model_config.current_model)
                elif config.model:
                    client.set_default_model(config.model)
            
            # Create all engine components
            planning_engine = PlanningEngine(client, self._state_manager, str(self.project_path))
            spec_generator = SpecificationGenerator(client, self._state_manager)
            code_generator = CodeGenerator(client, self._state_manager)
            integration_engine = IntegrationEngine(ai_client=client, state_manager=self._state_manager)
            
            # Initialize all engines
            planning_engine.initialize()
            spec_generator.initialize()
            code_generator.initialize()
            integration_engine.initialize()
            
            # Create project manager
            self._project_manager = ProjectManager(
                project_path=str(self.project_path),
                state_manager=self._state_manager,
                planning_engine=planning_engine,
                spec_generator=spec_generator,
                code_generator=code_generator,
                integration_engine=integration_engine
            )
            
            self._logger.info("Project manager initialized successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize project manager: {e}") from e
    
    def generate_tests(self, function_name: str, test_cases: List[Dict[str, Any]], project_path: str = ".") -> 'TestGenerationResult':
        """
        Generate targeted tests for a specific function with user-provided test case specifications.
        
        Args:
            function_name: Name of the function to generate tests for
            test_cases: List of test case specifications with input examples and expected outputs
            project_path: Path to the project directory
            
        Returns:
            TestGenerationResult: Results of the test generation process
            
        Raises:
            ConfigurationError: If API key is not set
            ValidationError: If function name or test cases are invalid
            OperationError: If test generation fails
        """
        self._ensure_initialized()
        
        try:
            # Validate input
            if not function_name or not function_name.strip():
                raise ValidationError(
                    "Function name cannot be empty",
                    "Please provide a valid function name to generate tests for."
                )
            
            if not test_cases or not isinstance(test_cases, list):
                raise ValidationError(
                    "Test cases must be a non-empty list",
                    "Please provide test case specifications with input examples and expected outputs."
                )
            
            # Update project path if different
            if project_path != ".":
                self.project_path = Path(project_path).resolve()
                self._state_manager = StateManager(str(self.project_path))
                self._state_manager.initialize()
            
            # Check if project exists
            plan = self._state_manager.load_project_plan()
            if not plan:
                raise ProjectStateError(
                    "No project plan found. Run plan() first to create a project plan."
                )
            
            # Find the function in the project plan
            target_function = None
            target_module = None
            
            for module in plan.modules:
                for func in module.functions:
                    if func.name == function_name:
                        target_function = func
                        target_module = module
                        break
                if target_function:
                    break
            
            if not target_function:
                raise ValidationError(
                    f"Function '{function_name}' not found in project plan",
                    f"Available functions: {', '.join([f.name for m in plan.modules for f in m.functions])}"
                )
            
            # Validate test case specifications
            validated_test_cases = []
            for i, test_case in enumerate(test_cases):
                try:
                    if not isinstance(test_case, dict):
                        raise ValidationError(f"Test case {i} must be a dictionary")
                    
                    # Required fields
                    if 'input_examples' not in test_case:
                        raise ValidationError(f"Test case {i} must include 'input_examples'")
                    
                    if 'expected_outputs' not in test_case:
                        raise ValidationError(f"Test case {i} must include 'expected_outputs'")
                    
                    # Validate input/output alignment
                    inputs = test_case['input_examples']
                    outputs = test_case['expected_outputs']
                    
                    if not isinstance(inputs, list) or not isinstance(outputs, list):
                        raise ValidationError(f"Test case {i}: input_examples and expected_outputs must be lists")
                    
                    if len(inputs) != len(outputs):
                        raise ValidationError(f"Test case {i}: number of input examples must match number of expected outputs")
                    
                    # Create validated test case
                    validated_case = {
                        'name': test_case.get('name', f'test_{function_name}_case_{i}'),
                        'description': test_case.get('description', f'Test case {i} for {function_name}'),
                        'input_examples': inputs,
                        'expected_outputs': outputs,
                        'validation_strategy': test_case.get('validation_strategy', 'exact_match'),
                        'test_type': test_case.get('test_type', 'unit')
                    }
                    
                    validated_test_cases.append(validated_case)
                    
                except Exception as e:
                    raise ValidationError(
                        f"Invalid test case specification at index {i}: {e}",
                        "Ensure each test case has 'input_examples' and 'expected_outputs' lists of equal length."
                    ) from e
            
            self._logger.info(f"Generating {len(validated_test_cases)} targeted tests for function '{function_name}'")
            
            # Initialize test generator
            from ..clients.openrouter import OpenRouterClient
            from ..engines.test_generator import TestGenerator
            from ..core.models import IntelligentTestCase, TestGenerationResult
            
            client = OpenRouterClient(self._api_key)
            test_generator = TestGenerator(client, self._state_manager)
            test_generator.initialize()
            
            # Generate intelligent test cases
            intelligent_tests = []
            
            for test_spec in validated_test_cases:
                try:
                    # Create IntelligentTestCase
                    test_case = IntelligentTestCase(
                        name=test_spec['name'],
                        function_name=function_name,
                        test_code="",  # Will be generated
                        expected_result="pass",
                        test_type=test_spec['test_type'],
                        dependencies=[],
                        input_examples=test_spec['input_examples'],
                        expected_outputs=test_spec['expected_outputs'],
                        test_description=test_spec['description'],
                        validation_strategy=test_spec['validation_strategy'],
                        ai_generated=False  # User-provided specifications
                    )
                    
                    # Generate executable test code
                    test_case.test_code = test_case.generate_test_code()
                    
                    # Validate the test case
                    test_case.validate()
                    intelligent_tests.append(test_case)
                    
                except Exception as e:
                    self._logger.error(f"Failed to create test case '{test_spec['name']}': {e}")
                    # Continue with other test cases
            
            if not intelligent_tests:
                raise OperationError(
                    "Failed to generate any valid test cases",
                    "Check your test case specifications and ensure they are properly formatted."
                )
            
            # Create test files
            test_files_created = []
            try:
                output_dir = self.project_path / "tests"
                output_dir.mkdir(exist_ok=True)
                
                # Create test file for the target module
                test_file_name = f"test_{target_module.name.replace('.', '_')}_targeted.py"
                test_file_path = output_dir / test_file_name
                
                # Generate test file content
                test_content = self._generate_targeted_test_file_content(target_module, intelligent_tests)
                
                # Write test file
                test_file_path.write_text(test_content, encoding='utf-8')
                test_files_created.append(str(test_file_path))
                
                self._logger.info(f"Created targeted test file: {test_file_path}")
                
            except Exception as e:
                self._logger.error(f"Failed to create test files: {e}")
                # Continue without failing the operation
            
            # Create result
            result = TestGenerationResult(
                generated_tests=intelligent_tests,
                test_files_created=test_files_created,
                execution_result=None,
                success=True,
                errors=[]
            )
            
            self._logger.info(f"Successfully generated {len(intelligent_tests)} targeted tests for '{function_name}'")
            return result
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, ValidationError, OperationError, ProjectStateError)):
                raise
            self._handle_unexpected_error("targeted test generation", e)
    
    def _generate_targeted_test_file_content(self, module, test_cases: List) -> str:
        """
        Generate test file content for targeted tests.
        
        Args:
            module: Module containing the function being tested
            test_cases: List of IntelligentTestCase objects
            
        Returns:
            str: Complete test file content
        """
        imports = self._generate_test_imports(module)
        class_name = f"Test{module.name.replace('.', '').title()}Targeted"
        
        content = f'''"""
Targeted unit tests for {module.name} module.

This file contains user-specified test cases with specific input/output examples.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
{imports}


class {class_name}(unittest.TestCase):
    """Targeted test cases for {module.name} module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def tearDown(self):
        """Clean up after each test method."""
        pass

{self._format_intelligent_test_methods(test_cases)}


if __name__ == '__main__':
    unittest.main()
'''
        
        return content
    
    def _generate_test_imports(self, module) -> str:
        """Generate import statements for test file."""
        # Import the module being tested
        module_import = f"from {module.name} import *"
        
        # Add any additional imports based on module dependencies
        additional_imports = []
        for dep in module.dependencies:
            additional_imports.append(f"import {dep}")
        
        if additional_imports:
            return f"{module_import}\n" + "\n".join(additional_imports)
        else:
            return module_import
    
    def _format_intelligent_test_methods(self, test_cases: List) -> str:
        """Format intelligent test cases as test methods."""
        formatted_methods = []
        
        for test_case in test_cases:
            # Ensure proper indentation
            indented_code = "\n".join(
                "    " + line if line.strip() else line 
                for line in test_case.test_code.split('\n')
            )
            formatted_methods.append(indented_code)
        
        return "\n\n".join(formatted_methods)
    
    def _get_phase_value(self, phase) -> str:
        """
        Helper method to safely get the phase value from either enum or string.
        
        Args:
            phase: Either a ProjectPhase enum or a string
            
        Returns:
            The phase value as a string
        """
        return phase.value if hasattr(phase, 'value') else phase
    
    def _handle_unexpected_error(self, operation: str, error: Exception) -> None:
        """
        Handle unexpected errors with user-friendly messages.
        
        Args:
            operation: The operation that failed
            error: The exception that occurred
            
        Raises:
            OperationError: Always raises with user-friendly message
        """
        self._logger.error(f"Unexpected error during {operation}: {error}")
        
        # Provide specific guidance based on error type
        if "network" in str(error).lower() or "connection" in str(error).lower():
            suggestion = "Check your internet connection and try again."
        elif "permission" in str(error).lower() or "access" in str(error).lower():
            suggestion = "Check file permissions and ensure you have write access to the project directory."
        elif "api" in str(error).lower() or "key" in str(error).lower():
            suggestion = "Verify your API key is correct and has sufficient credits."
        elif "timeout" in str(error).lower():
            suggestion = "The operation timed out. Try again or check your network connection."
        elif "analysis" in str(error).lower() or "scan" in str(error).lower():
            suggestion = "The project analysis failed. Ensure the project contains valid Python files and you have read permissions."
        elif "debug" in str(error).lower() or "revision" in str(error).lower():
            suggestion = "The debug analysis failed. The error may be too complex to analyze automatically."
        elif "execution" in str(error).lower() or "test" in str(error).lower():
            suggestion = "Code execution or testing failed. Check the function implementation and test files."
        else:
            suggestion = "This is an unexpected error. Please check the logs for more details and try again."
        
        raise OperationError(
            f"Unexpected error during {operation}: {error}",
            suggestion
        ) from error
    
    def _infer_module_path(self, function_spec: FunctionSpec) -> Optional[str]:
        """
        Infer the module file path from function specification.
        
        Args:
            function_spec: Function specification containing module information
            
        Returns:
            Inferred module path or None if not found
        """
        try:
            # Try to load project plan to get module information
            plan = self._state_manager.load_project_plan() if self._state_manager else None
            
            if plan:
                # Find the module in the plan
                for module in plan.modules:
                    if module.name == function_spec.module:
                        module_path = Path(module.file_path)
                        if not module_path.is_absolute():
                            module_path = self.project_path / module_path
                        if module_path.exists():
                            return str(module_path)
            
            # Fallback: construct path from module name
            if '.' in function_spec.module:
                # Convert dotted module name to path: 'parsers.html_parser' -> 'parsers/html_parser.py'
                module_file_path = function_spec.module.replace('.', '/') + '.py'
            else:
                module_file_path = f"{function_spec.module}.py"
            
            # Try relative to project path
            candidate_path = self.project_path / module_file_path
            if candidate_path.exists():
                return str(candidate_path)
            
            # Try in current directory
            candidate_path = Path(module_file_path)
            if candidate_path.exists():
                return str(candidate_path)
            
            return None
            
        except Exception:
            return None
    
    def _enhance_status_with_guidance(self, status: ProjectStatus) -> ProjectStatus:
        """
        Enhance project status with user-friendly guidance.
        
        Args:
            status: Original project status
            
        Returns:
            ProjectStatus: Enhanced status with guidance
        """
        if not status.progress:
            status.next_action = "Run plan() to start a new project"
            return status
        
        # Provide phase-specific guidance
        phase = status.progress.current_phase
        
        if phase == ProjectPhase.PLANNING:
            if status.progress.total_functions > 0:
                status.next_action = "Run generate_specs() to create function specifications"
            else:
                status.next_action = "Planning in progress or incomplete"
        
        elif phase == ProjectPhase.SPECIFICATION:
            status.next_action = "Run implement() to generate function implementations"
        
        elif phase == ProjectPhase.IMPLEMENTATION:
            if status.progress.failed_functions:
                failed_count = len(status.progress.failed_functions)
                status.next_action = f"Run integrate() to complete the project ({failed_count} functions failed)"
                if failed_count > status.progress.total_functions * 0.5:
                    status.next_action += ". Consider reviewing the objective or API key due to high failure rate."
            else:
                status.next_action = "Run integrate() to connect all modules"
        
        elif phase == ProjectPhase.INTEGRATION:
            status.next_action = "Integration in progress"
        
        elif phase == ProjectPhase.COMPLETED:
            status.next_action = "Project completed successfully! Check your project files."
        
        # Add progress information to next_action
        if status.progress.total_functions > 0:
            progress_pct = (status.progress.implemented_functions / status.progress.total_functions) * 100
            status.next_action += f" (Progress: {progress_pct:.1f}%)"
        
        return status
    
    def get_error_guidance(self, error: Exception) -> str:
        """
        Get user-friendly guidance for handling errors.
        
        Args:
            error: The exception that occurred
            
        Returns:
            str: User-friendly guidance message
        """
        if isinstance(error, A3Error):
            return error.get_user_message()
        
        # Provide guidance for common error patterns
        error_str = str(error).lower()
        
        if "api key" in error_str:
            return ("API Key Issue: Check that your API key is valid and has sufficient credits. "
                   "You can verify your key at https://openrouter.ai/keys")
        
        elif "network" in error_str or "connection" in error_str:
            return ("Network Issue: Check your internet connection and try again. "
                   "If the problem persists, the API service may be temporarily unavailable.")
        
        elif "permission" in error_str or "access" in error_str:
            return ("Permission Issue: Ensure you have write access to the project directory. "
                   "Try running with appropriate permissions or choose a different directory.")
        
        elif "not found" in error_str:
            return ("File Not Found: The required files may be missing or corrupted. "
                   "Try starting over with plan() or check your project directory.")
        
        elif "analysis" in error_str or "scan" in error_str:
            return ("Project Analysis Issue: The project structure could not be analyzed properly. "
                   "Ensure the directory contains valid Python files and you have read permissions.")
        
        elif "debug" in error_str or "revision" in error_str:
            return ("Debug Analysis Issue: The error could not be analyzed automatically. "
                   "Try simplifying the function or reviewing the error manually.")
        
        elif "execution" in error_str or "test" in error_str:
            return ("Execution/Testing Issue: The code could not be executed or tested properly. "
                   "Check the function implementation, dependencies, and test files.")
        
        else:
            return (f"Unexpected Error: {error}\n"
                   "Try the operation again. If the problem persists, check your configuration and network connection.")
    
    def print_status_report(self, project_path: str = ".") -> None:
        """
        Print a detailed, user-friendly status report.
        
        Args:
            project_path: Path to the project directory
        """
        try:
            status = self.status(project_path)
            
            print("\n" + "="*60)
            print("A3 PROJECT STATUS REPORT")
            print("="*60)
            
            if not status.is_active:
                print("Status: No active project")
                if status.errors:
                    print(f"Issues: {'; '.join(status.errors)}")
                print(f"Next Action: {status.next_action}")
                return
            
            print("Status: Active project found")
            
            if status.progress:
                progress = status.progress
                current_phase_value = self._get_phase_value(progress.current_phase)
                print(f"Current Phase: {current_phase_value.title()}")
                print(f"Last Updated: {progress.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if progress.total_functions > 0:
                    success_rate = (progress.implemented_functions / progress.total_functions) * 100
                    print(f"Progress: {progress.implemented_functions}/{progress.total_functions} functions ({success_rate:.1f}%)")
                    
                    if progress.failed_functions:
                        print(f"Failed Functions: {len(progress.failed_functions)}")
                        if len(progress.failed_functions) <= 5:
                            print(f"  - {', '.join(progress.failed_functions)}")
                        else:
                            print(f"  - {', '.join(progress.failed_functions[:5])} and {len(progress.failed_functions)-5} more")
                
                print(f"Completed Phases: {', '.join([p.value.title() for p in progress.completed_phases])}")
            
            if status.errors:
                print(f"Current Issues: {'; '.join(status.errors)}")
            
            print(f"Next Action: {status.next_action}")
            print("="*60)
            
        except Exception as e:
            print(f"Error generating status report: {e}")
            print("Try checking your project directory and permissions.")
    
    def validate_environment(self) -> Dict[str, bool]:
        """
        Validate the environment for A3 operations.
        
        Returns:
            Dict[str, bool]: Validation results for different components
        """
        results = {
            "api_key_set": self._api_key is not None,
            "api_key_valid": False,
            "project_directory_writable": False,
            "state_manager_initialized": self._state_manager is not None,
            "project_manager_initialized": self._project_manager is not None
        }
        
        # Test API key validity
        if self._api_key:
            try:
                from ..clients.openrouter import OpenRouterClient
                client = OpenRouterClient(self._api_key)
                results["api_key_valid"] = client.validate_api_key()
            except Exception:
                results["api_key_valid"] = False
        
        # Test project directory writability
        try:
            test_file = self.project_path / ".a3_test"
            test_file.write_text("test")
            test_file.unlink()
            results["project_directory_writable"] = True
        except Exception:
            results["project_directory_writable"] = False
        
        return results
    

    def get_available_models(self) -> List[str]:
        """
        Get list of available models from OpenRouter API.
        
        Returns:
            List[str]: List of available model names
            
        Raises:
            ConfigurationError: If API key is not set
            OperationError: If API request fails
        """
        self._ensure_initialized()
        
        try:
            from ..clients.openrouter import OpenRouterClient
            client = OpenRouterClient(self._api_key)
            
            # Try to get models from API with caching
            try:
                models = client.get_available_models()
                
                # Update cached models in configuration
                try:
                    config = self._state_manager.get_or_create_model_configuration()
                    config.available_models = models
                    config.last_updated = datetime.now()
                    self._state_manager.save_model_configuration(config)
                except Exception as e:
                    # Log warning but don't fail the operation
                    self._logger.warning(f"Failed to cache available models: {e}")
                
                return models
                
            except Exception as e:
                # Fallback to cached models if API fails
                self._logger.warning(f"Failed to fetch models from API: {e}")
                
                try:
                    config = self._state_manager.load_model_configuration()
                    if config and config.available_models:
                        self._logger.info("Using cached model list")
                        return config.available_models
                except Exception:
                    pass
                
                # Final fallback to hardcoded list
                fallback_models = [
                    "qwen/qwen-2.5-72b-instruct:free",
                    "qwen/qwen-2-72b-instruct:free", 
                    "openai/gpt-3.5-turbo",
                    "anthropic/claude-3-haiku",
                    "meta-llama/llama-3.1-8b-instruct:free",
                    "microsoft/wizardlm-2-8x22b:free"
                ]
                
                self._logger.info("Using fallback model list due to API unavailability")
                return fallback_models
                
        except Exception as e:
            if isinstance(e, (ConfigurationError, OperationError)):
                raise
            self._handle_unexpected_error("getting available models", e)

    def generate_structured_documentation(self, objective: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate structured documentation (requirements, design, tasks) from objective.
        
        Args:
            objective: High-level description of what the project should accomplish
            config: Optional documentation configuration
            
        Returns:
            Dict containing generated documentation components
            
        Raises:
            ConfigurationError: If API key is not set
            OperationError: If documentation generation fails
            ValidationError: If objective is empty or invalid
        """
        try:
            # Validate input
            if not objective or not objective.strip():
                raise ValidationError(
                    "Project objective cannot be empty",
                    "Please provide a clear description of what you want to build."
                )
            
            self._ensure_initialized()
            
            # Import required components
            from ..engines.planning import PlanningEngine
            from ..clients.openrouter import OpenRouterClient
            from ..core.models import DocumentationConfiguration
            
            # Initialize components
            client = OpenRouterClient(self._api_key)
            planning_engine = PlanningEngine(client)
            
            # Create documentation configuration
            doc_config = DocumentationConfiguration()
            if config:
                for key, value in config.items():
                    if hasattr(doc_config, key):
                        setattr(doc_config, key, value)
            
            self._logger.info(f"Generating structured documentation for objective: {objective}")
            
            # Generate enhanced project plan with documentation
            enhanced_plan = planning_engine.generate_plan_with_documentation(objective, doc_config)
            
            # Convert to dictionary format for API response
            result = {
                "success": True,
                "requirements": None,
                "design": None,
                "tasks": None,
                "generated_at": datetime.now().isoformat()
            }
            
            if enhanced_plan.requirements_document:
                result["requirements"] = {
                    "introduction": enhanced_plan.requirements_document.introduction,
                    "requirements": [
                        {
                            "id": req.id,
                            "user_story": req.user_story,
                            "acceptance_criteria": [
                                {"when_clause": ac.when_clause, "shall_clause": ac.shall_clause}
                                for ac in req.acceptance_criteria
                            ],
                            "priority": req.priority.value,
                            "category": req.category
                        }
                        for req in enhanced_plan.requirements_document.requirements
                    ]
                }
            
            if enhanced_plan.design_document:
                result["design"] = {
                    "overview": enhanced_plan.design_document.overview,
                    "architecture": enhanced_plan.design_document.architecture,
                    "components": [
                        {
                            "name": comp.name,
                            "description": comp.description,
                            "interfaces": comp.interfaces,
                            "dependencies": comp.dependencies
                        }
                        for comp in enhanced_plan.design_document.components
                    ]
                }
            
            if enhanced_plan.tasks_document:
                result["tasks"] = {
                    "tasks": [
                        {
                            "id": task.id,
                            "description": task.description,
                            "requirements": task.requirements,
                            "design_components": task.design_components,
                            "estimated_effort": task.estimated_effort,
                            "dependencies": task.dependencies
                        }
                        for task in enhanced_plan.tasks_document.tasks
                    ]
                }
            
            self._logger.info("Structured documentation generation completed successfully")
            return result
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, OperationError, ValidationError)):
                raise
            self._handle_unexpected_error("generating structured documentation", e)
    
    def export_documentation(self, format: str = "markdown", output_path: Optional[str] = None) -> str:
        """
        Export generated documentation to specified format.
        
        Args:
            format: Export format ("markdown", "json", "html")
            output_path: Optional output file path
            
        Returns:
            str: Path to exported file
            
        Raises:
            ProjectStateError: If no documentation exists
            ValidationError: If format is invalid
        """
        try:
            # Validate format
            valid_formats = ["markdown", "json", "html"]
            if format not in valid_formats:
                raise ValidationError(
                    f"Invalid export format: {format}",
                    f"Valid formats: {', '.join(valid_formats)}"
                )
            
            # Load enhanced project plan
            if not self._state_manager:
                self._state_manager = StateManager(str(self.project_path))
            
            try:
                enhanced_plan = self._state_manager.load_enhanced_project_plan()
                if not enhanced_plan:
                    raise ProjectStateError(
                        "No structured documentation found",
                        "Generate documentation first using generate_structured_documentation()"
                    )
            except Exception:
                raise ProjectStateError(
                    "No structured documentation found",
                    "Generate documentation first using generate_structured_documentation()"
                )
            
            # Determine output path
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(self.project_path / f"documentation_export_{timestamp}.{format}")
            
            output_file = Path(output_path)
            
            # Export based on format
            if format == "json":
                import json
                export_data = {
                    "requirements": {
                        "introduction": enhanced_plan.requirements_document.introduction if enhanced_plan.requirements_document else "",
                        "requirements": [
                            {
                                "id": req.id,
                                "user_story": req.user_story,
                                "acceptance_criteria": [
                                    {"when_clause": ac.when_clause, "shall_clause": ac.shall_clause}
                                    for ac in req.acceptance_criteria
                                ],
                                "priority": req.priority.value,
                                "category": req.category
                            }
                            for req in (enhanced_plan.requirements_document.requirements if enhanced_plan.requirements_document else [])
                        ]
                    } if enhanced_plan.requirements_document else None,
                    "design": {
                        "overview": enhanced_plan.design_document.overview if enhanced_plan.design_document else "",
                        "architecture": enhanced_plan.design_document.architecture if enhanced_plan.design_document else "",
                        "components": [
                            {
                                "name": comp.name,
                                "description": comp.description,
                                "interfaces": comp.interfaces,
                                "dependencies": comp.dependencies
                            }
                            for comp in (enhanced_plan.design_document.components if enhanced_plan.design_document else [])
                        ]
                    } if enhanced_plan.design_document else None,
                    "tasks": {
                        "tasks": [
                            {
                                "id": task.id,
                                "description": task.description,
                                "requirements": task.requirements,
                                "design_components": task.design_components,
                                "estimated_effort": task.estimated_effort,
                                "dependencies": task.dependencies
                            }
                            for task in (enhanced_plan.tasks_document.tasks if enhanced_plan.tasks_document else [])
                        ]
                    } if enhanced_plan.tasks_document else None,
                    "exported_at": datetime.now().isoformat()
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                    
            elif format == "markdown":
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("# Project Documentation Export\n\n")
                    f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    if enhanced_plan.requirements_document:
                        f.write("## Requirements\n\n")
                        f.write(f"{enhanced_plan.requirements_document.introduction}\n\n")
                        for req in enhanced_plan.requirements_document.requirements:
                            f.write(f"### {req.id}: {req.user_story}\n\n")
                            for ac in req.acceptance_criteria:
                                f.write(f"- {ac.when_clause} THEN {ac.shall_clause}\n")
                            f.write("\n")
                    
                    if enhanced_plan.design_document:
                        f.write("## Design\n\n")
                        f.write(f"{enhanced_plan.design_document.overview}\n\n")
                        f.write(f"### Architecture\n\n{enhanced_plan.design_document.architecture}\n\n")
                        for comp in enhanced_plan.design_document.components:
                            f.write(f"### Component: {comp.name}\n\n")
                            f.write(f"{comp.description}\n\n")
                    
                    if enhanced_plan.tasks_document:
                        f.write("## Implementation Tasks\n\n")
                        for task in enhanced_plan.tasks_document.tasks:
                            f.write(f"- [ ] **{task.id}**: {task.description}\n")
                            if task.requirements:
                                f.write(f"  - Requirements: {', '.join(task.requirements)}\n")
                            f.write("\n")
            
            elif format == "html":
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("<!DOCTYPE html>\n<html>\n<head>\n")
                    f.write("<title>Project Documentation</title>\n")
                    f.write("<style>body{font-family:Arial,sans-serif;margin:40px;} h1,h2,h3{color:#333;} .requirement{margin:20px 0;} .task{margin:10px 0;}</style>\n")
                    f.write("</head>\n<body>\n")
                    f.write("<h1>Project Documentation Export</h1>\n")
                    f.write(f"<p>Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
                    
                    if enhanced_plan.requirements_document:
                        f.write("<h2>Requirements</h2>\n")
                        f.write(f"<p>{enhanced_plan.requirements_document.introduction}</p>\n")
                        for req in enhanced_plan.requirements_document.requirements:
                            f.write(f"<div class='requirement'>\n")
                            f.write(f"<h3>{req.id}: {req.user_story}</h3>\n")
                            f.write("<ul>\n")
                            for ac in req.acceptance_criteria:
                                f.write(f"<li>{ac.when_clause} THEN {ac.shall_clause}</li>\n")
                            f.write("</ul>\n</div>\n")
                    
                    if enhanced_plan.design_document:
                        f.write("<h2>Design</h2>\n")
                        f.write(f"<p>{enhanced_plan.design_document.overview}</p>\n")
                        f.write(f"<h3>Architecture</h3>\n<p>{enhanced_plan.design_document.architecture}</p>\n")
                        for comp in enhanced_plan.design_document.components:
                            f.write(f"<h3>Component: {comp.name}</h3>\n")
                            f.write(f"<p>{comp.description}</p>\n")
                    
                    if enhanced_plan.tasks_document:
                        f.write("<h2>Implementation Tasks</h2>\n")
                        f.write("<ul>\n")
                        for task in enhanced_plan.tasks_document.tasks:
                            f.write(f"<li class='task'><strong>{task.id}</strong>: {task.description}")
                            if task.requirements:
                                f.write(f" (Requirements: {', '.join(task.requirements)})")
                            f.write("</li>\n")
                        f.write("</ul>\n")
                    
                    f.write("</body>\n</html>\n")
            
            self._logger.info(f"Documentation exported to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            if isinstance(e, (ProjectStateError, ValidationError)):
                raise
            self._handle_unexpected_error("exporting documentation", e)
    
    def validate_documentation(self, check_coverage: bool = True, check_consistency: bool = True) -> Dict[str, Any]:
        """
        Validate requirement coverage and document consistency.
        
        Args:
            check_coverage: Whether to check requirement coverage in implementation
            check_consistency: Whether to check consistency between documents
            
        Returns:
            Dict containing validation results
            
        Raises:
            ProjectStateError: If no documentation exists
        """
        try:
            # Load enhanced project plan
            if not self._state_manager:
                self._state_manager = StateManager(str(self.project_path))
            
            try:
                enhanced_plan = self._state_manager.load_enhanced_project_plan()
                if not enhanced_plan:
                    raise ProjectStateError(
                        "No structured documentation found",
                        "Generate documentation first using generate_structured_documentation()"
                    )
            except Exception:
                raise ProjectStateError(
                    "No structured documentation found",
                    "Generate documentation first using generate_structured_documentation()"
                )
            
            validation_result = {
                "success": True,
                "errors": [],
                "warnings": [],
                "coverage_percentage": 0,
                "validated_at": datetime.now().isoformat()
            }
            
            # Check consistency between documents
            if check_consistency:
                if enhanced_plan.requirements_document and enhanced_plan.design_document:
                    # Check that all requirements are referenced in design
                    req_ids = {req.id for req in enhanced_plan.requirements_document.requirements}
                    design_req_refs = set()
                    
                    for component in enhanced_plan.design_document.components:
                        if hasattr(component, 'requirement_references'):
                            design_req_refs.update(component.requirement_references)
                    
                    missing_in_design = req_ids - design_req_refs
                    if missing_in_design:
                        validation_result["warnings"].append(f"Requirements not referenced in design: {', '.join(missing_in_design)}")
                    
                    extra_in_design = design_req_refs - req_ids
                    if extra_in_design:
                        validation_result["errors"].append(f"Design references non-existent requirements: {', '.join(extra_in_design)}")
                
                if enhanced_plan.design_document and enhanced_plan.tasks_document:
                    # Check that all design components are covered by tasks
                    component_names = {comp.name for comp in enhanced_plan.design_document.components}
                    task_component_refs = set()
                    
                    for task in enhanced_plan.tasks_document.tasks:
                        if task.design_components:
                            task_component_refs.update(task.design_components)
                    
                    missing_in_tasks = component_names - task_component_refs
                    if missing_in_tasks:
                        validation_result["warnings"].append(f"Design components not covered by tasks: {', '.join(missing_in_tasks)}")
            
            # Check requirement coverage in implementation
            if check_coverage and enhanced_plan.requirements_document:
                # Look for Python files in the project
                python_files = []
                for root, dirs, files in os.walk(self.project_path):
                    # Skip hidden directories and common build/cache directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
                    for file in files:
                        if file.endswith('.py') and not file.startswith('.'):
                            python_files.append(os.path.join(root, file))
                
                if python_files:
                    # Check for requirement references in code
                    req_ids = {req.id for req in enhanced_plan.requirements_document.requirements}
                    found_refs = set()
                    
                    import re
                    for py_file in python_files:
                        try:
                            with open(py_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Look for requirement references in comments and docstrings
                            for req_id in req_ids:
                                if re.search(rf'(?i)requirement\s*{re.escape(req_id)}|req\s*{re.escape(req_id)}', content):
                                    found_refs.add(req_id)
                                    
                        except Exception as e:
                            validation_result["warnings"].append(f"Could not analyze {py_file}: {e}")
                    
                    missing_coverage = req_ids - found_refs
                    if missing_coverage:
                        validation_result["warnings"].append(f"Requirements not referenced in implementation: {', '.join(missing_coverage)}")
                    
                    validation_result["coverage_percentage"] = (len(found_refs) / len(req_ids)) * 100 if req_ids else 100
                else:
                    validation_result["warnings"].append("No Python files found for coverage analysis")
            
            # Set success based on errors
            validation_result["success"] = len(validation_result["errors"]) == 0
            
            self._logger.info(f"Documentation validation completed: {len(validation_result['errors'])} errors, {len(validation_result['warnings'])} warnings")
            return validation_result
            
        except Exception as e:
            if isinstance(e, ProjectStateError):
                raise
            self._handle_unexpected_error("validating documentation", e)
    
    def get_documentation_config(self) -> Dict[str, Any]:
        """
        Get current documentation configuration.
        
        Returns:
            Dict containing current documentation configuration
        """
        try:
            from ..core.models import DocumentationConfiguration
            import json
            
            # Try to load existing configuration
            config_path = self.project_path / '.a3' / 'documentation_config.json'
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    doc_config = DocumentationConfiguration(**config_data)
                except Exception:
                    doc_config = DocumentationConfiguration()
            else:
                doc_config = DocumentationConfiguration()
            
            return {
                "enable_requirements": doc_config.enable_requirements,
                "enable_design": doc_config.enable_design,
                "enable_tasks": doc_config.enable_tasks,
                "requirements_format": doc_config.requirements_format,
                "use_ears_format": doc_config.use_ears_format,
                "include_user_stories": doc_config.include_user_stories,
                "validate_requirements": doc_config.validate_requirements,
                "check_consistency": doc_config.check_consistency,
                "require_traceability": doc_config.require_traceability,
                "config_path": str(config_path)
            }
            
        except Exception as e:
            self._logger.error(f"Error getting documentation config: {e}")
            return {"error": str(e)}
    
    def set_documentation_config(self, **config_updates) -> None:
        """
        Update documentation configuration.
        
        Args:
            **config_updates: Configuration key-value pairs to update
            
        Raises:
            ValidationError: If configuration keys are invalid
        """
        try:
            from ..core.models import DocumentationConfiguration
            import json
            
            # Available configuration keys
            available_keys = [
                'enable_requirements', 'enable_design', 'enable_tasks',
                'requirements_format', 'use_ears_format', 'include_user_stories',
                'validate_requirements', 'check_consistency', 'require_traceability'
            ]
            
            # Validate keys
            invalid_keys = set(config_updates.keys()) - set(available_keys)
            if invalid_keys:
                raise ValidationError(
                    f"Invalid configuration keys: {', '.join(invalid_keys)}",
                    f"Valid keys: {', '.join(available_keys)}"
                )
            
            # Load existing configuration
            config_path = self.project_path / '.a3' / 'documentation_config.json'
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    doc_config = DocumentationConfiguration(**config_data)
                except Exception:
                    doc_config = DocumentationConfiguration()
            else:
                doc_config = DocumentationConfiguration()
            
            # Update configuration
            for key, value in config_updates.items():
                setattr(doc_config, key, value)
            
            # Save configuration
            config_data = {
                'enable_requirements': doc_config.enable_requirements,
                'enable_design': doc_config.enable_design,
                'enable_tasks': doc_config.enable_tasks,
                'requirements_format': doc_config.requirements_format,
                'use_ears_format': doc_config.use_ears_format,
                'include_user_stories': doc_config.include_user_stories,
                'validate_requirements': doc_config.validate_requirements,
                'check_consistency': doc_config.check_consistency,
                'require_traceability': doc_config.require_traceability
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            self._logger.info(f"Documentation configuration updated: {list(config_updates.keys())}")
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self._handle_unexpected_error("setting documentation configuration", e)

    def get_help_message(self, topic: Optional[str] = None) -> str:
        """
        Get help message for A3 usage.
        
        Args:
            topic: Specific topic to get help for
            
        Returns:
            str: Help message
        """
        if topic == "getting_started":
            return """
Getting Started with A3:

1. Set your API key:
   a3.set_api_key("your-openrouter-api-key")

2. Create a project plan:
   plan = a3.plan("Build a web scraper for news articles")

3. Generate specifications:
   specs = a3.generate_specs()

4. Implement the code:
   result = a3.implement()

5. Integrate modules:
   integration = a3.integrate()

6. Check status anytime:
   status = a3.status()
   a3.print_status_report()

For more help: a3.get_help_message("errors") or a3.get_help_message("troubleshooting")
"""
        
        elif topic == "errors":
            return """
Common A3 Errors and Solutions:

1. ConfigurationError:
   - Check your API key is valid
   - Ensure you have internet connection
   - Verify API key has sufficient credits

2. ProjectStateError:
   - Run operations in correct order: plan() → generate_specs() → implement() → integrate()
   - Check if project directory is corrupted
   - Use resume() for interrupted projects

3. OperationError:
   - Check network connection
   - Verify API service availability
   - Try the operation again

4. ValidationError:
   - Provide more detailed project objectives
   - Check input parameters
   - Ensure project directory is writable

Use a3.get_error_guidance(error) for specific error help.
"""
        
        elif topic == "troubleshooting":
            return """
A3 Troubleshooting Guide:

1. Project won't start:
   - Check API key: a3.validate_environment()
   - Verify directory permissions
   - Try a different project directory

2. Planning fails:
   - Make objective more specific and detailed
   - Check API key credits and validity
   - Ensure stable internet connection

3. Implementation has many failures:
   - Review generated specifications
   - Check if objective is too complex
   - Try breaking down into smaller projects

4. Integration issues:
   - Check for circular dependencies
   - Verify all implementations completed
   - Review module relationships

5. General debugging:
   - Use a3.print_status_report() for detailed status
   - Check logs for detailed error information
   - Use a3.status() to understand current state
"""
        
        else:
            return """
A3 - AI Project Builder Help

Available help topics:
- a3.get_help_message("getting_started") - Basic usage guide
- a3.get_help_message("errors") - Common errors and solutions  
- a3.get_help_message("troubleshooting") - Troubleshooting guide

Main methods:
- set_api_key(key) - Set your OpenRouter API key
- plan(objective) - Generate project plan from objective
- generate_specs() - Create function specifications
- implement() - Generate code implementations
- integrate() - Connect all modules
- status() - Get current project status
- resume() - Resume interrupted project
- print_status_report() - Detailed status display

Enhanced capabilities:
- analyze_project(path) - Analyze existing project structure
- debug_and_revise(error, func_spec, module_path) - Debug failed implementations
- execute_and_test(func_spec, module_path, test_files) - Execute and test code

Enhanced planning capabilities:
- generate_structured_documentation(objective, config) - Generate requirements, design, and tasks
- export_documentation(format, output_path) - Export documentation in various formats
- validate_documentation(check_coverage, check_consistency) - Validate requirement coverage
- get_documentation_config() - Get current documentation configuration
- set_documentation_config(**config) - Update documentation configuration

Utility methods:
- validate_environment() - Check system readiness
- get_error_guidance(error) - Get help for specific errors

For detailed documentation, visit: https://github.com/your-repo/a3
"""