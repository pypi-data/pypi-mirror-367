"""
End-to-end integration tests for the IntegrationEngine import fix.

This module tests the complete integration workflow with real project structures,
including the A3 Testing project that was failing, to verify that generated imports
can be executed without syntax errors.
"""

import pytest
import tempfile
import os
import sys
import subprocess
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict

from a3.engines.integration import IntegrationEngine
from a3.core.models import Module, FunctionSpec, ValidationResult, IntegrationResult
from a3.core.interfaces import DependencyAnalyzerInterface, FileSystemManagerInterface


class TestIntegrationEngineEndToEnd:
    """End-to-end integration tests for the fixed import logic."""
    
    @pytest.fixture
    def mock_dependency_analyzer(self):
        """Create a mock dependency analyzer for testing."""
        analyzer = Mock(spec=DependencyAnalyzerInterface)
        analyzer.get_build_order.return_value = []
        analyzer.detect_circular_dependencies.return_value = []
        analyzer.create_dependency_graph.return_value = Mock()
        analyzer.validate_dependency_graph.return_value = ValidationResult(
            is_valid=True, issues=[], warnings=[]
        )
        return analyzer
    
    @pytest.fixture
    def mock_filesystem_manager(self):
        """Create a mock filesystem manager for testing."""
        manager = Mock(spec=FileSystemManagerInterface)
        manager.file_exists.return_value = True
        manager.read_file.return_value = '"""\nModule docstring\n"""\n\n'
        manager.write_file.return_value = True
        manager.validate_permissions.return_value = True
        return manager
    
    @pytest.fixture
    def a3_testing_project_structure(self):
        """Create a replica of the A3 Testing project structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create the exact structure from A3 Testing project
            src_dir = project_root / "src"
            src_dir.mkdir()
            (src_dir / "__init__.py").write_text("")
            
            # Create analyzer package
            analyzer_dir = src_dir / "analyzer"
            analyzer_dir.mkdir()
            (analyzer_dir / "__init__.py").write_text("")
            (analyzer_dir / "sentiment_analyzer.py").write_text("""
from ..utils.validators import is_valid_article

def analyze_sentiment(text: str) -> float:
    '''Analyze sentiment of text.'''
    if not text:
        return 0.0
    return 0.5
""")
            
            # Create parser package
            parser_dir = src_dir / "parser"
            parser_dir.mkdir()
            (parser_dir / "__init__.py").write_text("")
            (parser_dir / "article_parser.py").write_text("""
from ..utils.validators import is_valid_article

def parse_article_html(html_content: str) -> dict:
    '''Parse article from HTML.'''
    return {
        "title": "Test Article",
        "content": html_content,
        "author": "Test Author",
        "published_date": "2024-01-01"
    }
""")
            
            # Create scraper package
            scraper_dir = src_dir / "scraper"
            scraper_dir.mkdir()
            (scraper_dir / "__init__.py").write_text("")
            (scraper_dir / "news_fetcher.py").write_text("""
from ..utils.logger import setup_logger
from .url_manager import validate_url

def fetch_article_content(url: str) -> str:
    '''Fetch article content from URL.'''
    return "<html><body>Test content</body></html>"
""")
            (scraper_dir / "url_manager.py").write_text("""
from ..utils.validators import is_valid_url

def validate_url(url: str) -> bool:
    '''Validate URL format.'''
    return is_valid_url(url)
""")
            
            # Create storage package
            storage_dir = src_dir / "storage"
            storage_dir.mkdir()
            (storage_dir / "__init__.py").write_text("")
            (storage_dir / "data_store.py").write_text("""
from ..utils.validators import is_valid_article

def save_article(article_data: dict) -> str:
    '''Save article data.'''
    if is_valid_article(article_data):
        return "saved_id"
    return None
""")
            
            # Create utils package
            utils_dir = src_dir / "utils"
            utils_dir.mkdir()
            (utils_dir / "__init__.py").write_text("")
            (utils_dir / "validators.py").write_text("""
def is_valid_article(article_data: dict) -> bool:
    '''Validate article data.'''
    if not isinstance(article_data, dict):
        return False
    required_fields = {'title', 'content', 'author', 'published_date'}
    return required_fields.issubset(article_data.keys())

def is_valid_url(url: str) -> bool:
    '''Validate URL format.'''
    if not isinstance(url, str) or not url:
        return False
    return url.startswith(('http://', 'https://'))
