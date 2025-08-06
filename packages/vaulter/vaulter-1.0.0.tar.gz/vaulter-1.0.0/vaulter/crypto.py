"""
vaulter ライブラリ用の暗号化ユーティリティ
AES-256-GCM暗号化を提供
"""

import base64
import os
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .exceptions import VaultDecryptionError, VaultKeyError


def generate_key() -> bytes:
    """
    安全なランダムAES-256キーを生成
    
    Returns:
        bytes: 32バイトのAES-256キー
    """
    return os.urandom(32)


def generate_nonce() -> bytes:
    """
    AES-GCM用の96ビットNonceを生成
    
    Returns:
        bytes: 12バイトのNonce
    """
    return os.urandom(12)


def encrypt(data: str, key: bytes) -> Tuple[bytes, bytes, bytes]:
    """
    AES-256-GCMでデータを暗号化
    
    Args:
        data: 暗号化する文字列
        key: AES-256キー（32バイト）
    
    Returns:
        Tuple[bytes, bytes, bytes]: (暗号文, nonce, tag)
    
    Raises:
        VaultKeyError: キーが不正な場合
    """
    if len(key) != 32:
        raise VaultKeyError("AES-256キーは32バイトである必要があります")
    
    try:
        # AES-GCM暗号化オブジェクトを作成
        aesgcm = AESGCM(key)
        
        # データをバイトに変換
        plaintext = data.encode('utf-8')
        
        # Nonceを生成
        nonce = generate_nonce()
        
        # 暗号化
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # 暗号文とタグを分離（最後の16バイトがタグ）
        ciphertext_only = ciphertext[:-16]
        tag = ciphertext[-16:]
        
        return ciphertext_only, nonce, tag
        
    except Exception as e:
        raise VaultDecryptionError(f"暗号化に失敗しました: {str(e)}")


def decrypt(ciphertext: bytes, nonce: bytes, tag: bytes, key: bytes) -> str:
    """
    AES-256-GCMでデータを復号
    
    Args:
        ciphertext: 暗号文
        nonce: Nonce
        tag: 認証タグ
        key: AES-256キー（32バイト）
    
    Returns:
        str: 復号された文字列
    
    Raises:
        VaultDecryptionError: 復号に失敗した場合
        VaultKeyError: キーが不正な場合
    """
    if len(key) != 32:
        raise VaultKeyError("AES-256キーは32バイトである必要があります")
    
    try:
        # AES-GCM暗号化オブジェクトを作成
        aesgcm = AESGCM(key)
        
        # 暗号文とタグを結合
        full_ciphertext = ciphertext + tag
        
        # 復号
        plaintext = aesgcm.decrypt(nonce, full_ciphertext, None)
        
        # 文字列に変換
        return plaintext.decode('utf-8')
        
    except Exception as e:
        raise VaultDecryptionError(f"復号に失敗しました: {str(e)}")


def encode_base64(data: bytes) -> str:
    """
    バイトデータをBase64エンコード
    
    Args:
        data: エンコードするバイトデータ
    
    Returns:
        str: Base64エンコードされた文字列
    """
    return base64.b64encode(data).decode('utf-8')


def decode_base64(data: str) -> bytes:
    """
    Base64エンコードされた文字列をデコード
    
    Args:
        data: Base64エンコードされた文字列
    
    Returns:
        bytes: デコードされたバイトデータ
    
    Raises:
        VaultFormatError: 不正なBase64フォーマットの場合
    """
    try:
        return base64.b64decode(data.encode('utf-8'))
    except Exception as e:
        raise VaultFormatError(f"Base64デコードに失敗しました: {str(e)}")


def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    パスワードからAES-256キーを導出（PBKDF2使用）
    
    Args:
        password: パスワード
        salt: ソルト（Noneの場合は自動生成）
    
    Returns:
        Tuple[bytes, bytes]: (導出されたキー, ソルト)
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = kdf.derive(password.encode('utf-8'))
    return key, salt 