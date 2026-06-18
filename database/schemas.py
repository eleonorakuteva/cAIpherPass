"""Schema definitions for cAIpherPass database entities."""


class VaultEntry:
    """Schema for vault entries — defines fields and validation rules.

    Fields:
        service_name: str (required) — name of the service (e.g., "Gmail")
        username: str (required) — username or email for this service
        encrypted_password: bytes (required) — Fernet-encrypted password
        created_at: str (required) — ISO timestamp when entry was created
        tags: str | None (optional) — comma-separated tags for searching
    """

    @staticmethod
    def validate(service_name, username, encrypted_password, created_at, tags=None):
        """Validate a vault entry against the schema.

        Raises ValueError with a clear message if validation fails.

        Args:
            service_name: Name of the service
            username: Username/email for this service
            encrypted_password: Encrypted password (bytes from Fernet)
            created_at: ISO timestamp string
            tags: Optional tags string

        Raises:
            ValueError: If any field violates the schema
        """
        # Validate service_name
        if not isinstance(service_name, str):
            raise ValueError("service_name must be a string")
        if not service_name.strip():
            raise ValueError("service_name cannot be empty")

        # Validate username
        if not isinstance(username, str):
            raise ValueError("username must be a string")
        if not username.strip():
            raise ValueError("username cannot be empty")

        # Validate encrypted_password
        if not isinstance(encrypted_password, bytes):
            raise ValueError("encrypted_password must be bytes")
        if len(encrypted_password) == 0:
            raise ValueError("encrypted_password cannot be empty")

        # Validate created_at
        if not isinstance(created_at, str):
            raise ValueError("created_at must be a string")
        if not created_at.strip():
            raise ValueError("created_at cannot be empty")

        # Validate tags (optional, but if provided must be string)
        if tags is not None:
            if not isinstance(tags, str):
                raise ValueError("tags must be a string or None")
            # Note: tags can be empty string (valid), just not non-string types
