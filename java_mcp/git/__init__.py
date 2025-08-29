"""
Git Operations Package for Java MCP Server

This package provides comprehensive git repository management capabilities for the Java MCP Server.
It serves as the foundation for git-based operations that enable AI assistants to work with Java
codebases stored in git repositories. The package handles repository cloning, validation, updating,
and provides high-level abstractions for managing multiple repositories efficiently.

The package is designed to integrate seamlessly with the broader Java MCP server ecosystem,
providing git repository access for Java source code analysis, documentation extraction,
and code understanding workflows.

Package Structure:
=================

Core Modules:
- git_repo_indexer.py: High-level GitRepoIndexer class for managing multiple repositories

Key Features:
============

Repository Management:
- Batch processing of multiple git repositories with validation
- Shallow cloning optimization (depth=1) for efficient storage and bandwidth usage
- Automatic repository updates with conflict detection and resolution
- Support for various git protocols (HTTP, HTTPS, SSH, git@)

Validation and Error Handling:
- Comprehensive git URL validation with protocol verification
- Repository accessibility checking without requiring full clone operations
- Robust error handling with detailed logging for debugging and monitoring
- Graceful handling of network failures and authentication issues

Integration Capabilities:
- Seamless integration with java_mcp.parser for Java source analysis
- Support for java_mcp.types components for code representation
- Compatible with MCP server tools for AI assistant interactions
- Designed for use in automated workflows and batch processing

Performance Optimizations:
- Efficient repository indexing and caching mechanisms
- Minimal network overhead through pre-validation and shallow cloning
- Intelligent folder management and organization
- Cross-platform compatibility with proper path handling

Usage Patterns:
==============

Basic Repository Management:
```python
from java_mcp.git import GitRepoIndexer

# Manage multiple repositories
repo_urls = [
    "https://github.com/spring-projects/spring-boot.git",
    "https://github.com/apache/maven.git",
    "git@github.com:user/private-repo.git"
]

# Initialize and clone repositories
indexer = GitRepoIndexer(repo_urls, "/tmp/java_repos")
repos = indexer.get_local_repos()

# Access repository information
for repo in repos:
    print(f"Repository: {repo.working_dir}")
    remote_url = GitRepoIndexer.get_remote_url(repo)
    print(f"Remote URL: {remote_url}")
```

Integration with Java Analysis Pipeline:
```python
from java_mcp.git import GitRepoIndexer
from java_mcp.parser import JavaPathIndexer

# Clone repositories and analyze Java content
indexer = GitRepoIndexer(repo_urls, "/tmp/analysis")
repos = indexer.get_local_repos()

analysis_results = []
for repo in repos:
    # Discover Java files in the cloned repository
    java_indexer = JavaPathIndexer(repo.working_dir)
    java_files = java_indexer.get_java_files()

    analysis_results.append({
        "repository": GitRepoIndexer.get_remote_url(repo),
        "java_files_count": len(java_files),
        "main_sources": len(java_indexer.get_main_java_files()),
        "test_sources": len(java_indexer.get_test_java_files())
    })
```

MCP Server Tool Integration:
```python
from fastmcp import FastMCP
from java_mcp.git import GitRepoIndexer

mcp = FastMCP("Java Analysis Server")

@mcp.tool()
def analyze_git_repositories(repo_urls: List[str], target_folder: str) -> str:
    '''Analyze Java repositories from git URLs and provide comprehensive insights.'''
    try:
        # Clone and validate repositories
        indexer = GitRepoIndexer(repo_urls, target_folder)
        repos = indexer.get_local_repos()

        # Perform analysis on cloned repositories
        results = []
        for repo in repos:
            result = perform_comprehensive_analysis(repo.working_dir)
            results.append(result)

        return format_analysis_results(results)

    except Exception as e:
        return f"Analysis failed: {str(e)}"
```

Error Handling and Resilience:
=============================

The package provides robust error handling for common git operation scenarios:

```python
from git import GitCommandError, InvalidGitRepositoryError
from java_mcp.git import GitRepoIndexer

def safe_repository_analysis(repo_urls: List[str], folder_path: str):
    try:
        indexer = GitRepoIndexer(repo_urls, folder_path)
        return {"status": "success", "repos": len(indexer.get_local_repos())}

    except InvalidGitRepositoryError as e:
        # Handle invalid repository URLs
        return {"status": "error", "type": "invalid_repository", "message": str(e)}

    except GitCommandError as e:
        # Handle git operation failures (network, authentication, etc.)
        return {"status": "error", "type": "git_operation_failed", "message": str(e)}

    except ValueError as e:
        # Handle invalid input parameters
        return {"status": "error", "type": "invalid_parameters", "message": str(e)}

    except OSError as e:
        # Handle file system and permission issues
        return {"status": "error", "type": "filesystem_error", "message": str(e)}
```

Security Considerations:
=======================

Repository URL Validation:
- Strict validation of git repository URLs to prevent malicious inputs
- Support for trusted protocols only (HTTPS, SSH, git@)
- Protection against directory traversal and path injection attacks

Authentication and Access:
- Secure handling of git credentials and SSH keys
- Support for authenticated repositories with proper credential management
- Isolation of cloned repositories in designated folders

Network Security:
- Validation of repository accessibility before clone operations
- Timeout handling for network operations to prevent hanging
- Graceful handling of certificate and SSL/TLS issues

Performance and Scalability:
===========================

Storage Optimization:
- Shallow cloning (depth=1) reduces storage requirements by 80-95%
- Efficient repository updates that only fetch necessary changes
- Intelligent folder organization with automatic cleanup capabilities

Network Efficiency:
- Pre-validation of repository URLs to avoid unnecessary network operations
- Parallel processing support for multiple repository operations
- Caching mechanisms to reduce repeated network requests

Memory Management:
- Efficient handling of large repositories with minimal memory footprint
- Proper resource cleanup and garbage collection
- Scalable architecture supporting hundreds of repositories

Integration Architecture:
=========================

The git package serves as a foundational layer in the Java MCP server architecture:

```
┌─────────────────────────────────────────────┐
│              MCP Server Tools               │
│         (AI Assistant Interface)            │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│           Java Analysis Layer               │
│    (java_mcp.parser, java_mcp.types)       │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│         Git Operations Layer                │
│           (java_mcp.git)                    │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│        Repository Storage Layer             │
│      (Local file system, Git repos)        │
└─────────────────────────────────────────────┘
```

Dependencies:
============

Core Dependencies:
- GitPython: Advanced git repository operations and management
- pathlib: Cross-platform path handling and file system operations
- typing: Type hints for better code documentation and IDE support

System Requirements:
- Git command-line tools installed and accessible in system PATH
- Network connectivity for repository cloning and updates
- Sufficient disk space for repository storage (shallow clones)

Optional Dependencies:
- SSH client for SSH-based repository access
- Git credential helpers for authenticated repository access

Logging and Monitoring:
======================

The package provides comprehensive logging capabilities:

Log Levels:
- DEBUG: Detailed operation traces, URL validation, path resolution
- INFO: Successful operations, repository statistics, performance metrics
- WARNING: Non-fatal issues, fallback behaviors, accessibility warnings
- ERROR: Critical failures, exception conditions, operation failures

Log Context:
- Repository URLs and local paths for operation tracking
- Operation timing and performance metrics
- Error details with stack traces for debugging
- Network operation status and retry information

Monitoring Integration:
- Structured logging format compatible with log aggregation systems
- Metrics collection for repository operation success rates
- Performance monitoring for clone and update operations

Extension Points:
================

The package is designed for extensibility and customization:

Custom Validation:
- Pluggable URL validation for organization-specific requirements
- Custom authentication handlers for enterprise git systems
- Repository filtering and access control mechanisms

Performance Tuning:
- Configurable clone depth for different use cases
- Custom retry policies for network operations
- Parallel processing configuration for batch operations

Integration Hooks:
- Pre and post-operation hooks for custom processing
- Event notifications for repository state changes
- Custom error handling and recovery strategies

See Also:
=========
- java_mcp.parser: Java source code parsing and analysis
- java_mcp.types: Type system for representing Java code elements
- java_mcp.server: MCP server implementation for AI assistant integration
- GitPython documentation: https://gitpython.readthedocs.io/
- Git documentation: https://git-scm.com/doc

Examples and Testing:
====================
For comprehensive examples and test cases, see:
- tests/test_git_repo_indexer.py: GitRepoIndexer class tests and usage examples

Version: 1.0.0
Last Updated: August 28, 2025
License: Apache-2.0
"""

# Import the main GitRepoIndexer class for convenient access
from .git_repo_indexer import GitRepoIndexer

# Define what gets exported when using "from java_mcp.git import *"
__all__ = [
    'GitRepoIndexer',
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Java MCP Server Team"
__description__ = "Git repository management for Java MCP Server"

# Module-level logging configuration
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Initialized java_mcp.git package version {__version__}")
