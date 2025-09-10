# manual_proxy_login.py として保存
import time
from profile_manager import ProfileManager
from account_manager import AccountManager
import undetected_chromedriver as uc


class ManualProxyLogin:
    """手動プロキシ認証を含むログインシステム"""

    def __init__(self):
        self.account_manager = AccountManager()
        self.profile_manager = ProfileManager()

    def login_with_manual_proxy_auth(self, account_id: int):
        """手動プロキシ認証を含むログイン"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            print("アカウントが見つかりません")
            return False

        print(f"\n[{account_id}] {account['email']} - ログイン開始")
        print("=" * 50)

        # プロファイルパス取得（新規作成）
        profile_path = self.profile_manager.get_profile_path(account["email"])

        # Chrome起動（プロキシ設定付き）
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f"--user-data-dir={profile_path}")

        # プロキシ設定（ホストとポートのみ）
        proxy = account["proxy"]
        proxy_server = f"{proxy['host']}:{proxy['port']}"
        chrome_options.add_argument(f"--proxy-server={proxy_server}")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        try:
            driver = uc.Chrome(options=chrome_options, version_main=139)
            driver.implicitly_wait(10)

            print("\n【手動操作が必要です】")
            print("=" * 50)
            print("1. プロキシ認証ダイアログが表示されたら：")
            print(f"   ユーザー名: {proxy['username']}")
            print(f"   パスワード: {proxy['password']}")
            print("   を入力してOKをクリック")
            print("\n2. X.comのログイン画面で：")
            print(f"   ユーザー名: {account['email']}")
            print(f"   パスワード: {account['password']}")
            print("   を入力してログイン")
            print("=" * 50)

            # X.comにアクセス
            driver.get("https://x.com/login")

            # ユーザーが手動でログインするのを待つ
            print("\nログインが完了したらEnterキーを押してください...")
            input()

            # ログイン状態確認
            driver.get("https://x.com/home")
            time.sleep(3)

            if "home" in driver.current_url.lower():
                print("✓ ログイン成功！プロファイルに保存されました")

                # プロファイル情報を保存
                self.profile_manager.save_profile_info(
                    account["email"],
                    {
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "login_status": "logged_in",
                        "proxy_authenticated": True,
                    },
                )

                driver.quit()
                return True
            else:
                print("✗ ログイン失敗")
                driver.quit()
                return False

        except Exception as e:
            print(f"エラー: {str(e)}")
            return False

    def batch_login(self, account_ids: list):
        """複数アカウントの順次ログイン"""
        print("\n複数アカウントの手動ログインを開始します")
        print("各アカウントで手動認証が必要です")

        success_count = 0
        failed_count = 0

        for account_id in account_ids:
            if self.login_with_manual_proxy_auth(account_id):
                success_count += 1
            else:
                failed_count += 1

            if account_id != account_ids[-1]:
                print("\n次のアカウントに進みますか？ (y/n): ", end="")
                if input().lower() != "y":
                    break

        print(f"\n完了: 成功 {success_count} / 失敗 {failed_count}")


# 実行用
if __name__ == "__main__":
    login = ManualProxyLogin()

    print("手動プロキシ認証ログイン")
    print("1. 単一アカウント")
    print("2. 複数アカウント")

    choice = input("選択: ")

    if choice == "1":
        account_id = int(input("アカウント番号: "))
        login.login_with_manual_proxy_auth(account_id)
    elif choice == "2":
        ids_str = input("アカウント番号（カンマ区切り）: ")
        account_ids = [int(x.strip()) for x in ids_str.split(",")]
        login.batch_login(account_ids)
