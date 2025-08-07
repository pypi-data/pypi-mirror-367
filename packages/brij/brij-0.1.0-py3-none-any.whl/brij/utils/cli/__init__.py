import importlib.util as imputil
import inspect
from pathlib import Path
from typing_extensions import Annotated

import typer

from brij.utils.server.base import BaseServer

app = typer.Typer(help="Brij CLI for servers with ZMQ")


def load_module(file_path: Path):
    spec = imputil.spec_from_file_location(file_path.stem, str(file_path))
    mod = imputil.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def find_server_class(module) -> type[BaseServer]:
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseServer) and obj is not BaseServer:
            return obj
    raise ValueError("❌ No subclass of BaseServer found in the module.")


@app.command("hello")
def hello():
    print("Welcome to Brij")


@app.command(name="serve")
def serve(
    server_file: Annotated[
        Path, typer.Argument(help="Path to the server implementation file")
    ],
    port: Annotated[
        int, typer.Option("--port", "-p", help="Port to bind the server to")
    ] = 5555,
):
    """
    Serve a ZMQ server from a given Python file.
    """
    typer.echo(f"🔍 Loading server from {server_file}...")
    module = load_module(server_file)
    server_class = find_server_class(module)

    typer.echo(f"🚀 Starting {server_class.__name__} on port {port}...")
    server_instance = server_class(port=port)
    try:
        server_instance.run()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server_instance.close()
