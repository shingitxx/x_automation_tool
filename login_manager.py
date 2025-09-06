import os
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from account_manager import AccountManager
from profile_manager import ProfileManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class LoginManager:
    """改良版ログイン管理システム（プロファイル対応）"""

    def __init__(self):
        self.account_manager = AccountManager()
        self.profile_manager = ProfileManager()
        self.cookies_dir = "cache/cookies"
        os.makedirs(self.cookies_dir, exist_ok=True)

        # スレッドセーフなロック
        self.profile_lock = threading.Lock()

    def manual_login(self, account_ids: List[int], max_concurrent: int = 1) -> Dict:
        """手動ログイン実行（プロファイル対応）"""
        results = {"success": [], "failed": [], "already_logged": []}

        print(f"\n{'='*60}")
        print(f" ログイン処理開始")
        print(f"{'='*60}")
        print(f"対象アカウント数: {len(account_ids)}")
        print(f"同時実行数: {max_concurrent}")
        print(f"{'='*60}\n")

        # プロファイル状態確認
        for account_id in account_ids:
            account = self.account_manager.get_account_by_id(account_id)
            if account:
                if self.profile_manager.profile_exists(account["email"]):
                    print(f"[{account_id}] {account['email']}: 既存プロファイルあり")
                else:
                    print(
                        f"[{account_id}] {account['email']}: 新規プロファイル作成予定"
                    )

        # 並列実行
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_account = {
                executor.submit(self._login_single_account, account_id): account_id
                for account_id in account_ids
            }

            for future in as_completed(future_to_account):
                account_id = future_to_account[future]
                try:
                    result = future.result()
                    if result["status"] == "success":
                        results["success"].append(account_id)
                    elif result["status"] == "already_logged":
                        results["already_logged"].append(account_id)
                    else:
                        results["failed"].append(account_id)
                except Exception as e:
                    print(f"[{account_id}] エラー: {str(e)[:100]}")
                    results["failed"].append(account_id)

        # 一時プロファイルクリーンアップ
        self.profile_manager.cleanup_temp_profiles()

        # 結果表示
        self._print_results(results)
        return results

    def _login_single_account(self, account_id: int) -> Dict:
        """単一アカウントログイン（プロファイル対応）"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return {"status": "failed", "error": "アカウントが見つかりません"}

        print(f"\n[{account_id}] {account['email']} - ログイン処理開始")

        # プロファイル存在確認
        if self.profile_manager.profile_exists(account["email"]):
            # 既存プロファイルでログイン状態確認
            if self._check_existing_profile_login(account):
                print(f"  ✓ 既にログイン済み（プロファイル使用）")
                return {"status": "already_logged"}
            else:
                print(f"  → 既存プロファイルで再ログインが必要")
                return self._perform_login_with_profile(account, use_existing=True)
        else:
            # 新規プロファイル作成してログイン
            print(f"  → 新規プロファイル作成してログイン")
            return self._perform_login_with_profile(account, use_existing=False)

    def _check_existing_profile_login(self, account: Dict) -> bool:
        """既存プロファイルのログイン状態確認"""
        driver = None
        try:
            proxy_url = self.account_manager.get_proxy_url(account["id"])
            driver = self.profile_manager.create_driver_with_profile(
                account["email"], proxy_url=proxy_url, use_temp=False
            )

            if not driver:
                return False

            driver.get("https://x.com/home")
            time.sleep(3)

            # ログイン済み確認
            if "home" in driver.current_url.lower():
                # Cookie保存
                self._save_cookies(driver, account["email"])
                return True

            return False

        except:
            return False
        finally:
            if driver:
                try:
                    self.profile_manager.close_driver(driver)
                except:
                    pass

    def _perform_login_with_profile(
        self, account: Dict, use_existing: bool = False
    ) -> Dict:
        """プロファイルを使用したログイン実行"""
        driver = None
        temp_profile_path = None

        try:
            proxy_url = self.account_manager.get_proxy_url(account["id"])

            if use_existing:
                # 既存プロファイルを使用
                driver = self.profile_manager.create_driver_with_profile(
                    account["email"], proxy_url=proxy_url, use_temp=False
                )
            else:
                # 一時プロファイルを使用
                driver = self.profile_manager.create_driver_with_profile(
                    account["email"], proxy_url=proxy_url, use_temp=True
                )
                temp_profile_path = self.profile_manager.get_temp_profile_path(
                    account["email"]
                )

            if not driver:
                return {"status": "failed", "error": "ドライバー作成失敗"}

            # ログインページへ
            driver.get("https://x.com/login")
            time.sleep(5)

            # ユーザー名入力
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[autocomplete='username']")
                )
            )
            username_input.clear()
            username_input.send_keys(account["email"])
            time.sleep(2)

            # 次へボタン
            next_button = driver.find_element(By.XPATH, "//span[text()='次へ']/..")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)

            # パスワード入力
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='password']")
                )
            )
            password_input.clear()
            password_input.send_keys(account["password"])
            time.sleep(2)

            # ログインボタン
            login_button = driver.find_element(By.XPATH, "//span[text()='ログイン']/..")
            driver.execute_script("arguments[0].click();", login_button)

            print(f"  → ログイン実行中...")
            time.sleep(10)

            # ログイン成功確認
            driver.get("https://x.com/home")
            time.sleep(3)

            if "home" in driver.current_url.lower():
                print(f"  ✓ ログイン成功")

                # Cookie保存
                self._save_cookies(driver, account["email"])

                # 一時プロファイルを永続化
                if temp_profile_path and not use_existing:
                    with self.profile_lock:
                        self.profile_manager.migrate_temp_to_permanent(
                            account["email"], temp_profile_path
                        )
                elif use_existing:
                    # 既存プロファイル情報更新
                    self.profile_manager.save_profile_info(
                        account["email"],
                        {"login_status": "logged_in", "cookies_saved": True},
                    )

                # アカウントステータス更新
                self._update_account_status(account["id"], "logged_in")

                return {"status": "success"}
            else:
                print(f"  ✗ ログイン失敗")
                return {"status": "failed", "error": "ログイン確認失敗"}

        except TimeoutException:
            print(f"  ✗ タイムアウト")
            return {"status": "failed", "error": "タイムアウト"}
        except Exception as e:
            print(f"  ✗ エラー: {str(e)[:100]}")
            return {"status": "failed", "error": str(e)[:100]}
        finally:
            if driver:
                try:
                    self.profile_manager.close_driver(driver)
                except:
                    pass

    def _save_cookies(self, driver: webdriver.Chrome, email: str):
        """Cookie保存"""
        try:
            cookies = driver.get_cookies()
            cookie_file = os.path.join(self.cookies_dir, f"{email}_cookies.json")

            cookie_data = {
                "cookies": cookies,
                "saved_at": datetime.now().isoformat(),
                "email": email,
            }

            with open(cookie_file, "w", encoding="utf-8") as f:
                json.dump(cookie_data, f, ensure_ascii=False, indent=2)

            print(f"  ✓ Cookie保存完了")
        except Exception as e:
            print(f"  ⚠ Cookie保存エラー: {str(e)[:50]}")

    def _update_account_status(self, account_id: int, status: str):
        """アカウントステータス更新"""
        for account in self.account_manager.accounts["accounts"]:
            if account["id"] == account_id:
                account["last_login"] = datetime.now().isoformat()
                account["status"] = status
                break
        self.account_manager._save_accounts()

    def _print_results(self, results: Dict):
        """結果表示"""
        print(f"\n{'='*60}")
        print(f" ログイン処理完了")
        print(f"{'='*60}")
        print(f"成功: {len(results['success'])}件")
        print(f"既にログイン済み: {len(results['already_logged'])}件")
        print(f"失敗: {len(results['failed'])}件")

        if results["failed"]:
            print(f"\n失敗したアカウント:")
            for account_id in results["failed"]:
                account = self.account_manager.get_account_by_id(account_id)
                if account:
                    print(f"  [{account_id}] {account['email']}")

        print(f"{'='*60}")

    def quick_login_check(self, account_id: int) -> bool:
        """クイックログインチェック（プロファイル使用）"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return False

        # プロファイル存在確認
        if self.profile_manager.profile_exists(account["email"]):
            return self._check_existing_profile_login(account)

        return False
