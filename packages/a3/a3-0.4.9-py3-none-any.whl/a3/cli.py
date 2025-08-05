from pathlib import Path
import json
import os
import re
import sys

from dataclasses import asdict
from typing import Optional
import argparse
import logging

from .clients.openrouter import OpenRouterClient
from .config import A3Config
from .core.api import A3, A3Error
from .core.migration import ProjectMigrator
from .core.models import DocumentationConfiguration
from .core.models import ProjectPhase
from .core.models import ValidationError
from .core.requirement_parser import RequirementParser
from .core.structured_document_generator import StructuredDocumentGenerator
from .engines.code_executor import CodeExecutor
from .engines.database_analyzer import DatabaseAnalyzer
from .engines.debug_analyzer import DebugAnalyzer
from .engines.planning import PlanningEngine
from .engines.project_analyzer import ProjectAnalyzer
from .managers.data_source_manager import DataSourceManager
from .managers.dependency import DependencyAnalyzer
from .managers.filesystem import FileSystemManager
from .managers.package_manager import PackageManager
from .managers.state import StateManager

#!/usr/bin/env python3
"""
Command Line Interface for AI Project Builder (A3).

This module provides CLI commands for project creation, analysis, and debugging.
"""




def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_api_key() -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv('A3_API_KEY') or os.getenv('OPENROUTER_API_KEY')


def resolve_project_path(path: str, workspace: Optional[str] = None, config: Optional[A3Config] = None) -> str:
    """Resolve project path with workspace support."""
    # Priority: explicit workspace > config workspace > no workspace
    effective_workspace = workspace or (config.default_workspace if config else None)
    
    if effective_workspace and not os.path.isabs(path):
        return str(Path(effective_workspace) / path)
    return path


def handle_error(error: Exception) -> None:
    """Handle and display errors in a user-friendly way."""
    if isinstance(error, A3Error):
        print(f"\n{error.get_user_message()}", file=sys.stderr)
    else:
        print(f"\nUnexpected error: {error}", file=sys.stderr)
        print("Please report this issue if it persists.", file=sys.stderr)
    sys.exit(1)


def create_project_command(args) -> None:
    """Handle the create project command."""
    try:
        # Resolve project path with workspace support
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        
        # Ensure target directory exists
        target_path = Path(project_path).resolve()
        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {target_path}")
        
        # Initialize A3 with resolved path
        a3 = A3(str(target_path))
        
        # Set API key (priority: CLI arg > config > environment)
        api_key = args.api_key or args.config.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required. Set A3_API_KEY environment variable, use --api-key option, or configure with 'a3 config set api_key YOUR_KEY'.")
            print("Get your API key from: https://openrouter.ai/")
            sys.exit(1)
        
        a3.set_api_key(api_key)
        
        # Set database connection if provided
        if hasattr(args, 'database') and args.database:
            print(f"Database connection: {args.database}")
            # Database connection will be handled by the enhanced A3 API
        
        print(f"Creating project in: {Path(project_path).resolve()}")
        print(f"Objective: {args.objective}")
        if hasattr(args, 'template') and args.template:
            print(f"Using template: {args.template}")
        if hasattr(args, 'generate_tests') and args.generate_tests:
            print("Test generation: Enabled")
        if hasattr(args, 'enforce_import_consistency') and args.enforce_import_consistency:
            print("Import consistency: Enforced")
        if hasattr(args, 'auto_generate_requirements') and args.auto_generate_requirements:
            print("Requirements generation: Enabled")
        print()
        
        # Analyze data sources if requested
        if hasattr(args, 'analyze_data_sources') and args.analyze_data_sources:
            print("Analyzing data sources in project directory...")
            try:
                project_analysis = a3.analyze_project(project_path, 
                                                    database_connection=getattr(args, 'database', None))
                print("✓ Data source analysis completed")
            except Exception as e:
                print(f"⚠ Data source analysis failed: {e}")
        
        # Execute the full pipeline
        if args.plan_only:
            print("Generating project plan...")
            plan = a3.plan(args.objective, project_path)
            print(f"✓ Plan generated with {len(plan.modules)} modules and {plan.estimated_functions} functions")
        else:
            print("Generating project plan...")
            plan = a3.plan(args.objective, project_path)
            print(f"✓ Plan generated with {len(plan.modules)} modules and {plan.estimated_functions} functions")
            
            print("Generating function specifications...")
            specs = a3.generate_specs(project_path)
            print(f"✓ Generated specifications for {len(specs.functions)} functions")
            
            print("Implementing functions...")
            impl_result = a3.implement(project_path)
            print(f"✓ Implemented {len(impl_result.implemented_functions)} functions")
            if impl_result.failed_functions:
                print(f"⚠ {len(impl_result.failed_functions)} functions failed to implement")
            
            print("Integrating modules...")
            # Pass test generation flag to integration
            generate_tests = getattr(args, 'generate_tests', False) or args.config.generate_tests
            integration_result = a3.integrate(project_path, generate_tests=generate_tests)
            if integration_result.success:
                print("✓ Project integration completed successfully")
                if hasattr(integration_result, 'test_result') and integration_result.test_result:
                    test_result = integration_result.test_result
                    if test_result.success:
                        print(f"✓ Generated and executed {len(test_result.generated_tests)} tests")
                    else:
                        print(f"⚠ Test generation completed with issues")
                
                # Generate requirements.txt if requested
                auto_generate_requirements = (getattr(args, 'auto_generate_requirements', False) or 
                                            args.config.auto_generate_requirements)
                if auto_generate_requirements:
                    try:
                        package_manager = PackageManager(project_path)
                        package_manager.initialize()
                        package_manager.update_requirements_file(project_path)
                        print("✓ Requirements.txt file generated")
                    except Exception as e:
                        print(f"⚠ Requirements generation failed: {e}")
            else:
                print("⚠ Integration completed with some issues")
                for error in integration_result.import_errors:
                    print(f"  - {error}")
        
        print(f"\nProject created successfully in: {Path(project_path).resolve()}")
        
    except Exception as e:
        handle_error(e)


def init_project_command(args) -> None:
    """Handle the init project command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        target_path = Path(project_path).resolve()
        
        # Check if directory exists
        if not target_path.exists():
            print(f"Error: Directory does not exist: {target_path}")
            print("Use 'a3 create' to create a new project, or create the directory first.")
            sys.exit(1)
        
        # Check if A3 is already initialized
        a3_dir = target_path / '.A3'
        if a3_dir.exists() and not args.force:
            print(f"A3 is already initialized in: {target_path}")
            print("Use --force to reinitialize, or 'a3 status' to check current state.")
            sys.exit(1)
        
        # Initialize A3
        a3 = A3(project_path)
        print(f"✓ A3 initialized in: {target_path}")
        print("You can now use 'a3 create' to start building a project.")
        
    except Exception as e:
        handle_error(e)


def status_command(args) -> None:
    """Handle the status command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        a3 = A3(project_path)
        status = a3.status(project_path)
        
        print(f"Project Status: {Path(project_path).resolve()}")
        print(f"Active: {'Yes' if status.is_active else 'No'}")
        
        if status.progress:
            print(f"Current Phase: {status.progress.current_phase.value.title()}")
            print(f"Progress: {status.progress.implemented_functions}/{status.progress.total_functions} functions")
            if status.progress.failed_functions:
                print(f"Failed Functions: {len(status.progress.failed_functions)}")
        
        if status.errors:
            print("Errors:")
            for error in status.errors:
                print(f"  - {error}")
        
        if status.next_action:
            print(f"Next Action: {status.next_action}")
        
        if status.can_resume:
            print("\nProject can be resumed with: a3 resume")
        
    except Exception as e:
        handle_error(e)


