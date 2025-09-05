# totp_handler.py
import pyotp
import time
from typing import Optional


class TOTPHandler:
    """2FA（TOTP）処理クラス"""

    def get_totp_code(self, secret_key: str) -> Optional[str]:
        """シークレットキーからTOTPコードを生成"""
        if not secret_key or secret_key == "":
            return None

        try:
            # スペースとハイフンを削除
            secret_key = secret_key.replace(" ", "").replace("-", "")

            # TOTPオブジェクトを作成
            totp = pyotp.TOTP(secret_key)

            # 現在の6桁コードを生成
            code = totp.now()

            # 残り有効時間を計算
            remaining = 30 - (int(time.time()) % 30)
            print(f"  → 2FAコード: {code} (残り{remaining}秒)")

            # 5秒以下なら新しいコードを待つ
            if remaining <= 5:
                print(f"  → 新しいコードを待機中...")
                time.sleep(remaining + 1)
                code = totp.now()
                print(f"  → 新コード: {code}")

            return code

        except Exception as e:
            print(f"  ✗ 2FAコード生成エラー: {str(e)[:50]}")
            return None
