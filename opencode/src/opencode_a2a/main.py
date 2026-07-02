"""
Entry point for the OpenCode A2A server.

Usage:
  opencode-a2a                                          # defaults
  opencode-a2a --port 9000                              # custom port
  opencode-a2a --opencode-url http://localhost:4096      # custom opencode url
  opencode-a2a --env-file staging.env                    # custom env file
"""

from __future__ import annotations

import argparse
import sys

import uvicorn

from .config import Settings
from .server import create_app


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="opencode-a2a",
        description="A2A agent card server for OpenCode",
    )
    parser.add_argument(
        "--port", type=int, default=None,
        help="Server port (default: 8000)",
    )
    parser.add_argument(
        "--opencode-url", type=str, default=None,
        help="OpenCode serve URL (default: http://127.0.0.1:4096)",
    )
    parser.add_argument(
        "--env-file", default=".env",
        help="Path to env file (default: .env)",
    )
    args = parser.parse_args()

    # ---------------------------------------------------------------------------
    # Load settings: .env file → env vars → CLI overrides
    # ---------------------------------------------------------------------------

    try:
        settings = Settings(_env_file=args.env_file)
    except Exception as e:
        print(f"Error loading settings: {e}", file=sys.stderr)
        sys.exit(1)

    if args.port is not None:
        settings.a2a_port = args.port
    if args.opencode_url is not None:
        settings.opencode_base_url = args.opencode_url

    # ---------------------------------------------------------------------------
    # Start server
    # ---------------------------------------------------------------------------

    app = create_app(settings)

    host, port = settings.a2a_host, settings.a2a_port
    print("OpenCode A2A Server")
    print(f"  Server:       http://{host}:{port}")
    print(f"  OpenCode:     {settings.opencode_base_url}")
    print(f"  Agent card:   http://{host}:{port}/.well-known/agent-card.json")
    print(f"  Swagger:      http://{host}:{port}/docs")
    print()

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
