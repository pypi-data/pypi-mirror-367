"""
vaulter ライブラリのテスト
"""

import unittest
import json
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vaulter import (
    Vault, 
    VaultError, 
    VaultDecryptionError, 
    VaultFormatError, 
    VaultKeyError,
    generate_key,
    encrypt,
    decrypt,
    secure_clear
)


class TestVault(unittest.TestCase):
    """Vaultクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # グローバルキーをクリア
        Vault.clear_global_key()
    
    def test_vault_creation(self):
        """Vault作成のテスト"""
        # 基本的な作成
        vault = Vault("TEST_KEY")
        self.assertEqual(vault.name, "TEST_KEY")
        self.assertIsNone(vault._ciphertext)
        
        # 初期値付きで作成
        vault = Vault("API_KEY", value="secret_value")
        self.assertEqual(vault.get(), "secret_value")
    
    def test_set_and_get(self):
        """set/getメソッドのテスト"""
        vault = Vault("TEST_KEY")
        
        # 値を設定
        vault.set("test_secret")
        self.assertEqual(vault.get(), "test_secret")
        
        # 値を更新
        vault.set("new_secret")
        self.assertEqual(vault.get(), "new_secret")
        
        # 空文字列
        vault.set("")
        self.assertEqual(vault.get(), "")
    
    def test_invalid_value_type(self):
        """不正な値の型のテスト"""
        vault = Vault("TEST_KEY")
        
        with self.assertRaises(ValueError):
            vault.set(123)  # 数値は不可
        
        with self.assertRaises(ValueError):
            vault.set(None)  # Noneは不可
    
    def test_json_serialization(self):
        """JSONシリアライズのテスト"""
        # データを作成
        vault = Vault("API_KEY", value="secret_api_key")
        
        # JSONに変換
        json_data = vault.to_json()
        data = json.loads(json_data)
        
        # 必須フィールドの確認
        self.assertIn("name", data)
        self.assertIn("ciphertext", data)
        self.assertIn("nonce", data)
        self.assertIn("tag", data)
        self.assertEqual(data["name"], "API_KEY")
        
        # JSONから復元（同じキーを使用）
        restored = Vault.from_json(json_data, key=vault._key)
        self.assertEqual(restored.name, "API_KEY")
        self.assertEqual(restored.get(), "secret_api_key")
    
    def test_json_with_different_keys(self):
        """異なるキーでのJSON復元テスト"""
        # キー1で暗号化
        key1 = generate_key()
        vault1 = Vault("TEST", value="secret", key=key1)
        json_data = vault1.to_json()
        
        # キー2で復元（失敗するはず）
        key2 = generate_key()
        vault2 = Vault("TEST", key=key2)
        vault2._ciphertext = vault1._ciphertext
        vault2._nonce = vault1._nonce
        vault2._tag = vault1._tag
        
        with self.assertRaises(VaultDecryptionError):
            vault2.get()
    
    def test_invalid_json_format(self):
        """不正なJSONフォーマットのテスト"""
        # 不完全なJSON
        with self.assertRaises(VaultFormatError):
            Vault.from_json('{"name": "test"}')
        
        # 不正なJSON
        with self.assertRaises(VaultFormatError):
            Vault.from_json('invalid json')
    
    def test_wipe_functionality(self):
        """wipeメソッドのテスト"""
        vault = Vault("TEST", value="secret")
        
        # データが存在することを確認
        self.assertIsNotNone(vault._ciphertext)
        self.assertIsNotNone(vault._nonce)
        self.assertIsNotNone(vault._tag)
        
        # wipe実行
        vault.wipe()
        
        # データがクリアされていることを確認
        self.assertIsNone(vault._ciphertext)
        self.assertIsNone(vault._nonce)
        self.assertIsNone(vault._tag)
        
        # 取得しようとするとエラー
        with self.assertRaises(VaultDecryptionError):
            vault.get()
    
    def test_global_key(self):
        """グローバルキーのテスト"""
        # グローバルキーを設定
        global_key = generate_key()
        Vault.set_global_key(global_key)
        
        # グローバルキーを使用してVaultを作成
        vault1 = Vault("TEST1", value="secret1")
        vault2 = Vault("TEST2", value="secret2")
        
        # 両方とも同じキーを使用していることを確認
        self.assertEqual(vault1._key, vault2._key)
        self.assertEqual(vault1._key, global_key)
        
        # 正常に動作することを確認
        self.assertEqual(vault1.get(), "secret1")
        self.assertEqual(vault2.get(), "secret2")
        
        # JSONシリアライズ/復元のテスト
        json_data = vault1.to_json()
        restored = Vault.from_json(json_data)  # グローバルキーが使用される
        self.assertEqual(restored.get(), "secret1")
        
        # グローバルキーをクリア
        Vault.clear_global_key()
        
        # 新しいVaultは新しいキーを使用
        vault3 = Vault("TEST3", value="secret3")
        self.assertNotEqual(vault3._key, global_key)
    
    def test_generate_key(self):
        """キー生成のテスト"""
        key1 = Vault.generate_key()
        key2 = Vault.generate_key()
        
        # キーサイズの確認
        self.assertEqual(len(key1), 32)
        self.assertEqual(len(key2), 32)
        
        # キーが異なることを確認
        self.assertNotEqual(key1, key2)
    
    def test_custom_key(self):
        """カスタムキーのテスト"""
        custom_key = generate_key()
        vault = Vault("TEST", value="secret", key=custom_key)
        
        self.assertEqual(vault._key, custom_key)
        self.assertEqual(vault.get(), "secret")
    
    def test_invalid_key_size(self):
        """不正なキーサイズのテスト"""
        # 短すぎるキー
        short_key = b"short"
        with self.assertRaises(VaultKeyError):
            Vault("TEST", key=short_key)
        
        # 長すぎるキー
        long_key = b"x" * 64
        with self.assertRaises(VaultKeyError):
            Vault("TEST", key=long_key)
    
    def test_empty_vault_get(self):
        """空のVaultからの取得テスト"""
        vault = Vault("TEST")
        with self.assertRaises(VaultDecryptionError):
            vault.get()
    
    def test_empty_vault_to_json(self):
        """空のVaultのJSON変換テスト"""
        vault = Vault("TEST")
        with self.assertRaises(VaultFormatError):
            vault.to_json()


class TestCrypto(unittest.TestCase):
    """暗号化機能のテスト"""
    
    def test_encrypt_decrypt(self):
        """暗号化/復号のテスト"""
        key = generate_key()
        plaintext = "test_secret"
        
        # 暗号化
        ciphertext, nonce, tag = encrypt(plaintext, key)
        
        # 復号
        decrypted = decrypt(ciphertext, nonce, tag, key)
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_decrypt_empty_string(self):
        """空文字列の暗号化/復号テスト"""
        key = generate_key()
        plaintext = ""
        
        ciphertext, nonce, tag = encrypt(plaintext, key)
        decrypted = decrypt(ciphertext, nonce, tag, key)
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_decrypt_unicode(self):
        """Unicode文字列の暗号化/復号テスト"""
        key = generate_key()
        plaintext = "テスト文字列🎉"
        
        ciphertext, nonce, tag = encrypt(plaintext, key)
        decrypted = decrypt(ciphertext, nonce, tag, key)
        self.assertEqual(decrypted, plaintext)
    
    def test_wrong_key_decrypt(self):
        """間違ったキーでの復号テスト"""
        key1 = generate_key()
        key2 = generate_key()
        plaintext = "test_secret"
        
        ciphertext, nonce, tag = encrypt(plaintext, key1)
        
        with self.assertRaises(VaultDecryptionError):
            decrypt(ciphertext, nonce, tag, key2)
    
    def test_invalid_key_size(self):
        """不正なキーサイズのテスト"""
        short_key = b"short"
        plaintext = "test"
        
        with self.assertRaises(VaultKeyError):
            encrypt(plaintext, short_key)
        
        with self.assertRaises(VaultKeyError):
            decrypt(b"test", b"nonce", b"tag", short_key)


class TestUtils(unittest.TestCase):
    """ユーティリティ機能のテスト"""
    
    def test_secure_clear_bytes(self):
        """バイトデータの安全なクリアテスト"""
        data = b"test_data"
        secure_clear(data)
        # クリア後もデータは存在するが、内容は変更されている可能性がある
    
    def test_secure_clear_string(self):
        """文字列データの安全なクリアテスト"""
        data = "test_string"
        secure_clear(data)
        # クリア後もデータは存在するが、内容は変更されている可能性がある


if __name__ == "__main__":
    unittest.main() 