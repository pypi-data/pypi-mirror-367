"""
Integration engine implementation for AI Project Builder.

This module provides the IntegrationEngine class that handles module integration,
import generation, and verification of module connections.
"""

import ast
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict

from .base import BaseIntegrationEngine
from ..core.models import (
    Module, IntegrationResult, ValidationResult, DependencyGraph,
    TestGenerationResult, ValidationLevel, ValidationErrorCategory
)
from dataclasses import dataclass
from ..core.interfaces import (
    DependencyAnalyzerInterface, FileSystemManagerInterface
)


class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass


class ImportGenerationError(IntegrationError):
    """Exception raised when import generation fails."""
    pass


class ModuleConnectionError(IntegrationError):
    """Exception raised when module connection fails."""
    pass


class ImportVerificationError(IntegrationError):
    """Exception raised when import verification fails."""
    pass


@dataclass
class ModuleConnectionResult:
    """Result of connecting a single module."""
    success: bool
    errors: List[str]


class IntegrationEngine(BaseIntegrationEngine):
    """
    Engine for integrating modules and managing imports.
    
    Handles automatic import generation, module connection according to
    dependency graphs, and verification of import resolution.
    """
    
    def __init__(self, 
                 dependency_analyzer: Optional[DependencyAnalyzerInterface] = None,
                 filesystem_manager: Optional[FileSystemManagerInterface] = None,
                 ai_client=None, 
                 state_manager=None,
                 test_generator=None,
                 package_manager=None):
        """
        Initialize the integration engine.
        
        Args:
            dependency_analyzer: Analyzer for module dependencies
            filesystem_manager: Manager for file system operations
            ai_client: AI client for assistance (inherited from base)
            state_manager: State manager for persistence (inherited from base)
            test_generator: Test generator for creating unit tests
            package_manager: Manager for package imports and consistency
        """
        super().__init__(ai_client, state_manager)
        self.dependency_analyzer = dependency_analyzer
        self.filesystem_manager = filesystem_manager
        self.test_generator = test_generator
        self.package_manager = package_manager
        self._import_cache: Dict[str, List[str]] = {}
        self._module_cache: Dict[str, Dict[str, Any]] = {}
        
        # Set up logging for import generation issues
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def initialize(self) -> None:
        """Initialize the integration engine."""
        super().initialize()
        
        if self.dependency_analyzer and hasattr(self.dependency_analyzer, 'initialize'):
            self.dependency_analyzer.initialize()
        
        if self.filesystem_manager and hasattr(self.filesystem_manager, 'initialize'):
            self.filesystem_manager.initialize()
        
        if self.package_manager and hasattr(self.package_manager, 'initialize'):
            self.package_manager.initialize()
    
    def validate_prerequisites(self) -> ValidationResult:
        """Validate prerequisites for integration operations."""
        result = super().validate_prerequisites()
        
        if self.dependency_analyzer is None:
            result.issues.append("Dependency analyzer is required but not provided")
        
        if self.filesystem_manager is None:
            result.issues.append("File system manager is required but not provided")
        
        # Package manager is optional but recommended
        if self.package_manager is None:
            result.warnings.append("Package manager not provided - import consistency may be limited")
        
        return result
    
    def generate_imports(self, modules: List[Module]) -> Dict[str, List[str]]:
        """
        Generate import statements for all modules.
        
        Args:
            modules: List of modules to generate imports for
            
        Returns:
            Dictionary mapping module names to their import statements
            
        Raises:
            ImportGenerationError: If import generation fails
        """
        self._ensure_initialized()
        
        if not modules:
            return {}
        
        try:
            # Clear cache for fresh generation
            self._import_cache.clear()
            
            # Build module information cache
            self._build_module_cache(modules)
            
            # Generate imports for each module
            import_map = {}
            
            for module in modules:
                try:
                    imports = self._generate_module_imports(module, modules)
                    import_map[module.name] = imports
                    self._import_cache[module.name] = imports
                    
                except Exception as e:
                    self.logger.error(f"Failed to generate imports for module '{module.name}': {e}")
                    # Continue with other modules instead of failing completely
                    import_map[module.name] = []
                    self._import_cache[module.name] = []
                    # Don't raise exception, just log and continue
            
            # Validate generated imports for circular dependencies with error handling
            try:
                self._validate_import_dependencies(import_map, modules)
                self.logger.debug("Import dependency validation completed successfully")
            except Exception as e:
                self.logger.warning(f"Import dependency validation failed: {e}")
                # Continue even if validation fails
            
            return import_map
            
        except ImportGenerationError:
            raise
        except Exception as e:
            raise ImportGenerationError(f"Import generation failed: {e}") from e
    
    def integrate_modules(self, modules: List[Module], generate_tests: bool = False) -> IntegrationResult:
        """
        Integrate all modules according to dependency graph.
        
        Args:
            modules: List of modules to integrate
            generate_tests: Whether to generate unit tests during integration
            
        Returns:
            IntegrationResult with integration status and details
        """
        self._ensure_initialized()
        
        if not modules:
            return IntegrationResult(
                integrated_modules=[],
                import_errors=[],
                success=True
            )
        
        integrated_modules = []
        import_errors = []
        
        try:
            # Validate modules before integration with graceful handling
            validation_errors = self._validate_modules_for_integration(modules)
            if validation_errors:
                import_errors.extend(validation_errors)
                self.logger.warning(f"Module validation found {len(validation_errors)} issues, but continuing with integration")
                # Don't return early - continue with integration despite validation errors
            
            # Generate imports for all modules with comprehensive error handling
            try:
                import_map = self.generate_imports(modules)
                self.logger.info(f"Generated imports for {len(import_map)} modules")
            except ImportGenerationError as e:
                self.logger.error(f"Import generation failed: {e}")
                # Continue with empty import map to allow basic integration
                import_map = {}
                import_errors.append(f"Import generation failed: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error during import generation: {e}")
                import_map = {}
                import_errors.append(f"Unexpected import generation error: {e}")
            
            # Get integration order from dependency analyzer
            if self.dependency_analyzer:
                try:
                    integration_order = self.dependency_analyzer.get_build_order(modules)
                except Exception as e:
                    import_errors.append(f"Failed to determine integration order: {e}")
                    # Fall back to original module order
                    integration_order = [module.name for module in modules]
            else:
                integration_order = [module.name for module in modules]
            
            # Connect modules in dependency order with graceful error handling
            for module_name in integration_order:
                try:
                    module = next((m for m in modules if m.name == module_name), None)
                    if not module:
                        error_msg = f"Module '{module_name}' not found in module list"
                        import_errors.append(error_msg)
                        self.logger.error(error_msg)
                        continue
                    
                    self.logger.info(f"Integrating module '{module_name}'")
                    
                    # Connect module with its dependencies
                    connection_result = self._connect_module(module, modules, import_map.get(module_name, []))
                    
                    if connection_result.success:
                        integrated_modules.append(module_name)
                        self.logger.info(f"Successfully integrated module '{module_name}'")
                    else:
                        # Log errors but continue with other modules
                        for error in connection_result.errors:
                            self.logger.error(f"Module '{module_name}' integration error: {error}")
                        import_errors.extend(connection_result.errors)
                        
                        # Still add to integrated modules if it's a partial success
                        # (e.g., file was created but some imports failed)
                        if self._is_partial_integration_acceptable(module, connection_result):
                            integrated_modules.append(module_name)
                            self.logger.warning(f"Module '{module_name}' integrated with warnings")
                        
                except Exception as e:
                    error_msg = f"Critical integration error for module '{module_name}': {e}"
                    import_errors.append(error_msg)
                    self.logger.error(error_msg)
                    # Continue with next module even if this one fails completely
            
            # Determine initial success status
            success = len(import_errors) == 0
            
            # Generate tests if requested
            test_result = None
            if generate_tests and success and self.test_generator:
                try:
                    test_result = self._generate_integration_tests(modules)
                    if not test_result.success:
                        import_errors.extend(test_result.errors)
                        success = False
                except Exception as e:
                    import_errors.append(f"Test generation failed: {e}")
                    success = False
            
            # Verify integration after all modules are connected
            verification_result = self.verify_integration(modules)
            if not verification_result.is_valid:
                import_errors.extend(verification_result.issues)
            
            # Final success determination
            success = len(import_errors) == 0
            
            # Update requirements file if package manager is available and integration succeeded
            package_updates = []
            if success and self.package_manager:
                try:
                    # Get project path from the first module's file path
                    if modules:
                        project_path = str(Path(modules[0].file_path).parent)
                        self.package_manager.update_requirements_file(project_path)
                        package_updates.append("Updated requirements.txt with package dependencies")
                except Exception as e:
                    import_errors.append(f"Failed to update requirements file: {e}")
            
            return IntegrationResult(
                integrated_modules=integrated_modules,
                import_errors=import_errors,
                success=success,
                test_result=test_result,
                package_updates=package_updates if package_updates else None
            )
            
        except Exception as e:
            return IntegrationResult(
                integrated_modules=integrated_modules,
                import_errors=[f"Integration process failed: {e}"],
                success=False
            )
    
    def verify_integration(self, modules: List[Module]) -> ValidationResult:
        """
        Verify that all imports resolve correctly.
        
        Args:
            modules: List of modules to verify
            
        Returns:
            ValidationResult with verification status
        """
        self._ensure_initialized()
        
        if not modules:
            return ValidationResult(is_valid=True, issues=[], warnings=[])
        
        issues = []
        warnings = []
        
        try:
            # Comprehensive module verification
            for module in modules:
                module_issues, module_warnings = self._comprehensive_module_verification(module, modules)
                issues.extend(module_issues)
                warnings.extend(module_warnings)
            
            # Check for circular import dependencies
            try:
                circular_imports = self._detect_circular_imports(modules)
                if circular_imports:
                    for cycle in circular_imports:
                        issues.append(f"Circular import dependency: {' -> '.join(cycle)}")
                        
            except Exception as e:
                warnings.append(f"Could not check for circular imports: {e}")
            
            # Check for unused imports
            try:
                unused_imports = self._find_unused_imports(modules)
                for module_name, unused in unused_imports.items():
                    if unused:
                        warnings.append(f"Module '{module_name}' has unused imports: {unused}")
                        
            except Exception as e:
                warnings.append(f"Could not check for unused imports: {e}")
            
            # Verify dependency graph consistency
            try:
                graph_issues = self._verify_dependency_graph_consistency(modules)
                issues.extend(graph_issues)
            except Exception as e:
                warnings.append(f"Could not verify dependency graph: {e}")
            
            return ValidationResult(
                is_valid=len(issues) == 0,
                issues=issues,
                warnings=warnings
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[f"Integration verification failed: {e}"],
                warnings=warnings
            )
    
    def _comprehensive_module_verification(self, module: Module, all_modules: List[Module]) -> Tuple[List[str], List[str]]:
        """Perform comprehensive verification of a single module."""
        issues = []
        warnings = []
        
        # Check if module file exists and is readable
        if not self._verify_module_file_exists(module):
            issues.append(f"Module file does not exist: {module.file_path}")
            return issues, warnings
        
        # Check file permissions
        if self.filesystem_manager and not self.filesystem_manager.validate_permissions(module.file_path):
            warnings.append(f"Limited permissions for module file: {module.file_path}")
        
        # Parse module file and check syntax
        try:
            content = self.filesystem_manager.read_file(module.file_path) if self.filesystem_manager else None
            if content is None:
                issues.append(f"Cannot read module file: {module.file_path}")
                return issues, warnings
            
            # Check for syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(f"Syntax error in module '{module.name}': {e}")
                return issues, warnings
            
            # Verify imports
            import_issues = self._verify_module_imports(module, all_modules)
            issues.extend(import_issues)
            
            # Check if expected functions are present
            function_issues = self._verify_module_functions(module, content)
            issues.extend(function_issues)
            
            # Check for naming conflicts
            naming_issues = self._check_naming_conflicts(module, content)
            warnings.extend(naming_issues)
            
        except Exception as e:
            issues.append(f"Failed to verify module '{module.name}': {e}")
        
        return issues, warnings
    
    def _verify_module_functions(self, module: Module, content: str) -> List[str]:
        """Verify that expected functions are present in module."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Extract function definitions from AST
            defined_functions = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_functions.add(node.name)
            
            # Check if all expected functions are defined
            for func_spec in module.functions:
                if func_spec.name not in defined_functions:
                    issues.append(f"Function '{func_spec.name}' not found in module '{module.name}'")
            
        except Exception as e:
            issues.append(f"Failed to verify functions in module '{module.name}': {e}")
        
        return issues
    
    def _check_naming_conflicts(self, module: Module, content: str) -> List[str]:
        """Check for naming conflicts in module."""
        warnings = []
        
        try:
            tree = ast.parse(content)
            
            # Extract all names defined in the module
            defined_names = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if node.name in defined_names:
                        warnings.append(f"Name conflict in module '{module.name}': '{node.name}' is defined multiple times")
                    defined_names.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id in defined_names:
                                warnings.append(f"Name conflict in module '{module.name}': '{target.id}' is defined multiple times")
                            defined_names.add(target.id)
            
        except Exception:
            # Not critical, so just skip if parsing fails
            pass
        
        return warnings
    
    def _get_configured_model(self) -> Optional[str]:
        """
        Get the currently configured model from state manager.
        
        Returns:
            Currently configured model name, or None to use client default
        """
        try:
            if self.state_manager:
                model_config = self.state_manager.load_model_configuration()
                if model_config:
                    return model_config.current_model
            return None
        except Exception as e:
            # Log warning but don't fail - fall back to client default
            # In a real implementation, you might want to log this warning
            return None
    
    def _verify_dependency_graph_consistency(self, modules: List[Module]) -> List[str]:
        """Verify that the dependency graph is consistent."""
        issues = []
        
        if not self.dependency_analyzer:
            return issues
        
        try:
            # Create dependency graph
            graph = self.dependency_analyzer.create_dependency_graph(modules)
            
            # Validate the graph
            validation_result = self.dependency_analyzer.validate_dependency_graph(graph)
            if not validation_result.is_valid:
                issues.extend(validation_result.issues)
            
        except Exception as e:
            issues.append(f"Failed to verify dependency graph consistency: {e}")
        
        return issues
    
    # Private helper methods
    
    def _validate_modules_for_integration(self, modules: List[Module]) -> List[str]:
        """Validate modules before integration using full dependency analysis."""
        errors = []
        
        try:
            # Check for duplicate module names
            module_names = [m.name for m in modules]
            if len(module_names) != len(set(module_names)):
                duplicates = [name for name in set(module_names) if module_names.count(name) > 1]
                errors.append(f"Duplicate module names found: {duplicates}")
            
            # Use dependency analyzer for comprehensive validation at integration level
            if self.dependency_analyzer:
                try:
                    from ..core.models import ValidationLevel
                    validation_result = self.dependency_analyzer.analyze_dependencies(
                        modules, validation_level=ValidationLevel.INTEGRATION
                    )
                    if not validation_result.is_valid:
                        # Add integration-specific context to error messages
                        for issue in validation_result.issues:
                            errors.append(f"Integration validation failed: {issue}")
                except Exception as e:
                    errors.append(f"Failed to perform integration-level dependency validation: {e}")
            else:
                # Fallback validation if no dependency analyzer
                # Check for missing dependencies
                for module in modules:
                    for dep in module.dependencies:
                        if not any(m.name == dep for m in modules):
                            errors.append(f"Integration validation failed: Module '{module.name}' depends on missing module '{dep}'")
            
            # Validate module file paths
            for module in modules:
                if not module.file_path or not module.file_path.strip():
                    errors.append(f"Module '{module.name}' has empty file path")
                elif not module.file_path.endswith('.py'):
                    errors.append(f"Module '{module.name}' file path must end with .py: {module.file_path}")
            
        except Exception as e:
            errors.append(f"Module validation failed: {e}")
        
        return errors
    
    def _connect_module(self, module: Module, all_modules: List[Module], imports: List[str]) -> 'ModuleConnectionResult':
        """Connect a module with its dependencies using graceful error handling."""
        errors = []
        warnings = []
        success = True
        
        try:
            self.logger.info(f"Connecting module '{module.name}' with {len(imports)} imports")
            
            # Ensure module file exists or create it with graceful handling
            try:
                if not self._ensure_module_file_exists(module):
                    error_msg = f"Failed to create/access module file: {module.file_path}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
                    success = False
                else:
                    self.logger.debug(f"Module file verified/created: {module.file_path}")
            except Exception as e:
                error_msg = f"Critical error ensuring module file exists for '{module.name}': {e}"
                errors.append(error_msg)
                self.logger.error(error_msg)
                success = False
            
            # Add imports to module file with individual error handling
            if imports:
                try:
                    import_success, import_errors = self._add_imports_to_module_with_fallback(module, imports)
                    if not import_success:
                        # Don't fail the entire connection if some imports fail
                        warnings.extend(import_errors)
                        self.logger.warning(f"Some imports failed for module '{module.name}', but continuing")
                    else:
                        self.logger.debug(f"Successfully added {len(imports)} imports to module '{module.name}'")
                except Exception as e:
                    warning_msg = f"Import addition failed for module '{module.name}': {e}"
                    warnings.append(warning_msg)
                    self.logger.warning(warning_msg)
                    # Continue with connection even if imports fail
            
            # Verify dependencies with graceful handling
            try:
                dependency_errors = self._verify_module_dependencies_with_fallback(module, all_modules)
                if dependency_errors:
                    # Treat dependency issues as warnings, not fatal errors
                    warnings.extend(dependency_errors)
                    self.logger.warning(f"Dependency issues found for module '{module.name}', but continuing")
                else:
                    self.logger.debug(f"All dependencies verified for module '{module.name}'")
            except Exception as e:
                warning_msg = f"Dependency verification failed for module '{module.name}': {e}"
                warnings.append(warning_msg)
                self.logger.warning(warning_msg)
                # Continue even if dependency verification fails
            
            # Add module initialization code with graceful handling
            try:
                if not self._ensure_module_initialization(module):
                    warning_msg = f"Failed to initialize module '{module.name}'"
                    warnings.append(warning_msg)
                    self.logger.warning(warning_msg)
                    # Don't fail connection for initialization issues
                else:
                    self.logger.debug(f"Module initialization verified for '{module.name}'")
            except Exception as e:
                warning_msg = f"Module initialization error for '{module.name}': {e}"
                warnings.append(warning_msg)
                self.logger.warning(warning_msg)
                # Continue even if initialization fails
            
            # Determine final success status
            # Only fail if critical errors occurred (file creation/access)
            final_success = success and len(errors) == 0
            
            # Combine errors and warnings for reporting
            all_issues = errors + warnings
            
            if final_success:
                self.logger.info(f"Successfully connected module '{module.name}' with {len(warnings)} warnings")
            else:
                self.logger.error(f"Failed to connect module '{module.name}' with {len(errors)} errors and {len(warnings)} warnings")
            
            return ModuleConnectionResult(success=final_success, errors=all_issues)
                
        except Exception as e:
            error_msg = f"Critical error in module connection for '{module.name}': {e}"
            errors.append(error_msg)
            self.logger.error(error_msg)
            return ModuleConnectionResult(success=False, errors=errors)
    
    def _ensure_module_file_exists(self, module: Module) -> bool:
        """Ensure module file exists, create if necessary."""
        if not self.filesystem_manager:
            return False
        
        try:
            if self.filesystem_manager.file_exists(module.file_path):
                return True
            
            # Create basic module structure
            module_content = f'"""\n{module.description}\n"""\n\n'
            
            # Add function stubs if functions are defined
            for func in module.functions:
                args_str = ", ".join([f"{arg.name}: {arg.type_hint}" + 
                                    (f" = {arg.default_value}" if arg.default_value else "")
                                    for arg in func.arguments])
                
                module_content += f'def {func.name}({args_str}) -> {func.return_type}:\n'
                module_content += f'    """{func.docstring}"""\n'
                module_content += '    pass\n\n'
            
            return self.filesystem_manager.write_file(module.file_path, module_content)
            
        except Exception:
            return False
    
    def _add_imports_to_module_with_fallback(self, module: Module, imports: List[str]) -> Tuple[bool, List[str]]:
        """
        Add imports to module file with individual error handling for each import.
        
        Args:
            module: Module to add imports to
            imports: List of import statements
            
        Returns:
            Tuple of (overall_success, list_of_errors)
        """
        errors = []
        successful_imports = []
        
        try:
            for import_statement in imports:
                try:
                    # Validate import syntax before adding
                    if not self._validate_import_syntax(import_statement):
                        error_msg = f"Invalid import syntax: {import_statement}"
                        errors.append(error_msg)
                        self.logger.warning(error_msg)
                        continue
                    
                    # Add individual import (this would need to be implemented)
                    if self._add_single_import_to_module(module, import_statement):
                        successful_imports.append(import_statement)
                        self.logger.debug(f"Added import to module '{module.name}': {import_statement}")
                    else:
                        error_msg = f"Failed to add import to module '{module.name}': {import_statement}"
                        errors.append(error_msg)
                        self.logger.warning(error_msg)
                        
                except Exception as e:
                    error_msg = f"Error adding import '{import_statement}' to module '{module.name}': {e}"
                    errors.append(error_msg)
                    self.logger.warning(error_msg)
            
            # Consider success if at least some imports were added
            overall_success = len(successful_imports) > 0 or len(imports) == 0
            
            if successful_imports:
                self.logger.info(f"Added {len(successful_imports)}/{len(imports)} imports to module '{module.name}'")
            
            return overall_success, errors
            
        except Exception as e:
            error_msg = f"Critical error adding imports to module '{module.name}': {e}"
            errors.append(error_msg)
            self.logger.error(error_msg)
            return False, errors
    
    def _add_single_import_to_module(self, module: Module, import_statement: str) -> bool:
        """
        Add a single import statement to a module file.
        
        Args:
            module: Module to add import to
            import_statement: Import statement to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.filesystem_manager:
                return False
            
            # Read current content
            current_content = self.filesystem_manager.read_file(module.file_path)
            if current_content is None:
                return False
            
            # Check if import already exists
            if import_statement.strip() in current_content:
                return True  # Already exists, consider it successful
            
            # Add import at the top of the file (after docstring if present)
            lines = current_content.split('\n')
            insert_index = 0
            
            # Skip docstring if present
            if lines and lines[0].strip().startswith('"""'):
                for i, line in enumerate(lines):
                    if i > 0 and '"""' in line:
                        insert_index = i + 1
                        break
            
            # Insert the import
            lines.insert(insert_index, import_statement)
            new_content = '\n'.join(lines)
            
            return self.filesystem_manager.write_file(module.file_path, new_content)
            
        except Exception as e:
            self.logger.error(f"Error adding single import to module '{module.name}': {e}")
            return False
    
    def _is_partial_integration_acceptable(self, module: Module, connection_result: 'ModuleConnectionResult') -> bool:
        """
        Determine if a module with connection errors can still be considered integrated.
        
        Args:
            module: Module that was being integrated
            connection_result: Result of the connection attempt
            
        Returns:
            True if partial integration is acceptable, False otherwise
        """
        try:
            # Check if the module file exists (minimum requirement)
            if self.filesystem_manager and self.filesystem_manager.file_exists(module.file_path):
                # If file exists, consider it partially integrated even with import errors
                self.logger.debug(f"Module '{module.name}' file exists, accepting partial integration")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking partial integration for module '{module.name}': {e}")
            return False
    
    def _verify_module_dependencies_with_fallback(self, module: Module, all_modules: List[Module]) -> List[str]:
        """
        Verify module dependencies with graceful error handling.
        
        Args:
            module: Module to verify dependencies for
            all_modules: List of all available modules
            
        Returns:
            List of warning messages (not fatal errors)
        """
        warnings = []
        
        try:
            for dep_name in module.dependencies:
                try:
                    # Find dependency module
                    dep_module = next((m for m in all_modules if m.name == dep_name), None)
                    if not dep_module:
                        warning_msg = f"Dependency '{dep_name}' not found for module '{module.name}'"
                        warnings.append(warning_msg)
                        self.logger.warning(warning_msg)
                        continue
                    
                    # Check if dependency file exists
                    if self.filesystem_manager:
                        if not self.filesystem_manager.file_exists(dep_module.file_path):
                            warning_msg = f"Dependency file does not exist: {dep_module.file_path}"
                            warnings.append(warning_msg)
                            self.logger.warning(warning_msg)
                        else:
                            self.logger.debug(f"Dependency '{dep_name}' verified for module '{module.name}'")
                    
                except Exception as e:
                    warning_msg = f"Error verifying dependency '{dep_name}' for module '{module.name}': {e}"
                    warnings.append(warning_msg)
                    self.logger.warning(warning_msg)
            
            return warnings
            
        except Exception as e:
            warning_msg = f"Critical error verifying dependencies for module '{module.name}': {e}"
            warnings.append(warning_msg)
            self.logger.error(warning_msg)
            return warnings
    
    def _verify_module_dependencies(self, module: Module, all_modules: List[Module]) -> List[str]:
        """Verify that module dependencies are accessible (legacy method)."""
        warnings = self._verify_module_dependencies_with_fallback(module, all_modules)
        # Convert warnings to errors for backward compatibility
        return warnings
    
    def _ensure_module_initialization(self, module: Module) -> bool:
        """Ensure module has proper initialization."""
        if not self.filesystem_manager:
            return False
        
        try:
            content = self.filesystem_manager.read_file(module.file_path)
            if content is None:
                return False
            
            # Check if module has basic structure
            if not content.strip():
                # Add basic module structure
                basic_content = f'"""\n{module.description}\n"""\n\n'
                return self.filesystem_manager.write_file(module.file_path, basic_content)
            
            return True
            
        except Exception:
            return False
    
    def _build_module_cache(self, modules: List[Module]) -> None:
        """Build cache of module information for import generation."""
        self._module_cache.clear()
        
        for module in modules:
            self._module_cache[module.name] = {
                'file_path': module.file_path,
                'dependencies': set(module.dependencies),
                'functions': [func.name for func in module.functions],
                'relative_path': self._get_relative_import_path(module.file_path)
            }
    
    def _generate_module_imports(self, module: Module, all_modules: List[Module]) -> List[str]:
        """Generate import statements for a single module with comprehensive error handling."""
        imports = []
        failed_imports = []
        
        try:
            # Use PackageManager to generate consistent imports if available
            if self.package_manager:
                try:
                    package_imports = self.package_manager.generate_imports_for_module(module)
                    imports.extend(package_imports)
                    self.logger.debug(f"Generated {len(package_imports)} package imports for module '{module.name}'")
                except Exception as e:
                    self.logger.warning(f"Package manager failed for module '{module.name}': {e}")
                    # Fall back to original logic if package manager fails
            
            # Get dependencies for this module
            dependencies = module.dependencies
            
            if dependencies:
                self.logger.debug(f"Processing {len(dependencies)} dependencies for module '{module.name}'")
                
                # Generate imports for each dependency with individual error handling
                for dep_name in dependencies:
                    try:
                        # Find the dependency module
                        dep_module = next((m for m in all_modules if m.name == dep_name), None)
                        if not dep_module:
                            self.logger.warning(f"Dependency module '{dep_name}' not found for module '{module.name}'")
                            # Add fallback import for missing dependency
                            fallback_import = self._generate_fallback_import(dep_name)
                            if fallback_import:
                                imports.append(fallback_import)
                                self.logger.info(f"Added fallback import for missing dependency '{dep_name}' in module '{module.name}'")
                            continue
                        
                        # Generate import statement with comprehensive error handling
                        import_statement = self._generate_import_statement_with_fallback(module, dep_module)
                        if import_statement:
                            imports.append(import_statement)
                            self.logger.debug(f"Generated import for dependency '{dep_name}' in module '{module.name}'")
                            
                            # Register package usage if package manager is available
                            if self.package_manager:
                                try:
                                    # Extract package name from import statement
                                    package_name = self._extract_package_name_from_import(import_statement)
                                    if package_name:
                                        alias = self.package_manager.get_standard_import_alias(package_name)
                                        self.package_manager.register_package_usage(package_name, alias, module.name)
                                except Exception as e:
                                    self.logger.debug(f"Package registration failed for '{dep_name}': {e}")
                                    # Continue if package registration fails
                        else:
                            failed_imports.append(dep_name)
                            self.logger.error(f"Failed to generate import for dependency '{dep_name}' in module '{module.name}'")
                            
                    except Exception as e:
                        self.logger.error(f"Error processing dependency '{dep_name}' for module '{module.name}': {e}")
                        failed_imports.append(dep_name)
                        
                        # Attempt to create a basic fallback import
                        try:
                            fallback_import = self._generate_fallback_import(dep_name)
                            if fallback_import:
                                imports.append(fallback_import)
                                self.logger.info(f"Added fallback import for failed dependency '{dep_name}' in module '{module.name}'")
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback import generation also failed for '{dep_name}': {fallback_error}")
            
            # Log summary of import generation
            if failed_imports:
                self.logger.warning(f"Module '{module.name}': {len(failed_imports)} imports failed, {len(imports)} imports generated")
            else:
                self.logger.info(f"Module '{module.name}': Successfully generated {len(imports)} imports")
            
            # Sort imports for consistency
            imports.sort()
            
            return imports
            
        except Exception as e:
            self.logger.error(f"Critical error in import generation for module '{module.name}': {e}")
            # Return whatever imports we managed to generate
            return sorted(imports) if imports else []
    
    def _generate_import_statement_with_fallback(self, from_module: Module, to_module: Module) -> Optional[str]:
        """
        Generate import statement with comprehensive fallback mechanisms.
        
        This method implements graceful degradation when import generation fails:
        1. Try relative imports first (if appropriate)
        2. Fall back to absolute imports
        3. Fall back to simple module name imports
        4. Log all failures and attempts
        
        Args:
            from_module: Source module
            to_module: Target module
            
        Returns:
            Import statement or None if all methods fail
        """
        try:
            # Get project root to respect project boundaries
            project_root = self._get_project_root(from_module.file_path)
            
            # Validate that target module exists before generating imports
            if not self._validate_target_module_exists(to_module):
                self.logger.warning(f"Target module not found: {to_module.file_path}")
                # Attempt to fix common problems automatically
                fixed_import = self._attempt_automatic_import_fix(from_module, to_module, project_root)
                if fixed_import:
                    self.logger.info(f"Automatically fixed import for missing target: {to_module.name}")
                    return fixed_import
                # Continue with fallback if automatic fix fails
            
            # Determine whether to use relative or absolute imports
            if self._should_use_relative_import(from_module, to_module, project_root):
                # Try relative import first
                try:
                    relative_import = self._calculate_relative_import_path(
                        from_module.file_path, 
                        to_module.file_path, 
                        project_root
                    )
                    
                    # Validate the generated relative import
                    if relative_import and self._validate_import_path(relative_import, from_module, project_root):
                        self.logger.debug(f"Generated relative import: {relative_import}")
                        return relative_import
                    else:
                        self.logger.debug(f"Relative import validation failed for {to_module.name}")
                        
                except Exception as e:
                    self.logger.debug(f"Relative import calculation failed for {to_module.name}: {e}")
                
                # Fall back to absolute import
                try:
                    absolute_import = self._generate_absolute_import(to_module, project_root)
                    if absolute_import and self._validate_import_path(absolute_import, from_module, project_root):
                        self.logger.debug(f"Fell back to absolute import: {absolute_import}")
                        return absolute_import
                    else:
                        self.logger.debug(f"Absolute import validation failed for {to_module.name}")
                        
                except Exception as e:
                    self.logger.debug(f"Absolute import generation failed for {to_module.name}: {e}")
            else:
                # Try absolute import first
                try:
                    absolute_import = self._generate_absolute_import(to_module, project_root)
                    if absolute_import and self._validate_import_path(absolute_import, from_module, project_root):
                        self.logger.debug(f"Generated absolute import: {absolute_import}")
                        return absolute_import
                    else:
                        self.logger.debug(f"Absolute import validation failed for {to_module.name}")
                        
                except Exception as e:
                    self.logger.debug(f"Absolute import generation failed for {to_module.name}: {e}")
            
            # Ultimate fallback - simple module name import
            fallback_import = f"from {to_module.name} import *"
            self.logger.warning(f"Using ultimate fallback import for {to_module.name}: {fallback_import}")
            return fallback_import
                    
        except Exception as e:
            self.logger.error(f"Critical error in import generation for {to_module.name}: {e}")
            # Return None to indicate complete failure
            return None
    
    def _generate_import_statement(self, from_module: Module, to_module: Module) -> str:
        """Generate import statement from one module to another (legacy method)."""
        result = self._generate_import_statement_with_fallback(from_module, to_module)
        if result is None:
            # Ultimate fallback with error comment
            return f"# ERROR: Import generation failed\nfrom {to_module.name} import *"
        return result
    
    def _generate_fallback_import(self, module_name: str) -> Optional[str]:
        """
        Generate a basic fallback import for a missing or failed dependency.
        
        Args:
            module_name: Name of the module to import
            
        Returns:
            Basic import statement or None if cannot generate
        """
        try:
            # Clean the module name
            clean_name = module_name.strip()
            if not clean_name:
                return None
            
            # Generate simple import statement (single line for better syntax validation)
            fallback = f"# FALLBACK: Module '{clean_name}' not found\nfrom {clean_name} import *  # May fail at runtime"
            self.logger.debug(f"Generated fallback import for '{clean_name}'")
            return fallback
            
        except Exception as e:
            self.logger.error(f"Failed to generate fallback import for '{module_name}': {e}")
            return None
    
    def _attempt_automatic_import_fix(self, from_module: Module, to_module: Module, project_root: str) -> Optional[str]:
        """
        Attempt to automatically fix common import problems.
        
        This method tries to fix common issues like:
        - Missing file extensions
        - Incorrect path separators
        - Case sensitivity issues
        
        Args:
            from_module: Source module
            to_module: Target module
            project_root: Project root directory
            
        Returns:
            Fixed import statement or None if cannot fix
        """
        try:
            # Try to find the target module with common variations
            target_variations = [
                to_module.file_path,
                to_module.file_path + '.py',
                to_module.file_path.replace('\\', '/'),
                to_module.file_path.replace('/', '\\'),
                to_module.file_path.lower(),
                to_module.file_path.upper(),
            ]
            
            for variation in target_variations:
                if self.filesystem_manager and self.filesystem_manager.file_exists(variation):
                    self.logger.info(f"Found target module at variation: {variation}")
                    # Create a temporary module with the corrected path
                    temp_module = Module(
                        name=to_module.name,
                        file_path=variation,
                        description=to_module.description,
                        functions=to_module.functions,
                        dependencies=to_module.dependencies
                    )
                    # Try to generate import with corrected path
                    return self._generate_import_statement_with_fallback(from_module, temp_module)
            
            # If file variations don't work, try different import strategies
            # Try absolute import with just module name
            simple_absolute = f"from {to_module.name} import *"
            if self._validate_import_syntax(simple_absolute):
                self.logger.info(f"Using simple absolute import as fix: {simple_absolute}")
                return simple_absolute
            
            return None
            
        except Exception as e:
            self.logger.error(f"Automatic import fix failed: {e}")
            return None
    
    def _calculate_relative_import_path(self, from_path: str, to_path: str, project_root: str) -> Optional[str]:
        """
        Calculate correct relative import path between two files.
        
        Args:
            from_path: Source file path
            to_path: Target file path  
            project_root: Project root directory path
            
        Returns:
            Relative import statement or None if not possible
        """
        try:
            # Convert to absolute paths for consistent handling
            from_path = str(Path(from_path).resolve())
            to_path = str(Path(to_path).resolve())
            project_root = str(Path(project_root).resolve())
            
            # Ensure both files are within the project boundaries
            if not (from_path.startswith(project_root) and to_path.startswith(project_root)):
                return None
            
            # Get the directory containing the source module
            from_dir = Path(from_path).parent
            to_file = Path(to_path)
            
            # Get relative paths from project root for both modules
            from_rel_to_project = from_dir.relative_to(project_root)
            to_rel_to_project = to_file.parent.relative_to(project_root)
            
            # Convert to parts for easier manipulation
            from_parts = from_rel_to_project.parts if from_rel_to_project != Path('.') else ()
            to_parts = to_rel_to_project.parts if to_rel_to_project != Path('.') else ()
            
            # Calculate the relative path between directories
            if from_parts == to_parts:
                # Same directory - simple relative import
                module_name = to_file.stem
                return f"from .{module_name} import *"
            
            # Find common ancestor
            common_length = 0
            for i in range(min(len(from_parts), len(to_parts))):
                if from_parts[i] == to_parts[i]:
                    common_length += 1
                else:
                    break
            
            # Calculate how many levels up we need to go from source
            levels_up = len(from_parts) - common_length
            
            # Ensure we don't go beyond project root
            if levels_up > len(from_parts):
                return None
            
            # Build the import path
            if levels_up == 0:
                # Target is in a subdirectory of source
                remaining_path = to_parts[common_length:]
                if remaining_path:
                    import_path = '.'.join(remaining_path + (to_file.stem,))
                    return f"from .{import_path} import *"
                else:
                    # This shouldn't happen if we're here, but handle it
                    return f"from .{to_file.stem} import *"
            else:
                # Need to go up one or more levels
                dots = '.' * (levels_up + 1)  # +1 for the initial relative import dot
                
                # Add the path down to the target
                remaining_path = to_parts[common_length:]
                if remaining_path:
                    import_path = '.'.join(remaining_path + (to_file.stem,))
                    return f"from {dots}{import_path} import *"
                else:
                    # Target is at the common ancestor level
                    return f"from {dots}{to_file.stem} import *"
                
        except Exception:
            return None
    
    def _validate_target_module_exists(self, to_module: Module) -> bool:
        """
        Validate that target module exists before generating imports.
        
        Args:
            to_module: Target module to validate
            
        Returns:
            True if target module exists and is accessible, False otherwise
        """
        try:
            # Check if file exists using filesystem manager
            if self.filesystem_manager:
                return self.filesystem_manager.file_exists(to_module.file_path)
            else:
                # Fallback to basic file existence check
                return Path(to_module.file_path).exists()
        except Exception:
            return False
    
    def _validate_import_path(self, import_statement: str, from_module: Module, project_root: str) -> bool:
        """
        Validate that an import statement can be resolved.
        
        This method verifies individual import statements by:
        1. Checking import syntax and structure
        2. Verifying that target modules exist at the specified paths
        3. Validating that the import can be resolved from the source module
        
        Args:
            import_statement: Import statement to validate
            from_module: Source module
            project_root: Project root directory
            
        Returns:
            True if import is valid, False otherwise
        """
        try:
            # Skip validation for comment lines or empty statements
            if not import_statement or import_statement.strip().startswith('#'):
                return False
            
            # Validate import syntax structure
            if not self._validate_import_syntax(import_statement):
                return False
            
            # Extract the module path from the import statement
            target_path = self._extract_target_path_from_import(import_statement, from_module, project_root)
            
            if not target_path:
                return False
            
            # Check if target file exists at the specified path
            target_exists = False
            if self.filesystem_manager:
                target_exists = self.filesystem_manager.file_exists(target_path)
            else:
                target_exists = Path(target_path).exists()
            
            if not target_exists:
                return False
            
            # Additional validation: check if the target file is a valid Python module
            if not self._validate_target_module_structure(target_path):
                return False
            
            # Validate that the import doesn't create circular dependencies
            if not self._validate_no_circular_import(import_statement, from_module, project_root):
                return False
                
            return True
                
        except Exception:
            return False
    
    def _validate_import_syntax(self, import_statement: str) -> bool:
        """
        Validate the syntax and structure of an import statement.
        
        Args:
            import_statement: Import statement to validate
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            # Clean the import statement
            statement = import_statement.strip()
            
            # Check for basic import statement patterns
            if not (statement.startswith('from ') or statement.startswith('import ')):
                return False
            
            # Try to parse the import statement using AST
            try:
                # Create a minimal module with just the import statement
                test_code = statement
                ast.parse(test_code)
                return True
            except SyntaxError:
                return False
            
        except Exception:
            return False
    
    def _validate_target_module_structure(self, target_path: str) -> bool:
        """
        Validate that the target file is a valid Python module.
        
        Args:
            target_path: Path to the target module file
            
        Returns:
            True if target is a valid Python module, False otherwise
        """
        try:
            # Check if file has .py extension
            if not target_path.endswith('.py'):
                return False
            
            # Check if file is readable and contains valid Python syntax
            content = None
            if self.filesystem_manager:
                content = self.filesystem_manager.read_file(target_path)
            else:
                try:
                    with open(target_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    return False
            
            if content is None:
                return False
            
            # Try to parse the content as Python code
            try:
                ast.parse(content)
                return True
            except SyntaxError:
                return False
                
        except Exception:
            return False
    
    def _validate_no_circular_import(self, import_statement: str, from_module: Module, project_root: str) -> bool:
        """
        Validate that the import doesn't create a circular dependency.
        
        Args:
            import_statement: Import statement to validate
            from_module: Source module
            project_root: Project root directory
            
        Returns:
            True if no circular dependency, False otherwise
        """
        try:
            # Extract the target module name from the import statement
            target_module_name = self._extract_module_name_from_import(import_statement)
            
            if not target_module_name:
                return True  # Can't determine target, assume no circular dependency
            
            # Check if the target module would import back to the source module
            # This is a simplified check - in practice, you'd need to traverse the entire dependency graph
            target_path = self._extract_target_path_from_import(import_statement, from_module, project_root)
            
            if not target_path:
                return True
            
            # Read the target module and check if it imports the source module
            try:
                if self.filesystem_manager:
                    target_content = self.filesystem_manager.read_file(target_path)
                else:
                    with open(target_path, 'r', encoding='utf-8') as f:
                        target_content = f.read()
                
                if target_content is None:
                    return True
                
                # Parse target module imports
                target_tree = ast.parse(target_content)
                target_imports = self._extract_imports_from_ast(target_tree)
                
                # Check if any import in target module references the source module
                source_module_name = Path(from_module.file_path).stem
                source_import_path = self._convert_file_path_to_import_path(from_module.file_path, project_root)
                
                for import_info in target_imports:
                    if import_info['type'] == 'from':
                        imported_module = import_info['module']
                        # Check for direct circular reference
                        if (imported_module == source_module_name or 
                            imported_module == source_import_path or
                            imported_module.endswith(f'.{source_module_name}')):
                            return False
                
                return True
                
            except Exception:
                # If we can't read the target, assume no circular dependency
                return True
                
        except Exception:
            return True  # Default to allowing the import if validation fails
    
    def _extract_module_name_from_import(self, import_statement: str) -> Optional[str]:
        """
        Extract the module name from an import statement.
        
        Args:
            import_statement: Import statement to parse
            
        Returns:
            Module name if found, None otherwise
        """
        try:
            statement = import_statement.strip()
            
            if statement.startswith('from '):
                # Extract module from "from module import ..."
                parts = statement.split()
                if len(parts) >= 2:
                    module_part = parts[1]
                    # Remove leading dots for relative imports
                    return module_part.lstrip('.')
            elif statement.startswith('import '):
                # Extract module from "import module"
                parts = statement.split()
                if len(parts) >= 2:
                    module_part = parts[1]
                    # Handle "import module as alias"
                    if 'as' in parts:
                        as_index = parts.index('as')
                        if as_index > 1:
                            module_part = parts[1]
                    return module_part.split('.')[0]  # Get root module name
            
            return None
            
        except Exception:
            return None
    
    def _extract_target_path_from_import(self, import_statement: str, from_module: Module, project_root: str) -> Optional[str]:
        """
        Extract the target file path from an import statement.
        
        Args:
            import_statement: Import statement to parse
            from_module: Source module
            project_root: Project root directory
            
        Returns:
            Target file path or None if cannot be determined
        """
        try:
            # Parse import statement
            if not import_statement.startswith('from '):
                return None
            
            parts = import_statement.split()
            if len(parts) < 2:
                return None
            
            module_part = parts[1]
            
            # Handle relative imports
            if module_part.startswith('.'):
                # Count leading dots to determine relative level
                dots = len(module_part) - len(module_part.lstrip('.'))
                relative_module = module_part.lstrip('.')
                
                # Get source module directory
                from_dir = Path(from_module.file_path).parent
                
                # Go up the required number of levels
                target_dir = from_dir
                for _ in range(dots - 1):  # -1 because first dot means current package
                    target_dir = target_dir.parent
                
                # Add the relative path
                if relative_module:
                    target_path = target_dir / relative_module.replace('.', os.sep)
                    # Add .py extension
                    return str(target_path) + '.py'
                else:
                    # This case shouldn't happen with our import format, but handle it
                    return str(target_dir) + '.py'
            
            else:
                # Handle absolute imports
                # Convert import path to file path
                relative_path = module_part.replace('.', os.sep) + '.py'
                return str(Path(project_root) / relative_path)
                
        except Exception:
            return None

    def _generate_absolute_import(self, to_module: Module, project_root: str) -> str:
        """
        Generate absolute import statement for a module.
        
        Args:
            to_module: Target module to import
            project_root: Project root directory
            
        Returns:
            Absolute import statement
        """
        try:
            # Convert module file path to import path
            import_path = self._convert_file_path_to_import_path(to_module.file_path, project_root)
            
            if import_path and import_path != to_module.name:
                return f"from {import_path} import *"
            else:
                # Fallback to module name
                return f"from {to_module.name} import *"
                
        except Exception:
            # Ultimate fallback
            return f"from {to_module.name} import *"
    
    def _should_use_relative_import(self, from_module: Module, to_module: Module, project_root: str) -> bool:
        """
        Determine whether to use relative or absolute imports.
        
        Args:
            from_module: Source module
            to_module: Target module
            project_root: Project root directory
            
        Returns:
            True if relative import should be used, False for absolute
        """
        try:
            # Convert to absolute paths for consistent handling
            from_path = Path(from_module.file_path).resolve()
            to_path = Path(to_module.file_path).resolve()
            project_root_path = Path(project_root).resolve()
            
            # Ensure both modules are within the project
            if not (str(from_path).startswith(str(project_root_path)) and 
                    str(to_path).startswith(str(project_root_path))):
                return False
            
            # Get relative paths from project root
            from_rel = from_path.parent.relative_to(project_root_path)
            to_rel = to_path.parent.relative_to(project_root_path)
            
            # Convert to parts for easier comparison
            from_parts = from_rel.parts if from_rel != Path('.') else ()
            to_parts = to_rel.parts if to_rel != Path('.') else ()
            
            # Always use relative imports for modules in the same directory
            if from_parts == to_parts:
                return True
            
            # Use relative imports if target is in a direct subdirectory
            if len(to_parts) == len(from_parts) + 1 and to_parts[:len(from_parts)] == from_parts:
                return True
            
            # Use relative imports if source is in a direct subdirectory of target
            if len(from_parts) == len(to_parts) + 1 and from_parts[:len(to_parts)] == to_parts:
                return True
            
            # Find common ancestor depth
            common_depth = 0
            for i in range(min(len(from_parts), len(to_parts))):
                if from_parts[i] == to_parts[i]:
                    common_depth += 1
                else:
                    break
            
            # Use relative imports if modules share a common parent and are within reasonable distance
            # This prevents overly complex relative imports like ....module
            max_levels_up = 2  # Don't go more than 2 levels up with relative imports
            levels_up_needed = len(from_parts) - common_depth
            
            if common_depth > 0 and levels_up_needed <= max_levels_up:
                # Also check that the total path complexity isn't too high
                total_complexity = levels_up_needed + (len(to_parts) - common_depth)
                if total_complexity <= 3:  # Keep relative imports simple
                    return True
            
            # For all other cases, use absolute imports for clarity
            return False
            
        except Exception:
            # Default to absolute imports on error for safety
            return False
    
    def _get_relative_import_path(self, file_path: str) -> str:
        """Get relative import path for a module file."""
        path = Path(file_path)
        
        # Remove .py extension and convert to import path
        import_path = str(path.with_suffix(''))
        import_path = import_path.replace(os.sep, '.')
        
        return import_path
    
    def _validate_import_dependencies(self, import_map: Dict[str, List[str]], modules: List[Module]) -> None:
        """
        Validate that generated imports don't create circular dependencies and are valid.
        
        Enhanced validation that:
        1. Uses the new _validate_import_path logic for individual import validation
        2. Provides specific error messages for invalid imports
        3. Enhanced circular dependency detection with detailed cycle information
        
        Args:
            import_map: Dictionary mapping module names to their import statements
            modules: List of all modules being integrated
            
        Raises:
            ImportGenerationError: If validation fails with detailed error information
        """
        validation_errors = []
        
        # Get project root for validation
        project_root = None
        if modules:
            project_root = self._get_project_root(modules[0].file_path)
        
        # Create module lookup for faster access
        module_lookup = {module.name: module for module in modules}
        
        # Phase 1: Validate individual import statements
        for module_name, imports in import_map.items():
            source_module = module_lookup.get(module_name)
            if not source_module:
                validation_errors.append(f"Source module '{module_name}' not found in module list")
                continue
            
            for import_stmt in imports:
                # Skip comment lines
                if not import_stmt or import_stmt.strip().startswith('#'):
                    continue
                
                # Use the enhanced _validate_import_path method
                if project_root and not self._validate_import_path(import_stmt, source_module, project_root):
                    # Provide specific error details
                    target_module = self._extract_module_from_import(import_stmt)
                    if target_module:
                        validation_errors.append(
                            f"Invalid import in module '{module_name}': '{import_stmt}' - "
                            f"target module '{target_module}' cannot be resolved"
                        )
                    else:
                        validation_errors.append(
                            f"Invalid import syntax in module '{module_name}': '{import_stmt}'"
                        )
        
        # Phase 2: Enhanced circular dependency detection
        import_graph = {}
        module_to_imports = {}
        
        # Build detailed import dependency graph
        for module_name, imports in import_map.items():
            import_graph[module_name] = []
            module_to_imports[module_name] = []
            
            for import_stmt in imports:
                # Skip comment lines
                if not import_stmt or import_stmt.strip().startswith('#'):
                    continue
                
                # Extract imported module name from import statement
                imported_module = self._extract_module_from_import(import_stmt)
                if imported_module and imported_module in import_map:
                    import_graph[module_name].append(imported_module)
                    module_to_imports[module_name].append((imported_module, import_stmt))
        
        # Check for cycles using enhanced DFS with path tracking
        cycles = self._detect_import_cycles_with_paths(import_graph)
        if cycles:
            for cycle in cycles:
                cycle_description = " -> ".join(cycle + [cycle[0]])  # Complete the cycle
                validation_errors.append(f"Circular import dependency detected: {cycle_description}")
                
                # Add specific import statements involved in the cycle
                for i in range(len(cycle)):
                    current_module = cycle[i]
                    next_module = cycle[(i + 1) % len(cycle)]
                    
                    # Find the specific import statement causing this dependency
                    if current_module in module_to_imports:
                        for imported_module, import_stmt in module_to_imports[current_module]:
                            if imported_module == next_module:
                                validation_errors.append(
                                    f"  - Module '{current_module}' imports '{next_module}' via: {import_stmt}"
                                )
                                break
        
        # Phase 3: Additional validation checks
        # Check for missing dependencies
        for module_name, imports in import_map.items():
            for import_stmt in imports:
                if not import_stmt or import_stmt.strip().startswith('#'):
                    continue
                
                imported_module = self._extract_module_from_import(import_stmt)
                if imported_module:
                    # Check if imported module exists in our module set or is a standard library
                    if (imported_module not in import_map and 
                        not self._is_standard_library_module(imported_module) and
                        not self._is_external_package(imported_module)):
                        validation_errors.append(
                            f"Module '{module_name}' imports missing module '{imported_module}' via: {import_stmt}"
                        )
        
        # Raise error with all validation issues if any were found
        if validation_errors:
            error_message = "Import validation failed with the following issues:\n" + "\n".join(validation_errors)
            raise ImportGenerationError(error_message)
    
    def _extract_module_from_import(self, import_statement: str) -> Optional[str]:
        """
        Extract module name from import statement.
        
        Enhanced version that handles more import formats and edge cases.
        
        Args:
            import_statement: Import statement to parse
            
        Returns:
            Module name if successfully extracted, None otherwise
        """
        try:
            # Clean the import statement
            statement = import_statement.strip()
            
            # Skip comment lines
            if not statement or statement.startswith('#'):
                return None
            
            # Handle "from module import ..." format
            if statement.startswith('from '):
                parts = statement.split()
                if len(parts) >= 2:
                    module_part = parts[1]
                    
                    # Handle relative imports by removing leading dots
                    if module_part.startswith('.'):
                        # For relative imports, we still want to track the module name
                        # but without the dots for dependency graph purposes
                        module_part = module_part.lstrip('.')
                        
                        # If after removing dots we have an empty string,
                        # this is a relative import from current package
                        if not module_part:
                            return None
                    
                    return module_part
            
            # Handle "import module" format
            elif statement.startswith('import '):
                parts = statement.split()
                if len(parts) >= 2:
                    module_part = parts[1]
                    
                    # Handle "import module as alias"
                    if 'as' in parts:
                        as_index = parts.index('as')
                        if as_index > 1:
                            module_part = parts[1]
                    
                    # For multi-level imports like "import package.module",
                    # we want the root package for dependency tracking
                    return module_part.split('.')[0]
            
            return None
            
        except Exception:
            return None
    
    def _detect_import_cycles_with_paths(self, import_graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Detect circular import dependencies and return the actual cycle paths.
        
        Enhanced version that returns detailed information about cycles found.
        
        Args:
            import_graph: Dictionary mapping module names to their dependencies
            
        Returns:
            List of cycles, where each cycle is a list of module names forming the cycle
        """
        visited = set()
        rec_stack = set()
        current_path = []
        cycles = []
        
        def dfs(node: str) -> None:
            if node in rec_stack:
                # Cycle detected - extract the cycle from current path
                cycle_start_index = current_path.index(node)
                cycle = current_path[cycle_start_index:]
                cycles.append(cycle.copy())
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            current_path.append(node)
            
            for neighbor in import_graph.get(node, []):
                dfs(neighbor)
            
            current_path.pop()
            rec_stack.remove(node)
        
        for node in import_graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def _has_import_cycles(self, import_graph: Dict[str, List[str]]) -> bool:
        """
        Check if import graph has cycles using DFS.
        
        Kept for backward compatibility, but now uses the enhanced detection method.
        """
        cycles = self._detect_import_cycles_with_paths(import_graph)
        return len(cycles) > 0
    
    def _is_standard_library_module(self, module_name: str) -> bool:
        """
        Check if a module is part of the Python standard library.
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            True if module is in standard library, False otherwise
        """
        # Common standard library modules that might be imported
        standard_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'math', 'random', 'collections',
            'itertools', 'functools', 'operator', 're', 'string', 'io', 'pathlib',
            'typing', 'dataclasses', 'enum', 'abc', 'contextlib', 'copy', 'pickle',
            'sqlite3', 'csv', 'xml', 'html', 'urllib', 'http', 'email', 'logging',
            'unittest', 'pytest', 'argparse', 'configparser', 'tempfile', 'shutil',
            'glob', 'fnmatch', 'linecache', 'textwrap', 'unicodedata', 'codecs',
            'base64', 'binascii', 'struct', 'array', 'weakref', 'gc', 'inspect',
            'ast', 'dis', 'importlib', 'pkgutil', 'modulefinder', 'runpy', 'site',
            'sysconfig', 'platform', 'ctypes', 'threading', 'multiprocessing',
            'concurrent', 'subprocess', 'socket', 'ssl', 'select', 'signal',
            'mmap', 'resource', 'getpass', 'pwd', 'grp', 'termios', 'tty', 'pty',
            'fcntl', 'pipes', 'posix', 'errno', 'stat', 'statvfs', 'filecmp',
            'tarfile', 'zipfile', 'gzip', 'bz2', 'lzma', 'zlib', 'hashlib',
            'hmac', 'secrets', 'uuid', 'calendar', 'locale', 'gettext', 'decimal',
            'fractions', 'statistics', 'cmath', 'numbers'
        }
        
        # Check if the root module name is in standard library
        root_module = module_name.split('.')[0]
        return root_module in standard_modules
    
    def _is_external_package(self, module_name: str) -> bool:
        """
        Check if a module is an external package (not part of the current project).
        
        This is a heuristic check for common external packages.
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            True if module appears to be an external package, False otherwise
        """
        # Common external packages that might be imported
        external_packages = {
            'numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy', 'sklearn',
            'tensorflow', 'torch', 'keras', 'requests', 'flask', 'django',
            'fastapi', 'sqlalchemy', 'pymongo', 'redis', 'celery', 'pytest',
            'click', 'pydantic', 'marshmallow', 'jinja2', 'werkzeug', 'gunicorn',
            'uvicorn', 'aiohttp', 'httpx', 'beautifulsoup4', 'lxml', 'pillow',
            'opencv', 'plotly', 'bokeh', 'streamlit', 'dash', 'jupyter',
            'ipython', 'notebook', 'black', 'flake8', 'mypy', 'isort',
            'pre-commit', 'tox', 'coverage', 'sphinx', 'mkdocs', 'poetry',
            'pipenv', 'virtualenv', 'conda', 'pip', 'setuptools', 'wheel',
            'twine', 'build', 'flit', 'hatch'
        }
        
        # Check if the root module name is a known external package
        root_module = module_name.split('.')[0]
        return root_module in external_packages
    
    def _add_imports_to_module(self, module: Module, imports: List[str]) -> bool:
        """Add import statements to a module file."""
        if not self.filesystem_manager:
            return False
        
        try:
            # Read existing module content
            existing_content = self.filesystem_manager.read_file(module.file_path)
            if existing_content is None:
                # File doesn't exist, create basic module structure
                existing_content = f'"""\n{module.description}\n"""\n\n'
            
            # Parse existing content to find where to insert imports
            new_content = self._insert_imports_into_content(existing_content, imports)
            
            # Write updated content back to file
            return self.filesystem_manager.write_file(module.file_path, new_content)
            
        except Exception:
            return False
    
    def _insert_imports_into_content(self, content: str, imports: List[str]) -> str:
        """Insert import statements into module content at the appropriate location."""
        if not imports:
            return content
        
        lines = content.split('\n')
        
        # Find the best position to insert imports
        insert_position = self._find_import_insertion_position(lines)
        
        # Create import section
        import_section = []
        if insert_position > 0 and lines[insert_position - 1].strip():
            import_section.append('')  # Add blank line before imports
        
        import_section.extend(imports)
        import_section.append('')  # Add blank line after imports
        
        # Insert imports at the determined position
        new_lines = lines[:insert_position] + import_section + lines[insert_position:]
        
        return '\n'.join(new_lines)
    
    def _find_import_insertion_position(self, lines: List[str]) -> int:
        """Find the best position to insert import statements."""
        # Look for existing imports or module docstring
        in_docstring = False
        docstring_end = 0
        last_import = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track docstring
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                elif stripped.endswith('"""') or stripped.endswith("'''"):
                    in_docstring = False
                    docstring_end = i + 1
            elif in_docstring and (stripped.endswith('"""') or stripped.endswith("'''")):
                in_docstring = False
                docstring_end = i + 1
            
            # Track imports
            if not in_docstring and (stripped.startswith('import ') or stripped.startswith('from ')):
                last_import = i + 1
        
        # Insert after existing imports, or after docstring, or at the beginning
        return max(last_import, docstring_end)
    
    def _verify_module_file_exists(self, module: Module) -> bool:
        """Verify that a module file exists and is readable."""
        if not self.filesystem_manager:
            return False
        
        return self.filesystem_manager.file_exists(module.file_path)
    
    def _verify_module_imports(self, module: Module, all_modules: List[Module]) -> List[str]:
        """Verify imports in a module file and return any issues."""
        issues = []
        
        if not self.filesystem_manager:
            issues.append(f"Cannot verify imports for '{module.name}': no file system manager")
            return issues
        
        try:
            # Read module content
            content = self.filesystem_manager.read_file(module.file_path)
            if content is None:
                issues.append(f"Cannot read module file: {module.file_path}")
                return issues
            
            # Parse the module to extract imports
            try:
                tree = ast.parse(content)
                imports = self._extract_imports_from_ast(tree)
                
                # Verify each import can be resolved
                for import_info in imports:
                    if not self._can_resolve_import(import_info, module, all_modules):
                        issues.append(f"Cannot resolve import in '{module.name}': {import_info['statement']}")
                        
            except SyntaxError as e:
                issues.append(f"Syntax error in module '{module.name}': {e}")
            except Exception as e:
                issues.append(f"Failed to parse module '{module.name}': {e}")
        
        except Exception as e:
            issues.append(f"Failed to verify imports for '{module.name}': {e}")
        
        return issues
    
    def _extract_imports_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import information from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'statement': f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                    })
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ''
                level = node.level
                
                for alias in node.names:
                    imports.append({
                        'type': 'from',
                        'module': module_name,
                        'name': alias.name,
                        'alias': alias.asname,
                        'level': level,
                        'statement': f"from {'.' * level}{module_name} import {alias.name}" + 
                                   (f" as {alias.asname}" if alias.asname else "")
                    })
        
        return imports
    
    def _can_resolve_import(self, import_info: Dict[str, Any], current_module: Module, all_modules: List[Module]) -> bool:
        """Check if an import can be resolved."""
        try:
            if import_info['type'] == 'import':
                # Direct import - check if module exists
                module_name = import_info['module']
                
                # Check if it's a project module
                if any(m.name == module_name for m in all_modules):
                    return True
                
                # Check if it's a standard library or third-party module
                return self._is_standard_or_third_party_import(module_name)
            
            elif import_info['type'] == 'from':
                # From import - check if source module exists
                module_name = import_info['module']
                level = import_info.get('level', 0)
                
                if level > 0:
                    # Relative import - resolve relative to current module
                    resolved_module = self._resolve_relative_import(module_name, level, current_module, all_modules)
                    return resolved_module is not None
                else:
                    # Absolute import - check project modules first
                    if any(m.name == module_name for m in all_modules):
                        return True
                    
                    # Check if it's a standard library or third-party module
                    return self._is_standard_or_third_party_import(module_name)
            
            return True  # Default to True for unknown import types
            
        except Exception:
            return False
    
    def _resolve_relative_import(self, module_name: str, level: int, current_module: Module, all_modules: List[Module]) -> Optional[Module]:
        """Resolve a relative import to find the target module."""
        try:
            # Get current module's directory path
            current_path = Path(current_module.file_path).parent
            
            # Go up 'level' directories
            target_path = current_path
            for _ in range(level - 1):
                target_path = target_path.parent
            
            # Add module name to path
            if module_name:
                target_path = target_path / f"{module_name}.py"
            
            # Find matching module
            for module in all_modules:
                if Path(module.file_path).resolve() == target_path.resolve():
                    return module
            
            return None
            
        except Exception:
            return None
    
    def _is_standard_or_third_party_import(self, module_name: str) -> bool:
        """Check if a module is from standard library or third-party packages."""
        try:
            # Common standard library modules
            standard_library_modules = {
                'typing', 'os', 'sys', 'json', 'datetime', 'time', 'math', 'random',
                'collections', 'itertools', 'functools', 're', 'pathlib', 'urllib',
                'http', 'email', 'html', 'xml', 'csv', 'sqlite3', 'logging',
                'unittest', 'threading', 'multiprocessing', 'subprocess', 'io',
                'tempfile', 'shutil', 'glob', 'pickle', 'base64', 'hashlib',
                'hmac', 'secrets', 'uuid', 'decimal', 'fractions', 'statistics',
                'enum', 'dataclasses', 'contextlib', 'warnings', 'traceback',
                'inspect', 'ast', 'dis', 'importlib', 'pkgutil', 'zipfile',
                'tarfile', 'gzip', 'bz2', 'lzma', 'zlib', 'socket', 'ssl',
                'select', 'asyncio', 'concurrent', 'queue', 'sched', 'copy',
                'pprint', 'reprlib', 'weakref', 'gc', 'types', 'operator',
                'keyword', 'builtins', '__future__'
            }
            
            # Check if it's a standard library module
            if module_name in standard_library_modules:
                return True
            
            # Check if it's a common third-party package
            common_third_party = {
                'requests', 'numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy',
                'sklearn', 'tensorflow', 'torch', 'keras', 'flask', 'django',
                'fastapi', 'sqlalchemy', 'psycopg2', 'pymongo', 'redis',
                'celery', 'pytest', 'click', 'pydantic', 'marshmallow',
                'jinja2', 'werkzeug', 'gunicorn', 'uvicorn', 'aiohttp',
                'httpx', 'beautifulsoup4', 'bs4', 'lxml', 'pillow', 'opencv',
                'plotly', 'bokeh', 'streamlit', 'dash', 'jupyter', 'ipython',
                'notebook', 'black', 'flake8', 'mypy', 'isort', 'pre-commit',
                'tox', 'coverage', 'sphinx', 'mkdocs', 'poetry', 'pipenv'
            }
            
            if module_name in common_third_party:
                return True
            
            # Try to import the module to check if it exists
            # This is a more comprehensive check but should be used carefully
            try:
                import importlib.util
                spec = importlib.util.find_spec(module_name)
                return spec is not None
            except (ImportError, ModuleNotFoundError, ValueError):
                # If we can't find the spec, assume it might be valid
                # This is to avoid false negatives for modules that might be installed
                # but not available in the current environment
                return True
            
        except Exception:
            # If anything goes wrong, assume the import is valid
            # This is a conservative approach to avoid blocking valid imports
            return True
    
    def _detect_circular_imports(self, modules: List[Module]) -> List[List[str]]:
        """Detect circular import dependencies."""
        # This is a simplified version - in practice, you'd need to parse actual import statements
        # For now, we'll use the module dependency graph as a proxy
        
        if not self.dependency_analyzer:
            return []
        
        try:
            return self.dependency_analyzer.detect_circular_dependencies(modules)
        except Exception:
            return []
    
    def _find_unused_imports(self, modules: List[Module]) -> Dict[str, List[str]]:
        """Find unused imports in modules."""
        unused_imports = {}
        
        # This is a simplified implementation
        # In practice, you'd need to parse the AST and check if imported names are used
        
        for module in modules:
            if not self.filesystem_manager:
                continue
            
            try:
                content = self.filesystem_manager.read_file(module.file_path)
                if content is None:
                    continue
                
                # Parse imports
                tree = ast.parse(content)
                imports = self._extract_imports_from_ast(tree)
                
                # Check usage (simplified - just check if import name appears in code)
                unused = []
                for import_info in imports:
                    if import_info['type'] == 'from' and import_info['name'] != '*':
                        name = import_info['alias'] or import_info['name']
                        if name not in content:
                            unused.append(import_info['statement'])
                
                if unused:
                    unused_imports[module.name] = unused
                    
            except Exception:
                continue
        
        return unused_imports
    
    def _generate_integration_tests(self, modules: List[Module]) -> TestGenerationResult:
        """
        Generate unit tests for integrated modules.
        
        Args:
            modules: List of modules to generate tests for
            
        Returns:
            TestGenerationResult with test generation status and details
        """
        if not self.test_generator:
            return TestGenerationResult(
                generated_tests=[],
                test_files_created=[],
                success=False,
                errors=["Test generator not available"]
            )
        
        try:
            all_test_cases = []
            test_files_created = []
            errors = []
            
            # Generate tests for each module
            for module in modules:
                try:
                    # Generate test cases for the module
                    test_cases = self.test_generator.generate_module_tests(module)
                    all_test_cases.extend(test_cases)
                    
                    # Create test file for the module
                    test_file_path = self._get_test_file_path(module)
                    if self._create_test_file(module, test_cases, test_file_path):
                        test_files_created.append(test_file_path)
                    else:
                        errors.append(f"Failed to create test file for module '{module.name}'")
                        
                except Exception as e:
                    errors.append(f"Failed to generate tests for module '{module.name}': {e}")
            
            # Execute generated tests if any were created
            execution_result = None
            if test_files_created and not errors:
                try:
                    execution_result = self.test_generator.execute_generated_tests(test_files_created)
                except Exception as e:
                    errors.append(f"Test execution failed: {e}")
            
            success = len(errors) == 0 and len(test_files_created) > 0
            
            return TestGenerationResult(
                generated_tests=all_test_cases,
                test_files_created=test_files_created,
                execution_result=execution_result,
                success=success,
                errors=errors
            )
            
        except Exception as e:
            return TestGenerationResult(
                generated_tests=[],
                test_files_created=[],
                success=False,
                errors=[f"Test generation process failed: {e}"]
            )
    
    def _get_test_file_path(self, module: Module) -> str:
        """
        Generate test file path for a module following naming convention.
        
        Args:
            module: Module to generate test file path for
            
        Returns:
            Path to the test file
        """
        module_path = Path(module.file_path)
        module_dir = module_path.parent
        module_name = module_path.stem
        
        # Create test file in the same directory as the module
        test_file_name = f"test_{module_name}.py"
        return str(module_dir / test_file_name)
    
    def _create_test_file(self, module: Module, test_cases: List, test_file_path: str) -> bool:
        """
        Create a test file with generated test cases.
        
        Args:
            module: Module being tested
            test_cases: List of test cases to include
            test_file_path: Path where test file should be created
            
        Returns:
            True if test file was created successfully, False otherwise
        """
        if not self.filesystem_manager:
            return False
        
        try:
            # Generate test file content
            test_content = self._generate_test_file_content(module, test_cases)
            
            # Write test file
            return self.filesystem_manager.write_file(test_file_path, test_content)
            
        except Exception:
            return False
    
    def _generate_test_file_content(self, module: Module, test_cases: List) -> str:
        """
        Generate content for a test file.
        
        Args:
            module: Module being tested
            test_cases: List of test cases
            
        Returns:
            Content for the test file
        """
        module_name = Path(module.file_path).stem
        
        content = f'''"""
Unit tests for {module.name} module.

This file contains automatically generated unit tests for the {module.name} module.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add module path to sys.path for imports
module_path = Path(__file__).parent
if str(module_path) not in sys.path:
    sys.path.insert(0, str(module_path))

from {module_name} import *


class Test{module.name.title().replace('_', '')}(unittest.TestCase):
    """Test cases for {module.name} module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def tearDown(self):
        """Clean up after each test method."""
        pass

'''
        
        # Add test methods for each function
        for func in module.functions:
            content += f'''
    def test_{func.name}(self):
        """Test {func.name} function."""
        # TODO: Implement test for {func.name}
        # This is a placeholder test that should be implemented
        self.assertTrue(True, "Placeholder test - implement actual test logic")
'''
        
        content += '''

if __name__ == '__main__':
    unittest.main()
'''
        
        return content
    
    def _extract_package_name_from_import(self, import_statement: str) -> Optional[str]:
        """
        Extract package name from an import statement.
        
        Args:
            import_statement: Import statement to parse
            
        Returns:
            Package name if found, None otherwise
        """
        try:
            # Handle different import formats
            if import_statement.startswith('from '):
                # "from package import ..." or "from .module import ..."
                parts = import_statement.split()
                if len(parts) >= 2:
                    module_part = parts[1]
                    # Skip relative imports (starting with .)
                    if not module_part.startswith('.'):
                        # Extract root package name
                        return module_part.split('.')[0]
            elif import_statement.startswith('import '):
                # "import package" or "import package as alias"
                parts = import_statement.split()
                if len(parts) >= 2:
                    package_part = parts[1]
                    # Extract root package name
                    return package_part.split('.')[0]
            
            return None
            
        except Exception:
            return None

    # Helper methods for project structure analysis
    
    def _get_project_root(self, module_path: str) -> str:
        """
        Determine the project root directory from a module path.
        
        Args:
            module_path: Path to any module file in the project
            
        Returns:
            Path to the project root directory
        """
        try:
            current_path = Path(module_path).resolve().parent
            
            # Look for common project root indicators
            project_indicators = [
                'setup.py', 'pyproject.toml', 'requirements.txt', 
                '.git', '.gitignore', 'README.md', 'README.rst',
                'Pipfile', 'poetry.lock', 'setup.cfg', 'tox.ini'
            ]
            
            # Traverse up the directory tree looking for project root indicators
            # Limit traversal to avoid going too far up (e.g., to user home directory)
            max_levels = 5  # Reduced to be more conservative
            level = 0
            original_path = current_path
            
            while current_path != current_path.parent and level < max_levels:
                # Check if any project indicators exist in current directory
                for indicator in project_indicators:
                    if (current_path / indicator).exists():
                        # Additional check: make sure we're not in a system directory
                        # by checking if the path is reasonably close to the original
                        if level <= 3:  # Only accept if within 3 levels
                            return str(current_path)
                
                # Check if this directory contains Python packages (has __init__.py)
                # and the parent doesn't - this might be the project root
                if (current_path / '__init__.py').exists():
                    parent = current_path.parent
                    if not (parent / '__init__.py').exists():
                        # Check if parent has project indicators
                        for indicator in project_indicators:
                            if (parent / indicator).exists() and level <= 2:
                                return str(parent)
                        # If no indicators in parent, current might be root
                        if level <= 2:
                            return str(current_path)
                
                current_path = current_path.parent
                level += 1
            
            # If no project root found, use the directory containing the module
            return str(Path(module_path).resolve().parent)
            
        except Exception:
            # Fallback to module's directory
            return str(Path(module_path).resolve().parent)
    
    def _convert_file_path_to_import_path(self, file_path: str, project_root: str) -> str:
        """
        Convert a file system path to a Python import path.
        
        Args:
            file_path: Absolute or relative file path to convert
            project_root: Project root directory path
            
        Returns:
            Python import path (dot-separated module path)
        """
        try:
            # Convert to absolute paths for consistent handling
            file_path = str(Path(file_path).resolve())
            project_root = str(Path(project_root).resolve())
            
            # Get relative path from project root
            rel_path = os.path.relpath(file_path, project_root)
            
            # Remove .py extension
            if rel_path.endswith('.py'):
                rel_path = rel_path[:-3]
            
            # Convert path separators to dots
            import_path = rel_path.replace(os.sep, '.')
            
            # Handle special cases
            if import_path.startswith('.'):
                import_path = import_path.lstrip('.')
            
            # Remove any double dots that might have been created
            import_path = re.sub(r'\.+', '.', import_path)
            
            return import_path
            
        except Exception:
            # Fallback: use just the filename without extension
            try:
                return Path(file_path).stem
            except Exception:
                # Ultimate fallback for completely invalid paths
                return ""
    
    def _analyze_project_structure(self, modules: List[Module]) -> Dict[str, Any]:
        """
        Analyze the project structure and map module relationships.
        
        Args:
            modules: List of modules to analyze
            
        Returns:
            Dictionary containing project structure information
        """
        try:
            if not modules:
                return {
                    'project_root': '',
                    'module_paths': {},
                    'package_hierarchy': {},
                    'directory_structure': {},
                    'import_relationships': {}
                }
            
            # Determine project root from the first module
            project_root = self._get_project_root(modules[0].file_path)
            
            # Build module path mapping
            module_paths = {}
            package_hierarchy = defaultdict(list)
            directory_structure = defaultdict(list)
            import_relationships = defaultdict(set)
            
            for module in modules:
                # Map module name to file path
                module_paths[module.name] = module.file_path
                
                # Convert to import path
                import_path = self._convert_file_path_to_import_path(module.file_path, project_root)
                
                # Build package hierarchy
                path_parts = import_path.split('.')
                if len(path_parts) > 1:
                    package_name = '.'.join(path_parts[:-1])
                    module_name = path_parts[-1]
                    package_hierarchy[package_name].append(module_name)
                else:
                    # Root level module
                    package_hierarchy[''].append(import_path)
                
                # Build directory structure
                dir_path = str(Path(module.file_path).parent)
                relative_dir = os.path.relpath(dir_path, project_root)
                directory_structure[relative_dir].append(module.name)
                
                # Map import relationships - ensure all modules are included
                for dep_name in module.dependencies:
                    import_relationships[module.name].add(dep_name)
                # Ensure module is in relationships even if it has no dependencies
                if module.name not in import_relationships:
                    import_relationships[module.name] = set()
            
            # Convert defaultdicts to regular dicts for JSON serialization
            package_hierarchy = dict(package_hierarchy)
            directory_structure = dict(directory_structure)
            import_relationships = {k: list(v) for k, v in import_relationships.items()}
            
            return {
                'project_root': project_root,
                'module_paths': module_paths,
                'package_hierarchy': package_hierarchy,
                'directory_structure': directory_structure,
                'import_relationships': import_relationships
            }
            
        except Exception as e:
            # Return minimal structure on error
            return {
                'project_root': str(Path(modules[0].file_path).parent) if modules else '',
                'module_paths': {m.name: m.file_path for m in modules},
                'package_hierarchy': {},
                'directory_structure': {},
                'import_relationships': {},
                'error': str(e)
            }