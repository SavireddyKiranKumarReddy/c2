"""Default to the simulation server when invoked as a module."""

from .cli import server_main

if __name__ == "__main__":
    server_main()

