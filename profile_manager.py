import os
import json
import shutil
from typing import Optional, Dict, List
from datetime import datetime
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class ProfileManager:
    """Chromeプロファイル管理システム"""

    def __init__(self):
        self.base_profile_dir = "profiles"
        self.temp_profile_dir = "temp_profiles"
        self.profile_index_file = "data/profile_index.json"

        # ディレクトリ作成
        os.makedirs(self.base_profile_dir, exist_ok=True)
        os.makedirs(self.temp_profile_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)

        # プロファイルインデックス読み込み
        self.profile_index = self._load_profile_index()

    def _load_profile_index(self) -> Dict:
        """プロファイルインデックス読み込み"""
        if os.path.exists(self.profile_index_file):
            with open(self.profile_index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"profiles": {}}

    def _save_profile_index(self):
        """プロファイルインデックス保存"""
        with open(self.profile_index_file, "w", encoding="utf-8") as f:
            json.dump(self.profile_index, f, ensure_ascii=False, indent=2)

    def get_profile_path(self, account_email: str) -> str:
        """アカウント用プロファイルパス取得"""
        safe_email = account_email.replace("@", "_at_").replace(".", "_")
        profile_path = os.path.join(self.base_profile_dir, f"profile_{safe_email}")
        return os.path.abspath(profile_path)

    def get_temp_profile_path(self, account_email: str) -> str:
        """一時プロファイルパス取得"""
        safe_email = account_email.replace("@", "_at_").replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        profile_path = os.path.join(
            self.temp_profile_dir, f"temp_{safe_email}_{timestamp}"
        )
        return os.path.abspath(profile_path)

    def profile_exists(self, account_email: str) -> bool:
        """プロファイル存在確認"""
        profile_path = self.get_profile_path(account_email)
        return os.path.exists(profile_path) and account_email in self.profile_index.get(
            "profiles", {}
        )

    def create_driver_with_profile(
        self,
        account_email: str,
        proxy_url: Optional[str] = None,
        use_temp: bool = False,
    ) -> Optional[webdriver.Chrome]:
        """プロファイル付きドライバー作成"""
        try:
            chrome_options = uc.ChromeOptions()

            # プロファイル設定
            if use_temp:
                profile_path = self.get_temp_profile_path(account_email)
                print(f"  → 一時プロファイル使用: {os.path.basename(profile_path)}")
            else:
                profile_path = self.get_profile_path(account_email)
                print(f"  → 専用プロファイル使用: {os.path.basename(profile_path)}")

            chrome_options.add_argument(f"--user-data-dir={profile_path}")

            # 基本設定
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")

            # プロキシ設定
            if proxy_url:
                chrome_options.add_argument(f"--proxy-server={proxy_url}")

            # ドライバー作成
            driver = uc.Chrome(options=chrome_options, version_main=139)
            driver.implicitly_wait(10)

            return driver

        except Exception as e:
            print(f"  ✗ ドライバー作成エラー: {str(e)[:100]}")
            return None

    def save_profile_info(self, account_email: str, info: Dict):
        """プロファイル情報保存"""
        self.profile_index["profiles"][account_email] = {
            "email": account_email,
            "profile_path": self.get_profile_path(account_email),
            "created_at": info.get("created_at", datetime.now().isoformat()),
            "last_used": datetime.now().isoformat(),
            "login_status": info.get("login_status", "logged_in"),
            "cookies_saved": info.get("cookies_saved", True),
        }
        self._save_profile_index()

    def migrate_temp_to_permanent(
        self, account_email: str, temp_profile_path: str
    ) -> bool:
        """一時プロファイルを永続プロファイルに移行"""
        try:
            permanent_path = self.get_profile_path(account_email)

            # 既存の永続プロファイルがある場合は削除
            if os.path.exists(permanent_path):
                shutil.rmtree(permanent_path)

            # 一時プロファイルを永続プロファイルに移動
            shutil.move(temp_profile_path, permanent_path)

            # インデックス更新
            self.save_profile_info(
                account_email,
                {
                    "created_at": datetime.now().isoformat(),
                    "login_status": "logged_in",
                    "cookies_saved": True,
                },
            )

            print(f"  ✓ プロファイル移行完了: {account_email}")
            return True

        except Exception as e:
            print(f"  ✗ プロファイル移行エラー: {str(e)[:100]}")
            return False

    def cleanup_temp_profiles(self):
        """一時プロファイルクリーンアップ"""
        try:
            for temp_dir in os.listdir(self.temp_profile_dir):
                temp_path = os.path.join(self.temp_profile_dir, temp_dir)
                if os.path.isdir(temp_path):
                    try:
                        shutil.rmtree(temp_path)
                        print(f"  ✓ 一時プロファイル削除: {temp_dir}")
                    except:
                        pass
        except Exception as e:
            print(f"  ⚠ クリーンアップエラー: {str(e)[:50]}")

    def get_all_profiles(self) -> List[Dict]:
        """全プロファイル情報取得"""
        profiles = []
        for email, info in self.profile_index.get("profiles", {}).items():
            profile_info = info.copy()
            profile_info["exists"] = os.path.exists(info.get("profile_path", ""))
            profiles.append(profile_info)
        return profiles

    def delete_profile(self, account_email: str) -> bool:
        """プロファイル削除"""
        try:
            profile_path = self.get_profile_path(account_email)

            # プロファイルディレクトリ削除
            if os.path.exists(profile_path):
                shutil.rmtree(profile_path)

            # インデックスから削除
            if account_email in self.profile_index.get("profiles", {}):
                del self.profile_index["profiles"][account_email]
                self._save_profile_index()

            print(f"  ✓ プロファイル削除: {account_email}")
            return True

        except Exception as e:
            print(f"  ✗ プロファイル削除エラー: {str(e)[:100]}")
            return False

    def check_profile_login_status(self, account_email: str) -> bool:
        """プロファイルのログイン状態確認"""
        if not self.profile_exists(account_email):
            return False

        driver = None
        try:
            driver = self.create_driver_with_profile(account_email)
            if not driver:
                return False

            driver.get("https://x.com/home")
            time.sleep(3)

            # ログイン状態確認
            if "home" in driver.current_url.lower():
                return True
            return False

        except:
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
