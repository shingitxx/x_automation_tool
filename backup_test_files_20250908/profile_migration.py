import os
import json
import shutil
import time
from datetime import datetime
from selenium import webdriver
import undetected_chromedriver as uc
from account_manager import AccountManager
from profile_manager import ProfileManager


class ProfileMigration:
    """既存ログイン済みアカウントのプロファイル移行ツール"""

    def __init__(self):
        self.account_manager = AccountManager()
        self.profile_manager = ProfileManager()
        self.cookies_dir = "cache/cookies"

    def migrate_logged_accounts(self, account_ids: list = None):
        """ログイン済みアカウントを個別プロファイルに移行"""

        if account_ids is None:
            # 全ログイン済みアカウントを取得
            account_ids = self.get_logged_account_ids()

        print(f"\n{'='*60}")
        print(f" プロファイル移行処理")
        print(f"{'='*60}")
        print(f"対象アカウント数: {len(account_ids)}")
        print(f"{'='*60}\n")

        success_count = 0
        failed_count = 0

        for account_id in account_ids:
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                print(f"[{account_id}] アカウントが見つかりません")
                failed_count += 1
                continue

            print(f"\n[{account_id}] {account['email']} - 移行開始")

            # 既にプロファイルがある場合はスキップ
            if self.profile_manager.profile_exists(account["email"]):
                print(f"  → 既にプロファイル存在（スキップ）")
                continue

            # Cookieファイル確認
            cookie_file = os.path.join(
                self.cookies_dir, f"{account['email']}_cookies.json"
            )
            if not os.path.exists(cookie_file):
                print(f"  ✗ Cookieファイルが見つかりません")
                failed_count += 1
                continue

            # プロファイル作成して移行
            if self.create_profile_from_cookies(account):
                print(f"  ✓ プロファイル移行成功")
                success_count += 1
            else:
                print(f"  ✗ プロファイル移行失敗")
                failed_count += 1

            # 次のアカウントまで少し待機
            time.sleep(2)

        print(f"\n{'='*60}")
        print(f" 移行結果")
        print(f"{'='*60}")
        print(f"成功: {success_count}")
        print(f"失敗: {failed_count}")
        print(f"{'='*60}")

    def get_logged_account_ids(self):
        """ログイン済みアカウントのIDリストを取得"""
        logged_ids = []
        for account in self.account_manager.accounts.get("accounts", []):
            cookie_file = os.path.join(
                self.cookies_dir, f"{account['email']}_cookies.json"
            )
            if os.path.exists(cookie_file):
                # プロファイルがまだない場合のみ対象
                if not self.profile_manager.profile_exists(account["email"]):
                    logged_ids.append(account["id"])
        return logged_ids

    def create_profile_from_cookies(self, account: dict) -> bool:
        """Cookieから専用プロファイルを作成"""
        driver = None
        temp_profile_path = None

        try:
            # Cookie読み込み
            cookie_file = os.path.join(
                self.cookies_dir, f"{account['email']}_cookies.json"
            )
            with open(cookie_file, "r", encoding="utf-8") as f:
                cookie_data = json.load(f)

            # 一時プロファイルでドライバー作成
            proxy_url = self.account_manager.get_proxy_url(account["id"])
            temp_profile_path = self.profile_manager.get_temp_profile_path(
                account["email"]
            )

            chrome_options = uc.ChromeOptions()
            chrome_options.add_argument(f"--user-data-dir={temp_profile_path}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            if proxy_url:
                chrome_options.add_argument(f"--proxy-server={proxy_url}")

            driver = uc.Chrome(options=chrome_options, version_main=139)
            driver.implicitly_wait(10)

            # X.comにアクセス
            driver.get("https://x.com")
            time.sleep(3)

            # Cookie適用
            for cookie in cookie_data.get("cookies", []):
                try:
                    # 必要なフィールドのみ使用
                    cleaned_cookie = {
                        "name": cookie.get("name"),
                        "value": cookie.get("value"),
                        "domain": cookie.get("domain", ".x.com"),
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", True),
                    }

                    # HttpOnlyとSameSiteは省略（ドライバーが自動設定）
                    if cookie.get("httpOnly"):
                        cleaned_cookie["httpOnly"] = cookie["httpOnly"]

                    driver.add_cookie(cleaned_cookie)
                except Exception as e:
                    pass  # 個別のCookieエラーは無視

            # リフレッシュしてログイン確認
            driver.refresh()
            time.sleep(5)

            driver.get("https://x.com/home")
            time.sleep(3)

            if "home" in driver.current_url.lower():
                print(f"  → ログイン状態確認OK")

                # ドライバーを閉じる
                driver.quit()
                driver = None
                time.sleep(1)

                # 一時プロファイルを永続プロファイルに移行
                permanent_path = self.profile_manager.get_profile_path(account["email"])

                # 既存の永続プロファイルがある場合は削除
                if os.path.exists(permanent_path):
                    shutil.rmtree(permanent_path)

                # 一時プロファイルを永続プロファイルに移動
                shutil.move(temp_profile_path, permanent_path)

                # インデックス更新
                self.profile_manager.save_profile_info(
                    account["email"],
                    {
                        "created_at": datetime.now().isoformat(),
                        "login_status": "logged_in",
                        "cookies_saved": True,
                        "migrated_from_cookies": True,
                    },
                )

                return True
            else:
                print(f"  → ログイン状態確認失敗")
                return False

        except Exception as e:
            print(f"  エラー: {str(e)[:100]}")
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

            # 一時プロファイルが残っていたら削除
            if temp_profile_path and os.path.exists(temp_profile_path):
                try:
                    shutil.rmtree(temp_profile_path)
                except:
                    pass


def main():
    """スタンドアロン実行"""
    migrator = ProfileMigration()

    print("\n既存のログイン済みアカウントを個別プロファイルに移行します")
    print("この処理により、各アカウントが独立したプロファイルを持つようになります\n")

    # ログイン済みアカウントを確認
    logged_ids = migrator.get_logged_account_ids()

    if not logged_ids:
        print("移行対象のアカウントがありません")
        return

    print(f"移行対象アカウント: {logged_ids}")

    confirm = input("\n移行を実行しますか？ (y/n): ")
    if confirm.lower() == "y":
        migrator.migrate_logged_accounts(logged_ids)
    else:
        print("キャンセルしました")


if __name__ == "__main__":
    main()
