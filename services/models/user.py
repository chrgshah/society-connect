"""Application user model and its creation manager."""

from django.db import models

from services.shared.password import hash_string, verify_hash

from .base import BaseModel, SoftDeleteManager


class UserManager(SoftDeleteManager):
    """Create users while normalizing identity fields and hashing passwords."""

    def create_user(self, username, email, password=None, **extra_fields):
        """Validate required fields and persist a new user."""
        if not username:
            raise ValueError("The username is required.")
        if not email:
            raise ValueError("The email address is required.")
        if not password:
            raise ValueError("The password is required.")

        user = self.model(
            username=username.strip(),
            email=email.strip().lower(),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(BaseModel):
    """Represent an authenticated application user."""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    class Meta:
        """Order users by username by default."""

        ordering = ["username"]

    def set_password(self, raw_password: str) -> None:
        """Hash and store a raw password without saving the model."""
        self.password = hash_string(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Return whether a raw password matches the stored digest."""
        return verify_hash(raw_password, self.password)

    @property
    def is_authenticated(self) -> bool:
        """Identify loaded user instances as authenticated to Django/DRF."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Identify loaded user instances as non-anonymous."""
        return False

    def __str__(self):
        """Return the username used to display this user."""
        return self.username
