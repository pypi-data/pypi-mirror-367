"""
vaulter ライブラリ用のカスタム例外クラス
"""


class VaultError(Exception):
    """vaulterライブラリの基底例外クラス"""
    pass


class VaultDecryptionError(VaultError):
    """復号失敗時の例外"""
    pass


class VaultFormatError(VaultError):
    """不正フォーマット時の例外"""
    pass


class VaultKeyError(VaultError):
    """暗号鍵関連のエラー"""
    pass 