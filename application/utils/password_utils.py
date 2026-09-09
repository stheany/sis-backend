"""
Secure password hashing using bcrypt.
Includes legacy SHA-256 fallback to support migration of existing accounts.
"""
import hashlib
import bcrypt


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, stored: str) -> bool:
    """
    Verify a plaintext password against a stored hash.
    Supports both bcrypt hashes and legacy SHA-256 hashes for migration.
    """
    if stored.startswith(("$2b$", "$2a$", "$2y$")):
        return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
    # Legacy SHA-256 path — accounts not yet migrated
    return hashlib.sha256(plain.encode("utf-8")).hexdigest() == stored