""")
            (utils_dir / "logger.py").write_text("""
import logging

def setup_logger(name: str) -> logging.Logger:
    '''Set up logger.'''
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
""")
            
            # Create project indicators
            (project_root / "setup.py").write_text("from setuptools import setup, find_packages\nsetup(name='test_project')")
            (project_root / ".a3config.json").write_text('{"project_name": "test_project"}')
            
            yield {
                'root': str(project_root),
                'src': str(src_dir),
                'analyzer': str(analyzer_dir / "sentiment_analyzer.py"),
                'parser': str(parser_dir / "article_parser.py"),
                'scraper_fetcher': str(scraper_dir / "news_fetcher.py"),
                'scraper_manager': str(scraper_dir / "url_manager.py"),
                'storage': str(storage_dir / "data_store.py"),
                'validators': str(utils_dir / "validators.py"),
                'logger': str(utils_dir / "logger.py")
            }
    
    def test_a3_testing_project_import_generation(self, mock_dependency_analyzer, mock_filesystem_manager, a3_testing_project_structure):
        """Test import generation with the actual A3 Testing project structure."""
        # Create modules that mirror the A3 Testing project
        modules = [
            Module(
                name="sentiment_analyzer",
                description="Sentiment analysis module",
                file_path=a3_testing_project_structure['analyzer'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="analyze_sentiment", module="sentiment_analyzer", docstring="Analyze text sentiment")
                ]
            ),
            Module(
                name="article_parser",
                description="Article parsing module",
                file_path=a3_testing_project_structure['parser'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="parse_article_html", module="article_parser", docstring="Parse HTML article")
                ]
            ),
            Module(
                name="news_fetcher",
                description="News fetching module",
                file_path=a3_testing_project_structure['scraper_fetcher'],
                dependencies=["logger", "url_manager"],
                functions=[
                    FunctionSpec(name="fetch_article_content", module="news_fetcher", docstring="Fetch article content")
                ]
            ),
            Module(
                name="url_manager",
                description="URL management module",
                file_path=a3_testing_project_structure['scraper_manager'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="validate_url", module="url_manager", docstring="Validate URL")
                ]
            ),
            Module(
                name="data_store",
                description="Data storage module",
                file_path=a3_testing_project_structure['storage'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="save_article", module="data_store", docstring="Save article data")
                ]
            ),
            Module(
                name="validators",
                description="Validation utilities",
                file_path=a3_testing_project_structure['validators'],
                dependencies=[],
                functions=[
                    FunctionSpec(name="is_valid_article", module="validators", docstring="Validate article"),
                    FunctionSpec(name="is_valid_url", module="validators", docstring="Validate URL")
                ]
            ),
            Module(
                name="logger",
                description="Logging utilities",
                file_path=a3_testing_project_structure['logger'],
                dependencies=[],
                functions=[
                    FunctionSpec(name="setup_logger", module="logger", docstring="Setup logger")
                ]
            )
        ]
        
        # Set up dependency analyzer to return proper build order
        mock_dependency_analyzer.get_build_order.return_value = [
            "validators", "logger", "url_manager", "article_parser", 
            "sentiment_analyzer", "data_store", "news_fetcher"
        ]
        
        # Create integration engine
        integration_engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager
        )
        integration_engine.initialize()
        
        # Generate imports
        import_map = integration_engine.generate_imports(modules)
        
        # Verify imports were generated for all modules
        assert len(import_map) == len(modules)
        
        # Verify specific import patterns that were failing before
        # news_fetcher should import from utils.logger and scraper.url_manager
        news_fetcher_imports = import_map.get("news_fetcher", [])
        assert any("utils.logger" in imp for imp in news_fetcher_imports), f"Expected utils.logger import in: {news_fetcher_imports}"
        assert any("url_manager" in imp for imp in news_fetcher_imports), f"Expected url_manager import in: {news_fetcher_imports}"
        
        # article_parser should import from utils.validators
        parser_imports = import_map.get("article_parser", [])
        assert any("utils.validators" in imp for imp in parser_imports), f"Expected utils.validators import in: {parser_imports}"
        
        # Verify no excessive parent directory traversals (the original bug)
        for module_name, imports in import_map.items():
            for import_stmt in imports:
                # Should not have more than 3 dots (which would be ...)
                dot_count = import_stmt.count('.')
                # Count consecutive dots at the start of relative imports
                if import_stmt.strip().startswith("from ."):
                    relative_part = import_stmt.strip().split()[1]  # Get the "from ...." part
                    consecutive_dots = len(relative_part) - len(relative_part.lstrip('.'))
                    assert consecutive_dots <= 3, f"Excessive parent traversal in {module_name}: {import_stmt}"
    
    def test_generated_imports_syntax_validation(self, mock_dependency_analyzer, mock_filesystem_manager, a3_testing_project_structure):
        """Test that generated imports have valid Python syntax."""
        modules = [
            Module(
                name="test_module_a",
                description="Test module A",
                file_path=a3_testing_project_structure['analyzer'],
                dependencies=["test_module_b"],
                functions=[]
            ),
            Module(
                name="test_module_b",
                description="Test module B",
                file_path=a3_testing_project_structure['validators'],
                dependencies=[],
                functions=[]
            )
        ]
        
        mock_dependency_analyzer.get_build_order.return_value = ["test_module_b", "test_module_a"]
        
        integration_engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager
        )
        integration_engine.initialize()
        
        import_map = integration_engine.generate_imports(modules)
        
        # Validate syntax of each generated import
        for module_name, imports in import_map.items():
            for import_stmt in imports:
                if import_stmt.strip() and not import_stmt.strip().startswith('#'):
                    # Try to compile the import statement
                    try:
                        compile(import_stmt, '<string>', 'exec')
                    except SyntaxError as e:
                        pytest.fail(f"Invalid syntax in import for {module_name}: {import_stmt} - {e}")
    
    def test_integration_with_various_project_structures(self, mock_dependency_analyzer, mock_filesystem_manager):
        """Test integration with various project structures to ensure robustness."""
        test_structures = [
            self._create_flat_project_structure,
            self._create_src_layout_project_structure,
            self._create_nested_package_structure,
            self._create_mixed_depth_structure
        ]
        
        for create_structure in test_structures:
            with create_structure() as structure:
                modules = self._create_modules_for_structure(structure)
                
                mock_dependency_analyzer.get_build_order.return_value = [m.name for m in modules]
                
                integration_engine = IntegrationEngine(
                    dependency_analyzer=mock_dependency_analyzer,
                    filesystem_manager=mock_filesystem_manager
                )
                integration_engine.initialize()
                
                # Test import generation
                import_map = integration_engine.generate_imports(modules)
                
                # Verify imports were generated
                assert len(import_map) == len(modules)
                
                # Verify no import has excessive parent directory traversals
                for module_name, imports in import_map.items():
                    for import_stmt in imports:
                        if import_stmt.strip().startswith("from ."):
                            relative_part = import_stmt.strip().split()[1]
                            consecutive_dots = len(relative_part) - len(relative_part.lstrip('.'))
                            assert consecutive_dots <= 5, f"Excessive traversal in {structure['name']}: {import_stmt}"
    
    def test_end_to_end_integration_workflow(self, mock_dependency_analyzer, mock_filesystem_manager, a3_testing_project_structure):
        """Test the complete integration workflow end-to-end."""
        modules = [
            Module(
                name="main_module",
                description="Main application module",
                file_path=a3_testing_project_structure['analyzer'],
                dependencies=["utils_module"],
                functions=[FunctionSpec(name="main", module="main_module", docstring="Main function")]
            ),
            Module(
                name="utils_module",
                description="Utility functions",
                file_path=a3_testing_project_structure['validators'],
                dependencies=[],
                functions=[FunctionSpec(name="helper", module="utils_module", docstring="Helper function")]
            )
        ]
        
        mock_dependency_analyzer.get_build_order.return_value = ["utils_module", "main_module"]
        
        integration_engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager
        )
        integration_engine.initialize()
        
        # Run complete integration
        result = integration_engine.integrate_modules(modules, generate_tests=False)
        
        # Verify integration succeeded
        assert isinstance(result, IntegrationResult)
        # Allow some errors since we're using mock filesystem that doesn't have actual function implementations
        assert len(result.integrated_modules) == len(modules), f"Not all modules integrated: {result.integrated_modules}"
    
    def test_import_validation_with_real_files(self, mock_dependency_analyzer, a3_testing_project_structure):
        """Test import validation using real file system operations."""
        # Use real filesystem manager for this test
        from a3.managers.filesystem import FileSystemManager
        real_filesystem_manager = FileSystemManager(project_path=a3_testing_project_structure['root'])
        
        modules = [
            Module(
                name="validator_module",
                description="Validation module",
                file_path=a3_testing_project_structure['validators'],
                dependencies=[],
                functions=[]
            ),
            Module(
                name="parser_module",
                description="Parser module",
                file_path=a3_testing_project_structure['parser'],
                dependencies=["validator_module"],
                functions=[]
            )
        ]
        
        mock_dependency_analyzer.get_build_order.return_value = ["validator_module", "parser_module"]
        
        integration_engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=real_filesystem_manager
        )
        integration_engine.initialize()
        
        # Generate imports
        import_map = integration_engine.generate_imports(modules)
        
        # Verify imports
        verification_result = integration_engine.verify_integration(modules)
        
        # Should have minimal issues since we're using real files
        assert verification_result.is_valid or len(verification_result.issues) <= 2, f"Too many validation issues: {verification_result.issues}"
    
    def test_circular_dependency_detection(self, mock_dependency_analyzer, mock_filesystem_manager, a3_testing_project_structure):
        """Test that circular dependencies are properly detected and handled."""
        # Create modules with circular dependencies
        modules = [
            Module(
                name="module_a",
                description="Module A",
                file_path=a3_testing_project_structure['analyzer'],
                dependencies=["module_b"],
                functions=[]
            ),
            Module(
                name="module_b",
                description="Module B",
                file_path=a3_testing_project_structure['parser'],
                dependencies=["module_a"],  # Circular dependency
                functions=[]
            )
        ]
        
        # Mock circular dependency detection
        mock_dependency_analyzer.detect_circular_dependencies.return_value = [["module_a", "module_b", "module_a"]]
        mock_dependency_analyzer.get_build_order.return_value = ["module_a", "module_b"]
        
        integration_engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager
        )
        integration_engine.initialize()
        
        # Verify integration detects the circular dependency
        verification_result = integration_engine.verify_integration(modules)
        
        # Should detect circular import
        assert not verification_result.is_valid
        assert any("circular" in issue.lower() for issue in verification_result.issues)
    
    def test_error_recovery_and_graceful_degradation(self, mock_dependency_analyzer, mock_filesystem_manager, a3_testing_project_structure):
        """Test that the integration engine recovers gracefully from errors."""
        modules = [
            Module(
                name="good_module",
                description="Working module",
                file_path=a3_testing_project_structure['validators'],
                dependencies=[],
                functions=[]
            ),
            Module(
                name="problematic_module",
                description="Module with issues",
                file_path="/nonexistent/path.py",  # Invalid path
                dependencies=["good_module"],
                functions=[]
            )
        ]
        
        mock_dependency_analyzer.get_build_order.return_value = ["good_module", "problematic_module"]
        
        integration_engine = IntegrationEngine(
            dependency_analyzer=mock_dependency_analyzer,
            filesystem_manager=mock_filesystem_manager
        )
        integration_engine.initialize()
        
        # Should not crash despite problematic module
        result = integration_engine.integrate_modules(modules)
        
        # Should have processed the good module even if the problematic one failed
        assert isinstance(result, IntegrationResult)
        assert "good_module" in result.integrated_modules or len(result.import_errors) > 0
    
    # Helper methods for creating test structures
    
    def _create_flat_project_structure(self):
        """Create a flat project structure for testing."""
        return tempfile.TemporaryDirectory()
    
    def _create_src_layout_project_structure(self):
        """Create a src/ layout project structure."""
        temp_dir = tempfile.TemporaryDirectory()
        project_root = Path(temp_dir.name)
        
        (project_root / "setup.py").touch()
        src_dir = project_root / "src"
        src_dir.mkdir()
        (src_dir / "module_a.py").touch()
        (src_dir / "module_b.py").touch()
        
        return temp_dir
    
    def _create_nested_package_structure(self):
        """Create a nested package structure."""
        temp_dir = tempfile.TemporaryDirectory()
        project_root = Path(temp_dir.name)
        
        (project_root / "setup.py").touch()
        package_dir = project_root / "mypackage"
        package_dir.mkdir()
        (package_dir / "__init__.py").touch()
        
        subpackage_dir = package_dir / "subpackage"
        subpackage_dir.mkdir()
        (subpackage_dir / "__init__.py").touch()
        (subpackage_dir / "module.py").touch()
        
        return temp_dir
    
    def _create_mixed_depth_structure(self):
        """Create a mixed depth project structure."""
        temp_dir = tempfile.TemporaryDirectory()
        project_root = Path(temp_dir.name)
        
        (project_root / "setup.py").touch()
        (project_root / "root_module.py").touch()
        
        utils_dir = project_root / "utils"
        utils_dir.mkdir()
        (utils_dir / "helpers.py").touch()
        
        deep_dir = project_root / "deep" / "nested" / "package"
        deep_dir.mkdir(parents=True)
        (deep_dir / "module.py").touch()
        
        return temp_dir
    
    def _create_modules_for_structure(self, structure):
        """Create test modules for a given structure."""
        # This is a simplified version - in practice you'd analyze the structure
        structure_path = structure if isinstance(structure, str) else structure.name
        return [
            Module(
                name="test_module",
                description="Test module",
                file_path=str(Path(structure_path) / "test_module.py"),
                dependencies=[],
                functions=[]
            )
        ]


class TestRealWorldScenarios:
    """Test real-world scenarios that were causing issues."""
    
    def test_a3_testing_original_failure_case(self):
        """Test the specific case that was failing in A3 Testing project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Recreate the exact failing scenario
            src_dir = project_root / "src"
            src_dir.mkdir()
            (src_dir / "__init__.py").touch()
            
            # Create the problematic structure
            scraper_dir = src_dir / "scraper"
            scraper_dir.mkdir()
            (scraper_dir / "__init__.py").touch()
            news_fetcher_file = scraper_dir / "news_fetcher.py"
            news_fetcher_file.touch()
            
            utils_dir = src_dir / "utils"
            utils_dir.mkdir()
            (utils_dir / "__init__.py").touch()
            validators_file = utils_dir / "validators.py"
            validators_file.touch()
            
            # Create project indicator
            (project_root / ".a3config.json").touch()
            
            # Test the specific import that was failing
            integration_engine = IntegrationEngine()
            
            result = integration_engine._calculate_relative_import_path(
                str(news_fetcher_file),
                str(validators_file),
                str(project_root)
            )
            
            # Should generate correct relative import, not excessive dots
            assert result is not None
            assert result == "from ..utils.validators import *"
            
            # Verify it doesn't generate the problematic "from ...utils.validators import *"
            assert not result.startswith("from ...utils")
    
    def test_import_execution_validation(self):
        """Test that generated imports can actually be executed without syntax errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create a realistic project structure
            src_dir = project_root / "src"
            src_dir.mkdir()
            (src_dir / "__init__.py").write_text("")
            
            # Create modules with actual content
            utils_dir = src_dir / "utils"
            utils_dir.mkdir()
            (utils_dir / "__init__.py").write_text("")
            (utils_dir / "helpers.py").write_text("""
