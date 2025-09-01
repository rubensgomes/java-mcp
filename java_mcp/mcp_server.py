"""
FastMCP Server for Java Analysis

A MCP (Model Context Protocol) server implementation using FastMCP for
analyzing Java codebases and providing AI assistants with Java-specific
development capabilities.

This server exposes tools for:
- Java class analysis
- API extraction
- Method searching
- Development guide generation

Author: Rubens Gomes
License: Apache-2.0
Version: 0.1.1
Last Updated: August 29, 2025
"""

import logging
from typing import List
from fastmcp import FastMCP
from pathlib import Path
from git import Repo

from java_mcp.model.analyze_class_request import AnalyzeClassRequest
from java_mcp.model.extract_apis_request import ExtractAPIsRequest
from java_mcp.model.generate_guide_request import GenerateGuideRequest
from java_mcp.model.search_methods_request import SearchMethodsRequest
from java_mcp.git.git_repo_indexer import GitRepoIndexer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Java MCP Server")


@mcp.tool()
def analyze_java_class(request: AnalyzeClassRequest) -> str:
    """
    Analyze a specific Java class and provide detailed information.

    This tool performs comprehensive analysis of Java classes including:
    - Class structure and hierarchy
    - Method signatures and documentation
    - Field definitions and types
    - Annotations and metadata

    Args:
        request: AnalyzeClassRequest containing class_name and optional repository

    Returns:
        str: Detailed analysis of the Java class in structured format

    Example usage:
        analyze_java_class with AnalyzeClassRequest(class_name="UserService")
        -> returns a detailed analysis string (implementation pending)
    """
    logger.info(f"Analyzing Java class: {request.class_name}")

    # TODO: Implement actual Java class analysis logic
    # This would typically involve:
    # 1. Locating the class file in the repository
    # 2. Parsing the Java source code
    # 3. Extracting class metadata, methods, fields
    # 4. Generating structured analysis report

    return f"Analysis for class '{request.class_name}' - Implementation pending"


@mcp.tool()
def extract_apis(request: ExtractAPIsRequest) -> str:
    """
    Extract API information from Java repositories.

    This tool scans Java codebases to identify and document APIs including:
    - Public methods and their signatures
    - REST endpoints and HTTP mappings
    - Service interfaces and contracts
    - API documentation and examples

    Args:
        request: ExtractApisRequest containing extraction parameters

    Returns:
        str: Comprehensive API documentation in structured format

    Example usage:
        extract_apis with ExtractAPIsRequest(repo_url="https://github.com/user/repo.git")
        -> returns API documentation string (implementation pending)
    """
    logger.info(f"Extracting APIs from repositories: {request.repository_urls}")

    # TODO: Implement API extraction logic
    # This would typically involve:
    # 1. Cloning/accessing specified repositories
    # 2. Scanning for API-related annotations (@RestController, @RequestMapping, etc.)
    # 3. Parsing method signatures and documentation
    # 4. Generating comprehensive API documentation

    return f"API extraction for {len(request.repository_urls)} repositories - Implementation pending"


@mcp.tool()
def search_methods(request: SearchMethodsRequest) -> str:
    """
    Search for specific methods across Java codebases.

    This tool provides intelligent method discovery including:
    - Method name pattern matching
    - Parameter type filtering
    - Return type analysis
    - Usage examples and context

    Args:
        request: SearchMethodsRequest containing search criteria

    Returns:
        str: List of matching methods with detailed information

    Example usage:
        search_methods with SearchMethodsRequest(method_name="findUser")
        -> returns a list/summary of matching methods (implementation pending)
    """
    logger.info(f"Searching for methods: {request.method_name}")

    # TODO: Implement method search logic
    # This would typically involve:
    # 1. Indexing Java source files
    # 2. Parsing method signatures
    # 3. Applying search filters (name, parameters, return type)
    # 4. Ranking and formatting results

    return f"Method search for '{request.method_name}' - Implementation pending"


