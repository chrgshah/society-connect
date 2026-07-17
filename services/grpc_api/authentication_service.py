"""Implement the gRPC version of the login operation."""

import grpc

from services.factories.authentication import AuthenticationFactory
from services.grpc_api import authentication_pb2, authentication_pb2_grpc
from services.serializers.authentication import LoginSerializer
from services.shared.logger import logger


class AuthenticationService(authentication_pb2_grpc.AuthenticationServiceServicer):
    """Expose existing authentication behavior through gRPC."""

    def Login(self, request, context):  # noqa: N802 - protobuf defines the RPC name
        """Validate credentials and return a JWT pair to the gRPC client."""
        if not request.username.strip() or not request.password:
            logger.warning(
                "[SOCIETY_CONNECT] event=grpc_login_rejected reason=missing_credentials"
            )
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Username and password are required.",
            )

        serializer = LoginSerializer(
            data={"username": request.username, "password": request.password}
        )
        if not serializer.is_valid():
            logger.warning(
                "[SOCIETY_CONNECT] event=grpc_login_rejected reason=invalid_credentials"
            )
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Invalid username or password.",
            )

        user = serializer.validated_data["user"]
        tokens = AuthenticationFactory.login_user(user)
        logger.info("[SOCIETY_CONNECT] event=grpc_login_succeeded user_id=%s", user.id)
        return authentication_pb2.LoginResponse(
            success=True,
            message="Logged in successfully.",
            access_token=tokens["access"],
            refresh_token=tokens["refresh"],
            user_id=str(user.id),
            username=user.username,
            email=user.email,
        )
