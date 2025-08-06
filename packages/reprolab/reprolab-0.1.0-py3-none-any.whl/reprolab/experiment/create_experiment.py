import subprocess
import re
from typing import List
import glob
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def save_notebooks():
    """
    Save all Jupyter notebooks in the current directory.
    This triggers the actual Jupyter save action to ensure outputs are persisted.
    Uses multiple methods to ensure outputs are captured.
    """
    logger.info("Attempting to save all Jupyter notebooks...")
    
    # Method 1: Try using ipylab to save current notebook
    try:
        from ipylab import JupyterFrontEnd
        
        logger.debug("Method 1: Using ipylab to save current notebook")
        app = JupyterFrontEnd()
        logger.debug("Executing save command: docmanager:save")
        app.commands.execute('docmanager:save')
        
        # Give a moment for the save to complete
        logger.debug("Waiting 0.5 seconds for save to complete")
        time.sleep(0.5)
        logger.info("ipylab save command executed successfully")
            
    except ImportError:
        logger.warning("ipylab not available. Install with: pip install ipylab")
    except Exception as e:
        logger.warning(f"Error using ipylab save: {e}")
    
    # Method 2: Try using nbformat to save all notebooks
    try:
        import nbformat
        import glob
        
        logger.debug("Method 2: Using nbformat to save all notebooks")
        notebook_files = glob.glob('*.ipynb')
        
        for notebook_file in notebook_files:
            logger.debug(f"Processing notebook: {notebook_file}")
            try:
                # Read the notebook
                with open(notebook_file, 'r', encoding='utf-8') as f:
                    nb = nbformat.read(f, as_version=4)
                
                # Write it back (this can help normalize the format and ensure outputs are saved)
                with open(notebook_file, 'w', encoding='utf-8') as f:
                    nbformat.write(nb, f)
                
                logger.debug(f"Successfully processed notebook: {notebook_file}")
                
            except Exception as e:
                logger.warning(f"Error processing notebook {notebook_file}: {e}")
        
        logger.info(f"nbformat processing completed for {len(notebook_files)} notebooks")
        
    except ImportError:
        logger.warning("nbformat not available. Install with: pip install nbformat")
    except Exception as e:
        logger.warning(f"Error using nbformat save: {e}")
    
    # Method 3: Force save using Jupyter's save_all command if available
    try:
        from ipylab import JupyterFrontEnd
        
        logger.debug("Method 3: Trying to save all documents")
        app = JupyterFrontEnd()
        
        # Try to save all documents
        try:
            app.commands.execute('docmanager:save-all')
            logger.debug("Executed save-all command")
        except:
            # If save-all doesn't work, try saving each document individually
            logger.debug("save-all not available, trying individual saves")
            try:
                # Get all open documents and save them
                for doc_id in app.shell.widget_manager.get_document_ids():
                    app.commands.execute('docmanager:save', {'id': doc_id})
                    logger.debug(f"Saved document: {doc_id}")
            except Exception as e:
                logger.debug(f"Error saving individual documents: {e}")
        
        # Give a moment for saves to complete
        time.sleep(0.5)
        logger.info("Jupyter save commands executed successfully")
            
    except Exception as e:
        logger.debug(f"Error in Method 3: {e}")
    
    logger.info("All save methods completed")


def get_current_notebook_name():
    """
    Get the name of the current Jupyter notebook.
    
    Returns:
        str: The notebook filename or None if not found
    """
    logger.debug("Searching for notebook files in current directory")
    try:
        import glob
        import os
        
        # Look for .ipynb files in current directory
        notebook_files = glob.glob('*.ipynb')
        logger.debug(f"Found {len(notebook_files)} notebook files: {notebook_files}")
        
        if len(notebook_files) == 1:
            logger.info(f"Single notebook found: {notebook_files[0]}")
            return notebook_files[0]
        elif len(notebook_files) > 1:
            # If multiple notebooks, try to guess based on most recent modification
            logger.info(f"Multiple notebooks found ({len(notebook_files)}), selecting most recent")
            most_recent = max(notebook_files, key=lambda f: os.path.getmtime(f))
            logger.info(f"Selected most recent notebook: {most_recent}")
            return most_recent
        else:
            logger.warning("No notebook files found in current directory")
            return None
            
    except Exception as e:
        logger.error(f"Error getting notebook name: {e}")
        return None


