"""Call the local login RPC from an interactive command-line client."""

from getpass import getpass

import grpc
from django.core.management.base import BaseCommand, CommandError

from services.grpc_api import authentication_pb2, authentication_pb2_grpc


class Command(BaseCommand):
    """Send credentials to the gRPC server and display its response."""

    help = "Log in through the local gRPC API."

    def add_arguments(self, parser):
        """Accept the username and optional server address."""
        parser.add_argument("username")
        parser.add_argument("--address", default="127.0.0.1:50051")

    def handle(self, *args, **options):
        """Prompt securely for a password and invoke the Login RPC."""
        password = getpass("Password: ")
        try:
            with grpc.insecure_channel(options["address"]) as channel:
                stub = authentication_pb2_grpc.AuthenticationServiceStub(channel)
                response = stub.Login(
                    authentication_pb2.LoginRequest(
                        username=options["username"], password=password
                    ),
                    timeout=5,
                )
        except grpc.RpcError as exc:
            raise CommandError(
                f"gRPC login failed ({exc.code().name}): {exc.details()}"
            ) from exc

        self.stdout.write(self.style.SUCCESS(response.message))
        self.stdout.write(
            f"User: {response.username} <{response.email}> ({response.user_id})"
        )
        self.stdout.write(f"Access token: {response.access_token}")
        self.stdout.write(f"Refresh token: {response.refresh_token}")
