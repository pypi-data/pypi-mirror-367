"""
Module for cleaning unused imports from Python files.

This module provides functionality to analyze Python files and remove
unused import statements while preserving the functionality of the code.
"""

import re
import logging

logger = logging.getLogger(__name__)


def get_clean_import(file_path):
    """
    Clean unused imports from a Python file.
    
    Args:
        file_path (str): Path to the Python file to clean.
        
    Returns:
        list: List of lines with unused imports removed.
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        IOError: If there's an error reading the file.
    """
    content = read_file(file_path)
    filtered_content = []
    in_multiline = False
    buffer = []
    
    for line in content:
        stripped = line.strip()

        if in_multiline:
            buffer.append(line)
            if ')' in stripped:
                in_multiline = False
                full_import = "\n".join(buffer)
                cleaned = clean_multiline_import(full_import, content)

                if cleaned:
                    filtered_content.append(cleaned)
                buffer = []    
            continue
        
        if ' as ' in stripped:
            parts = stripped.split(' as ')
            module = _get_next_words(' as ', line, split=False)
            if _is_module_used(module, content):
                filtered_content.append(
                    parts[0].strip() + ' as ' + module
                )
            continue    

        if stripped.startswith('import '):
            modules = _get_next_words('import', line)
            logger.debug(f"Found import modules: {modules}")
            kept = [
                m.strip() for m in modules 
                if _is_module_used(m.strip(), content)
            ]   
            if kept:  
                filtered_content.append('import ' + ', '.join(kept)) 
            continue

        if stripped.startswith('from '):
            if '(' in stripped:
                in_multiline = True
                buffer = [line]
                continue
                
            parts = stripped.split('import')
            if len(parts) < 2:
                continue
                
            module = parts[0].replace("from", '').strip()
            modules = [m.strip() for m in parts[1].split(',')]
            kept = [m for m in modules if _is_module_used(m, content)]
            
            if kept:
                filtered_content.append(
                    f'from {module} import ' + ', '.join(kept)
                )
            continue                             
    
        filtered_content.append(line)
        
    return filtered_content


def clean_multiline_import(import_block, content):
    """
    Clean a multiline import statement by removing unused imports.
    
    Args:
        import_block (str): The complete multiline import block.
        content (list): List of all lines in the file for usage checking.
        
    Returns:
        str: Cleaned import block or empty string if no imports are used.
    """
    lines = import_block.splitlines()
  
    if len(lines) < 3:
        return ''
        
    head = lines[0]
    tail = lines[1:-1]
    end = lines[-1]     
    
    used_imports = []

    for line in tail:
        module = line.strip().rstrip(',')
        if _is_module_used(module, content):
            used_imports.append(f"    {module},")

    if not used_imports:
        return ''
        
    return '\n'.join([head] + used_imports + [end])        


def write_file(file_path, filtered_content):
    """
    Write the filtered content back to the file.
    
    Args:
        file_path (str): Path to the file to write.
        filtered_content (list): List of lines to write.
        
    Raises:
        IOError: If there's an error writing to the file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in filtered_content:
                f.write(line + '\n')
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise


def read_file(file_path):
    """
    Read the content of a Python file.
    
    Args:
        file_path (str): Path to the file to read.
        
    Returns:
        list: List of lines from the file.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        IOError: If there's an error reading the file.
    """
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            content = f.read().splitlines()
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def _get_next_words(word, line, split=True):
    """
    Extract words that come after a specific word in a line.
    
    Args:
        word (str): The word to search for.
        line (str): The line to search in.
        split (bool): Whether to split the result by commas.
        
    Returns:
        list or str: Split words if split=True, otherwise the string.
    """
    start = line.find(word)    
    after_target = line[start + len(word):].strip()
    
    if split:
        return after_target.split(',')
    return after_target if after_target else None


def _is_module_used(module, content):
    """
    Check if a module is used anywhere in the file content.
    
    Args:
        module (str): The module name to check for usage.
        content (list): List of lines to search through.
        
    Returns:
        bool: True if the module is used, False otherwise.
    """
    if not module:
        return False
        
    pattern = r'\b' + re.escape(module) + r'\b'
    in_multiline_import = False
    logger.debug(f"Checking usage of: {module}")

    for line in content:
        stripped = line.strip()

        # Skip multiline import blocks
        if 'import' in stripped and '(' in stripped:
            in_multiline_import = True
            continue

        if in_multiline_import:
            if ')' in stripped:
                in_multiline_import = False
            continue

        # Skip all import lines
        if 'import' in stripped:
            continue

        # Check for module usage
        if re.search(pattern, stripped):
            logger.debug(f"✔ {module} is used in: {line.strip()}")
            return True
            
    logger.debug(f"✘ {module} is NOT used")
    return False