def check_notebook_outputs():
    """
    Debug function to check if notebooks contain outputs.
    This helps diagnose if outputs are being saved properly.
    """
    logger.info("Checking notebook outputs for debugging...")
    try:
        import nbformat
        import glob
        import json
        
        notebook_files = glob.glob('*.ipynb')
        
        for notebook_file in notebook_files:
            logger.info(f"Analyzing notebook: {notebook_file}")
            try:
                with open(notebook_file, 'r', encoding='utf-8') as f:
                    nb = nbformat.read(f, as_version=4)
                
                total_cells = len(nb.cells)
                cells_with_outputs = 0
                cells_with_execution_count = 0
                
                for i, cell in enumerate(nb.cells):
                    if cell.cell_type == 'code':
                        if hasattr(cell, 'outputs') and cell.outputs:
                            cells_with_outputs += 1
                            logger.debug(f"  Cell {i}: Has {len(cell.outputs)} outputs")
                        
                        if hasattr(cell, 'execution_count') and cell.execution_count is not None:
                            cells_with_execution_count += 1
                            logger.debug(f"  Cell {i}: Execution count = {cell.execution_count}")
                
                logger.info(f"  Total cells: {total_cells}")
                logger.info(f"  Cells with outputs: {cells_with_outputs}")
                logger.info(f"  Cells with execution count: {cells_with_execution_count}")
                
                # Check file size to see if it's substantial
                file_size = os.path.getsize(notebook_file)
                logger.info(f"  File size: {file_size} bytes")
                
            except Exception as e:
                logger.error(f"Error analyzing notebook {notebook_file}: {e}")
        
    except ImportError:
        logger.warning("nbformat not available for output checking")
    except Exception as e:
        logger.error(f"Error checking notebook outputs: {e}")


