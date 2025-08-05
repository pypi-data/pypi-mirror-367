"""The common module contains common functions and classes used by the other modules."""

import sys
import os
from pathlib import Path
from datetime import datetime


def safe_import_with_fallback(module_names, fallback_path=None):
    """
    Safely import modules with fallback handling for different execution contexts.

    This handles the common pattern throughout autorpt where modules need to be
    imported differently depending on whether running as package or script.

    Args:
        module_names (list): List of module import attempts in order of preference
        fallback_path (str): Optional path to add to sys.path for script execution

    Returns:
        module: The successfully imported module, or None if all failed
    """
    for module_name in module_names:
        try:
            if '.' in module_name:
                # Relative or absolute import
                parts = module_name.split('.')
                if module_name.startswith('.'):
                    # Relative import
                    module = __import__(module_name, fromlist=[
                                        parts[-1]], level=1)
                else:
                    # Absolute import
                    module = __import__(module_name, fromlist=[parts[-1]])
            else:
                # Simple import
                module = __import__(module_name)
            return module
        except ImportError:
            continue

    # Try fallback with path modification
    if fallback_path:
        current_dir = Path(fallback_path).parent if fallback_path != Path(
            __file__).parent else Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        for module_name in module_names:
            try:
                if '.' not in module_name:
                    module = __import__(module_name)
                    return module
            except ImportError:
                continue

    return None


def get_unique_filename(base_filepath, max_attempts=100):
    """
    Ensure unique filename by adding increment if file exists.

    Used throughout autorpt to avoid overwriting existing files.

    Args:
        base_filepath (Path): Base file path
        max_attempts (int): Maximum number of attempts before using timestamp

    Returns:
        Path: Unique file path
    """
    if isinstance(base_filepath, str):
        base_filepath = Path(base_filepath)

    if not base_filepath.exists():
        return base_filepath

    # If file exists, add increment: project_report_2025-01-25_v2.docx
    name_stem = base_filepath.stem
    extension = base_filepath.suffix
    parent_dir = base_filepath.parent

    counter = 2
    while counter <= max_attempts:
        new_filename = f"{name_stem}_v{counter}{extension}"
        new_filepath = parent_dir / new_filename
        if not new_filepath.exists():
            return new_filepath
        counter += 1

    # Use timestamp as fallback
    timestamp = datetime.now().strftime("%H%M%S")
    return parent_dir / f"{name_stem}_{timestamp}{extension}"


def print_results_summary(results, operation_name="Operation"):
    """
    Print a standardized summary of operation results.

    Used throughout autorpt for consistent result reporting.

    Args:
        results (dict): Results dictionary with success/failed/errors keys
        operation_name (str): Name of the operation for display
    """
    print(f"\n📊 {operation_name} Summary:")
    print(f"   ✅ Successful: {results.get('success', 0)}")
    print(f"   ❌ Failed: {results.get('failed', 0)}")

    if results.get('discovered'):
        print(f"   🔍 Discovered: {results['discovered']}")

    if results.get('errors'):
        print("   📝 Errors:")
        for error in results['errors']:
            print(f"      - {error}")


def ensure_reports_directory(reports_dir="reports"):
    """
    Ensure the reports directory exists, create if necessary.

    Args:
        reports_dir (str): Directory path to create

    Returns:
        Path: Path object for the reports directory
    """
    reports_path = Path(reports_dir)
    reports_path.mkdir(exist_ok=True)
    return reports_path


def generate_timestamped_filename(base_name, extension=".docx", include_time=False):
    """
    Generate a filename with timestamp.

    Args:
        base_name (str): Base name for the file
        extension (str): File extension (default: .docx)
        include_time (bool): Whether to include time in timestamp

    Returns:
        str: Timestamped filename
    """
    if include_time:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d")

    return f"{base_name}_{timestamp}{extension}"


def validate_file_exists(filepath, description="File"):
    """
    Validate that a file exists and print appropriate message.

    Args:
        filepath (str): Path to check
        description (str): Description for error message

    Returns:
        bool: True if file exists, False otherwise
    """
    if not os.path.exists(filepath):
        print(f"❌ {description} not found: {filepath}")
        return False
    return True


def print_operation_start(operation_description):
    """Print a standardized operation start message."""
    print(f"🚀 {operation_description}...")


def print_success(message):
    """Print a standardized success message."""
    print(f"✅ {message}")


def print_error(message):
    """Print a standardized error message."""
    print(f"❌ {message}")


def print_warning(message):
    """Print a standardized warning message."""
    print(f"⚠️  {message}")


def print_info(message):
    """Print a standardized info message."""
    print(f"ℹ️  {message}")


def get_file_list_by_pattern(directory, patterns, recursive=True):
    """
    Get list of files matching patterns in directory.

    Args:
        directory (str): Directory to search
        patterns (list): List of glob patterns to match
        recursive (bool): Whether to search recursively

    Returns:
        list: List of matching file paths
    """
    directory = Path(directory)
    if not directory.exists():
        return []

    files = []
    for pattern in patterns:
        if recursive:
            files.extend(directory.rglob(pattern))
        else:
            files.extend(directory.glob(pattern))

    return sorted(list(set(files)))  # Remove duplicates and sort
