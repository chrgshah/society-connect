"""Run the local Society Connect gRPC server."""

from concurrent import futures

import grpc
from django.core.management.base import BaseCommand

from services.grpc_api import authentication_pb2_grpc
from services.grpc_api.authentication_service import AuthenticationService
from services.shared.logger import logger


def create_server(host: str, port: int, workers: int):
    """Build and bind a gRPC server containing the authentication service."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
    authentication_pb2_grpc.add_AuthenticationServiceServicer_to_server(
        AuthenticationService(), server
    )
    address = f"{host}:{port}"
    if server.add_insecure_port(address) == 0:
        raise RuntimeError(f"Could not bind the gRPC server to {address}.")
    return server, address


class Command(BaseCommand):
    """Start the gRPC server as a foreground development process."""

    help = "Run the local gRPC API server."

    def add_arguments(self, parser):
        """Define network and worker-count command options."""
        parser.add_argument("--host", default="127.0.0.1")
        parser.add_argument("--port", type=int, default=50051)
        parser.add_argument("--workers", type=int, default=4)

    def handle(self, *args, **options):
        """Run until interrupted, then stop accepting RPCs cleanly."""
        server, address = create_server(
            options["host"], options["port"], options["workers"]
        )
        server.start()
        logger.info("[SOCIETY_CONNECT] event=grpc_server_started address=%s", address)
        self.stdout.write(self.style.SUCCESS(f"gRPC server listening on {address}"))
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("[SOCIETY_CONNECT] event=grpc_server_stopping")
            server.stop(grace=5).wait()