def resume_command(args) -> None:
    """Handle the resume command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        a3 = A3(project_path)
        
        # Set API key (priority: CLI arg > config > environment)
        api_key = args.api_key or args.config.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required. Set A3_API_KEY environment variable, use --api-key option, or configure with 'a3 config set api_key YOUR_KEY'.")
            sys.exit(1)
        
        a3.set_api_key(api_key)
        
        print(f"Resuming project in: {Path(project_path).resolve()}")
        
        result = a3.resume(project_path)
        
        if result.success:
            print("✓ Project resumed and completed successfully")
        else:
            print(f"⚠ Project resumption completed with issues: {result.message}")
            if result.errors:
                for error in result.errors:
                    print(f"  - {error}")
        
    except Exception as e:
        handle_error(e)


def integrate_project_command(args) -> None:
    """Handle the integrate project command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        a3 = A3(project_path)
        
        # Set API key (priority: CLI arg > config > environment)
        api_key = args.api_key or args.config.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required. Set A3_API_KEY environment variable, use --api-key option, or configure with 'a3 config set api_key YOUR_KEY'.")
            sys.exit(1)
        
        a3.set_api_key(api_key)
        
        print(f"Integrating modules in: {Path(project_path).resolve()}")
        
        # Determine test generation setting
        generate_tests = getattr(args, 'generate_tests', False) or args.config.generate_tests
        if generate_tests:
            print("Test generation: Enabled")
        
        # Determine package management settings
        enforce_import_consistency = (getattr(args, 'enforce_import_consistency', False) or 
                                    args.config.enforce_import_consistency)
        auto_generate_requirements = (getattr(args, 'auto_generate_requirements', False) or 
                                    args.config.auto_generate_requirements)
        
        if enforce_import_consistency:
            print("Import consistency: Enforced")
        if auto_generate_requirements:
            print("Requirements generation: Enabled")
        
        # Execute integration with enhanced options
        integration_result = a3.integrate(project_path, generate_tests=generate_tests)
        
        if integration_result.success:
            print("✓ Module integration completed successfully")
            if hasattr(integration_result, 'test_result') and integration_result.test_result:
                test_result = integration_result.test_result
                if test_result.success:
                    print(f"✓ Generated and executed {len(test_result.generated_tests)} tests")
                    if hasattr(test_result, 'execution_result') and test_result.execution_result:
                        exec_result = test_result.execution_result
                        print(f"✓ Test results: {exec_result.passed_tests}/{exec_result.total_tests} passed")
                else:
                    print(f"⚠ Test generation completed with issues")
                    for error in test_result.errors:
                        print(f"  - {error}")
            
            # Generate requirements.txt if requested
            if auto_generate_requirements:
                try:
                    package_manager = PackageManager(project_path)
                    package_manager.initialize()
                    package_manager.update_requirements_file(project_path)
                    print("✓ Requirements.txt file updated")
                except Exception as e:
                    print(f"⚠ Requirements generation failed: {e}")
        else:
            print("⚠ Integration completed with some issues")
            for error in integration_result.import_errors:
                print(f"  - {error}")
        
    except Exception as e:
        handle_error(e)


def analyze_project_command(args) -> None:
    """Handle the analyze project command."""
    try:
        # Import project analyzer and enhanced components
        
        # Set API key
        api_key = args.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required for project analysis. Set A3_API_KEY environment variable or use --api-key option.")
            sys.exit(1)
        
        # Initialize components
        client = OpenRouterClient(api_key)
        dependency_analyzer = DependencyAnalyzer()
        data_source_manager = DataSourceManager()
        database_analyzer = DatabaseAnalyzer(client) if hasattr(args, 'database') and args.database else None
        analyzer = ProjectAnalyzer(client, dependency_analyzer, data_source_manager, database_analyzer)
        
        print(f"Analyzing project: {Path(args.path).resolve()}")
        
        # Set database connection if provided
        if hasattr(args, 'database') and args.database and database_analyzer:
            print(f"Connecting to database: {args.database}")
            try:
                database_analyzer.connect_to_database(args.database)
                print("✓ Database connection established")
            except Exception as e:
                print(f"⚠ Database connection failed: {e}")
                database_analyzer = None
        
        # Scan project structure with enhanced capabilities
        project_structure = analyzer.scan_project_folder(args.path)
        print(f"✓ Found {len(project_structure.source_files)} source files")
        
        # Analyze data sources if requested
        if hasattr(args, 'analyze_data_sources') and args.analyze_data_sources:
            print("Analyzing data sources...")
            data_sources = analyzer.scan_data_sources(args.path)
            if data_sources.csv_files:
                print(f"✓ Found {len(data_sources.csv_files)} CSV files")
            if data_sources.json_files:
                print(f"✓ Found {len(data_sources.json_files)} JSON files")
            if data_sources.xml_files:
                print(f"✓ Found {len(data_sources.xml_files)} XML files")
            if data_sources.excel_files:
                print(f"✓ Found {len(data_sources.excel_files)} Excel files")
            
            # Save data source analysis
            data_analysis_path = Path(args.path) / "data_sources_analysis.json"
            with open(data_analysis_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'csv_files': [asdict(csv) for csv in data_sources.csv_files],
                    'json_files': [asdict(json_file) for json_file in data_sources.json_files],
                    'xml_files': [asdict(xml) for xml in data_sources.xml_files],
                    'excel_files': [asdict(excel) for excel in data_sources.excel_files]
                }, f, indent=2, default=str)
            print(f"✓ Data source analysis saved to: {data_analysis_path}")
        
        # Analyze database schema if connected
        if database_analyzer and hasattr(database_analyzer, 'connection'):
            print("Analyzing database schema...")
            try:
                schema = database_analyzer.analyze_database_schema()
                print(f"✓ Found {len(schema.tables)} database tables")
                
                # Save database schema analysis
                schema_path = Path(args.path) / "database_schema.json"
                with open(schema_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(schema), f, indent=2, default=str)
                print(f"✓ Database schema saved to: {schema_path}")
            except Exception as e:
                print(f"⚠ Database schema analysis failed: {e}")
        
        # Generate documentation if requested
        if args.generate_docs:
            print("Generating project documentation...")
            documentation = analyzer.generate_project_documentation(project_structure)
            
            # Save documentation
            docs_path = Path(args.path) / "PROJECT_ANALYSIS.md"
            with open(docs_path, 'w', encoding='utf-8') as f:
                f.write(documentation.content)
            print(f"✓ Documentation saved to: {docs_path}")
        
        # Build dependency graph if requested
        if args.dependency_graph:
            print("Building dependency graph...")
            dep_graph = analyzer.build_dependency_graph(project_structure)
            print(f"✓ Dependency graph created with {len(dep_graph.nodes)} modules")
            
            # Save dependency graph visualization
            graph_path = Path(args.path) / "dependency_graph.txt"
            with open(graph_path, 'w', encoding='utf-8') as f:
                f.write("Dependency Graph:\n")
                f.write("================\n\n")
                for node in dep_graph.nodes:
                    deps = dep_graph.get_dependencies(node)
                    f.write(f"{node}:\n")
                    if deps:
                        for dep in deps:
                            f.write(f"  -> {dep}\n")
                    else:
                        f.write("  (no dependencies)\n")
                    f.write("\n")
            print(f"✓ Dependency graph saved to: {graph_path}")
        
        # Analyze code patterns if requested
        if args.code_patterns:
            print("Analyzing code patterns...")
            patterns = analyzer.analyze_code_patterns(project_structure)
            
            patterns_path = Path(args.path) / "code_patterns.txt"
            with open(patterns_path, 'w', encoding='utf-8') as f:
                f.write("Code Patterns Analysis:\n")
                f.write("======================\n\n")
                f.write(f"Architectural Patterns: {', '.join(patterns.architectural_patterns)}\n")
                f.write(f"Design Patterns: {', '.join(patterns.design_patterns)}\n")
                f.write(f"Common Utilities: {', '.join(patterns.common_utilities)}\n")
                f.write(f"Test Patterns: {', '.join(patterns.test_patterns)}\n")
            print(f"✓ Code patterns analysis saved to: {patterns_path}")
        
        print("\nProject analysis completed successfully!")
        
    except Exception as e:
        handle_error(e)


