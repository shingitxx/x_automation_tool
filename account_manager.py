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
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        with open(self.key_file, 'rb') as f:
            self.cipher = Fernet(f.read())
    
    def _load_accounts(self) -> Dict:
        """アカウントデータ読み込み"""
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"accounts": []}
    
    def _save_accounts(self):
        """アカウントデータ保存"""
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)
    
    def import_from_csv(self, csv_path: str) -> Dict[str, int]:
        """CSVからアカウント一括インポート"""
        if not os.path.exists(csv_path):
            return {"error": "ファイルが見つかりません"}
        
        results = {"imported": 0, "skipped": 0, "errors": 0}
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    email = row.get('アカウントID', '').strip()
                    password = row.get('パスワード', '').strip()
                    proxy_host = row.get('プロキシホスト', '').strip()
                    proxy_port = row.get('プロキシポート', '').strip()
                    proxy_user = row.get('プロキシユーザー', '').strip()
                    proxy_pass = row.get('プロキシパスワード', '').strip()
                    
                    if not all([email, password, proxy_host, proxy_port, proxy_user, proxy_pass]):
                        results["errors"] += 1
                        continue
                    
                    if self._account_exists(email):
                        results["skipped"] += 1
                        continue
                    
                    account_id = self._get_next_id()
                    encrypted_password = self.cipher.encrypt(password.encode()).decode()
                    
                    account = {
                        "id": account_id,
                        "email": email,
                        "password": encrypted_password,
                        "proxy": {
                            "host": proxy_host,
                            "port": proxy_port,
                            "username": proxy_user,
                            "password": proxy_pass
                        },
                        "created_at": datetime.now().isoformat(),
                        "last_login": None,
                        "status": "not_logged_in"
                    }
                    
                    self.accounts["accounts"].append(account)
                    results["imported"] += 1
            
            self._save_accounts()
            return results
            
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
        """プロキシURL取得"""
        account = self.get_account_by_id(account_id)
        if not account:
            return None
        
        proxy = account["proxy"]
        return f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
    
    def _get_account_status(self, account: Dict) -> str:
        """アカウントステータス取得"""
        cookie_file = os.path.join(self.cookies_dir, f"{account['email']}_cookies.json")
        
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie_data = json.load(f)
                
                saved_time = datetime.fromisoformat(cookie_data.get("saved_at", ""))
                if (datetime.now() - saved_time).days < 30:
                    return "✓ログイン済み"
                else:
                    return "⚠Cookie期限切れ"
            except:
                return "✗未ログイン"
        
        return "✗未ログイン"
