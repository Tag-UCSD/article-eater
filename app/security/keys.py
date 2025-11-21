#!/usr/bin/env python3
"""
Article Eater v18.4 - Secure API Key Management
Per-user API key storage with Fernet encryption-at-rest
"""

import os
import base64
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class KeyManager:
    """
    Manages per-user API keys with encryption-at-rest
    
    Security properties:
    - Keys encrypted with Fernet (AES-128-CBC + HMAC-SHA256)
    - Master key derived from MASTER_KEY env var
    - Keys never logged in plaintext
    - Masked when returned to user
    
    Usage:
        km = KeyManager()
        
        # Store key
        km.store_key('user123', 'openai', 'sk-proj-abc123...')
        
        # Retrieve key
        key = km.retrieve_key('user123', 'openai')
        
        # Delete key
        km.delete_key('user123', 'openai')
    
    Environment:
        MASTER_KEY: Base64-encoded Fernet key
        Generate with:
            python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    """
    
    def __init__(self, db_path: str = "./ae.db"):
        """
        Initialize with master key from environment
        
        Args:
            db_path: Database path
            
        Raises:
            ValueError: If MASTER_KEY not set or invalid
        """
        self.db_path = db_path
        
        master_key_b64 = os.environ.get('MASTER_KEY')
        if not master_key_b64:
            raise ValueError(
                "MASTER_KEY environment variable not set. "
                "Generate with: python -c 'from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())'"
            )
        
        try:
            from cryptography.fernet import Fernet
            self.cipher = Fernet(master_key_b64.encode())
            logger.info("KeyManager initialized successfully")
        except ImportError:
            raise ValueError(
                "cryptography package not installed. "
                "Install with: pip install cryptography==41.0.7"
            )
        except Exception as e:
            raise ValueError(f"Invalid MASTER_KEY format: {e}")
    
    def encrypt_key(self, api_key: str) -> str:
        """
        Encrypt API key for storage
        
        Args:
            api_key: Plaintext API key from user
            
        Returns:
            Base64-encoded encrypted key
            
        Raises:
            ValueError: If api_key is empty
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        encrypted = self.cipher.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """
        Decrypt API key for use
        
        Args:
            encrypted_key: Base64-encoded encrypted key from database
            
        Returns:
            Plaintext API key
            
        Raises:
            ValueError: If decryption fails
        """
        if not encrypted_key:
            raise ValueError("Encrypted key cannot be empty")
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_key.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Key decryption failed: {e}")
            raise ValueError("Failed to decrypt API key - key may be corrupted")
    
    def mask_key(self, api_key: str) -> str:
        """
        Mask API key for display to user
        Shows first 10 and last 4 characters
        
        Args:
            api_key: Plaintext API key
            
        Returns:
            Masked key (e.g., "sk-proj-abc...xyz")
            
        Examples:
            >>> km.mask_key("sk-proj-abc123xyz789")
            "sk-proj-abc...xyz789"[-4:]
        """
        if not api_key or len(api_key) < 8:
            return "***"
        
        # Show first 10 and last 4 characters
        if len(api_key) <= 14:
            return api_key[:len(api_key)//2] + "***"
        
        return f"{api_key[:10]}...{api_key[-4:]}"
    
    def store_key(
        self, 
        user_id: str, 
        provider: str, 
        api_key: str
    ) -> bool:
        """
        Store encrypted API key for user
        
        Args:
            user_id: User identifier
            provider: API provider (openai, anthropic, google)
            api_key: Plaintext API key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import sqlite3
            
            # Validate inputs
            if not user_id or not provider or not api_key:
                raise ValueError("user_id, provider, and api_key are required")
            
            provider = provider.lower()
            if provider not in ['openai', 'anthropic', 'google']:
                logger.warning(f"Unknown provider: {provider}")
            
            # Encrypt key
            encrypted = self.encrypt_key(api_key)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_api_keys (
                    user_id, provider, encrypted_key, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, provider) DO UPDATE SET
                    encrypted_key = excluded.encrypted_key,
                    updated_at = excluded.updated_at,
                    usage_count = 0
            """, (
                user_id,
                provider,
                encrypted,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Log with masked key
            logger.info(
                f"Stored {provider} key for user {user_id}: {self.mask_key(api_key)}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to store key for user {user_id}: {e}")
            return False
    
    def retrieve_key(self, user_id: str, provider: str) -> Optional[str]:
        """
        Retrieve and decrypt API key for user
        
        Args:
            user_id: User identifier
            provider: API provider
            
        Returns:
            Plaintext API key or None if not found
        """
        try:
            import sqlite3
            
            provider = provider.lower()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT encrypted_key
                FROM user_api_keys
                WHERE user_id = ? AND provider = ?
            """, (user_id, provider))
            
            row = cursor.fetchone()
            
            if row:
                encrypted_key = row[0]
                
                # Update last_used_at and usage_count
                cursor.execute("""
                    UPDATE user_api_keys
                    SET 
                        last_used_at = ?,
                        usage_count = usage_count + 1
                    WHERE user_id = ? AND provider = ?
                """, (datetime.utcnow().isoformat(), user_id, provider))
                
                conn.commit()
                conn.close()
                
                decrypted = self.decrypt_key(encrypted_key)
                logger.info(
                    f"Retrieved {provider} key for user {user_id}: {self.mask_key(decrypted)}"
                )
                return decrypted
            
            conn.close()
            logger.warning(f"No {provider} key found for user {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve key for user {user_id}: {e}")
            return None
    
    def delete_key(self, user_id: str, provider: str) -> bool:
        """
        Delete API key for user
        
        Args:
            user_id: User identifier
            provider: API provider
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import sqlite3
            
            provider = provider.lower()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_api_keys
                WHERE user_id = ? AND provider = ?
            """, (user_id, provider))
            
            deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted > 0:
                logger.info(f"Deleted {provider} key for user {user_id}")
                return True
            else:
                logger.warning(f"No {provider} key to delete for user {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete key for user {user_id}: {e}")
            return False
    
    def list_providers(self, user_id: str) -> list:
        """
        List all providers for which user has stored keys
        
        Args:
            user_id: User identifier
            
        Returns:
            List of provider names
        """
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT provider, created_at, last_used_at, usage_count
                FROM user_api_keys
                WHERE user_id = ?
                ORDER BY provider
            """, (user_id,))
            
            providers = []
            for row in cursor.fetchall():
                providers.append({
                    'provider': row[0],
                    'created_at': row[1],
                    'last_used_at': row[2],
                    'usage_count': row[3]
                })
            
            conn.close()
            return providers
            
        except Exception as e:
            logger.error(f"Failed to list providers for user {user_id}: {e}")
            return []


if __name__ == '__main__':
    # Test key manager
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    # Check for MASTER_KEY
    if 'MASTER_KEY' not in os.environ:
        print("Error: MASTER_KEY environment variable not set")
        print("\nGenerate one with:")
        print("  python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
        print("\nThen set it:")
        print("  export MASTER_KEY=<generated-key>")
        sys.exit(1)
    
    # Run tests
    print("Testing KeyManager...")
    
    km = KeyManager(db_path=":memory:")  # In-memory DB for testing
    
    # Test encryption/decryption
    test_key = "sk-proj-test123456789"
    encrypted = km.encrypt_key(test_key)
    print(f"✓ Encrypted: {encrypted[:20]}...")
    
    decrypted = km.decrypt_key(encrypted)
    assert decrypted == test_key
    print(f"✓ Decrypted correctly")
    
    # Test masking
    masked = km.mask_key(test_key)
    print(f"✓ Masked: {masked}")
    assert "test123" not in masked or "..." in masked
    
    print("\n✅ All tests passed!")
