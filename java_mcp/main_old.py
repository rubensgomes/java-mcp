


def start_server(repo_urls: List[str],
                 folder_path: str = DEFAULT_FOLDER_PATH,
                 name: str = DEFAULT_SERVER_NAME,
                 host: str = DEFAULT_HOST,
                 port: int = DEFAULT_PORT) -> MCPServer:
    """
    Start the MCP server with the specified configuration.

    Creates and initializes an MCPServer instance with the provided repository
    paths and server configuration. The server will index the specified repositories
    and be ready to serve MCP client requests.

    Args:
        repo_urls (List[str]): List of Git repositories URLs to index.
        folder_path (str): The base path where the repository should be located or cloned.
        name (str, optional): Name identifier for the MCP server. Defaults to "ghmcp-server".
        host (str, optional): Host address to bind the server to. Defaults to "localhost".
        port (int, optional): Port number to bind the server to. Defaults to 8000.

    Returns:
        MCPServer: The initialized and started server instance.

    Raises:
        ValueError: If no valid repositories are found in the provided paths.
        RuntimeError: If the server fails to start.

    Example:
        server = start_server(['/Users/user/repos/project1', '/Users/user/repos/project2'])
        print(f"Server started with {len(server.indexer.repos)} repositories indexed")
    """
    global _server_instance

    logger.info(f"Starting MCP server '{name}' on {host}:{port}")
    logger.info(f"Git repository URLs: {repo_urls}")
    logger.debug(f"Server configuration - name: {name}, host: {host}, port: {port}")

    try:
        # Create server instance with explicit name parameter
        logger.debug("Creating MCPServer instance...")
        server = MCPServer(repo_urls, folder_path, name=name)
        _server_instance = server

        # Validate that repositories were found
        logger.debug("Validating indexed repositories...")
        if not server.indexer.local_repos:
            raise ValueError("No valid Git repositories found in the provided paths")

        logger.info(f"Successfully indexed {len(server.indexer.local_repos)} repositories:")
        for repo in server.indexer.local_repos:
            repo_name = os.path.basename(repo.working_dir)
            logger.info(f"  - {repo_name} ({repo.working_dir})")
            logger.debug(f"    Repository working directory: {repo.working_dir}")

        # Set up signal handlers for graceful shutdown
        logger.debug("Setting up signal handlers...")
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        logger.info(f"MCP GitHub server '{name}' started successfully")
        return server

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.debug(f"Server startup error details:", exc_info=True)
        raise RuntimeError(f"Server startup failed: {e}") from e


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for the MCP server.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="MCP Git Server - Index and serve Git repositories via MCP protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Start with current directory (standard mode)
  %(prog)s --repos /path/to/repo1 /path/to/repo2  # Start with specific repositories
  %(prog)s --name my-server --port 9000      # Start with custom name and port
  %(prog)s --log-level DEBUG                 # Start with debug logging
  %(prog)s --stdio                           # Start in stdio mode for MCP clients
  %(prog)s --stdio --repos /my/repos         # Start in stdio mode with custom repos
  %(prog)s --log-level WARNING --repos /my/repos  # Start with warning level and custom repos

Modes:
  Standard Mode - Regular server operation for direct interaction
  Stdio Mode    - Communicate via stdin/stdout for MCP client integration

Logging Levels:
  DEBUG     - Detailed information for debugging
  INFO      - General information about server operations (default)
  WARNING   - Warning messages for potential issues
  ERROR     - Error messages for serious problems
  CRITICAL  - Critical error messages
        """
    )

    parser.add_argument(
        '--name', '-n',
        type=str,
        default='ghmcp-server',
        help='Server name identifier (default: ghmcp-server)'
    )

    parser.add_argument(
        '--host', '-H',
        type=str,
        default='localhost',
        help='Server host address (default: localhost)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        help='Server port number (default: 8000)'
    )

    parser.add_argument(
        '--repos', '-r',
        type=str,
        nargs='*',
        help='Repository paths to index (default: current directory)'
    )

    parser.add_argument(
        '--log-level', '-l',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--stdio', '-s',
        action='store_true',
        help='Run the server in stdio mode for MCP client communication'
    )

    return parser.parse_args()

def main() -> None:
    """
    Main entry point for the MCP server application.

    This function parses command line arguments and starts the server
    with the specified configuration. Supports both regular mode and
    stdio mode for MCP client communication.
    """
    import os

    # Parse command line arguments
    args = parse_arguments()

    # Configure logging based on command line argument
    configure_logging(args.log_level)

    logger.info("Starting MCP server application")
    logger.debug(f"Command line arguments: {vars(args)}")

    # Use provided repos or default to current directory
    repo_paths = args.repos if args.repos else [os.getcwd()]

    logger.info(f"Configuration:")
    logger.info(f"  Name: {args.name}")
    logger.info(f"  Mode: {'stdio' if args.stdio else 'standard'}")
    logger.info(f"  Host: {args.host}")
    logger.info(f"  Port: {args.port}")
    logger.info(f"  Log Level: {args.log_level}")
    logger.info(f"  Repositories: {repo_paths}")

    try:
        if args.stdio:
            # Run in stdio mode for MCP client communication
            logger.info("Running server in stdio mode")
            asyncio.run(run_stdio_server(repo_paths, name=args.name))
        else:
            # Run in standard mode
            logger.info("Running server in standard mode")
            server = start_server(repo_paths, name=args.name, host=args.host, port=args.port)
            logger.info("Server is running. Press Ctrl+C to stop.")

            # Keep the main thread alive
            try:
                while True:
                    asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
            finally:
                stop_server(server)

    except Exception as e:
        logger.error(f"Server failed: {e}")
        logger.debug("Main function error details:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
