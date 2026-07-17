"""Integration tests for the learning-focused gRPC login API."""

from concurrent import futures

import grpc
import pytest

from services.grpc_api import authentication_pb2, authentication_pb2_grpc
from services.grpc_api.authentication_service import AuthenticationService


@pytest.fixture
def grpc_stub():
    """Run an in-process gRPC server and provide its generated client stub."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    authentication_pb2_grpc.add_AuthenticationServiceServicer_to_server(
        AuthenticationService(), server
    )
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    try:
        yield authentication_pb2_grpc.AuthenticationServiceStub(channel)
    finally:
        channel.close()
        server.stop(grace=None).wait()


@pytest.mark.django_db(transaction=True)
def test_grpc_login_returns_tokens_and_user(grpc_stub, staff_user):
    """Verify valid credentials return tokens and the matching identity."""
    response = grpc_stub.Login(
        authentication_pb2.LoginRequest(
            username="admin",
            password="Admin@12345",  # nosec B106
        )
    )

    assert response.success is True
    assert response.message == "Logged in successfully."
    assert response.access_token
    assert response.refresh_token
    assert response.user_id == str(staff_user.id)
    assert response.username == "admin"
    assert response.email == "admin@example.com"


@pytest.mark.django_db(transaction=True)
def test_grpc_login_rejects_invalid_credentials(grpc_stub, staff_user):
    """Verify an incorrect password uses the gRPC authentication status."""
    with pytest.raises(grpc.RpcError) as error:
        grpc_stub.Login(
            authentication_pb2.LoginRequest(
                username="admin",
                password="incorrect",  # nosec B106
            )
        )

    assert error.value.code() == grpc.StatusCode.UNAUTHENTICATED
    assert error.value.details() == "Invalid username or password."


@pytest.mark.django_db(transaction=True)
def test_grpc_login_requires_both_fields(grpc_stub):
    """Verify an incomplete protobuf request is rejected as invalid input."""
    with pytest.raises(grpc.RpcError) as error:
        grpc_stub.Login(authentication_pb2.LoginRequest(username="admin"))

    assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert error.value.details() == "Username and password are required."
