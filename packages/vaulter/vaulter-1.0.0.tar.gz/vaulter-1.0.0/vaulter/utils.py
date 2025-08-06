"""
vaulter ライブラリ用のメモリ管理ユーティリティ
安全なメモリクリアとゼロ化機能を提供
"""

import array
import ctypes
from typing import Union, Any


def zeroize_bytes(data: bytes) -> None:
    """
    バイトデータをゼロ化（メモリ上で0で上書き）
    
    Args:
        data: ゼロ化するバイトデータ
    """
    if not data:
        return
    
    # bytearrayに変換してゼロ化
    buffer = bytearray(data)
    for i in range(len(buffer)):
        buffer[i] = 0


def zeroize_string(data: str) -> None:
    """
    文字列データをゼロ化（メモリ上で0で上書き）
    
    Args:
        data: ゼロ化する文字列データ
    """
    if not data:
        return
    
    # 文字列をバイトに変換してゼロ化
    buffer = bytearray(data.encode('utf-8'))
    for i in range(len(buffer)):
        buffer[i] = 0


def zeroize_array(arr: array.array) -> None:
    """
    配列データをゼロ化
    
    Args:
        arr: ゼロ化する配列
    """
    if not arr:
        return
    
    for i in range(len(arr)):
        arr[i] = 0


def secure_clear(data: Union[bytes, str, array.array, Any]) -> None:
    """
    データを安全にクリア（ゼロ化）
    
    Args:
        data: クリアするデータ（bytes, str, array.array, その他）
    """
    if data is None:
        return
    
    try:
        if isinstance(data, bytes):
            zeroize_bytes(data)
        elif isinstance(data, str):
            zeroize_string(data)
        elif isinstance(data, array.array):
            zeroize_array(data)
        elif isinstance(data, bytearray):
            for i in range(len(data)):
                data[i] = 0
        elif hasattr(data, '__iter__'):
            # イテラブルオブジェクトの場合
            for item in data:
                secure_clear(item)
    except Exception:
        # ゼロ化に失敗した場合でも例外を出さない
        pass


def secure_delete(data: Union[bytes, str, array.array, Any]) -> None:
    """
    データを安全に削除（クリア後に参照を削除）
    
    Args:
        data: 削除するデータ
    """
    secure_clear(data)
    # 参照を削除（ガベージコレクションに任せる）
    del data


def create_secure_buffer(size: int) -> bytearray:
    """
    安全なバッファを作成（ゼロ初期化）
    
    Args:
        size: バッファサイズ
    
    Returns:
        bytearray: ゼロ初期化されたバッファ
    """
    return bytearray(size)


def secure_copy(source: Union[bytes, str], dest: bytearray) -> None:
    """
    データを安全にコピー（コピー後にソースをゼロ化）
    
    Args:
        source: コピー元データ
        dest: コピー先バッファ
    """
    if isinstance(source, str):
        source_bytes = source.encode('utf-8')
    else:
        source_bytes = source
    
    # コピー
    dest[:len(source_bytes)] = source_bytes
    
    # ソースをゼロ化
    secure_clear(source_bytes)


def get_memory_address(obj: Any) -> int:
    """
    オブジェクトのメモリアドレスを取得（デバッグ用）
    
    Args:
        obj: 対象オブジェクト
    
    Returns:
        int: メモリアドレス
    """
    return id(obj)


def is_memory_locked() -> bool:
    """
    メモリロック機能が利用可能かチェック（Linux mlock対応予定）
    
    Returns:
        bool: メモリロックが利用可能な場合True
    """
    try:
        import ctypes
        import ctypes.util
        
        # Linuxの場合のみmlockをチェック
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
        return hasattr(libc, 'mlock')
    except:
        return False


def lock_memory(address: int, size: int) -> bool:
    """
    メモリをロック（Linux mlock対応予定）
    
    Args:
        address: メモリアドレス
        size: ロックするサイズ
    
    Returns:
        bool: ロック成功時True
    """
    if not is_memory_locked():
        return False
    
    try:
        import ctypes
        import ctypes.util
        
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
        result = libc.mlock(address, size)
        return result == 0
    except:
        return False 