"""
vaulter - 機密情報自動暗号化ライブラリ

機密情報（APIキー、パスワード、トークン等）を扱う変数を自動的に暗号化し、
メモリ上でも平文を保持しないPythonライブラリです。

特徴:
- 自動暗号化／自動復号（アクセス時のみ一時復号）
- メモリ上での平文保持を最小化
- AES-GCMによる強固な暗号化
- シリアライズ対応（ファイル保存・DB保存時も暗号化状態維持）
- Zeroization（破棄時にメモリクリア）

使用例:
    from vaulter import Vault
    
    # 暗号化されたVaultオブジェクトを作成
    secret = Vault("API_KEY", value="sk_live_abc123")
    
    # 文字列として取得（復号は内部で一時的に行われる）
    print(secret.get())  # "sk_live_abc123"
    
    # 値を更新
    secret.set("new_api_key_456")
    
    # JSONシリアライズ時も暗号化状態を維持
    encrypted_data = secret.to_json()
    
    # 復元
    restored = Vault.from_json(encrypted_data)
    print(restored.get())  # "new_api_key_456"
"""

__version__ = "1.0.0"
__author__ = "vaulter"
__license__ = "MIT"

# メインクラスと例外をエクスポート
from .core import Vault
from .exceptions import (
    VaultError,
    VaultDecryptionError,
    VaultFormatError,
    VaultKeyError
)

# 暗号化ユーティリティをエクスポート
from .crypto import (
    generate_key,
    encrypt,
    decrypt,
    encode_base64,
    decode_base64,
    derive_key_from_password
)

# メモリ管理ユーティリティをエクスポート
from .utils import (
    secure_clear,
    secure_delete,
    create_secure_buffer,
    secure_copy,
    zeroize_bytes,
    zeroize_string
)

__all__ = [
    # メインクラス
    "Vault",
    
    # 例外クラス
    "VaultError",
    "VaultDecryptionError", 
    "VaultFormatError",
    "VaultKeyError",
    
    # 暗号化ユーティリティ
    "generate_key",
    "encrypt",
    "decrypt", 
    "encode_base64",
    "decode_base64",
    "derive_key_from_password",
    
    # メモリ管理ユーティリティ
    "secure_clear",
    "secure_delete",
    "create_secure_buffer",
    "secure_copy",
    "zeroize_bytes",
    "zeroize_string"
] 