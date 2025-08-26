"""
java_analyzer.py
-----------------------
Analyzes Java and Kotlin source code to extract API information for MCP resources.

This module provides comprehensive analysis of Java/Kotlin source files to extract:
- Class and interface definitions
- Method signatures and documentation
- Field definitions
- Usage examples and patterns
- Code snippets and documentation

Classes:
    JavaKotlinAnalyzer: Main analyzer for Java/Kotlin source code
    APIElement: Represents a code element (class, method, field)
    CodeExample: Represents usage examples and code snippets
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from git import Repo

logger = logging.getLogger(__name__)

@dataclass
class APIElement:
    """Represents an API element (class, method, field, etc.)"""
    name: str
    type: str  # 'class', 'interface', 'method', 'field', 'constructor'
    signature: str
    documentation: str
    file_path: str
    line_number: int
    package: str
    modifiers: List[str]
    parameters: List[Dict[str, str]]  # For methods/constructors
    return_type: Optional[str]  # For methods
    annotations: List[str]
    parent_class: Optional[str]
    implemented_interfaces: List[str]

@dataclass
class CodeExample:
    """Represents a code usage example"""
    title: str
    description: str
    code: str
    file_path: str
    line_number: int
    context: str  # surrounding context
    tags: List[str]  # categorization tags

class JavaAnalyzer:
    """
    Analyzes Java and Kotlin source code to extract comprehensive API information.

    This analyzer scans repositories for Java/Kotlin files and extracts:
    - Class and interface definitions with documentation
    - Method signatures with parameters and return types
    - Field definitions and annotations
    - Usage examples and code patterns
    - Documentation comments and annotations
    """

    def __init__(self, repos: List[Repo]):
        """
        Initialize the analyzer with Git repositories.

        Args:
            repos: List of GitPython Repo objects to analyze
        """
        self.repos = repos
        self.api_elements: List[APIElement] = []
        self.code_examples: List[CodeExample] = []
        self.file_patterns = {
            'java': r'\.java$',
            'kotlin': r'\.kt$'
        }
        logger.info(f"Initialized JavaKotlinAnalyzer with {len(repos)} repositories")

    def analyze_repositories(self) -> None:
        """Analyze all repositories for Java/Kotlin source code."""
        logger.info("Starting analysis of repositories for Java/Kotlin code")

        for repo in self.repos:
            try:
                self._analyze_repository(repo)
            except Exception as e:
                logger.error(f"Error analyzing repository {repo.working_dir}: {e}")
                logger.debug(f"Repository analysis error details:", exc_info=True)

        logger.info(f"Analysis complete: found {len(self.api_elements)} API elements and {len(self.code_examples)} code examples")

    def _analyze_repository(self, repo: Repo) -> None:
        """Analyze a single repository for Java/Kotlin files."""
        repo_path = Path(repo.working_dir)
        logger.debug(f"Analyzing repository: {repo_path}")

        # Find all Java/Kotlin files
        java_files = list(repo_path.glob("**/*.java"))
        kotlin_files = list(repo_path.glob("**/*.kt"))

        all_files = java_files + kotlin_files
        logger.debug(f"Found {len(java_files)} Java files and {len(kotlin_files)} Kotlin files")

        for file_path in all_files:
            try:
                self._analyze_source_file(file_path, repo_path)
            except Exception as e:
                logger.warning(f"Error analyzing file {file_path}: {e}")

    def _analyze_source_file(self, file_path: Path, repo_path: Path) -> None:
        """Analyze a single Java/Kotlin source file."""
        logger.debug(f"Analyzing source file: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            logger.warning(f"Could not decode file {file_path}, skipping")
            return

        relative_path = str(file_path.relative_to(repo_path))
        language = 'kotlin' if file_path.suffix == '.kt' else 'java'

        # Extract package name
        package = self._extract_package(content)

        # Extract API elements
        if language == 'java':
            self._analyze_java_content(content, relative_path, package)
        else:
            self._analyze_kotlin_content(content, relative_path, package)

        # Extract code examples
        self._extract_code_examples(content, relative_path)

    def _extract_package(self, content: str) -> str:
        """Extract package name from source content."""
        package_match = re.search(r'package\s+([\w.]+)\s*;?', content)
        return package_match.group(1) if package_match else ""

    def _analyze_java_content(self, content: str, file_path: str, package: str) -> None:
        """Analyze Java source content for API elements."""
        lines = content.split('\n')

        # Extract classes and interfaces
        class_pattern = r'(public|private|protected)?\s*(abstract|final)?\s*(class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?'

        for i, line in enumerate(lines):
            # Class/Interface definitions
            class_match = re.search(class_pattern, line)
            if class_match:
                modifiers = [m for m in [class_match.group(1), class_match.group(2)] if m]
                element_type = class_match.group(3)
                name = class_match.group(4)
                parent_class = class_match.group(5)
                interfaces = [intf.strip() for intf in (class_match.group(6) or "").split(',') if intf.strip()]

                # Extract documentation
                doc = self._extract_javadoc(lines, i)

                api_element = APIElement(
                    name=name,
                    type=element_type,
                    signature=line.strip(),
                    documentation=doc,
                    file_path=file_path,
                    line_number=i + 1,
                    package=package,
                    modifiers=modifiers,
                    parameters=[],
                    return_type=None,
                    annotations=self._extract_annotations(lines, i),
                    parent_class=parent_class,
                    implemented_interfaces=interfaces
                )
                self.api_elements.append(api_element)

            # Method definitions
            method_match = re.search(r'(public|private|protected)?\s*(static|final|abstract)?\s*(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)', line)
            if method_match and not re.search(r'(class|interface)', line):
                modifiers = [m for m in [method_match.group(1), method_match.group(2)] if m]
                return_type = method_match.group(3)
                method_name = method_match.group(4)
                params_str = method_match.group(5)

                # Parse parameters
                parameters = self._parse_java_parameters(params_str)

                # Extract documentation
                doc = self._extract_javadoc(lines, i)

                api_element = APIElement(
                    name=method_name,
                    type='method',
                    signature=line.strip(),
                    documentation=doc,
                    file_path=file_path,
                    line_number=i + 1,
                    package=package,
                    modifiers=modifiers,
                    parameters=parameters,
                    return_type=return_type,
                    annotations=self._extract_annotations(lines, i),
                    parent_class=None,
                    implemented_interfaces=[]
                )
                self.api_elements.append(api_element)

    def _analyze_kotlin_content(self, content: str, file_path: str, package: str) -> None:
        """Analyze Kotlin source content for API elements."""
        lines = content.split('\n')

        # Extract classes and interfaces
        class_pattern = r'(open|abstract|final|sealed)?\s*(class|interface|object)\s+(\w+)(?:\s*:\s*([\w,\s<>]+))?'

        for i, line in enumerate(lines):
            # Class/Interface definitions
            class_match = re.search(class_pattern, line)
            if class_match:
                modifiers = [class_match.group(1)] if class_match.group(1) else []
                element_type = class_match.group(2)
                name = class_match.group(3)
                inheritance = class_match.group(4) or ""

                # Parse inheritance (parent class and interfaces)
                parent_class = None
                interfaces = []
                if inheritance:
                    parts = [part.strip() for part in inheritance.split(',')]
                    # In Kotlin, first item is typically parent class if it exists
                    if parts and not parts[0].endswith('()'):
                        parent_class = parts[0]
                        interfaces = parts[1:]
                    else:
                        interfaces = parts

                # Extract documentation
                doc = self._extract_kdoc(lines, i)

                api_element = APIElement(
                    name=name,
                    type=element_type,
                    signature=line.strip(),
                    documentation=doc,
                    file_path=file_path,
                    line_number=i + 1,
                    package=package,
                    modifiers=modifiers,
                    parameters=[],
                    return_type=None,
                    annotations=self._extract_annotations(lines, i),
                    parent_class=parent_class,
                    implemented_interfaces=interfaces
                )
                self.api_elements.append(api_element)

            # Function definitions
            fun_match = re.search(r'(override|open|final|abstract)?\s*fun\s+(\w+)\s*\(([^)]*)\)\s*:\s*(\w+(?:<[^>]+>)?)', line)
            if fun_match:
                modifiers = [fun_match.group(1)] if fun_match.group(1) else []
                function_name = fun_match.group(2)
                params_str = fun_match.group(3)
                return_type = fun_match.group(4)

                # Parse parameters
                parameters = self._parse_kotlin_parameters(params_str)

                # Extract documentation
                doc = self._extract_kdoc(lines, i)

                api_element = APIElement(
                    name=function_name,
                    type='method',
                    signature=line.strip(),
                    documentation=doc,
                    file_path=file_path,
                    line_number=i + 1,
                    package=package,
                    modifiers=modifiers,
                    parameters=parameters,
                    return_type=return_type,
                    annotations=self._extract_annotations(lines, i),
                    parent_class=None,
                    implemented_interfaces=[]
                )
                self.api_elements.append(api_element)

    def _extract_javadoc(self, lines: List[str], line_index: int) -> str:
        """Extract Javadoc comment preceding the given line."""
        doc_lines = []
        i = line_index - 1

        # Skip empty lines
        while i >= 0 and lines[i].strip() == "":
            i -= 1

        # Check if there's a Javadoc comment
        if i >= 0 and lines[i].strip().endswith("*/"):
            doc_lines.append(lines[i])
            i -= 1

            while i >= 0:
                line = lines[i]
                doc_lines.append(line)
                if line.strip().startswith("/**"):
                    break
                i -= 1

        if doc_lines:
            doc_lines.reverse()
            # Clean up the Javadoc
            cleaned_doc = []
            for line in doc_lines:
                cleaned = re.sub(r'^\s*\*?\s?', '', line.strip())
                if cleaned and not cleaned.startswith('/**') and not cleaned.startswith('*/'):
                    cleaned_doc.append(cleaned)
            return '\n'.join(cleaned_doc)

        return ""

    def _extract_kdoc(self, lines: List[str], line_index: int) -> str:
        """Extract KDoc comment preceding the given line."""
        # Similar to Javadoc but for Kotlin
        return self._extract_javadoc(lines, line_index)

    def _extract_annotations(self, lines: List[str], line_index: int) -> List[str]:
        """Extract annotations preceding the given line."""
        annotations = []
        i = line_index - 1

        while i >= 0:
            line = lines[i].strip()
            if line.startswith('@'):
                annotations.append(line)
                i -= 1
            elif line == "":
                i -= 1
            else:
                break

        annotations.reverse()
        return annotations

    def _parse_java_parameters(self, params_str: str) -> List[Dict[str, str]]:
        """Parse Java method parameters."""
        parameters = []
        if params_str.strip():
            for param in params_str.split(','):
                param = param.strip()
                if param:
                    parts = param.split()
                    if len(parts) >= 2:
                        param_type = ' '.join(parts[:-1])
                        param_name = parts[-1]
                        parameters.append({
                            'name': param_name,
                            'type': param_type,
                            'description': ''
                        })
        return parameters

    def _parse_kotlin_parameters(self, params_str: str) -> List[Dict[str, str]]:
        """Parse Kotlin function parameters."""
        parameters = []
        if params_str.strip():
            for param in params_str.split(','):
                param = param.strip()
                if param and ':' in param:
                    name_part, type_part = param.split(':', 1)
                    param_name = name_part.strip()
                    param_type = type_part.strip()
                    parameters.append({
                        'name': param_name,
                        'type': param_type,
                        'description': ''
                    })
        return parameters

    def _extract_code_examples(self, content: str, file_path: str) -> None:
        """Extract code examples from source files."""
        lines = content.split('\n')

        # Look for example methods, test methods, and demo code
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['example', 'demo', 'test', 'sample']):
                # Extract surrounding context
                start = max(0, i - 5)
                end = min(len(lines), i + 20)
                context = '\n'.join(lines[start:end])

                example = CodeExample(
                    title=f"Code example from {file_path}",
                    description=f"Example usage found at line {i + 1}",
                    code=context,
                    file_path=file_path,
                    line_number=i + 1,
                    context=context,
                    tags=['example', 'usage']
                )
                self.code_examples.append(example)

    def get_api_elements_by_type(self, element_type: str) -> List[APIElement]:
        """Get API elements filtered by type."""
        return [elem for elem in self.api_elements if elem.type == element_type]

    def get_api_elements_by_package(self, package: str) -> List[APIElement]:
        """Get API elements filtered by package."""
        return [elem for elem in self.api_elements if elem.package.startswith(package)]

    def search_api_elements(self, query: str) -> List[APIElement]:
        """Search API elements by name or documentation."""
        query_lower = query.lower()
        return [
            elem for elem in self.api_elements
            if query_lower in elem.name.lower() or query_lower in elem.documentation.lower()
        ]

    def get_method_signatures_summary(self) -> Dict[str, List[str]]:
        """Get a summary of all method signatures grouped by class."""
        summary = {}
        for elem in self.api_elements:
            if elem.type == 'method':
                class_key = f"{elem.package}.{elem.parent_class or 'Global'}"
                if class_key not in summary:
                    summary[class_key] = []
                summary[class_key].append(elem.signature)
        return summary