def debug_project_command(args) -> None:
    """Handle the debug project command."""
    try:
        # Import debug analyzer
        
        # Set API key
        api_key = args.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required for debugging. Set A3_API_KEY environment variable or use --api-key option.")
            sys.exit(1)
        
        # Initialize components
        client = OpenRouterClient(api_key)
        file_manager = FileSystemManager(args.path)
        executor = CodeExecutor(args.path, file_manager)
        debug_analyzer = DebugAnalyzer(client)
        
        print(f"Debugging project: {Path(args.path).resolve()}")
        
        if args.execute_tests:
            print("Executing tests...")
            # Find test files
            test_files = []
            for root, dirs, files in os.walk(args.path):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_files.append(os.path.join(root, file))
            
            if test_files:
                test_result = executor.run_tests(test_files)
                print(f"✓ Tests executed: {test_result.passed_tests}/{test_result.total_tests} passed")
                
                if test_result.failed_tests > 0:
                    print("Failed tests:")
                    for detail in test_result.test_details:
                        if not detail.passed:
                            print(f"  - {detail.name}: {detail.error}")
            else:
                print("No test files found")
        
        if args.validate_imports:
            print("Validating imports...")
            # Find Python files
            python_files = []
            for root, dirs, files in os.walk(args.path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('test_'):
                        python_files.append(os.path.join(root, file))
            
            import_errors = []
            for py_file in python_files:
                try:
                    result = executor.validate_imports(py_file)
                    if not result.valid:
                        import_errors.extend(result.errors)
                except Exception as e:
                    import_errors.append(f"{py_file}: {e}")
            
            if import_errors:
                print("Import validation errors:")
                for error in import_errors:
                    print(f"  - {error}")
            else:
                print("✓ All imports are valid")
        
        print("\nDebugging completed!")
        
    except Exception as e:
        handle_error(e)


def config_show_command(args) -> None:
    """Handle the config show command."""
    try:
        config = A3Config.load()
        
        print("A3 Configuration:")
        print("=================")
        print()
        print("API Settings:")
        print(f"  API Key: {'Set' if config.api_key else 'Not set'}")
        print(f"  Model: {config.model}")
        print(f"  Max Retries: {config.max_retries}")
        print()
        print("Project Settings:")
        print(f"  Default Workspace: {config.default_workspace or 'Not set'}")
        print(f"  Auto Install Dependencies: {config.auto_install_deps}")
        print(f"  Generate Tests: {config.generate_tests}")
        print()
        print("Code Style Settings:")
        print(f"  Code Style: {config.code_style}")
        print(f"  Line Length: {config.line_length}")
        print(f"  Type Checking: {config.type_checking}")
        print()
        print("Quality Settings:")
        print(f"  Enforce Single Responsibility: {config.enforce_single_responsibility}")
        print(f"  Max Functions Per Module: {config.max_functions_per_module}")
        print()
        print("Test Generation Settings:")
        print(f"  Test Framework: {config.test_framework}")
        print(f"  Test Coverage Threshold: {config.test_coverage_threshold}%")
        print(f"  Generate Integration Tests: {config.generate_integration_tests}")
        print(f"  Test File Naming: {config.test_file_naming}")
        print(f"  Mock External Dependencies: {config.mock_external_dependencies}")
        print()
        print("Database Settings:")
        print(f"  Default Database URL: {'Set' if config.default_database_url else 'Not set'}")
        print(f"  Connection Timeout: {config.database_connection_timeout}s")
        print(f"  Pool Size: {config.database_pool_size}")
        print(f"  SSL Mode: {config.database_ssl_mode}")
        print()
        print("Package Management Settings:")
        print(f"  Enforce Import Consistency: {config.enforce_import_consistency}")
        print(f"  Auto Generate Requirements: {config.auto_generate_requirements}")
        print(f"  Requirements File Name: {config.requirements_file_name}")
        print(f"  Package Aliases: {len(config.package_aliases)} configured")
        print()
        print("Data Source Analysis Settings:")
        print(f"  Analyze Data Sources by Default: {config.analyze_data_sources_by_default}")
        print(f"  Max Data File Size: {config.max_data_file_size_mb}MB")
        print(f"  Data Sample Size: {config.data_sample_size}")
        print(f"  Supported Formats: {', '.join(config.supported_data_formats)}")
        
    except Exception as e:
        handle_error(e)


def config_set_command(args) -> None:
    """Handle the config set command."""
    try:
        config = A3Config.load()
        
        # List of available configuration keys
        available_keys = [
            # API settings
            'api_key', 'model', 'max_retries',
            # Project settings
            'default_workspace', 'auto_install_deps', 'generate_tests',
            # Code style settings
            'code_style', 'line_length', 'type_checking',
            # Quality settings
            'enforce_single_responsibility', 'max_functions_per_module',
            # Test generation settings
            'test_framework', 'test_coverage_threshold', 'generate_integration_tests',
            'test_file_naming', 'mock_external_dependencies',
            # Database settings
            'default_database_url', 'database_connection_timeout', 'database_pool_size', 'database_ssl_mode',
            # Package management settings
            'enforce_import_consistency', 'auto_generate_requirements', 'requirements_file_name',
            # Data source analysis settings
            'analyze_data_sources_by_default', 'max_data_file_size_mb', 'data_sample_size'
        ]
        
        # Validate key
        if args.key not in available_keys:
            print(f"Error: Unknown configuration key '{args.key}'")
            print("Available keys:")
            print("  API Settings: api_key, model, max_retries")
            print("  Project Settings: default_workspace, auto_install_deps, generate_tests")
            print("  Code Style: code_style, line_length, type_checking")
            print("  Quality: enforce_single_responsibility, max_functions_per_module")
            print("  Test Generation: test_framework, test_coverage_threshold, generate_integration_tests, test_file_naming, mock_external_dependencies")
            print("  Database: default_database_url, database_connection_timeout, database_pool_size, database_ssl_mode")
            print("  Package Management: enforce_import_consistency, auto_generate_requirements, requirements_file_name")
            print("  Data Analysis: analyze_data_sources_by_default, max_data_file_size_mb, data_sample_size")
            sys.exit(1)
        
        # Handle special case for package aliases
        if args.key == 'package_aliases':
            print("Error: Package aliases must be configured using 'a3 config set-alias' command")
            sys.exit(1)
        
        # Convert value to appropriate type
        current_value = getattr(config, args.key)
        if isinstance(current_value, bool):
            value = args.value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current_value, int):
            try:
                value = int(args.value)
            except ValueError:
                print(f"Error: '{args.key}' requires an integer value")
                sys.exit(1)
        elif isinstance(current_value, float):
            try:
                value = float(args.value)
            except ValueError:
                print(f"Error: '{args.key}' requires a numeric value")
                sys.exit(1)
        else:
            value = args.value
        
        # Set the value
        setattr(config, args.key, value)
        
        # Save configuration
        if args.global_config:
            config_path = Path.home() / '.a3config.json'
        else:
            config_path = Path.cwd() / '.a3config.json'
        
        config.save(str(config_path))
        print(f"✓ Set {args.key} = {value}")
        print(f"Configuration saved to: {config_path}")
        
    except Exception as e:
        handle_error(e)