def add_all_files() -> bool:
    """
    Add all files in the repository to git staging area.
    Forces add even if no changes are detected.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Starting process to add all files to git staging area")
    
    try:
        # Check git status for all files
        logger.info("Checking git status for all files")
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                     check=True, capture_output=True, text=True)
        logger.debug(f"Git status output: {status_result.stdout}")
        
        # Count different types of changes
        untracked_files = []
        modified_files = []
        deleted_files = []
        
        for line in status_result.stdout.split('\n'):
            if line.strip():
                status = line[:2].strip()
                filename = line[3:].strip()
                
                if status == '??':  # Untracked file
                    untracked_files.append(filename)
                elif status in ['M ', ' M', 'MM']:  # Modified file
                    modified_files.append(filename)
                elif status == ' D':  # Deleted file
                    deleted_files.append(filename)
        
        logger.info(f"Found {len(untracked_files)} untracked files")
        logger.info(f"Found {len(modified_files)} modified files")
        logger.info(f"Found {len(deleted_files)} deleted files")
        
        if not (untracked_files or modified_files or deleted_files):
            logger.info("No changes detected, but proceeding with add anyway")
        
        # Add all files to staging (indiscriminately)
        logger.info("Adding all files to git staging")
        add_result = subprocess.run(['git', 'add', '.'], 
                                  check=True, capture_output=True, text=True)
        logger.debug(f"Git add output: {add_result.stdout}")
        
        logger.info("Successfully added all files to staging")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error adding files: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return False


def commit_all_files(message: str) -> bool:
    """
    Add all files and create a commit with the given message.
    Forces commit even if no changes are detected.
    
    Args:
        message (str): Commit message
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Starting commit process with message: '{message}'")
    try:
        # Add all files
        logger.info("Adding all files to staging area")
        if not add_all_files():
            logger.warning("Failed to add files")
            return False
        
        # Check if there are staged changes
        logger.info("Checking for staged changes")
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                     check=True, capture_output=True, text=True)
        logger.debug(f"Git status after adding: {status_result.stdout}")
        
        has_staged_changes = False
        staged_files = []
        for line in status_result.stdout.split('\n'):
            if line.strip() and line[:2] in ['A ', 'M ', 'MM']:  # Staged changes
                has_staged_changes = True
                staged_files.append(line[3:].strip())
                logger.debug(f"Found staged change: {line}")
        
        if not has_staged_changes:
            logger.warning("No staged changes detected, but proceeding with commit anyway")
            logger.info("This will create an empty commit if no changes are present")
        else:
            logger.info(f"Staged {len(staged_files)} files for commit")
        
        # Create commit with the message (even if no staged changes)
        logger.info(f"Creating commit with message: '{message}'")
        commit_result = subprocess.run(['git', 'commit', '-m', message], 
                                     check=True, capture_output=True, text=True)
        logger.debug(f"Commit output: {commit_result.stdout}")
        
        logger.info(f"Successfully committed: {message}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating commit: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return False


def add_and_commit_all_files(message: str) -> bool:
    """
    Convenience function that combines adding all files and committing in one step.
    
    Args:
        message (str): Commit message
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Combined add and commit operation with message: '{message}'")
    return commit_all_files(message)


def get_next_tag_name() -> str:
    """
    Determines the next tag name in the format vX.Y.Z by incrementing the middle version number.
    Returns:
        str: The next tag name (e.g., 'v1.3.0')
    """
    logger.info("Determining next tag name")
    existing_tags = get_all_tags()
    logger.debug(f"Existing tags: {existing_tags}")
    
    if not existing_tags:
        logger.info("No existing tags found, using initial tag: v1.0.0")
        return "v1.0.0"
    
    version_pattern = re.compile(r'^v(\d+)\.(\d+)\.(\d+)$')
    version_tags = []
    for tag in existing_tags:
        match = version_pattern.match(tag)
        if match:
            major, minor, patch = map(int, match.groups())
            version_tags.append((major, minor, patch, tag))
            logger.debug(f"Parsed version tag: {tag} -> ({major}, {minor}, {patch})")
    
    if not version_tags:
        logger.info("No valid version tags found, using initial tag: v1.0.0")
        return "v1.0.0"
    
    version_tags.sort()
    latest_major, latest_minor, latest_patch, latest_tag = version_tags[-1]
    new_minor = latest_minor + 1
    new_tag = f"v{latest_major}.{new_minor}.0"
    logger.info(f"Latest tag: {latest_tag}, next tag: {new_tag}")
    return new_tag


def start_experiment() -> str:
    """
    Save all notebooks, then commit them with a message indicating the project state before running an experiment.
    The tag name is automatically determined as the next tag.
    Returns:
        str: The tag name used in the message, or empty string on failure
    """
    logger.info("Starting experiment process")
    # Save all notebooks first
    logger.info("Step 1: Saving all notebooks")
    save_notebooks()
    
    logger.info("Step 2: Determining next tag name")
    next_tag = get_next_tag_name()
    message = f"Project state before running experiment {next_tag}"
    logger.info(f"Step 3: Committing with message: '{message}'")
    
    commit_success = commit_all_files(message)
    if commit_success:
        logger.info(f"Successfully started experiment: {next_tag}")
        return next_tag
    else:
        logger.error("Failed to start experiment")
        return ""


def end_experiment() -> str:
    """
    Save all notebooks, commit them with a message indicating the project state after running an experiment,
    create the next tag, and push the tag to the remote.
    Returns:
        str: The new tag name if successful, empty string otherwise
    """
    logger.info("Ending experiment process")
    # Save all notebooks first
    logger.info("Step 1: Saving all notebooks")
    save_notebooks()
    
    logger.info("Step 2: Determining next tag name")
    next_tag = get_next_tag_name()
    message = f"Project state after running experiment {next_tag}"
    logger.info(f"Step 3: Committing with message: '{message}'")
    
    commit_success = commit_all_files(message)
    if not commit_success:
        logger.error("Failed to end experiment - commit failed")
        return ""
    
    # Now create the tag
    logger.info(f"Step 4: Creating tag: {next_tag}")
    try:
        tag_result = subprocess.run(['git', 'tag', next_tag], 
                                  check=True, capture_output=True, text=True)
        logger.debug(f"Tag creation output: {tag_result.stdout}")
        logger.info(f"Successfully created tag: {next_tag}")
        
        logger.info(f"Step 5: Pushing tag to remote: {next_tag}")
        push_result = subprocess.run(['git', 'push', 'origin', next_tag], 
                                   check=True, capture_output=True, text=True)
        logger.debug(f"Tag push output: {push_result.stdout}")
        logger.info(f"Successfully pushed tag: {next_tag}")
        
        logger.info(f"Successfully ended experiment: {next_tag}")
        return next_tag
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating or pushing tag: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return ""


def get_all_tags() -> List[str]:
    """
    Fetch all tags from remote repositories and return them as a Python list.
    
    Returns:
        List[str]: List of all Git tags
    """
    logger.info("Fetching all tags from remote repositories")
    try:
        # Fetch all tags from all remotes
        logger.debug("Running: git fetch --all --tags")
        fetch_result = subprocess.run(['git', 'fetch', '--all', '--tags'], 
                                    check=True, capture_output=True, text=True)
        logger.debug(f"Fetch output: {fetch_result.stdout}")
        
        # Get all tags
        logger.debug("Running: git tag")
        result = subprocess.run(['git', 'tag'], 
                              check=True, capture_output=True, text=True)
        
        # Split by newlines and filter out empty strings
        tags = [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
        logger.info(f"Found {len(tags)} tags: {tags}")
        
        return tags
    except subprocess.CalledProcessError as e:
        logger.error(f"Error fetching tags: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return []


def create_next_tag() -> str:
    """
    Create a new tag by incrementing the middle version number.
    Expects tags in format vX.Y.Z and creates vX.(Y+1).0
    
    Returns:
        str: The newly created tag name
    """
    logger.info("Creating next tag")
    # Get the next tag name
    new_tag = get_next_tag_name()
    logger.info(f"Creating tag: {new_tag}")
    
    try:
        # Create the new tag
        tag_result = subprocess.run(['git', 'tag', new_tag], 
                                  check=True, capture_output=True, text=True)
        logger.debug(f"Tag creation output: {tag_result.stdout}")
        logger.info(f"Successfully created new tag: {new_tag}")
        return new_tag
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating tag: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        return ""
