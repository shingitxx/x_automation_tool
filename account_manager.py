import os
import json
import csv
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet


class AccountManager:
    """アカウント管理システム"""

    def __init__(self):
        self.data_dir = "data"
        self.config_dir = "config"
        self.cache_dir = "cache"
        self.cookies_dir = os.path.join(self.cache_dir, "cookies")

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)

        self.accounts_file = os.path.join(self.data_dir, "account_status.json")
        self.key_file = os.path.join(self.cache_dir, "encryption.key")

        self._init_encryption()
        self.accounts = self._load_accounts()

    def _init_encryption(self):
        """暗号化キー初期化"""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)

        with open(self.key_file, "rb") as f:
            self.cipher = Fernet(f.read())

    def _load_accounts(self) -> Dict:
        """アカウントデータ読み込み"""
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"accounts": []}

    def _save_accounts(self):
        """アカウントデータ保存"""
        with open(self.accounts_file, "w", encoding="utf-8") as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)

    def import_from_csv(self, csv_path: str = "config/accounts.csv") -> Dict:
        """CSVファイルからアカウント情報をインポート"""
        try:
            if not os.path.exists(csv_path):
                return {"error": "CSVファイルが見つかりません"}

            imported = 0
            skipped = 0
            errors = 0

            with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        email = row.get("アカウントID", "").strip()
                        password = row.get("パスワード", "").strip()
                        proxy_host = row.get("プロキシホスト", "").strip()
                        proxy_port = row.get("プロキシポート", "").strip()
                        proxy_username = row.get("プロキシユーザー", "").strip()
                        proxy_password = row.get("プロキシパスワード", "").strip()
                        secret_key = row.get("シークレットキー", "").strip()  # 追加

                        if not email or not password:
                            errors += 1
                            continue

                        # 既存チェック
                        if any(
                            acc["email"] == email for acc in self.accounts["accounts"]
                        ):
                            skipped += 1
                            continue

                        # 新規アカウント追加
                        next_id = len(self.accounts["accounts"]) + 1

                        account_data = {
                            "id": next_id,
                            "email": email,
                            "password": password,
                            "proxy": {
                                "host": proxy_host,
                                "port": proxy_port,
                                "username": proxy_username,
                                "password": proxy_password,
                            },
                            "secret_key": secret_key,  # 追加
                            "created_at": datetime.now().isoformat(),
                            "status": "not_logged_in",
                        }

                        self.accounts["accounts"].append(account_data)
                        imported += 1

                    except Exception as e:
                        errors += 1
                        continue

            self._save_accounts()

            return {"imported": imported, "skipped": skipped, "errors": errors}

        except Exception as e:
            return {"error": str(e)}

    def _account_exists(self, email: str) -> bool:
        """アカウント存在確認"""
        return any(acc["email"] == email for acc in self.accounts["accounts"])

    def _get_next_id(self) -> int:
        """次のアカウントID取得"""
        if not self.accounts["accounts"]:
            return 1
        return max(acc["id"] for acc in self.accounts["accounts"]) + 1

    def get_account_by_id(self, account_id: int) -> Optional[Dict]:
        """IDでアカウント取得"""
        for account in self.accounts["accounts"]:
            if account["id"] == account_id:
                # パスワードを復号化
                decrypted_account = account.copy()
                try:
                    decrypted_account["password"] = self.cipher.decrypt(
                        account["password"].encode()
                    ).decode()
                except:
                    decrypted_account["password"] = account["password"]
                return decrypted_account
        return None

    def get_proxy_url(self, account_id: int) -> Optional[str]:
        """プロキシURLを取得（認証情報付き）"""
        account = self.get_account_by_id(account_id)
        if account and account.get("proxy"):
            proxy = account["proxy"]
            # 認証情報を含むURL形式で返す
            if proxy.get("username") and proxy.get("password"):
                return f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
            else:
                return f"http://{proxy['host']}:{proxy['port']}"
        return None

    def _get_account_status(self, account: Dict) -> str:
        """アカウントステータス取得"""
        cookie_file = os.path.join(self.cookies_dir, f"{account['email']}_cookies.json")

        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, "r", encoding="utf-8") as f:
                    cookie_data = json.load(f)

                saved_time = datetime.fromisoformat(cookie_data.get("saved_at", ""))
                if (datetime.now() - saved_time).days < 30:
                    return "✓ログイン済み"
                else:
                    return "⚠Cookie期限切れ"
            except:
                return "✗未ログイン"

        return "✗未ログイン"
