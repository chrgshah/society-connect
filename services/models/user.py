from django.db import models

from services.shared.password import hash_string, verify_hash

from .base import BaseModel


class UserManager(models.Manager):
    def create_user(self, username, email, password=None, **extra_fields):
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
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    class Meta:
        ordering = ["username"]

    def set_password(self, raw_password: str) -> None:
        self.password = hash_string(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return verify_hash(raw_password, self.password)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def __str__(self):
        return self.username
