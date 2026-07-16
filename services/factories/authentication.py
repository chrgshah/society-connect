from core.authentication.jwt_service import create_tokens, invalidate_session


class AuthenticationFactory:
    @staticmethod
    def login_user(user):
        return create_tokens(user)

    @staticmethod
    def refresh_token(refresh_token):
        from core.authentication.jwt_service import refresh_tokens

        return refresh_tokens(refresh_token)

    @staticmethod
    def logout_user(user_id: int, jti: str):
        invalidate_session(user_id, jti)