@mcp.tool()
def generate_guide(request: GenerateGuideRequest) -> str:
    """
    Generate development guides and documentation.

    This tool creates comprehensive development documentation including:
    - Setup and configuration guides
    - Code examples and best practices
    - Architecture explanations
    - Integration patterns

    Args:
        request: GenerateGuideRequest containing guide parameters

    Returns:
        str: Generated development guide in markdown format

    Example usage:
        generate_guide with GenerateGuideRequest(use_case="Spring Boot Setup")
        -> returns markdown guide string (implementation pending)
    """
    # Generate guide based on provided use_case
    logger.info("Generating guide for use_case: %s", request.use_case)

    # TODO: Implement guide generation logic
    # This would typically involve:
    # 1. Analyzing repository structure and dependencies
    # 2. Identifying common patterns and configurations
    # 3. Generating step-by-step documentation
    # 4. Including relevant code examples

    return f"Development guide for use_case '{request.use_case}' - Implementation pending"


@mcp.tool()
def health_check() -> str:
    """
    Perform a health check of the MCP server.

    This tool verifies that the server is running correctly and all
    dependencies are properly configured.

    Returns:
        str: Health status information

    Example usage:
        health_check -> returns a brief server health summary string
    """
    logger.info("Performing health check")

    try:
        # Basic health checks
        status = {
            "server": "Java MCP Server",
            "version": "0.1.1",
            "status": "healthy",
            "tools_available": 5,
            "dependencies": {
                "fastmcp": "available",
                "gitpython": "available",
                "antlr4": "available",
                "pydantic": "available"
            }
        }

        return f"Health Check Results: {status}"

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return f"Health Check Failed: {str(e)}"


# -------------------- MCP Resources --------------------


@mcp.resource(uri="/resources/get_repo_indexer")
def get_repo_indexer(repo_urls: List[str], folder_path: str = "/tmp/java_repos") -> dict:
    """
    Create or update a GitRepoIndexer for the given repository URLs and return basic info.

    This resource instantiates GitRepoIndexer (which performs validation and shallow clones)
    and returns a lightweight summary including the local folder path and the resolved
    repository working directories. Errors are returned as an error payload rather than
    raising to allow MCP clients to handle failures gracefully.
    """
    logger.info("Creating/updating GitRepoIndexer for %d repos into %s", len(repo_urls), folder_path)
    try:
        indexer = GitRepoIndexer(repo_urls, folder_path)
        repos = indexer.get_local_repos()
        return {
            "folder_path": folder_path,
            "repositories": [str(repo.working_dir) for repo in repos]
        }
    except Exception as e:
        logger.error("Failed to create GitRepoIndexer: %s", e)
        return {"error": str(e)}


@mcp.resource(uri="/resources/list_repo_remotes")
def list_repo_remotes(folder_path: str = "/tmp/java_repos") -> dict:
    """
    List remote URLs for all git repositories found directly under folder_path.

    Returns a mapping of repository folder name -> origin URL (or None if missing).
    """
    logger.info("Listing repository remotes in folder: %s", folder_path)
    results = {}
    try:
        base = Path(folder_path)
        if not base.exists():
            return {"error": f"folder_path does not exist: {folder_path}"}

        for child in base.iterdir():
            if not child.is_dir():
                continue
            git_dir = child / '.git'
            if not git_dir.exists():
                continue

            try:
                repo = Repo(str(child))
                origin = GitRepoIndexer.get_remote_url(repo)
                results[child.name] = origin
            except Exception as e:
                logger.warning("Failed to read repo at %s: %s", child, e)
                results[child.name] = {"error": str(e)}

        return results
    except Exception as e:
        logger.error("Error listing remotes: %s", e)
        return {"error": str(e)}


@mcp.resource(uri="/resources/server_state")
def server_state() -> dict:
    """
    Return a lightweight server state resource for clients to inspect.

    Includes server name, version and number of exposed tools/resources.
    """
    return {
        "server": "Java MCP Server",
        "version": "0.1.1",
        "status": "running",
        "tools": ["analyze_java_class", "extract_apis", "search_methods", "generate_guide", "health_check"],
        "resources": ["get_repo_indexer", "list_repo_remotes", "server_state"]
    }


def main():
    """
    Main entry point for the FastMCP server.

    Starts the MCP server and begins listening for requests.
    This function is typically called when running the server directly.
    """
    logger.info("Starting Java MCP Server...")

    try:
        # Start the FastMCP server
        # The server will handle MCP protocol communication automatically
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Java MCP Server stopped")


if __name__ == "__main__":
    main()
