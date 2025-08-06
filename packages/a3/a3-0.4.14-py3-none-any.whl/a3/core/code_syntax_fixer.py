"""
Code syntax fixer for A3 generated Python files.

This module provides utilities to fix common syntax errors in generated Python code,
particularly import statement placement and indentation issues.
"""

from pathlib import Path
import re

from typing import List, Dict, Tuple, Optional
import ast
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
            
            # First check if the file already has valid syntax
            try:
                ast.parse(content)
                logger.info(f"File {file_path} already has valid syntax, skipping")
                return True
            except SyntaxError as original_error:
                logger.info(f"File {file_path} has syntax errors, attempting to fix: {original_error}")
            
            # Apply fixes only if there are syntax errors
            fixed_content = self._fix_import_placement(content)
            fixed_content = self._fix_indentation_issues(fixed_content)
            fixed_content = self._fix_incomplete_blocks(fixed_content)
            fixed_content = self._fix_invalid_syntax(fixed_content)
            fixed_content = self._remove_duplicate_imports(fixed_content)
            
            # Validate the fixed content
            try:
                ast.parse(fixed_content)
            except SyntaxError as e:
                # Try one more round of fixes for specific syntax errors
                if "expected an indented block" in str(e):
                    fixed_content = self._fix_missing_indented_blocks(fixed_content, e)
                    try:
                        ast.parse(fixed_content)
                    except SyntaxError as e2:
                        logger.error(f"Failed to fix syntax errors in {file_path}: {e2}")
                        self.errors.append(f"Could not fix {file_path}: {e2}")
                        return False
                else:
                    logger.error(f"Failed to fix syntax errors in {file_path}: {e}")
                    self.errors.append(f"Could not fix {file_path}: {e}")
                    return False
            
            # Only write back if content actually changed and is now valid
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info(f"Successfully fixed syntax errors in {file_path}")
            else:
                logger.info(f"No changes needed for {file_path}")
            
            self.fixed_files.append(file_path)
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
        """Fix misplaced import statements by moving them to the top and making them more robust."""
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
                    # Convert to top-level import and make it more robust
                    import_line = self._make_import_robust(line.strip())
                    if import_line not in [imp.strip() for imp in imports]:
                        imports.append(import_line)
                else:
                    non_imports.append(line)
            else:
                # Top-level imports
                if stripped.startswith('from ') or stripped.startswith('import '):
                    robust_import = self._make_import_robust(line.strip())
                    if robust_import not in imports:
                        imports.append(robust_import)
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
                elif any(lib in imp_stripped for lib in ['os', 'sys', 'json', 're', 'datetime', 'pathlib', 'time', 'logging']):
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
    
    def _make_import_robust(self, import_line: str) -> str:
        """Make an import statement more robust by converting wildcard imports to specific imports."""
        # Convert wildcard imports to specific imports to avoid conflicts
        if ' import *' in import_line:
            # This is a basic conversion - in practice, you'd need to analyze what's actually used
            import_line = import_line.replace(' import *', ' import *  # TODO: Replace with specific imports')
        return import_line
    
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
                continue
            
            # Fix lines that are over-indented (common AI generation issue)
            if line.strip() and i > 0:
                prev_line = lines[i-1] if i > 0 else ""
                
                # If previous line doesn't end with : and current line is indented more than expected
                if (not prev_line.strip().endswith(':') and 
                    not prev_line.strip().endswith('\\') and
                    line.startswith('        ') and  # 8+ spaces
                    not line.strip().startswith('#')):  # Not a comment
                    
                    # Reduce indentation by 4 spaces
                    fixed_line = line[4:] if len(line) >= 4 else line
                    fixed_lines.append(fixed_line)
                    continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_blocks(self, content: str) -> str:
        """Fix incomplete code blocks (if, for, while, try, etc.) by adding missing content."""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check for blocks that require indented content
            if (stripped.endswith(':') and 
                (stripped.startswith('if ') or stripped.startswith('elif ') or 
                 stripped.startswith('else:') or stripped.startswith('for ') or 
                 stripped.startswith('while ') or stripped.startswith('try:') or
                 stripped.startswith('def ') or stripped.startswith('class ') or
                 stripped.startswith('with ') or stripped.startswith('except') or
                 stripped.startswith('finally:'))):
                
                fixed_lines.append(line)
                block_indent = len(line) - len(line.lstrip())
                i += 1
                
                # Check if there's properly indented content following
                has_content = False
                
                # Look ahead to see if there's indented content
                j = i
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    
                    # Skip empty lines
                    if not next_stripped:
                        j += 1
                        continue
                    
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # If we find properly indented content, we're good
                    if next_indent > block_indent:
                        has_content = True
                        break
                    
                    # If we find content at same or lower level, block is incomplete
                    elif next_indent <= block_indent:
                        break
                    
                    j += 1
                
                # If no indented content found, add appropriate content
                if not has_content:
                    if stripped.startswith('try:'):
                        # For try blocks, add except
                        fixed_lines.append(' ' * (block_indent + 4) + 'pass')
                        fixed_lines.append(' ' * block_indent + 'except Exception as e:')
                        fixed_lines.append(' ' * (block_indent + 4) + 'pass')
                    elif stripped.startswith('except') or stripped.startswith('finally:'):
                        # For except/finally blocks, just add pass
                        fixed_lines.append(' ' * (block_indent + 4) + 'pass')
                    elif (stripped.startswith('if ') or stripped.startswith('elif ') or 
                          stripped.startswith('else:') or stripped.startswith('for ') or 
                          stripped.startswith('while ') or stripped.startswith('with ')):
                        # For control flow blocks, add pass
                        fixed_lines.append(' ' * (block_indent + 4) + 'pass')
                    elif stripped.startswith('def ') or stripped.startswith('class '):
                        # For function/class definitions, add pass
                        fixed_lines.append(' ' * (block_indent + 4) + 'pass')
                    else:
                        # Generic case, add pass
                        fixed_lines.append(' ' * (block_indent + 4) + 'pass')
                
                # Continue processing from where we left off
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_invalid_syntax(self, content: str) -> str:
        """Fix common invalid syntax issues."""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue
            
            # Fix common syntax issues
            fixed_line = line
            
            # Fix missing colons after control statements
            if (re.match(r'^\s*(if|elif|else|for|while|try|except|finally|def|class|with)\s+.*[^:]$', line) and
                not stripped.endswith(':') and 
                not stripped.endswith('\\') and
                not stripped.startswith('#')):
                
                # Check if this looks like it should end with a colon
                if (stripped.startswith('if ') or stripped.startswith('elif ') or 
                    stripped.startswith('for ') or stripped.startswith('while ') or
                    stripped.startswith('with ') or stripped == 'else' or
                    stripped == 'try' or stripped.startswith('except') or
                    stripped == 'finally' or stripped.startswith('def ') or
                    stripped.startswith('class ')):
                    fixed_line = line + ':'
            
            # Fix malformed function definitions
            if stripped.startswith('def ') and '(' in stripped and ')' in stripped:
                # Ensure proper function definition format
                if not re.match(r'^\s*def\s+\w+\s*\([^)]*\)\s*(->\s*[^:]+)?\s*:\s*$', line):
                    # Try to fix common issues
                    if not stripped.endswith(':'):
                        fixed_line = line + ':'
            
            # Fix incomplete string literals (basic attempt)
            quote_count_single = stripped.count("'")
            quote_count_double = stripped.count('"')
            quote_count_triple_single = stripped.count("'''")
            quote_count_triple_double = stripped.count('"""')
            
            # If we have unmatched quotes, try to close them
            if (quote_count_single % 2 == 1 and quote_count_triple_single == 0 and 
                not stripped.endswith("'") and "'" in stripped):
                fixed_line = line + "'"
            elif (quote_count_double % 2 == 1 and quote_count_triple_double == 0 and 
                  not stripped.endswith('"') and '"' in stripped):
                fixed_line = line + '"'
            
            fixed_lines.append(fixed_line)
        
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
    
    def _fix_missing_indented_blocks(self, content: str, syntax_error: SyntaxError) -> str:
        """Fix missing indented blocks based on specific syntax error information."""
        lines = content.split('\n')
        
        # Get the line number from the syntax error (1-based)
        error_line_num = syntax_error.lineno - 1 if syntax_error.lineno else 0
        
        # Ensure we don't go out of bounds
        if error_line_num >= len(lines) or error_line_num < 0:
            return content
        
        # Find the line that needs an indented block
        target_line_num = error_line_num
        
        # Look backwards to find the line ending with ':'
        while target_line_num >= 0:
            line = lines[target_line_num]
            if line.strip().endswith(':'):
                break
            target_line_num -= 1
        
        if target_line_num < 0:
            return content
        
        # Get the indentation level of the line with ':'
        colon_line = lines[target_line_num]
        base_indent = len(colon_line) - len(colon_line.lstrip())
        required_indent = base_indent + 4
        
        # Insert a 'pass' statement after the colon line
        fixed_lines = lines[:target_line_num + 1]
        fixed_lines.append(' ' * required_indent + 'pass')
        fixed_lines.extend(lines[target_line_num + 1:])
        
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