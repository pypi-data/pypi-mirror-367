import os
import base64
from cryptography.fernet                       import Fernet, InvalidToken
from cryptography.hazmat.backends              import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from kres.utils.logger import Logger


class TokenEncryption:
    def __init__(self, log: str = "INFO") -> None:
        self._fernet: Fernet | None = None
        self._salt: bytes | None    = None
        self.logger                 = Logger(log)

    def _get_random_salt(self) -> bytes:
        salt = os.urandom(16) 
        self.logger.debug("Generated random salt for encryption.")
        return salt

    def _derive_key(self, paraphrase: str, salt: bytes) -> bytes:
        self.logger.debug("Deriving key from paraphrase and salt.")
        kdf = Scrypt(
            salt    = salt,
            length  = 32,
            n       = 2**14,
            r       = 8,
            p       = 1,
            backend = default_backend()
        )
        key = kdf.derive(paraphrase.encode())
        self.logger.debug("Key derived and encoded.")
        return base64.urlsafe_b64encode(key) 

    def login(self, paraphrase: str, token: str) -> bytes:
        self.logger.debug("Starting login process for token encryption.")
        if self._salt is None:
            self._salt = self._get_random_salt()

        key            = self._derive_key(paraphrase, self._salt)
        self._fernet   = Fernet(key)
        encryptedToken = self._fernet.encrypt(token.encode())
        self.logger.info("Token encrypted successfully.")

        return encryptedToken

    def decryptToken(self, token: bytes) -> str:
        self.logger.debug("Attempting to decrypt token.")
        if not self._fernet:
            self.logger.error("Decryption failed: No key loaded. Please login first.")
            raise Exception("Decryption failed: No key loaded. Please login first.")

        try:
            self.logger.debug("Token decrypted successfully.")
            return self._fernet.decrypt(token).decode()
        except InvalidToken:
            self.logger.error("Invalid paraphrase or corrupted data during decryption.")
            raise Exception("Invalid paraphrase or corrupted data during decryption.")
        
    def deleteKey(self) -> bool:
        self.logger.debug("Deleting encryption key and salt from memory.")
        if self._fernet:
            del self._fernet
            del self._salt
            self._fernet = None
            self._salt   = None
            self.logger.debug("Deleting encryption key and salt from memory.")
        return True

    def status(self) -> bool:
        status = self._fernet is not None
        self.logger.debug(f"Encryption key loaded: {status}")
        return status