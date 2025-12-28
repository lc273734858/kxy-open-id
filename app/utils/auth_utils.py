from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import binascii
from pyDes import des, CBC, PAD_PKCS5
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS, DES_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(username: str) -> str:
    """Create a JWT token for a user"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    to_encode = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[str]:
    """Decode a JWT token and return the username"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


class DesEncryption:
    """DES encryption utility using CBC mode with PKCS5 padding"""

    def __init__(self, key: str = None):
        """
        Initialize DES encryption with a key

        Args:
            key: Encryption key (8 bytes). If not provided, uses DES_KEY from config
        """
        self.key = key if key else DES_KEY
        if len(self.key) != 8:
            raise ValueError("DES key must be exactly 8 bytes")

    def encrypt(self, password: str) -> str:
        """
        Encrypt a password using DES algorithm

        Args:
            password: Plain text password to encrypt

        Returns:
            Hex-encoded encrypted string
        """
        iv = self.key
        k = des(self.key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        # Encode string to bytes for pyDes compatibility
        password_bytes = password.encode('utf-8')
        en = k.encrypt(password_bytes, padmode=PAD_PKCS5)
        return binascii.b2a_hex(en).decode('utf-8')

    def decrypt(self, text: str) -> str:
        """
        Decrypt an encrypted text

        Args:
            text: Hex-encoded encrypted string

        Returns:
            Decrypted plain text string
        """
        iv = self.key
        k = des(self.key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        de = k.decrypt(binascii.a2b_hex(text), padmode=PAD_PKCS5)
        return de.decode('utf-8')


# Global instance for DES encryption
des_crypto = DesEncryption()


def encrypt_password(password: str) -> str:
    """
    Encrypt a password using DES encryption

    Args:
        password: Plain text password

    Returns:
        Encrypted password (hex-encoded)
    """
    return des_crypto.encrypt(password)


def decrypt_password(encrypted_text: str) -> str:
    """
    Decrypt an encrypted password

    Args:
        encrypted_text: Hex-encoded encrypted string

    Returns:
        Decrypted plain text password
    """
    return des_crypto.decrypt(encrypted_text)
