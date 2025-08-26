"""
server.py
---------
Implements an enhanced MCP server for indexing GitHub repositories and exposing
Java/Kotlin source code API resources to AI coding assistants.

Classes:
    GitHubRepoIndexer: Indexes local git repositories.
    MCPGitHubServer: Enhanced MCP server with resource capabilities for Java/Kotlin APIs.

Usage:
    Instantiate MCPGitHubServer with a list of local repo paths to index repositories
    and expose comprehensive API resources for AI coding assistants.
    For stdio mode: server.run_stdio() or use run_stdio_server() function.
"""

from mcp.server import Server
from mcp.types import Resource, TextResourceContents
from ghmcp.utility import get_repo
from java_mcp.java_analyzer import JavaAnalyzer
from java_mcp.resource_manager import ResourceManager
import os
import os.path
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional

# Configure logging for this module
logger = logging.getLogger(__name__)


class MCPServer(Server):
    """
    Enhanced MCP server implementation for Git repository indexing of Java API resources.

    This server extends the base MCP Server class to provide Git repository
    indexing capabilities and expose comprehensive Java source code API resources
    for AI coding assistants. It uses GitRepoIndexer to scan and index Git
    repositories, JavaAnalyzer to parse source code, and ResourceManager to
    provide structured API information.

    Attributes:
        indexer (GitRepoIndexer): Repository indexer instance.
        analyzer (JavaAnalyzer): Java source code analyzer.
        resource_manager (ResourceManager): Resource manager for handling API resources.
        name (str): Server name identifier.

    Args:
        repo_urls (List[str]): List of Git repository URLs to index.
        folder_path (str): The base path where the Git repository should be located or cloned.
        name (str, optional): Server name identifier.
        *args: Additional arguments passed to parent Server class.
        **kwargs: Additional keyword arguments passed to parent Server class.

    Example:
        server = MCPServer(['https://github.com/somepath/repo1', 'https://github.com/somepath/repo2'], folder_path='/tmp/mcp-server', name="my-server")
    """
    def __init__(self,
                 repo_urls: List[str],
                 folder_path: str,
                 name: str,
                 *args,
                 **kwargs):
        logger.info(f"Initializing MCPServer '{name}' with {len(repo_urls)} repository URLs")
        logger.debug(f"Repository URLs: {repo_urls}")
        logger.debug(f"Folder path: {folder_path}")
        logger.debug(f"Server args: {args}, kwargs: {kwargs}")

        # Validate inputs
        if not repo_urls:
            raise ValueError("At least one repository URL must be provided")

        if not folder_path or not isinstance(folder_path, str):
            raise ValueError("Folder path must be a non-empty string")

        if not name or not isinstance(name, str):
            raise ValueError("Server name must be a non-empty string")

        try:
            # Pass the name to the parent Server class constructor
            logger.debug(f"Calling parent Server.__init__ with name='{name}'")
            super().__init__(name, *args, **kwargs)
            self.name = name
            logger.debug(f"Parent Server class initialized successfully")

            logger.info("Creating GitRepoIndexer instance")
            self.indexer = GitRepoIndexer(repo_urls, folder_path)

            # Validate that indexer was created successfully
            if not hasattr(self, 'indexer') or self.indexer is None:
                raise RuntimeError("Failed to create GitRepoIndexer instance")

            # Initialize Java analyzer with indexed repositories
            logger.info("Creating JavaAnalyzer instance")
            self.analyzer = JavaKotlinAnalyzer(self.indexer.repos)

            # Analyze repositories for Java/Kotlin code
            logger.info("Analyzing repositories for Java/Kotlin source code")
            self.analyzer.analyze_repositories()

            # Initialize resource manager with analyzer
            logger.info("Creating ResourceManager instance")
            self.resource_manager = ResourceManager(self.analyzer)

            # Validate that resource manager was created successfully
            if not hasattr(self, 'resource_manager') or self.resource_manager is None:
                raise RuntimeError("Failed to create ResourceManager instance")

            logger.info(f"MCPGitHubServer '{name}' initialized successfully")
            logger.info(f"Found {len(self.analyzer.api_elements)} API elements and {len(self.analyzer.code_examples)} code examples")

        except Exception as e:
            logger.error(f"Failed to initialize MCPGitHubServer '{name}': {e}")
            logger.debug(f"MCPGitHubServer initialization error details:", exc_info=True)
            raise

    def get_capabilities(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Get the capabilities that this MCP server supports.

        This enhanced server implementation declares resource capabilities for
        Java/Kotlin source code APIs to support AI coding assistants.

        Args:
            *args: Additional positional arguments from MCP framework
            **kwargs: Additional keyword arguments from MCP framework

        Returns:
            Dict[str, Any]: Server capabilities configuration
        """
        logger.debug(f"Getting capabilities for MCPGitHubServer '{self.name}' with args: {args}, kwargs: {kwargs}")

        capabilities = {
            "resources": {
                "listChanged": True,
                "subscribe": True
            }
        }

        logger.info(f"Server '{self.name}' capabilities: {list(capabilities.keys())}")
        return capabilities

    async def run_stdio(self):
        """
        Run the MCP server in stdio mode.

        This method runs the server in stdio mode using the MCP stdio_server
        transport for proper communication via stdin/stdout.

        Example:
            server = MCPGitHubServer(['/path/to/repo'])
            await server.run_stdio()
        """
        logger.info(f"Starting MCPGitHubServer '{self.name}' in stdio mode")
        logger.debug(f"Server will communicate via stdin/stdout")
        try:
            from mcp.server.stdio import stdio_server

            # Use the stdio_server transport to run the server
            async with stdio_server() as (read_stream, write_stream):
                logger.debug("Stdio server transport established")

                # Create initialization options for the server
                initialization_options = self.create_initialization_options()

                # Run the server with stdio streams
                await self.run(
                    read_stream=read_stream,
                    write_stream=write_stream,
                    initialization_options=initialization_options
                )

        except KeyboardInterrupt:
            logger.info(f"Received keyboard interrupt, shutting down stdio server '{self.name}'")
        except Exception as e:
            logger.error(f"Error running server '{self.name}' in stdio mode: {e}")
            logger.debug(f"Server stdio error details:", exc_info=True)
            raise
        finally:
            logger.info(f"MCPGitHubServer '{self.name}' stdio mode stopped")

    async def list_resources(self) -> List[Resource]:
        """
        List all available Java/Kotlin API resources.

        Returns:
            List[Resource]: Available resources for Java/Kotlin APIs
        """
        logger.debug("Listing available Java/Kotlin API resources")

        resources = []
        available_resources = self.resource_manager.get_available_resources()

        for resource_info in available_resources:
            resource = Resource(
                uri=resource_info["uri"],
                name=resource_info["name"],
                description=resource_info["description"],
                mimeType=resource_info["mimeType"]
            )
            resources.append(resource)

        logger.info(f"Listed {len(resources)} available Java/Kotlin API resources")
        return resources

    async def read_resource(self, uri: str) -> str:
        """
        Read the content of a specific Java/Kotlin API resource.

        Args:
            uri: Resource URI to read

        Returns:
            str: Resource content as JSON string
        """
        logger.debug(f"Reading Java/Kotlin API resource: {uri}")

        try:
            content = self.resource_manager.get_resource_content(uri)
            result = json.dumps(content, indent=2, ensure_ascii=False)
            logger.debug(f"Successfully read resource {uri}, content length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            error_content = {"error": f"Failed to read resource: {str(e)}"}
            return json.dumps(error_content, indent=2)


async def run_stdio_server(repo_paths: List[str], name: str = "ghmcp-server",
                          loop: Optional[asyncio.AbstractEventLoop] = None):
    """
    Create and run an MCPGitHubServer in stdio mode.

    This is a convenience function that creates an MCPGitHubServer instance
    and immediately runs it in stdio mode for MCP client communication.

    Args:
        repo_paths (List[str]): List of filesystem paths to Git repositories to index.
        name (str, optional): Server name identifier. Defaults to "ghmcp-server".
        loop (Optional[asyncio.AbstractEventLoop]): Optional event loop to run the server (deprecated, ignored).

    Raises:
        ValueError: If no valid repositories are found in the provided paths.
        RuntimeError: If the server fails to start.

    Example:
        import asyncio
        asyncio.run(run_stdio_server(['/path/to/repo1', '/path/to/repo2']))
    """
    logger.info(f"Creating and running MCPGitHubServer '{name}' in stdio mode")
    logger.debug(f"Repository paths for stdio server: {repo_paths}")

    try:
        # Create server instance
        server = MCPGitHubServer(repo_paths, name=name)

        # Validate that repositories were found before starting stdio mode
        if not server.indexer.repos:
            raise ValueError("No valid Git repositories found in the provided paths")

        logger.info(f"Successfully indexed {len(server.indexer.repos)} repositories, starting stdio mode")

        # Run in stdio mode (removed loop parameter as it's not supported)
        await server.run_stdio()

    except Exception as e:
        logger.error(f"Failed to run stdio server '{name}': {e}")
        logger.debug(f"Stdio server error details:", exc_info=True)
        raise
