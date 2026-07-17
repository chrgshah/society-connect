"""Select and load settings for the configured deployment environment."""

import os

# Start with base settings
from .base import *  # noqa: F403, F401

# Determine environment and load appropriate overrides
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev").lower()

if ENVIRONMENT == "prod":
    from .prod import *  # noqa: F403, F401
elif ENVIRONMENT == "stage":
    from .stage import *  # noqa: F403, F401
elif ENVIRONMENT == "dev":
    from .dev import *  # noqa: F403, F401
else:
    raise ValueError(
        f"Invalid ENVIRONMENT value: {ENVIRONMENT}. "
        "Must be one of: 'dev', 'stage', 'prod'"
    )
