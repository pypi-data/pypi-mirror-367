import os
import sys
def is_repo_root(dirname: str) -> bool:
    """
    Check if the given directory is the root of a git repository.
    Args:
        dirname (str): The directory to check.
    Returns:
        bool: True if the directory is a git repository root, False otherwise.
    """
    if not dirname.strip() or not os.path.exists(dirname):
        return False
    if not os.path.isdir(dirname):
        return False
    for b in [[".git"], ["README.md"], ["LICENSE"]]:
        filename = os.path.join(dirname, *b)
        if not os.path.exists(filename):
            return False
    return True

def get_repo_root(ref: str = os.getcwd(), raise_if_not_found: bool = True) -> str:
    """
    Get the root directory of the git repository containing the given file.
    Args:
        ref (str): The reference file or directory to start the search from.
        raise_if_not_found (bool): If True, raises an error if the root is not found.
    Returns:
        str: The absolute path to the repository root directory.
    """
    root = os.path.abspath(ref)
    while root:
        if root == os.path.dirname(root):
            break
        if is_repo_root(root):
            return root
        root = os.path.dirname(root)
    if raise_if_not_found:
        raise FileNotFoundError("Could not find the repository root directory.")
    return None

def get_repo_tmpdir(ref: str = __file__, name: str = ".tmp", raise_if_not_found: bool = True) -> str:
    """
    Get the temporary directory for the git repository containing the given file.
    Args:
        ref (str): The reference file or directory to start the search from.
        raise_if_not_found (bool): If True, raises an error if the temporary directory is not found.
    Returns:
        str: The absolute path to the repository temporary directory.
    """
    root = get_repo_root(ref, raise_if_not_found)
    if not root:
        return None
    tmpdir = os.path.join(root, name)
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    return tmpdir

def repoinit() -> int:
    """
    Initialize the repository by adding its root to the system path.
    Returns:
        str: The absolute path to the repository root directory.
    """
    reporoot = get_repo_root(os.getcwd())
    if not (reporoot in sys.path):
        sys.path.insert(0, reporoot)
    return 200
