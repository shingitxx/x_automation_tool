import os
import json
import shutil
from typing import Optional, Dict, List
from datetime import datetime
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import tempfile
import uuid
import threading
import random


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

        # ポート管理用
        self.used_ports = set()
        self.port_lock = threading.Lock()

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

    def _get_free_port(self) -> int:
        """未使用のポート番号を取得（範囲拡大版）"""
        with self.port_lock:
            # ポート範囲を拡大
            port = random.randint(9000, 65000)
            while port in self.used_ports:
                port = random.randint(9000, 65000)
            self.used_ports.add(port)
            return port

    def _release_port(self, port: int):
        """ポート番号を解放"""
        with self.port_lock:
            self.used_ports.discard(port)

    def get_profile_path(self, account_email: str) -> str:
        """アカウント用プロファイルパス取得（絶対パス版）"""
        safe_email = account_email.replace("@", "_at_").replace(".", "_")
        current_dir = os.getcwd()
        profile_path = os.path.join(
            current_dir, self.base_profile_dir, f"profile_{safe_email}"
        )
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
        """プロファイル付きドライバー作成（修正版）"""
        port = None
        max_retries = 3
        proxy_extension = None

        for attempt in range(max_retries):
            try:
                chrome_options = uc.ChromeOptions()

                # プロファイル設定
                if use_temp:
                    profile_path = self.get_temp_profile_path(account_email)
                    print(f"  → 一時プロファイル使用: {os.path.basename(profile_path)}")
                else:
                    profile_path = self.get_profile_path(account_email)
                    print(f"  → 専用プロファイル使用: {os.path.basename(profile_path)}")

                # プロファイルのロックファイルをクリーンアップ
                profile_lock_files = [
                    os.path.join(profile_path, "SingletonLock"),
                    os.path.join(profile_path, "SingletonSocket"),
                    os.path.join(profile_path, "SingletonCookie"),
                    os.path.join(profile_path, "DevToolsActivePort"),
                    os.path.join(profile_path, "Default", "DevToolsActivePort"),
                ]
                for lock_file in profile_lock_files:
                    if os.path.exists(lock_file):
                        try:
                            os.remove(lock_file)
                            print(
                                f"  → ロックファイル削除: {os.path.basename(lock_file)}"
                            )
                        except:
                            pass

                chrome_options.add_argument(f"--user-data-dir={profile_path}")
                chrome_options.add_argument("--profile-directory=Default")

                # 基本設定
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(
                    "--disable-blink-features=AutomationControlled"
                )
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-popup-blocking")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--no-default-browser-check")

                # 動的ポート割り当て
                port = self._get_free_port()
                chrome_options.add_argument(f"--remote-debugging-port={port}")

                # プロキシ設定
                if proxy_url:
                    if "@" in proxy_url:
                        # http://username:password@host:port の形式から分解
                        try:
                            auth_part = proxy_url.split("//")[1].split("@")[0]
                            proxy_username, proxy_password = auth_part.split(":")
                            host_part = proxy_url.split("@")[1]
                            proxy_host, proxy_port_str = host_part.split(":")

                            # プロキシ認証拡張機能を作成
                            import zipfile

                            manifest_json = """
                            {
                                "version": "1.0.0",
                                "manifest_version": 2,
                                "name": "Chrome Proxy",
                                "permissions": [
                                    "proxy",
                                    "tabs",
                                    "unlimitedStorage",
                                    "storage",
                                    "<all_urls>",
                                    "webRequest",
                                    "webRequestBlocking"
                                ],
                                "background": {
                                    "scripts": ["background.js"]
                                },
                                "minimum_chrome_version":"22.0.0"
                            }
                            """

                            background_js = """
                            var config = {
                                    mode: "fixed_servers",
                                    rules: {
                                    singleProxy: {
                                        scheme: "http",
                                        host: "%s",
                                        port: parseInt(%s)
                                    },
                                    bypassList: ["localhost"]
                                    }
                                };

                            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                            function callbackFn(details) {
                                return {
                                    authCredentials: {
                                        username: "%s",
                                        password: "%s"
                                    }
                                };
                            }

                            chrome.webRequest.onAuthRequired.addListener(
                                        callbackFn,
                                        {urls: ["<all_urls>"]},
                                        ['blocking']
                            );
                            """ % (
                                proxy_host,
                                proxy_port_str,
                                proxy_username,
                                proxy_password,
                            )

                            # 拡張機能を作成
                            proxy_extension = f'proxy_auth_plugin_{account_email.replace("@", "_")}.zip'
                            with zipfile.ZipFile(proxy_extension, "w") as zp:
                                zp.writestr("manifest.json", manifest_json)
                                zp.writestr("background.js", background_js)

                            chrome_options.add_extension(proxy_extension)
                            print(f"  → プロキシ設定: {proxy_host}:{proxy_port_str}")
                        except:
                            # 分解に失敗した場合は通常のプロキシ設定
                            chrome_options.add_argument(f"--proxy-server={proxy_url}")
                            print(f"  → プロキシ設定: {proxy_url}")
                    else:
                        chrome_options.add_argument(f"--proxy-server={proxy_url}")
                        print(f"  → プロキシ設定: {proxy_url}")

                # 一時ディレクトリを個別に設定
                temp_dir = tempfile.mkdtemp(
                    prefix=f"uc_{account_email.replace('@', '_')}_"
                )

                # 環境変数で一時ディレクトリを指定
                old_temp = os.environ.get("TEMP")
                old_tmp = os.environ.get("TMP")
                os.environ["TEMP"] = temp_dir
                os.environ["TMP"] = temp_dir

                try:
                    # ドライバー作成
                    driver = uc.Chrome(
                        options=chrome_options,
                        version_main=139,
                        driver_executable_path=None,
                        use_subprocess=True,
                    )
                    driver.implicitly_wait(10)

                    # ポート情報を保持
                    driver._debug_port = port
                    driver._temp_dir = temp_dir

                    print(f"  ✓ ドライバー起動成功 (ポート: {port})")

                    # プロキシ拡張ファイルを削除
                    if proxy_extension and os.path.exists(proxy_extension):
                        try:
                            os.remove(proxy_extension)
                        except:
                            pass

                    return driver

                finally:
                    # 環境変数を元に戻す
                    if old_temp:
                        os.environ["TEMP"] = old_temp
                    else:
                        if "TEMP" in os.environ:
                            del os.environ["TEMP"]

                    if old_tmp:
                        os.environ["TMP"] = old_tmp
                    else:
                        if "TMP" in os.environ:
                            del os.environ["TMP"]

            except Exception as e:
                if port:
                    self._release_port(port)

                # プロキシ拡張ファイルを削除
                if proxy_extension and os.path.exists(proxy_extension):
                    try:
                        os.remove(proxy_extension)
                    except:
                        pass

                if attempt < max_retries - 1:
                    print(
                        f"  ⚠ 起動失敗 (試行 {attempt + 1}/{max_retries}): {str(e)[:50]}"
                    )
                    time.sleep(3)
                    continue
                else:
                    print(f"  ✗ ドライバー作成エラー: {str(e)[:100]}")
                    return None

    def close_driver(self, driver: webdriver.Chrome):
        """ドライバーを安全に終了"""
        try:
            # ポート解放
            if hasattr(driver, "_debug_port"):
                self._release_port(driver._debug_port)

            # 一時ディレクトリ削除
            if hasattr(driver, "_temp_dir") and os.path.exists(driver._temp_dir):
                try:
                    shutil.rmtree(driver._temp_dir)
                except:
                    pass

            driver.quit()
        except:
            pass

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
            # 一時プロファイルが存在するか確認
            if not os.path.exists(temp_profile_path):
                print(
                    f"  ⚠ 一時プロファイルが既に削除されています: {temp_profile_path}"
                )
                return False

            permanent_path = self.get_profile_path(account_email)

            if os.path.exists(permanent_path):
                shutil.rmtree(permanent_path)

            shutil.move(temp_profile_path, permanent_path)

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
            # エラーでも永続プロファイルを作成
            permanent_path = self.get_profile_path(account_email)
            os.makedirs(permanent_path, exist_ok=True)
            self.save_profile_info(
                account_email,
                {
                    "created_at": datetime.now().isoformat(),
                    "login_status": "logged_in",
                    "cookies_saved": True,
                },
            )
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

            if os.path.exists(profile_path):
                shutil.rmtree(profile_path)

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

            if "home" in driver.current_url.lower():
                return True
            return False

        except:
            return False
        finally:
            if driver:
                try:
                    self.close_driver(driver)
                except:
                    pass