def config_set_alias_command(args) -> None:
    """Handle the config set-alias command."""
    try:
        config = A3Config.load()
        
        # Update package alias
        config.package_aliases[args.package] = args.alias
        
        # Save configuration
        if args.global_config:
            config_path = Path.home() / '.a3config.json'
        else:
            config_path = Path.cwd() / '.a3config.json'
        
        config.save(str(config_path))
        print(f"✓ Set package alias: {args.package} -> {args.alias}")
        print(f"Configuration saved to: {config_path}")
        
    except Exception as e:
        handle_error(e)


def config_show_aliases_command(args) -> None:
    """Handle the config show-aliases command."""
    try:
        config = A3Config.load()
        
        print("Package Import Aliases:")
        print("======================")
        
        if config.package_aliases:
            for package, alias in sorted(config.package_aliases.items()):
                print(f"  {package} -> {alias}")
        else:
            print("  No package aliases configured")
        
    except Exception as e:
        handle_error(e)


def package_generate_requirements_command(args) -> None:
    """Handle the package generate-requirements command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        print(f"Generating requirements.txt for: {Path(project_path).resolve()}")
        
        package_manager = PackageManager(project_path)
        package_manager.initialize()
        package_manager.update_requirements_file(project_path)
        
        requirements_path = Path(project_path) / "requirements.txt"
        if requirements_path.exists():
            print(f"✓ Requirements.txt generated successfully")
            print(f"Location: {requirements_path}")
            
            # Show contents
            with open(requirements_path, 'r') as f:
                requirements = f.read().strip()
                if requirements:
                    print("\nGenerated requirements:")
                    for line in requirements.split('\n'):
                        print(f"  {line}")
                else:
                    print("No requirements found in project")
        else:
            print("⚠ Requirements.txt file was not created")
        
    except Exception as e:
        handle_error(e)


def package_validate_imports_command(args) -> None:
    """Handle the package validate-imports command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        print(f"Validating import consistency in: {Path(project_path).resolve()}")
        
        package_manager = PackageManager(project_path)
        package_manager.initialize()
        dependency_analyzer = DependencyAnalyzer(project_path, package_manager)
        
        # Find Python files
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))
        
        if not python_files:
            print("No Python files found in project")
            return
        
        print(f"Analyzing {len(python_files)} Python files...")
        
        inconsistencies = []
        for py_file in python_files:
            try:
                # Analyze imports in the file
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple import pattern matching
                import_lines = re.findall(r'^(?:from\s+\S+\s+)?import\s+.+$', content, re.MULTILINE)
                
                for line in import_lines:
                    # Check for common packages with standard aliases
                    if 'pandas' in line and 'as pd' not in line and 'import pandas' in line:
                        inconsistencies.append(f"{py_file}: pandas should be imported as 'pd'")
                    elif 'numpy' in line and 'as np' not in line and 'import numpy' in line:
                        inconsistencies.append(f"{py_file}: numpy should be imported as 'np'")
                    elif 'matplotlib.pyplot' in line and 'as plt' not in line:
                        inconsistencies.append(f"{py_file}: matplotlib.pyplot should be imported as 'plt'")
                        
            except Exception as e:
                print(f"⚠ Could not analyze {py_file}: {e}")
        
        if inconsistencies:
            print(f"\nFound {len(inconsistencies)} import inconsistencies:")
            for inconsistency in inconsistencies:
                print(f"  - {inconsistency}")
            
            if args.fix:
                print("\nFixing import inconsistencies...")
                fixed_count = 0
                for py_file in python_files:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Fix common import patterns
                        content = re.sub(r'^import pandas$', 'import pandas as pd', content, flags=re.MULTILINE)
                        content = re.sub(r'^import numpy$', 'import numpy as np', content, flags=re.MULTILINE)
                        content = re.sub(r'^import matplotlib\.pyplot$', 'import matplotlib.pyplot as plt', content, flags=re.MULTILINE)
                        
                        if content != original_content:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            fixed_count += 1
                            print(f"  ✓ Fixed imports in {py_file}")
                            
                    except Exception as e:
                        print(f"  ⚠ Could not fix {py_file}: {e}")
                
                print(f"\n✓ Fixed imports in {fixed_count} files")
            else:
                print("\nUse --fix flag to automatically correct these issues")
        else:
            print("✓ All imports are consistent")
        
    except Exception as e:
        handle_error(e)


