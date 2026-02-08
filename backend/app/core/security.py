from passlib.context import CryptContext
import hashlib

# Configure the password context to use pbkdf2_sha256 as it's more reliable
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Apply the same transformation that was used during hashing
    if len(plain_password.encode('utf-8')) > 72:
        # Use SHA-256 hash of the password as a workaround for length limitation
        truncated_password = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    else:
        truncated_password = plain_password
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes if needed to comply with bcrypt limitations
    # Although we're using pbkdf2_sha256, this is a safe practice
    if len(password.encode('utf-8')) > 72:
        # Use SHA-256 hash of the password as a workaround for length limitation
        truncated_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    else:
        truncated_password = password
    return pwd_context.hash(truncated_password)
