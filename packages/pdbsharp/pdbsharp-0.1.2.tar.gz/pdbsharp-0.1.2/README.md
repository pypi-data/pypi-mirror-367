# PDB# - The Terminal Remote Debugger

PDB# (styled `pdbsharp`) is an experimental drop-in replacement for pdb as a debugger, based on Textual and the remote debugging protocol.

## Useful Commands

- `uv run pdbsharp` - run the debugger
- `uv run pdbsharp - p <PID>` - attach to a python process at the given pid
- `uv run dummy` - start a simple forever loop that prints its own PID, for testing purposes

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup guidelines.