def package_show_usage_command(args) -> None:
    """Handle the package show-usage command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        print(f"Analyzing package usage in: {Path(project_path).resolve()}")
        
        # Find Python files and analyze imports
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))
        
        if not python_files:
            print("No Python files found in project")
            return
        
        package_usage = {}
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract import statements
                import_lines = re.findall(r'^(?:from\s+(\S+)\s+import|import\s+(\S+)).*$', content, re.MULTILINE)
                
                for from_pkg, import_pkg in import_lines:
                    package = from_pkg or import_pkg
                    if package:
                        # Get the root package name
                        root_package = package.split('.')[0]
                        if root_package not in ['os', 'sys', 'json', 'typing', 're', 'pathlib', 'datetime']:
                            if root_package not in package_usage:
                                package_usage[root_package] = {'files': set(), 'imports': []}
                            package_usage[root_package]['files'].add(py_file)
                            package_usage[root_package]['imports'].append(package)
                            
            except Exception as e:
                print(f"⚠ Could not analyze {py_file}: {e}")
        
        if package_usage:
            print(f"\nPackage Usage Summary:")
            print("=" * 50)
            
            for package, info in sorted(package_usage.items()):
                print(f"\n{package}:")
                print(f"  Used in {len(info['files'])} files")
                print(f"  Import variations: {len(set(info['imports']))}")
                
                # Show unique imports
                unique_imports = sorted(set(info['imports']))
                for imp in unique_imports[:5]:  # Show first 5
                    print(f"    - {imp}")
                if len(unique_imports) > 5:
                    print(f"    ... and {len(unique_imports) - 5} more")
            
            print(f"\nTotal external packages detected: {len(package_usage)}")
        else:
            print("No external package usage detected")
        
    except Exception as e:
        handle_error(e)


def planning_generate_docs_command(args) -> None:
    """Handle the planning generate-docs command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), args.config)
        
        # Set API key
        api_key = args.api_key or get_api_key()
        if not api_key:
            print("Error: API key is required for documentation generation. Set A3_API_KEY environment variable or use --api-key option.")
            sys.exit(1)
        
        # Initialize components
        client = OpenRouterClient(api_key)
        requirement_parser = RequirementParser(client)
        doc_generator = StructuredDocumentGenerator(requirement_parser)
        planning_engine = PlanningEngine(client)
        
        print(f"Generating structured documentation for: {Path(project_path).resolve()}")
        print(f"Objective: {args.objective}")
        
        # Load or create documentation configuration
        doc_config = None
        if args.config:
            try:
                with open(args.config, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                doc_config = DocumentationConfiguration(**config_data)
                print(f"Using configuration from: {args.config}")
            except Exception as e:
                print(f"⚠ Could not load configuration file: {e}")
                print("Using default configuration")
        
        if not doc_config:
            doc_config = DocumentationConfiguration()
        
        # Generate documentation based on flags
        context = {"project_path": project_path}
        
        if args.requirements_only:
            print("Generating requirements document...")
            requirements_doc = doc_generator.generate_requirements_document(args.objective, context)
            
            # Save requirements document
            req_path = Path(project_path) / "requirements.md"
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write(f"# Requirements Document\n\n")
                f.write(f"## Introduction\n\n{requirements_doc.introduction}\n\n")
                f.write(f"## Requirements\n\n")
                for req in requirements_doc.requirements:
                    f.write(f"### Requirement {req.id}\n\n")
                    f.write(f"**User Story:** {req.user_story}\n\n")
                    f.write(f"#### Acceptance Criteria\n\n")
                    for i, criterion in enumerate(req.acceptance_criteria, 1):
                        f.write(f"{i}. {criterion.when_clause} THEN {criterion.shall_clause}\n")
                    f.write("\n")
            
            print(f"✓ Requirements document saved to: {req_path}")
            
        elif args.design_only:
            print("Error: Design-only generation requires existing requirements document")
            print("Generate requirements first or use full documentation generation")
            sys.exit(1)
            
        elif args.tasks_only:
            print("Error: Tasks-only generation requires existing requirements and design documents")
            print("Generate requirements and design first or use full documentation generation")
            sys.exit(1)
            
        else:
            # Generate full documentation set
            print("Generating complete documentation set...")
            
            # Generate enhanced project plan with documentation
            enhanced_plan = planning_engine.generate_plan_with_documentation(args.objective, doc_config)
            
            if enhanced_plan.requirements_document:
                req_path = Path(project_path) / "requirements.md"
                with open(req_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Requirements Document\n\n")
                    f.write(f"## Introduction\n\n{enhanced_plan.requirements_document.introduction}\n\n")
                    f.write(f"## Requirements\n\n")
                    for req in enhanced_plan.requirements_document.requirements:
                        f.write(f"### Requirement {req.id}\n\n")
                        f.write(f"**User Story:** {req.user_story}\n\n")
                        f.write(f"#### Acceptance Criteria\n\n")
                        for i, criterion in enumerate(req.acceptance_criteria, 1):
                            f.write(f"{i}. {criterion.when_clause} THEN {criterion.shall_clause}\n")
                        f.write("\n")
                print(f"✓ Requirements document saved to: {req_path}")
            
            if enhanced_plan.design_document:
                design_path = Path(project_path) / "design.md"
                with open(design_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Design Document\n\n")
                    f.write(f"## Overview\n\n{enhanced_plan.design_document.overview}\n\n")
                    f.write(f"## Architecture\n\n{enhanced_plan.design_document.architecture}\n\n")
                    f.write(f"## Components\n\n")
                    for component in enhanced_plan.design_document.components:
                        f.write(f"### {component.name}\n\n")
                        f.write(f"{component.description}\n\n")
                        if component.interfaces:
                            f.write(f"**Interfaces:** {', '.join(component.interfaces)}\n\n")
                        if component.dependencies:
                            f.write(f"**Dependencies:** {', '.join(component.dependencies)}\n\n")
                print(f"✓ Design document saved to: {design_path}")
            
            if enhanced_plan.tasks_document:
                tasks_path = Path(project_path) / "tasks.md"
                with open(tasks_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Implementation Tasks\n\n")
                    for task in enhanced_plan.tasks_document.tasks:
                        f.write(f"- [ ] {task.id}. {task.description}\n")
                        if task.requirements:
                            f.write(f"  - Requirements: {', '.join(task.requirements)}\n")
                        if task.design_components:
                            f.write(f"  - Design Components: {', '.join(task.design_components)}\n")
                        f.write("\n")
                print(f"✓ Tasks document saved to: {tasks_path}")
        
        print("\nDocumentation generation completed successfully!")
        
    except Exception as e:
        handle_error(e)


def planning_export_command(args) -> None:
    """Handle the planning export command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        print(f"Exporting documentation from: {Path(project_path).resolve()}")
        
        # Initialize state manager to load documentation
        state_manager = StateManager(project_path)
        
        # Try to load enhanced project plan
        try:
            enhanced_plan = state_manager.load_enhanced_project_plan()
            if not enhanced_plan:
                print("No enhanced project plan found. Generate documentation first using 'a3 planning generate-docs'")
                sys.exit(1)
        except Exception:
            print("No enhanced project plan found. Generate documentation first using 'a3 planning generate-docs'")
            sys.exit(1)
        
        # Determine output file
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(project_path) / f"documentation_export_{timestamp}.{args.format}"
        
        # Export based on format
        if args.format == 'json':
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
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        elif args.format == 'markdown':
            with open(output_path, 'w', encoding='utf-8') as f:
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
        
        elif args.format == 'html':
            with open(output_path, 'w', encoding='utf-8') as f:
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
        
        print(f"✓ Documentation exported to: {output_path}")
        
    except Exception as e:
        handle_error(e)


def planning_validate_command(args) -> None:
    """Handle the planning validate command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        print(f"Validating documentation in: {Path(project_path).resolve()}")
        
        # Initialize state manager
        state_manager = StateManager(project_path)
        
        # Load enhanced project plan
        try:
            enhanced_plan = state_manager.load_enhanced_project_plan()
            if not enhanced_plan:
                print("No enhanced project plan found. Generate documentation first using 'a3 planning generate-docs'")
                sys.exit(1)
        except Exception:
            print("No enhanced project plan found. Generate documentation first using 'a3 planning generate-docs'")
            sys.exit(1)
        
        validation_errors = []
        validation_warnings = []
        
        # Check consistency between documents
        if args.check_consistency or not (args.check_coverage or args.check_consistency):
            print("Checking document consistency...")
            
            if enhanced_plan.requirements_document and enhanced_plan.design_document:
                # Check that all requirements are referenced in design
                req_ids = {req.id for req in enhanced_plan.requirements_document.requirements}
                design_req_refs = set()
                
                for component in enhanced_plan.design_document.components:
                    if hasattr(component, 'requirement_references'):
                        design_req_refs.update(component.requirement_references)
                
                missing_in_design = req_ids - design_req_refs
                if missing_in_design:
                    validation_warnings.append(f"Requirements not referenced in design: {', '.join(missing_in_design)}")
                
                extra_in_design = design_req_refs - req_ids
                if extra_in_design:
                    validation_errors.append(f"Design references non-existent requirements: {', '.join(extra_in_design)}")
            
            if enhanced_plan.design_document and enhanced_plan.tasks_document:
                # Check that all design components are covered by tasks
                component_names = {comp.name for comp in enhanced_plan.design_document.components}
                task_component_refs = set()
                
                for task in enhanced_plan.tasks_document.tasks:
                    if task.design_components:
                        task_component_refs.update(task.design_components)
                
                missing_in_tasks = component_names - task_component_refs
                if missing_in_tasks:
                    validation_warnings.append(f"Design components not covered by tasks: {', '.join(missing_in_tasks)}")
        
        # Check requirement coverage in implementation
        if args.check_coverage or not (args.check_coverage or args.check_consistency):
            print("Checking requirement coverage...")
            
            if enhanced_plan.requirements_document:
                # Look for Python files in the project
                python_files = []
                for root, dirs, files in os.walk(project_path):
                    # Skip hidden directories and common build/cache directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
                    for file in files:
                        if file.endswith('.py') and not file.startswith('.'):
                            python_files.append(os.path.join(root, file))
                
                if python_files:
                    # Check for requirement references in code
                    req_ids = {req.id for req in enhanced_plan.requirements_document.requirements}
                    found_refs = set()
                    
                    for py_file in python_files:
                        try:
                            with open(py_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Look for requirement references in comments and docstrings
                            for req_id in req_ids:
                                if re.search(rf'(?i)requirement\s*{re.escape(req_id)}|req\s*{re.escape(req_id)}', content):
                                    found_refs.add(req_id)
                                    
                        except Exception as e:
                            validation_warnings.append(f"Could not analyze {py_file}: {e}")
                    
                    missing_coverage = req_ids - found_refs
                    if missing_coverage:
                        validation_warnings.append(f"Requirements not referenced in implementation: {', '.join(missing_coverage)}")
                    
                    coverage_percentage = (len(found_refs) / len(req_ids)) * 100 if req_ids else 100
                    print(f"Requirement coverage: {coverage_percentage:.1f}% ({len(found_refs)}/{len(req_ids)} requirements)")
                else:
                    validation_warnings.append("No Python files found for coverage analysis")
        
        # Report results
        if validation_errors:
            print("\n❌ Validation Errors:")
            for error in validation_errors:
                print(f"  - {error}")
        
        if validation_warnings:
            print("\n⚠️  Validation Warnings:")
            for warning in validation_warnings:
                print(f"  - {warning}")
        
        if not validation_errors and not validation_warnings:
            print("\n✅ All validation checks passed!")
        elif not validation_errors:
            print(f"\n✅ Validation completed with {len(validation_warnings)} warnings")
        else:
            print(f"\n❌ Validation failed with {len(validation_errors)} errors and {len(validation_warnings)} warnings")
            sys.exit(1)
        
    except Exception as e:
        handle_error(e)


def planning_config_show_command(args) -> None:
    """Handle the planning config show command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        print(f"Documentation Configuration for: {Path(project_path).resolve()}")
        print("=" * 60)
        
        # Try to load existing configuration
        config_path = Path(project_path) / '.a3' / 'documentation_config.json'
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                doc_config = DocumentationConfiguration(**config_data)
                print("Configuration loaded from project settings")
            except Exception as e:
                print(f"Error loading configuration: {e}")
                doc_config = DocumentationConfiguration()
                print("Using default configuration")
        else:
            doc_config = DocumentationConfiguration()
            print("Using default configuration (no project config found)")
        
        print()
        print("Documentation Generation:")
        print(f"  Enable Requirements: {doc_config.enable_requirements}")
        print(f"  Enable Design: {doc_config.enable_design}")
        print(f"  Enable Tasks: {doc_config.enable_tasks}")
        print()
        print("Format Settings:")
        print(f"  Requirements Format: {doc_config.requirements_format}")
        print(f"  Use EARS Format: {doc_config.use_ears_format}")
        print(f"  Include User Stories: {doc_config.include_user_stories}")
        print()
        print("Template Settings:")
        print(f"  Requirements Template: {'Custom' if doc_config.requirements_template else 'Default'}")
        print(f"  Design Template: {'Custom' if doc_config.design_template else 'Default'}")
        print(f"  Tasks Template: {'Custom' if doc_config.tasks_template else 'Default'}")
        print()
        print("Validation Settings:")
        print(f"  Validate Requirements: {doc_config.validate_requirements}")
        print(f"  Check Consistency: {doc_config.check_consistency}")
        print(f"  Require Traceability: {doc_config.require_traceability}")
        
    except Exception as e:
        handle_error(e)


def planning_config_set_command(args) -> None:
    """Handle the planning config set command."""
    try:
        
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        # Available configuration keys
        available_keys = [
            'enable_requirements', 'enable_design', 'enable_tasks',
            'requirements_format', 'use_ears_format', 'include_user_stories',
            'validate_requirements', 'check_consistency', 'require_traceability'
        ]
        
        if args.key not in available_keys:
            print(f"Error: Unknown configuration key '{args.key}'")
            print("Available keys:")
            print("  Documentation: enable_requirements, enable_design, enable_tasks")
            print("  Format: requirements_format, use_ears_format, include_user_stories")
            print("  Validation: validate_requirements, check_consistency, require_traceability")
            sys.exit(1)
        
        # Load existing configuration
        config_path = Path(project_path) / '.a3' / 'documentation_config.json'
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
        
        # Convert value to appropriate type
        current_value = getattr(doc_config, args.key)
        if isinstance(current_value, bool):
            value = args.value.lower() in ('true', '1', 'yes', 'on')
        else:
            value = args.value
        
        # Set the new value
        setattr(doc_config, args.key, value)
        
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
        
        print(f"✓ Configuration updated: {args.key} = {value}")
        print(f"Configuration saved to: {config_path}")
        
    except Exception as e:
        handle_error(e)


def planning_migrate_command(args) -> None:
    """Handle the planning migrate command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        migrator = ProjectMigrator(project_path)
        
        if args.check_only:
            # Only check compatibility
            result = migrator.check_compatibility()
            
            print(f"Project compatibility check for: {Path(project_path).resolve()}")
            print(f"Compatible: {'Yes' if result['compatible'] else 'No'}")
            print(f"Has existing plan: {'Yes' if result['has_existing_plan'] else 'No'}")
            print(f"Already enhanced: {'Yes' if result['is_already_enhanced'] else 'No'}")
            print(f"Migration needed: {'Yes' if result['migration_needed'] else 'No'}")
            
            if result['issues']:
                print("\nIssues:")
                for issue in result['issues']:
                    print(f"  - {issue}")
            
            if result['warnings']:
                print("\nWarnings:")
                for warning in result['warnings']:
                    print(f"  - {warning}")
        else:
            # Perform migration
            backup = not args.no_backup
            result = migrator.migrate_project(backup=backup)
            
            if result['success']:
                print(f"✓ {result['message']}")
                if result['backup_created']:
                    print(f"  Backup created: {result['backup_id']}")
            else:
                print(f"✗ {result['message']}")
                sys.exit(1)
        
    except Exception as e:
        handle_error(e)


def planning_status_command(args) -> None:
    """Handle the planning status command."""
    try:
        project_path = resolve_project_path(args.path, getattr(args, 'workspace', None), 
                                          getattr(args, 'config', A3Config.load()))
        
        migrator = ProjectMigrator(project_path)
        status = migrator.get_migration_status()
        
        print(f"Enhanced planning status for: {Path(project_path).resolve()}")
        print(f"Status: {status['status']}")
        print(f"Message: {status['message']}")
        print(f"Enhanced features: {'Yes' if status['is_enhanced'] else 'No'}")
        print(f"Can migrate: {'Yes' if status['can_migrate'] else 'No'}")
        
        if status['status'] == 'enhanced':
            print(f"Has requirements: {'Yes' if status.get('has_requirements', False) else 'No'}")
            print(f"Has design: {'Yes' if status.get('has_design', False) else 'No'}")
            print(f"Has tasks: {'Yes' if status.get('has_tasks', False) else 'No'}")
            print(f"Enhanced functions: {status.get('enhanced_functions_count', 0)}")
        elif status['status'] == 'basic':
            print(f"Modules: {status.get('modules_count', 0)}")
            print(f"Estimated functions: {status.get('estimated_functions', 0)}")
        
    except Exception as e:
        handle_error(e)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Project Builder (A3) - Automated project creation through AI-powered planning and code generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  a3 create "A web scraper for news articles" --path ./news-scraper
  a3 status --path ./my-project
  a3 resume --path ./my-project
  a3 analyze ./existing-project --generate-docs --dependency-graph
  a3 debug ./my-project --execute-tests --validate-imports

Environment Variables:
  A3_API_KEY or OPENROUTER_API_KEY: Your OpenRouter API key
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--api-key', help='OpenRouter API key (overrides environment variable)')
    parser.add_argument('--workspace', help='Set default workspace directory for all operations')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('objective', help='High-level description of the project')
    create_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    create_parser.add_argument('--plan-only', action='store_true', help='Only generate the project plan')
    create_parser.add_argument('--template', choices=['web-api', 'cli-tool', 'data-pipeline', 'ml-project'], 
                              help='Use a predefined project template')
    create_parser.add_argument('--auto-install', action='store_true', 
                              help='Automatically install dependencies after creation')
    create_parser.add_argument('--generate-tests', action='store_true',
                              help='Generate unit tests during integration')
    create_parser.add_argument('--database', type=str,
                              help='PostgreSQL connection string for database integration')
    create_parser.add_argument('--analyze-data-sources', action='store_true',
                              help='Analyze data files (CSV, JSON, XML, Excel) in project directory')
    create_parser.add_argument('--enforce-import-consistency', action='store_true',
                              help='Enforce consistent import patterns across modules')
    create_parser.add_argument('--auto-generate-requirements', action='store_true',
                              help='Automatically generate requirements.txt file')
    create_parser.set_defaults(func=create_project_command)
    
    # Init command - initialize A3 in existing directory
    init_parser = subparsers.add_parser('init', help='Initialize A3 in an existing project directory')
    init_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    init_parser.add_argument('--force', action='store_true', help='Force initialization even if A3 files exist')
    init_parser.set_defaults(func=init_project_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check project status')
    status_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    status_parser.set_defaults(func=status_command)
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume an interrupted project')
    resume_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    resume_parser.set_defaults(func=resume_command)
    
    # Integrate command
    integrate_parser = subparsers.add_parser('integrate', help='Integrate modules in an existing project')
    integrate_parser.add_argument('--path', default='.', help='Project directory path (default: current directory)')
    integrate_parser.add_argument('--generate-tests', action='store_true',
                                help='Generate unit tests during integration')
    integrate_parser.add_argument('--enforce-import-consistency', action='store_true',
                                help='Enforce consistent import patterns during integration')
    integrate_parser.add_argument('--auto-generate-requirements', action='store_true',
                                help='Automatically generate requirements.txt file after integration')
    integrate_parser.set_defaults(func=integrate_project_command)
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze an existing project')
    analyze_parser.add_argument('path', help='Project directory path to analyze')
    analyze_parser.add_argument('--generate-docs', action='store_true', help='Generate project documentation')
    analyze_parser.add_argument('--dependency-graph', action='store_true', help='Create dependency graph')
    analyze_parser.add_argument('--code-patterns', action='store_true', help='Analyze code patterns')
    analyze_parser.add_argument('--database', type=str,
                              help='PostgreSQL connection string for database analysis')
    analyze_parser.add_argument('--analyze-data-sources', action='store_true',
                              help='Analyze data files (CSV, JSON, XML, Excel) in project directory')
    analyze_parser.set_defaults(func=analyze_project_command)
    
    # Debug command
    debug_parser = subparsers.add_parser('debug', help='Debug and test project code')
    debug_parser.add_argument('path', help='Project directory path to debug')
    debug_parser.add_argument('--execute-tests', action='store_true', help='Execute all tests')
    debug_parser.add_argument('--validate-imports', action='store_true', help='Validate all imports')
    debug_parser.set_defaults(func=debug_project_command)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage A3 configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Configuration actions')
    
    # Config show
    config_show_parser = config_subparsers.add_parser('show', help='Show current configuration')
    config_show_parser.set_defaults(func=config_show_command)
    
    # Config set
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('key', help='Configuration key')
    config_set_parser.add_argument('value', help='Configuration value')
    config_set_parser.add_argument('--global', action='store_true', dest='global_config', 
                                  help='Set global configuration')
    config_set_parser.set_defaults(func=config_set_command)
    
    # Config set-alias
    config_alias_parser = config_subparsers.add_parser('set-alias', help='Set package import alias')
    config_alias_parser.add_argument('package', help='Package name')
    config_alias_parser.add_argument('alias', help='Import alias')
    config_alias_parser.add_argument('--global', action='store_true', dest='global_config', 
                                    help='Set global configuration')
    config_alias_parser.set_defaults(func=config_set_alias_command)
    
    # Config show-aliases
    config_show_aliases_parser = config_subparsers.add_parser('show-aliases', help='Show package aliases')
    config_show_aliases_parser.set_defaults(func=config_show_aliases_command)
    
    # Package management command
    package_parser = subparsers.add_parser('package', help='Package management operations')
    package_subparsers = package_parser.add_subparsers(dest='package_action', help='Package management actions')
    
    # Package generate-requirements
    package_gen_req_parser = package_subparsers.add_parser('generate-requirements', 
                                                          help='Generate requirements.txt file')
    package_gen_req_parser.add_argument('--path', default='.', 
                                       help='Project directory path (default: current directory)')
    package_gen_req_parser.set_defaults(func=package_generate_requirements_command)
    
    # Package validate-imports
    package_validate_parser = package_subparsers.add_parser('validate-imports', 
                                                           help='Validate import consistency')
    package_validate_parser.add_argument('--path', default='.', 
                                        help='Project directory path (default: current directory)')
    package_validate_parser.add_argument('--fix', action='store_true', 
                                        help='Automatically fix import inconsistencies')
    package_validate_parser.set_defaults(func=package_validate_imports_command)
    
    # Package show-usage
    package_usage_parser = package_subparsers.add_parser('show-usage', 
                                                        help='Show package usage statistics')
    package_usage_parser.add_argument('--path', default='.', 
                                     help='Project directory path (default: current directory)')
    package_usage_parser.set_defaults(func=package_show_usage_command)
    
    # Enhanced planning command
    planning_parser = subparsers.add_parser('planning', help='Enhanced planning operations')
    planning_subparsers = planning_parser.add_subparsers(dest='planning_action', help='Planning actions')
    
    # Planning generate-docs
    planning_gen_docs_parser = planning_subparsers.add_parser('generate-docs', 
                                                             help='Generate structured documentation (requirements, design, tasks)')
    planning_gen_docs_parser.add_argument('objective', help='High-level description of the project')
    planning_gen_docs_parser.add_argument('--path', default='.', 
                                         help='Project directory path (default: current directory)')
    planning_gen_docs_parser.add_argument('--config', type=str,
                                         help='Path to documentation configuration file')
    planning_gen_docs_parser.add_argument('--requirements-only', action='store_true',
                                         help='Generate only requirements document')
    planning_gen_docs_parser.add_argument('--design-only', action='store_true',
                                         help='Generate only design document')
    planning_gen_docs_parser.add_argument('--tasks-only', action='store_true',
                                         help='Generate only tasks document')
    planning_gen_docs_parser.set_defaults(func=planning_generate_docs_command)
    
    # Planning export
    planning_export_parser = planning_subparsers.add_parser('export', 
                                                           help='Export generated documentation')
    planning_export_parser.add_argument('--path', default='.', 
                                       help='Project directory path (default: current directory)')
    planning_export_parser.add_argument('--format', choices=['markdown', 'json', 'html'], default='markdown',
                                       help='Export format (default: markdown)')
    planning_export_parser.add_argument('--output', type=str,
                                       help='Output file path (default: auto-generated)')
    planning_export_parser.set_defaults(func=planning_export_command)
    
    # Planning validate
    planning_validate_parser = planning_subparsers.add_parser('validate', 
                                                             help='Validate requirement coverage and consistency')
    planning_validate_parser.add_argument('--path', default='.', 
                                         help='Project directory path (default: current directory)')
    planning_validate_parser.add_argument('--check-coverage', action='store_true',
                                         help='Check requirement coverage in implementation')
    planning_validate_parser.add_argument('--check-consistency', action='store_true',
                                         help='Check consistency between documents')
    planning_validate_parser.set_defaults(func=planning_validate_command)
    
    # Planning config
    planning_config_parser = planning_subparsers.add_parser('config', 
                                                           help='Manage documentation configuration')
    planning_config_subparsers = planning_config_parser.add_subparsers(dest='planning_config_action', 
                                                                      help='Configuration actions')
    
    # Planning config show
    planning_config_show_parser = planning_config_subparsers.add_parser('show', 
                                                                       help='Show current documentation configuration')
    planning_config_show_parser.add_argument('--path', default='.', 
                                            help='Project directory path (default: current directory)')
    planning_config_show_parser.set_defaults(func=planning_config_show_command)
    
    # Planning config set
    planning_config_set_parser = planning_config_subparsers.add_parser('set', 
                                                                      help='Set documentation configuration')
    planning_config_set_parser.add_argument('key', help='Configuration key')
    planning_config_set_parser.add_argument('value', help='Configuration value')
    planning_config_set_parser.add_argument('--path', default='.', 
                                           help='Project directory path (default: current directory)')
    planning_config_set_parser.set_defaults(func=planning_config_set_command)
    
    # Planning migrate
    planning_migrate_parser = planning_subparsers.add_parser('migrate', 
                                                           help='Migrate project to enhanced planning')
    planning_migrate_parser.add_argument('--path', default='.', 
                                       help='Project directory path (default: current directory)')
    planning_migrate_parser.add_argument('--no-backup', action='store_true',
                                       help='Skip creating backup before migration')
    planning_migrate_parser.add_argument('--check-only', action='store_true',
                                       help='Only check compatibility, do not migrate')
    planning_migrate_parser.set_defaults(func=planning_migrate_command)
    
    # Planning status
    planning_status_parser = planning_subparsers.add_parser('status', 
                                                          help='Check enhanced planning status')
    planning_status_parser.add_argument('--path', default='.', 
                                      help='Project directory path (default: current directory)')
    planning_status_parser.set_defaults(func=planning_status_command)
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Load configuration
    config = A3Config.load()
    
    # Apply workspace from config if not specified
    if hasattr(args, 'workspace') and not args.workspace:
        args.workspace = config.default_workspace
    
    # Store config in args for command functions
    args.config = config
    
    # Handle no command
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle package command with no action
    if args.command == 'package' and not hasattr(args, 'package_action'):
        print("Error: Package command requires an action")
        print("Available actions: generate-requirements, validate-imports, show-usage")
        print("Use 'a3 package --help' for more information")
        sys.exit(1)
    
    # Handle planning command with no action
    if args.command == 'planning' and not hasattr(args, 'planning_action'):
        print("Error: Planning command requires an action")
        print("Available actions: generate-docs, export, validate, config, migrate, status")
        print("Use 'a3 planning --help' for more information")
        sys.exit(1)
    
    # Handle planning config command with no action
    if (args.command == 'planning' and hasattr(args, 'planning_action') and 
        args.planning_action == 'config' and not hasattr(args, 'planning_config_action')):
        print("Error: Planning config command requires an action")
        print("Available actions: show, set")
        print("Use 'a3 planning config --help' for more information")
        sys.exit(1)
    
    # Execute command
    args.func(args)


def analyze_project() -> None:
    """Entry point for a3-analyze command."""
    parser = argparse.ArgumentParser(description="Analyze an existing project")
    parser.add_argument('path', help='Project directory path to analyze')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--generate-docs', action='store_true', help='Generate project documentation')
    parser.add_argument('--dependency-graph', action='store_true', help='Create dependency graph')
    parser.add_argument('--code-patterns', action='store_true', help='Analyze code patterns')
    parser.add_argument('--database', type=str,
                      help='PostgreSQL connection string for database analysis')
    parser.add_argument('--analyze-data-sources', action='store_true',
                      help='Analyze data files (CSV, JSON, XML, Excel) in project directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    analyze_project_command(args)


def debug_project() -> None:
    """Entry point for a3-debug command."""
    parser = argparse.ArgumentParser(description="Debug and test project code")
    parser.add_argument('path', help='Project directory path to debug')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--execute-tests', action='store_true', help='Execute all tests')
    parser.add_argument('--validate-imports', action='store_true', help='Validate all imports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    debug_project_command(args)


if __name__ == '__main__':
    main()