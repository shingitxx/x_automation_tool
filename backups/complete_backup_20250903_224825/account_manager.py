import json
import os
import csv
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
from cryptography.fernet import Fernet

class AccountManager:
    """Xアカウントとプロキシ設定を管理するクラス"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.config_dir = os.path.join(base_dir, "config")
        self.cache_dir = os.path.join(base_dir, "cache")
        self.data_dir = os.path.join(base_dir, "data")
        self.cookies_dir = os.path.join(self.cache_dir, "cookies")
        
        # 必要なディレクトリを作成
        self._create_directories()
        
        # 暗号化キーの初期化
        self.cipher_suite = self._init_encryption()
        
        # アカウントステータスファイル
        self.status_file = os.path.join(self.data_dir, "account_status.json")
        self.accounts_csv = os.path.join(self.config_dir, "accounts.csv")
        
        # アカウントデータの読み込み
        self.accounts = self._load_account_status()
    
    def _create_directories(self):
        """必要なディレクトリを作成"""
        dirs = [self.config_dir, self.cache_dir, self.data_dir, self.cookies_dir]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _init_encryption(self) -> Fernet:
        """暗号化キーの初期化"""
        key_file = os.path.join(self.cache_dir, "encryption.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def _load_account_status(self) -> Dict:
        """アカウントステータスファイルを読み込み"""
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"accounts": []}
    
    def _save_account_status(self):
        """アカウントステータスファイルを保存"""
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)
    
    def import_accounts_from_csv(self, csv_path: str = None) -> Dict:
        """CSVファイルからアカウント情報をインポート"""
        if csv_path is None:
            csv_path = self.accounts_csv
        
        if not os.path.exists(csv_path):
            return {"success": False, "message": f"CSVファイルが見つかりません: {csv_path}"}
        
        imported = 0
        skipped = 0
        errors = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # 既存アカウントの確認
                        account_id = row['アカウントID']
                        if self._account_exists(account_id):
                            skipped += 1
                            continue
                        
                        # アカウント情報の作成
                        account_info = {
                            "id": len(self.accounts["accounts"]) + 1,
                            "email": account_id,
                            "password": self._encrypt_password(row['パスワード']),
                            "proxy": {
                                "host": row['プロキシホスト'],
                                "port": row['プロキシポート'],
                                "username": row['プロキシユーザー'],
                                "password": row['プロキシパスワード']
                            },
                            "last_login": None,
                            "cookie_expires": None,
                            "status": "not_logged_in",
                            "created_at": datetime.now().isoformat()
                        }
                        
                        self.accounts["accounts"].append(account_info)
                        imported += 1
                        
                    except KeyError as e:
                        errors.append(f"行{row_num}: 必須フィールドが不足 - {e}")
                    except Exception as e:
                        errors.append(f"行{row_num}: エラー - {e}")
            
            # ステータスファイルを保存
            self._save_account_status()
            
            result = {
                "success": True,
                "imported": imported,
                "skipped": skipped,
                "total": imported + skipped,
                "message": f"{imported}件のアカウントをインポートしました"
            }
            
            if errors:
                result["errors"] = errors
            
            return result
            
        except Exception as e:
            return {"success": False, "message": f"CSVファイルの読み込みエラー: {e}"}
    
    def _encrypt_password(self, password: str) -> str:
        """パスワードを暗号化"""
        encrypted = self.cipher_suite.encrypt(password.encode())
        return encrypted.decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """パスワードを復号化"""
        decrypted = self.cipher_suite.decrypt(encrypted_password.encode())
        return decrypted.decode()
    
    def _account_exists(self, email: str) -> bool:
        """アカウントが既に存在するか確認"""
        for account in self.accounts["accounts"]:
            if account["email"] == email:
                return True
        return False
    
    def add_single_account(self, email: str, password: str, proxy_info: Dict) -> Dict:
        """単一アカウントを追加"""
        if self._account_exists(email):
            return {"success": False, "message": f"アカウント {email} は既に存在します"}
        
        account_info = {
            "id": len(self.accounts["accounts"]) + 1,
            "email": email,
            "password": self._encrypt_password(password),
            "proxy": proxy_info,
            "last_login": None,
            "cookie_expires": None,
            "status": "not_logged_in",
            "created_at": datetime.now().isoformat()
        }
        
        self.accounts["accounts"].append(account_info)
        self._save_account_status()
        
        return {"success": True, "message": f"アカウント {email} を追加しました", "id": account_info["id"]}
    
    def get_account_list(self, filter_status: Optional[str] = None) -> List[Dict]:
        """アカウントリストを取得"""
        accounts = []
        for account in self.accounts["accounts"]:
            account_data = {
                "id": account["id"],
                "email": account["email"],
                "status": self._get_account_status(account),
                "proxy": f"{account['proxy']['host']}:{account['proxy']['port']}",
                "last_login": account.get("last_login", "未ログイン")
            }
            
            if filter_status is None or account_data["status"] == filter_status:
                accounts.append(account_data)
        
        return accounts
    
    def _get_account_status(self, account: Dict) -> str:
        """アカウントのステータスを取得"""
        cookie_file = os.path.join(self.cookies_dir, f"{account['email']}_cookies.json")
        
        if not os.path.exists(cookie_file):
            return "✗未ログイン"
        
        # Cookie期限チェック（簡易版）
        if account.get("cookie_expires"):
            expire_date = datetime.fromisoformat(account["cookie_expires"])
            if expire_date < datetime.now():
                return "⚠Cookie期限切れ"
        
        return "✓ログイン済み"
    
    def get_account_by_id(self, account_id: int) -> Optional[Dict]:
        """IDでアカウント情報を取得"""
        for account in self.accounts["accounts"]:
            if account["id"] == account_id:
                # パスワードを復号化して返す
                account_copy = account.copy()
                account_copy["password"] = self._decrypt_password(account["password"])
                return account_copy
        return None
    
    def get_accounts_by_range(self, start_id: int, end_id: int) -> List[Dict]:
        """範囲指定でアカウントを取得"""
        accounts = []
        for account_id in range(start_id, end_id + 1):
            account = self.get_account_by_id(account_id)
            if account:
                accounts.append(account)
        return accounts
    
    def get_accounts_by_ids(self, ids: List[int]) -> List[Dict]:
        """複数IDでアカウントを取得"""
        accounts = []
        for account_id in ids:
            account = self.get_account_by_id(account_id)
            if account:
                accounts.append(account)
        return accounts
    
    def update_login_status(self, account_id: int, success: bool, cookie_expires: Optional[str] = None):
        """ログインステータスを更新"""
        for account in self.accounts["accounts"]:
            if account["id"] == account_id:
                if success:
                    account["last_login"] = datetime.now().isoformat()
                    account["status"] = "logged_in"
                    if cookie_expires:
                        account["cookie_expires"] = cookie_expires
                else:
                    account["status"] = "login_failed"
                
                self._save_account_status()
                return True
        return False
    
    def get_proxy_url(self, account_id: int) -> Optional[str]:
        """アカウントのプロキシURLを取得"""
        account = self.get_account_by_id(account_id)
        if account:
            proxy = account["proxy"]
            return f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
        return None
    
    def display_accounts(self):
        """アカウント一覧を表示用に整形"""
        accounts = self.get_account_list()
        
        print("\n" + "="*60)
        print("登録アカウント一覧")
        print("="*60)
        
        logged_in = 0
        not_logged_in = 0
        
        for account in accounts:
            status = account["status"]
            print(f"[{account['id']:3d}] {account['email']:30s} - {status:15s} | プロキシ: {account['proxy']}")
            
            if "✓" in status:
                logged_in += 1
            else:
                not_logged_in += 1
        
        print("-"*60)
        print(f"総アカウント数: {len(accounts)}")
        print(f"ログイン済み: {logged_in}")
        print(f"未ログイン: {not_logged_in}")
        print("="*60)
        
        return accounts


# サンプルCSVファイルを生成する関数
def create_sample_csv(filepath: str = "config/accounts.csv"):
    """サンプルのアカウントCSVファイルを生成"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    sample_data = [
        {
            "アカウントID": "user1@example.com",
            "パスワード": "password123",
            "プロキシホスト": "iproyalfast.hellworld.io",
            "プロキシポート": "12321",
            "プロキシユーザー": "kmco9q1aon",
            "プロキシパスワード": "mqxrtj7pia_country-jp_session-rdbr0lr8_lifetime-1440m"
        },
        {
            "アカウントID": "user2@example.com",
            "パスワード": "password456",
            "プロキシホスト": "iproyalfast.hellworld.io",
            "プロキシポート": "12322",
            "プロキシユーザー": "kmco9q1aon",
            "プロキシパスワード": "mqxrtj7pia_country-jp_session-xyz123_lifetime-1440m"
        }
    ]
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["アカウントID", "パスワード", "プロキシホスト", 
                     "プロキシポート", "プロキシユーザー", "プロキシパスワード"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"サンプルCSVファイルを作成しました: {filepath}")


if __name__ == "__main__":
    # テスト実行
    manager = AccountManager()
    
    # サンプルCSVの作成
    create_sample_csv()
    
    # CSVからインポート
    result = manager.import_accounts_from_csv()
    print(f"\nインポート結果: {result}")
    
    # アカウント一覧表示
    manager.display_accounts()
