"""Tests for the gRPC server and interactive client commands."""

from argparse import ArgumentParser
from io import StringIO

import grpc
import pytest
from django.core.management.base import CommandError

from services.grpc_api import authentication_pb2
from services.management.commands import grpc_login, run_grpc_server


class FakeChannel:
    """Act as a context-managed channel without opening a socket."""

    def __enter__(self):
        """Return the fake channel to the command."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Leave the channel context without suppressing errors."""
        return False


class FakeRpcError(grpc.RpcError):
    """Provide status details expected by the client command."""

    def code(self):
        """Return a representative authentication failure status."""
        return grpc.StatusCode.UNAUTHENTICATED

    def details(self):
        """Return a representative server error message."""
        return "Invalid username or password."


def test_grpc_login_command_prints_success(monkeypatch):
    """Verify the client sends the prompted password and displays the result."""
    response = authentication_pb2.LoginResponse(  # nosec B106
        success=True,
        message="Logged in successfully.",
        access_token="access-token",
        refresh_token="refresh-token",
        user_id="user-1",
        username="admin",
        email="admin@example.com",
    )

    class FakeStub:
        """Record and answer the outgoing login call."""

        def __init__(self, channel):
            self.channel = channel

        def Login(self, request, timeout):  # noqa: N802
            assert request.username == "admin"
            assert request.password == "Admin@12345"  # nosec B105
            assert timeout == 5
            return response

    monkeypatch.setattr(grpc_login, "getpass", lambda prompt: "Admin@12345")
    monkeypatch.setattr(
        grpc_login.grpc, "insecure_channel", lambda address: FakeChannel()
    )
    monkeypatch.setattr(
        grpc_login.authentication_pb2_grpc, "AuthenticationServiceStub", FakeStub
    )
    output = StringIO()
    command = grpc_login.Command(stdout=output)

    command.handle(username="admin", address="127.0.0.1:50051")

    rendered = output.getvalue()
    assert "Logged in successfully." in rendered
    assert "admin@example.com" in rendered
    assert "Access token: access-token" in rendered
    assert "Refresh token: refresh-token" in rendered


def test_grpc_login_command_converts_rpc_error(monkeypatch):
    """Verify transport failures become readable Django command errors."""

    class FailingStub:
        """Raise a controlled RPC error for the command."""

        def __init__(self, channel):
            self.channel = channel

        def Login(self, request, timeout):  # noqa: N802
            raise FakeRpcError

    monkeypatch.setattr(grpc_login, "getpass", lambda prompt: "wrong")
    monkeypatch.setattr(
        grpc_login.grpc, "insecure_channel", lambda address: FakeChannel()
    )
    monkeypatch.setattr(
        grpc_login.authentication_pb2_grpc,
        "AuthenticationServiceStub",
        FailingStub,
    )

    with pytest.raises(CommandError, match="UNAUTHENTICATED"):
        grpc_login.Command().handle(username="admin", address="127.0.0.1:50051")


def test_grpc_command_argument_definitions():
    """Verify both commands register their documented CLI options."""
    server_parser = ArgumentParser()
    run_grpc_server.Command().add_arguments(server_parser)
    assert server_parser.parse_args([]).port == 50051
    assert server_parser.parse_args(["--workers", "2"]).workers == 2

    client_parser = ArgumentParser()
    grpc_login.Command().add_arguments(client_parser)
    client_options = client_parser.parse_args(["admin"])
    assert client_options.username == "admin"
    assert client_options.address == "127.0.0.1:50051"


def test_create_grpc_server_binds_and_can_stop():
    """Verify the server factory registers the service and opens a port."""
    server, address = run_grpc_server.create_server("127.0.0.1", 0, 1)
    assert address == "127.0.0.1:0"
    server.start()
    server.stop(grace=None).wait()


def test_create_grpc_server_reports_bind_failure(monkeypatch):
    """Verify an unavailable address produces an actionable error."""

    class UnboundServer:
        """Represent a server unable to reserve its requested address."""

        def add_insecure_port(self, address):
            return 0

    monkeypatch.setattr(
        run_grpc_server.grpc, "server", lambda executor: UnboundServer()
    )
    monkeypatch.setattr(
        run_grpc_server.authentication_pb2_grpc,
        "add_AuthenticationServiceServicer_to_server",
        lambda service, server: None,
    )

    with pytest.raises(RuntimeError, match="Could not bind"):
        run_grpc_server.create_server("127.0.0.1", 50051, 1)


def test_run_grpc_server_stops_on_keyboard_interrupt(monkeypatch):
    """Verify Ctrl+C triggers the server's graceful-stop path."""

    class StopResult:
        """Represent the waitable result of stopping a server."""

        def wait(self):
            return None

    class InterruptingServer:
        """Stop the command loop immediately as if Ctrl+C was pressed."""

        started = False
        stopped_with = None

        def start(self):
            self.started = True

        def wait_for_termination(self):
            raise KeyboardInterrupt

        def stop(self, grace):
            self.stopped_with = grace
            return StopResult()

    server = InterruptingServer()
    monkeypatch.setattr(
        run_grpc_server,
        "create_server",
        lambda host, port, workers: (server, f"{host}:{port}"),
    )
    output = StringIO()
    command = run_grpc_server.Command(stdout=output)

    command.handle(host="127.0.0.1", port=50051, workers=4)

    assert server.started is True
    assert server.stopped_with == 5
    assert "gRPC server listening" in output.getvalue()