def helper_function():
    return "helper"
""")
            
            main_dir = src_dir / "main"
            main_dir.mkdir()
            (main_dir / "__init__.py").write_text("")
            main_module = main_dir / "app.py"
            
            # Generate the import statement
            integration_engine = IntegrationEngine()
            import_stmt = integration_engine._calculate_relative_import_path(
                str(main_module),
                str(utils_dir / "helpers.py"),
                str(project_root)
            )
            
            # Write a test module with the generated import
            main_module.write_text(f"""
{import_stmt}

def main():
    return helper_function()
""")
            
            # Try to validate the syntax by compiling
            try:
                with open(main_module, 'r') as f:
                    content = f.read()
                compile(content, str(main_module), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Generated import caused syntax error: {e}")
    
    def test_performance_with_large_project_structure(self):
        """Test performance with a large project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "setup.py").touch()
            
            # Create a large project structure
            for i in range(10):  # 10 packages
                package_dir = project_root / f"package_{i}"
                package_dir.mkdir()
                (package_dir / "__init__.py").touch()
                
                for j in range(5):  # 5 modules per package
                    (package_dir / f"module_{j}.py").touch()
            
            # Test import calculation performance
            integration_engine = IntegrationEngine()
            
            import time
            start_time = time.time()
            
            # Test multiple import calculations
            for i in range(10):
                for j in range(5):
                    from_path = str(project_root / f"package_{i}" / f"module_{j}.py")
                    to_path = str(project_root / f"package_{(i+1)%10}" / f"module_{(j+1)%5}.py")
                    
                    result = integration_engine._calculate_relative_import_path(
                        from_path, to_path, str(project_root)
                    )
                    assert result is not None
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete within reasonable time (less than 5 seconds)
            assert execution_time < 5.0, f"Import calculation took too long: {execution_time}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])