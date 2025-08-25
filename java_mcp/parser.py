from pathlib import Path
from typing import List

def _find_java_files(self, repo_path: Path) -> List[Path]:
    """Find all Java source files in the repository."""
    java_files = []
    for java_file in repo_path.rglob("*.java"):
        # Skip test files and build directories
        if not any(part in java_file.parts for part in ['test', 'tests', 'target', 'build', '.git']):
            java_files.append(java_file)
    return java_files

