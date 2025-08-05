"""
Code syntax fixer for A3 generated Python files.

This module provides utilities to fix common syntax errors in generated Python code,
particularly import statement placement and indentation issues.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CodeSyntaxFixer:
    """Fixes common syntax errors in generated Python code."""
    
    def __init__(self):
        """Initialize the code syntax fixer."""
        self.fixed_files = []
        self.errors = []
    
    def fix_file(self, file_path: str) -> bool:
        """
        Fix syntax errors in a single Python file.
        
        Args:
            file_path: Path to the Python file to fix
            
        Returns:
            True if file was fixed successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply fixes
            fixed_content = self._fix_import_placement(content)
            fixed_content = self._fix_indentation_issues(fixed_content)
            fixed_content = self._fix_incomplete_try_blocks(fixed_content)
            fixed_content = self._remove_duplicate_imports(fixed_content)
            
            # Validate the fixed content
            try:
                ast.parse(fixed_content)
            except SyntaxError as e:
                logger.error(f"Failed to fix syntax errors in {file_path}: {e}")
                self.errors.append(f"Could not fix {file_path}: {e}")
                return False
            
            # Write the fixed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            self.fixed_files.append(file_path)
            logger.info(f"Successfully fixed syntax errors in {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error fixing file {file_path}: {e}")
            self.errors.append(f"Error fixing {file_path}: {e}")
            return False
    
    def fix_directory(self, directory_path: str) -> Dict[str, bool]:
        """
        Fix syntax errors in all Python files in a directory.
        
        Args:
            directory_path: Path to directory containing Python files
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        directory = Path(directory_path)
        
        for py_file in directory.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue  # Skip __init__.py files
            
            success = self.fix_file(str(py_file))
            results[str(py_file)] = success
        
        return results
    
    def _fix_import_placement(self, content: str) -> str:
        """Fix misplaced import statements by moving them to the top."""
        lines = content.split('\n')
        
        # Extract imports and non-import lines
        imports = []
        non_imports = []
        docstring_lines = []
        in_function = False
        function_indent = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Handle module docstring at the beginning
            if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
                quote = '"""' if stripped.startswith('"""') else "'''"
                docstring_lines.append(line)
                i += 1
                
                # Multi-line docstring
                if not (stripped.endswith(quote) and len(stripped) > 3):
                    while i < len(lines):
                        docstring_lines.append(lines[i])
                        if lines[i].strip().endswith(quote):
                            break
                        i += 1
                i += 1
                continue
            
            # Check if we're entering a function
            if stripped.startswith('def ') or stripped.startswith('class '):
                in_function = True
                function_indent = len(line) - len(line.lstrip())
                non_imports.append(line)
            elif in_function:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else function_indent + 4
                
                # Check if we're still inside the function
                if line.strip() and current_indent <= function_indent:
                    in_function = False
                
                # Extract misplaced imports from inside functions
                if (stripped.startswith('from ') or stripped.startswith('import ')) and in_function:
                    # Convert to top-level import
                    import_line = line.strip()
                    if import_line not in [imp.strip() for imp in imports]:
                        imports.append(import_line)
                else:
                    non_imports.append(line)
            else:
                # Top-level imports
                if stripped.startswith('from ') or stripped.startswith('import '):
                    if line not in imports:
                        imports.append(line)
                else:
                    non_imports.append(line)
            
            i += 1
        
        # Reconstruct the file with proper import placement
        result_lines = []
        
        # Add docstring first
        result_lines.extend(docstring_lines)
        
        # Add empty line after docstring if it exists
        if docstring_lines:
            result_lines.append('')
        
        # Add imports
        if imports:
            # Sort imports: standard library, third-party, local
            std_imports = []
            third_party_imports = []
            local_imports = []
            
            for imp in imports:
                imp_stripped = imp.strip()
                if imp_stripped.startswith('from .') or imp_stripped.startswith('from ..'):
                    local_imports.append(imp_stripped)
                elif any(lib in imp_stripped for lib in ['os', 'sys', 'json', 're', 'datetime', 'pathlib']):
                    std_imports.append(imp_stripped)
                else:
                    third_party_imports.append(imp_stripped)
            
            # Add imports in order with spacing
            for group in [std_imports, third_party_imports, local_imports]:
                if group:
                    result_lines.extend(sorted(set(group)))
                    result_lines.append('')
        
        # Add the rest of the code
        result_lines.extend(non_imports)
        
        return '\n'.join(result_lines)
    
    def _fix_indentation_issues(self, content: str) -> str:
        """Fix common indentation issues."""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                fixed_lines.append(line)
                continue
            
            # Check for unexpected indentation at the start of functions
            if line.strip().startswith('def ') and line.startswith('    '):
                # This might be a misplaced function definition
                fixed_lines.append(line.lstrip())
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_try_blocks(self, content: str) -> str:
        """Fix incomplete try blocks by adding missing except/finally."""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check for try block
            if stripped.startswith('try:'):
                fixed_lines.append(line)
                try_indent = len(line) - len(line.lstrip())
                i += 1
                
                # Look for the corresponding except/finally
                found_except_or_finally = False
                
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()
                    current_indent = len(current_line) - len(current_line.lstrip()) if current_line.strip() else try_indent + 4
                    
                    # If we find except or finally at the same level, we're good
                    if (current_stripped.startswith('except') or current_stripped.startswith('finally')) and current_indent == try_indent:
                        found_except_or_finally = True
                        fixed_lines.append(current_line)
                        break
                    
                    # If we find a line at the same or lower indentation level that's not except/finally
                    elif current_line.strip() and current_indent <= try_indent and not (current_stripped.startswith('except') or current_stripped.startswith('finally')):
                        # Add a generic except block
                        if not found_except_or_finally:
                            fixed_lines.append(' ' * try_indent + 'except Exception as e:')
                            fixed_lines.append(' ' * (try_indent + 4) + 'pass')
                        fixed_lines.append(current_line)
                        break
                    else:
                        fixed_lines.append(current_line)
                    
                    i += 1
                
                # If we reached the end without finding except/finally
                if not found_except_or_finally and i >= len(lines):
                    fixed_lines.append(' ' * try_indent + 'except Exception as e:')
                    fixed_lines.append(' ' * (try_indent + 4) + 'pass')
            else:
                fixed_lines.append(line)
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _remove_duplicate_imports(self, content: str) -> str:
        """Remove duplicate import statements."""
        lines = content.split('\n')
        seen_imports = set()
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('from ') or stripped.startswith('import '):
                if stripped not in seen_imports:
                    seen_imports.add(stripped)
                    fixed_lines.append(line)
                # Skip duplicate imports
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def get_summary(self) -> Dict[str, List[str]]:
        """Get a summary of the fixing operation."""
        return {
            'fixed_files': self.fixed_files,
            'errors': self.errors
        }


def fix_project_syntax_errors(project_path: str) -> bool:
    """
    Fix syntax errors in all Python files in a project.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        True if all files were fixed successfully, False otherwise
    """
    fixer = CodeSyntaxFixer()
    results = fixer.fix_directory(project_path)
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    logger.info(f"Fixed {success_count}/{total_count} files successfully")
    
    if fixer.errors:
        logger.error("Errors encountered:")
        for error in fixer.errors:
            logger.error(f"  {error}")
    
    return success_count == total_count