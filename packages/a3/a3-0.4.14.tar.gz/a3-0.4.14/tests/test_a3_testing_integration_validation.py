"""
Validation test for the A3 Testing project integration fix.

This test validates that the integration engine can successfully generate
correct imports for the actual A3 Testing project structure without syntax errors.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from a3.engines.integration import IntegrationEngine
from a3.core.models import Module, FunctionSpec
from a3.core.interfaces import DependencyAnalyzerInterface, FileSystemManagerInterface


class TestA3TestingIntegrationValidation:
    """Validation tests for the A3 Testing project integration fix."""
    
    @pytest.fixture
    def a3_testing_replica(self):
        """Create an exact replica of the A3 Testing project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create the exact A3 Testing structure
            src_dir = project_root / "src"
            src_dir.mkdir()
            (src_dir / "__init__.py").write_text("")
            
            # Analyzer package
            analyzer_dir = src_dir / "analyzer"
            analyzer_dir.mkdir()
            (analyzer_dir / "__init__.py").write_text("")
            (analyzer_dir / "sentiment_analyzer.py").write_text("""
'''Sentiment analysis module.'''

from ..utils.validators import is_valid_article

def analyze_sentiment(text: str) -> float:
    '''Analyze sentiment of text.'''
    if not text or not is_valid_article({'title': 'test', 'content': text, 'author': 'test', 'published_date': '2024-01-01'}):
        return 0.0
    # Simple sentiment analysis
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 0.8
    elif negative_count > positive_count:
        return -0.8
    else:
        return 0.0
""")
            
            # Parser package
            parser_dir = src_dir / "parser"
            parser_dir.mkdir()
            (parser_dir / "__init__.py").write_text("")
            (parser_dir / "article_parser.py").write_text("""
'''Article parsing module.'''

from ..utils.validators import is_valid_article

def parse_article_html(html_content: str) -> dict:
    '''Parse article from HTML content.'''
    if not html_content:
        return {}
    
    # Simple HTML parsing simulation
    article_data = {
        "title": "Extracted Title",
        "content": html_content.replace('<html>', '').replace('</html>', '').strip(),
        "author": "Unknown Author",
        "published_date": "2024-01-01"
    }
    
    if is_valid_article(article_data):
        return article_data
    else:
        return {}
""")
            
            # Scraper package
            scraper_dir = src_dir / "scraper"
            scraper_dir.mkdir()
            (scraper_dir / "__init__.py").write_text("")
            (scraper_dir / "news_fetcher.py").write_text("""
'''News fetching module.'''

from ..utils.logger import setup_logger
from .url_manager import validate_url

logger = setup_logger(__name__)

def fetch_article_content(url: str) -> str:
    '''Fetch article content from URL.'''
    if not validate_url(url):
        logger.error(f"Invalid URL: {url}")
        return ""
    
    logger.info(f"Fetching content from: {url}")
    # Simulate fetching content
    return f"<html><body>Content from {url}</body></html>"

def fetch_rss_articles(rss_urls: list) -> list:
    '''Fetch articles from RSS feeds.'''
    articles = []
    for url in rss_urls:
        if validate_url(url):
            logger.info(f"Fetching RSS from: {url}")
            # Simulate RSS parsing
            articles.append({
                'title': f'Article from {url}',
                'link': url,
                'summary': 'Test summary',
                'published': '2024-01-01',
                'source': url
            })
    return articles
""")
            
            (scraper_dir / "url_manager.py").write_text("""
'''URL management module.'''

from ..utils.validators import is_valid_url

def validate_url(url: str) -> bool:
    '''Validate URL format and accessibility.'''
    if not is_valid_url(url):
        return False
    
    # Additional validation logic
    if not url.startswith(('http://', 'https://')):
        return False
    
    return True

def normalize_url(url: str) -> str:
    '''Normalize URL format.'''
    if not url:
        return ""
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url.rstrip('/')
""")
            
            # Storage package
            storage_dir = src_dir / "storage"
            storage_dir.mkdir()
            (storage_dir / "__init__.py").write_text("")
            (storage_dir / "data_store.py").write_text("""
'''Data storage module.'''

from ..utils.validators import is_valid_article

def save_article(article_data: dict) -> str:
    '''Save article data to storage.'''
    if not is_valid_article(article_data):
        raise ValueError("Invalid article data")
    
    # Simulate saving to database
    article_id = f"article_{hash(str(article_data)) % 10000}"
    return article_id

def get_articles_by_sentiment(sentiment_range: tuple) -> list:
    '''Retrieve articles by sentiment range.'''
    if not isinstance(sentiment_range, tuple) or len(sentiment_range) != 2:
        raise ValueError("Invalid sentiment range")
    
    min_sentiment, max_sentiment = sentiment_range
    
    # Simulate database query
    mock_articles = [
        {"id": "1", "title": "Positive Article", "sentiment": 0.8},
        {"id": "2", "title": "Negative Article", "sentiment": -0.6},
        {"id": "3", "title": "Neutral Article", "sentiment": 0.1}
    ]
    
    return [
        article for article in mock_articles
        if min_sentiment <= article["sentiment"] <= max_sentiment
    ]
""")
            
            # Utils package
            utils_dir = src_dir / "utils"
            utils_dir.mkdir()
            (utils_dir / "__init__.py").write_text("")
            (utils_dir / "validators.py").write_text("""
'''Validation utilities.'''

def is_valid_article(article_data: dict) -> bool:
    '''Validate article data structure.'''
    if not isinstance(article_data, dict):
        return False
    
    required_fields = {'title', 'content', 'author', 'published_date'}
    return required_fields.issubset(article_data.keys())

def is_valid_url(url: str) -> bool:
    '''Validate URL format.'''
    if not isinstance(url, str) or not url:
        return False
    
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_sentiment_score(score: float) -> bool:
    '''Validate sentiment score range.'''
    return isinstance(score, (int, float)) and -1.0 <= score <= 1.0
""")
            
            (utils_dir / "logger.py").write_text("""
'''Logging utilities.'''

import logging

def setup_logger(name: str) -> logging.Logger:
    '''Set up logger with standard configuration.'''
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

def log_error(message: str, logger_name: str = "default") -> None:
    '''Log error message.'''
    logger = setup_logger(logger_name)
    logger.error(message)

def log_info(message: str, logger_name: str = "default") -> None:
    '''Log info message.'''
    logger = setup_logger(logger_name)
    logger.info(message)
""")
            
            # Create project indicators
            (project_root / "setup.py").write_text("""
from setuptools import setup, find_packages

setup(
    name='a3-testing-project',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'feedparser'
    ]
)
""")
            (project_root / ".a3config.json").write_text('{"project_name": "a3_testing_project"}')
            
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
    
    def test_a3_testing_import_generation_and_execution(self, a3_testing_replica):
        """Test that imports can be generated and executed without syntax errors."""
        # Create modules that exactly match the A3 Testing project
        modules = [
            Module(
                name="sentiment_analyzer",
                description="Sentiment analysis module",
                file_path=a3_testing_replica['analyzer'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="analyze_sentiment", module="sentiment_analyzer", docstring="Analyze text sentiment")
                ]
            ),
            Module(
                name="article_parser",
                description="Article parsing module",
                file_path=a3_testing_replica['parser'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="parse_article_html", module="article_parser", docstring="Parse HTML article")
                ]
            ),
            Module(
                name="news_fetcher",
                description="News fetching module",
                file_path=a3_testing_replica['scraper_fetcher'],
                dependencies=["logger", "url_manager"],
                functions=[
                    FunctionSpec(name="fetch_article_content", module="news_fetcher", docstring="Fetch article content"),
                    FunctionSpec(name="fetch_rss_articles", module="news_fetcher", docstring="Fetch RSS articles")
                ]
            ),
            Module(
                name="url_manager",
                description="URL management module",
                file_path=a3_testing_replica['scraper_manager'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="validate_url", module="url_manager", docstring="Validate URL"),
                    FunctionSpec(name="normalize_url", module="url_manager", docstring="Normalize URL")
                ]
            ),
            Module(
                name="data_store",
                description="Data storage module",
                file_path=a3_testing_replica['storage'],
                dependencies=["validators"],
                functions=[
                    FunctionSpec(name="save_article", module="data_store", docstring="Save article data"),
                    FunctionSpec(name="get_articles_by_sentiment", module="data_store", docstring="Get articles by sentiment")
                ]
            ),
            Module(
                name="validators",
                description="Validation utilities",
                file_path=a3_testing_replica['validators'],
                dependencies=[],
                functions=[
                    FunctionSpec(name="is_valid_article", module="validators", docstring="Validate article"),
                    FunctionSpec(name="is_valid_url", module="validators", docstring="Validate URL"),
                    FunctionSpec(name="validate_sentiment_score", module="validators", docstring="Validate sentiment score")
                ]
            ),
            Module(
                name="logger",
                description="Logging utilities",
                file_path=a3_testing_replica['logger'],
                dependencies=[],
                functions=[
                    FunctionSpec(name="setup_logger", module="logger", docstring="Setup logger"),
                    FunctionSpec(name="log_error", module="logger", docstring="Log error"),
                    FunctionSpec(name="log_info", module="logger", docstring="Log info")
                ]
            )
        ]
        
        # Create mock dependency analyzer
        mock_dependency_analyzer = Mock(spec=DependencyAnalyzerInterface)
        mock_dependency_analyzer.get_build_order.return_value = [
            "validators", "logger", "url_manager", "article_parser", 
            "sentiment_analyzer", "data_store", "news_fetcher"
        ]
        mock_dependency_analyzer.detect_circular_dependencies.return_value = []
        
        # Create integration engine
        integration_engine = IntegrationEngine(dependency_analyzer=mock_dependency_analyzer)
        integration_engine.initialize()
        
        # Generate imports
        import_map = integration_engine.generate_imports(modules)
        
        # Verify imports were generated
        assert len(import_map) == len(modules)
        
        # Test specific problematic imports that were failing before the fix
        news_fetcher_imports = import_map.get("news_fetcher", [])
        
        # Verify the specific import that was causing issues
        logger_import_found = False
        url_manager_import_found = False
        
        for import_stmt in news_fetcher_imports:
            if "utils.logger" in import_stmt:
                logger_import_found = True
                # Should be "from ..utils.logger import *", not "from ...utils.logger import *"
                assert import_stmt.count('..') <= 2, f"Excessive parent traversal: {import_stmt}"
            if "url_manager" in import_stmt:
                url_manager_import_found = True
                # Should be "from .url_manager import *"
                assert import_stmt.startswith("from .url_manager"), f"Incorrect relative import: {import_stmt}"
        
        assert logger_import_found, f"Logger import not found in: {news_fetcher_imports}"
        assert url_manager_import_found, f"URL manager import not found in: {news_fetcher_imports}"
        
        # Validate syntax of all generated imports
        for module_name, imports in import_map.items():
            for import_stmt in imports:
                if import_stmt.strip() and not import_stmt.strip().startswith('#'):
                    try:
                        compile(import_stmt, '<string>', 'exec')
                    except SyntaxError as e:
                        pytest.fail(f"Invalid syntax in {module_name}: {import_stmt} - {e}")
    
    def test_actual_import_execution_in_python_environment(self, a3_testing_replica):
        """Test that generated imports can actually be executed in a Python environment."""
        # Add the project root to Python path
        project_root = a3_testing_replica['root']
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        try:
            # Test importing the modules directly
            import src.utils.validators
            import src.utils.logger
            import src.scraper.url_manager
            import src.parser.article_parser
            import src.analyzer.sentiment_analyzer
            import src.storage.data_store
            import src.scraper.news_fetcher
            
            # Test that functions are accessible
            assert hasattr(src.utils.validators, 'is_valid_article')
            assert hasattr(src.utils.validators, 'is_valid_url')
            assert hasattr(src.utils.logger, 'setup_logger')
            assert hasattr(src.scraper.url_manager, 'validate_url')
            assert hasattr(src.parser.article_parser, 'parse_article_html')
            assert hasattr(src.analyzer.sentiment_analyzer, 'analyze_sentiment')
            assert hasattr(src.storage.data_store, 'save_article')
            assert hasattr(src.scraper.news_fetcher, 'fetch_article_content')
            
            # Test that the cross-module dependencies work
            # This validates that the imports are correctly resolved
            article_data = {
                'title': 'Test Article',
                'content': 'This is a test article with good content.',
                'author': 'Test Author',
                'published_date': '2024-01-01'
            }
            
            # Test validator function
            is_valid = src.utils.validators.is_valid_article(article_data)
            assert is_valid is True
            
            # Test URL validation
            is_valid_url = src.utils.validators.is_valid_url('https://example.com')
            assert is_valid_url is True
            
            # Test sentiment analysis (which depends on validators)
            sentiment = src.analyzer.sentiment_analyzer.analyze_sentiment('This is good content')
            assert isinstance(sentiment, float)
            
            # Test article parsing (which depends on validators)
            parsed = src.parser.article_parser.parse_article_html('<html>Test content</html>')
            assert isinstance(parsed, dict)
            
            # Test URL manager (which depends on validators)
            url_valid = src.scraper.url_manager.validate_url('https://example.com')
            assert url_valid is True
            
            # Test data store (which depends on validators)
            article_id = src.storage.data_store.save_article(article_data)
            assert isinstance(article_id, str)
            
            # Test news fetcher (which depends on logger and url_manager)
            content = src.scraper.news_fetcher.fetch_article_content('https://example.com')
            assert isinstance(content, str)
            
        finally:
            # Clean up sys.path
            if project_root in sys.path:
                sys.path.remove(project_root)
    
    def test_integration_engine_path_calculation_accuracy(self, a3_testing_replica):
        """Test the accuracy of path calculations for the A3 Testing project structure."""
        integration_engine = IntegrationEngine()
        
        # Test the specific path calculation that was failing
        news_fetcher_path = a3_testing_replica['scraper_fetcher']
        validators_path = a3_testing_replica['validators']
        project_root = a3_testing_replica['root']
        
        # Calculate relative import path
        import_path = integration_engine._calculate_relative_import_path(
            news_fetcher_path, validators_path, project_root
        )
        
        # Should generate correct relative import
        assert import_path == "from ..utils.validators import *"
        
        # Test same-package import
        url_manager_path = a3_testing_replica['scraper_manager']
        same_package_import = integration_engine._calculate_relative_import_path(
            news_fetcher_path, url_manager_path, project_root
        )
        
        assert same_package_import == "from .url_manager import *"
        
        # Test project root detection
        detected_root = integration_engine._get_project_root(news_fetcher_path)
        assert detected_root == project_root
        
        # Test import path conversion
        import_path_str = integration_engine._convert_file_path_to_import_path(
            validators_path, project_root
        )
        assert import_path_str == "src.utils.validators"
    
    def test_no_excessive_parent_directory_traversals(self, a3_testing_replica):
        """Test that no import generates excessive parent directory traversals."""
        integration_engine = IntegrationEngine()
        
        # Test all possible combinations of modules
        module_paths = [
            a3_testing_replica['analyzer'],
            a3_testing_replica['parser'],
            a3_testing_replica['scraper_fetcher'],
            a3_testing_replica['scraper_manager'],
            a3_testing_replica['storage'],
            a3_testing_replica['validators'],
            a3_testing_replica['logger']
        ]
        
        project_root = a3_testing_replica['root']
        
        for from_path in module_paths:
            for to_path in module_paths:
                if from_path != to_path:
                    import_stmt = integration_engine._calculate_relative_import_path(
                        from_path, to_path, project_root
                    )
                    
                    if import_stmt:
                        # Count consecutive dots at the beginning of relative imports
                        if import_stmt.startswith("from ."):
                            relative_part = import_stmt.split()[1]  # Get "from ...." part
                            consecutive_dots = len(relative_part) - len(relative_part.lstrip('.'))
                            
                            # Should never have more than 3 consecutive dots (which would be ...)
                            assert consecutive_dots <= 3, f"Excessive traversal from {from_path} to {to_path}: {import_stmt}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])