"""
vaulter ライブラリのコア機能
Vaultクラスとその関連機能を提供
"""

import json
import os
from typing import Optional, Dict, Any
from .crypto import encrypt, decrypt, generate_key, encode_base64, decode_base64
from .utils import secure_clear, secure_delete
from .exceptions import VaultDecryptionError, VaultFormatError, VaultKeyError


class Vault:
    """
    機密情報を自動暗号化して管理するクラス
    メモリ上でも平文を保持せず、アクセス時のみ一時復号
    """
    
    # グローバルキー（プロセス全体で共有）
    _global_key: Optional[bytes] = None
    
    def __init__(self, name: str, value: Optional[str] = None, key: Optional[bytes] = None):
        """
        Vaultインスタンスを初期化
        
        Args:
            name: 識別名（例: "API_KEY"）
            value: 初期値（任意）
            key: AESキー（指定しない場合は自動生成またはグローバルキー使用）
        """
        self.name = name
        self._ciphertext: Optional[bytes] = None
        self._nonce: Optional[bytes] = None
        self._tag: Optional[bytes] = None
        
        # キーの設定
        if key is not None:
            if len(key) != 32:
                raise VaultKeyError("AES-256キーは32バイトである必要があります")
            self._key = key
        elif Vault._global_key is not None:
            self._key = Vault._global_key
        else:
            self._key = generate_key()
        
        # 初期値が指定されている場合は暗号化
        if value is not None:
            self.set(value)
    
    def set(self, value: str) -> None:
        """
        値を暗号化して保存
        
        Args:
            value: 暗号化する文字列
        """
        if not isinstance(value, str):
            raise ValueError("値は文字列である必要があります")
        
        # 既存のデータをクリア
        self._clear_encrypted_data()
        
        # 暗号化
        ciphertext, nonce, tag = encrypt(value, self._key)
        
        # 暗号化データを保存
        self._ciphertext = ciphertext
        self._nonce = nonce
        self._tag = tag
    
    def get(self) -> str:
        """
        一時的に復号して値を取得
        
        Returns:
            str: 復号された値
            
        Raises:
            VaultDecryptionError: 復号に失敗した場合
        """
        if self._ciphertext is None or self._nonce is None or self._tag is None:
            raise VaultDecryptionError("暗号化されたデータが存在しません")
        
        try:
            # 復号
            decrypted_value = decrypt(self._ciphertext, self._nonce, self._tag, self._key)
            return decrypted_value
        except Exception as e:
            raise VaultDecryptionError(f"復号に失敗しました: {str(e)}")
    
    def to_json(self) -> str:
        """
        暗号化データとメタ情報をJSON文字列で出力
        
        Returns:
            str: JSON文字列
        """
        if self._ciphertext is None or self._nonce is None or self._tag is None:
            raise VaultFormatError("暗号化されたデータが存在しません")
        
        data = {
            "name": self.name,
            "ciphertext": encode_base64(self._ciphertext),
            "nonce": encode_base64(self._nonce),
            "tag": encode_base64(self._tag)
        }
        
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str, key: Optional[bytes] = None) -> 'Vault':
        """
        JSONから復元してVaultインスタンスを生成
        
        Args:
            json_str: JSON文字列
            key: 復号に使用するキー（指定しない場合はグローバルキーまたは新規生成）
            
        Returns:
            Vault: 復元されたVaultインスタンス
            
        Raises:
            VaultFormatError: JSONフォーマットが不正な場合
        """
        try:
            data = json.loads(json_str)
            
            # 必須フィールドのチェック
            required_fields = ["name", "ciphertext", "nonce", "tag"]
            for field in required_fields:
                if field not in data:
                    raise VaultFormatError(f"必須フィールド '{field}' が存在しません")
            
            # Base64デコード
            ciphertext = decode_base64(data["ciphertext"])
            nonce = decode_base64(data["nonce"])
            tag = decode_base64(data["tag"])
            
            # Vaultインスタンスを作成（キーを指定）
            vault = cls(data["name"], key=key)
            vault._ciphertext = ciphertext
            vault._nonce = nonce
            vault._tag = tag
            
            return vault
            
        except json.JSONDecodeError as e:
            raise VaultFormatError(f"JSONデコードに失敗しました: {str(e)}")
        except Exception as e:
            raise VaultFormatError(f"JSON復元に失敗しました: {str(e)}")
    
    def wipe(self) -> None:
        """
        内部メモリを完全クリア（鍵・データ）
        """
        self._clear_encrypted_data()
        self._clear_key()
    
    def _clear_encrypted_data(self) -> None:
        """暗号化データをクリア"""
        if self._ciphertext is not None:
            secure_clear(self._ciphertext)
            self._ciphertext = None
        
        if self._nonce is not None:
            secure_clear(self._nonce)
            self._nonce = None
        
        if self._tag is not None:
            secure_clear(self._tag)
            self._tag = None
    
    def _clear_key(self) -> None:
        """暗号鍵をクリア"""
        if hasattr(self, '_key') and self._key is not None:
            secure_clear(self._key)
            self._key = None
    
    @classmethod
    def generate_key(cls) -> bytes:
        """
        安全なランダムAESキーを生成
        
        Returns:
            bytes: 32バイトのAES-256キー
        """
        return generate_key()
    
    @classmethod
    def set_global_key(cls, key: bytes) -> None:
        """
        全Vaultインスタンスで共有するグローバルキーを設定
        
        Args:
            key: AES-256キー（32バイト）
        """
        if len(key) != 32:
            raise VaultKeyError("AES-256キーは32バイトである必要があります")
        
        # 既存のグローバルキーをクリア
        if cls._global_key is not None:
            secure_clear(cls._global_key)
        
        cls._global_key = key
    
    @classmethod
    def clear_global_key(cls) -> None:
        """グローバルキーをクリア"""
        if cls._global_key is not None:
            secure_clear(cls._global_key)
            cls._global_key = None
    
    def __str__(self) -> str:
        """文字列表現"""
        return f"Vault(name='{self.name}', encrypted={self._ciphertext is not None})"
    
    def __repr__(self) -> str:
        """詳細な文字列表現"""
        return f"Vault(name='{self.name}', encrypted={self._ciphertext is not None})"
    
    def __del__(self):
        """デストラクタ：メモリクリア"""
        self.wipe() 