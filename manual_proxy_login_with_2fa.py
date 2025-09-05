# manual_proxy_login_with_2fa.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from profile_manager import ProfileManager
from account_manager import AccountManager
from totp_handler import TOTPHandler
import undetected_chromedriver as uc


class ManualProxyLoginWith2FA:
    """2FA対応の手動プロキシログイン"""

    def __init__(self):
        self.account_manager = AccountManager()
        self.profile_manager = ProfileManager()
        self.totp_handler = TOTPHandler()

    def login_with_2fa(self, account_id: int):
        """2FA自動入力を含むログイン"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            print("アカウントが見つかりません")
            return False

        print(f"\n[{account_id}] {account['email']} - ログイン開始")
        print("=" * 50)

        # プロファイルパス取得
        profile_path = self.profile_manager.get_profile_path(account["email"])

        # Chrome起動
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--profile-directory=Default")

        # プロキシ設定
        proxy = account["proxy"]
        proxy_server = f"{proxy['host']}:{proxy['port']}"
        chrome_options.add_argument(f"--proxy-server={proxy_server}")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        try:
            driver = uc.Chrome(options=chrome_options, version_main=139)
            driver.implicitly_wait(10)

            # プロキシ認証情報表示
            print("\n【手動操作】")
            print("1. プロキシ認証（必要な場合）:")
            print(f"   ユーザー名: {proxy['username']}")
            print(f"   パスワード: {proxy['password']}")

            # X.comにアクセス
            driver.get("https://x.com/login")
            time.sleep(3)

            # ログイン処理
            try:
                # ユーザー名入力
                username_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[autocomplete='username']")
                    )
                )
                username_input.clear()
                username_input.send_keys(account["email"])
                time.sleep(1)

                # 次へボタン
                next_button = driver.find_element(By.XPATH, "//span[text()='次へ']/..")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)

                # パスワード入力
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[type='password']")
                    )
                )
                password_input.clear()
                password_input.send_keys(account["password"])
                time.sleep(1)

                # ログインボタン
                login_button = driver.find_element(
                    By.XPATH, "//span[text()='ログイン']/.."
                )
                driver.execute_script("arguments[0].click();", login_button)
                time.sleep(3)

                # メール/電話番号認証画面のチェック（追加）
                print("\n【追加認証の確認中...】")
                time.sleep(5)

                try:
                    # メール認証画面の検出
                    email_verify = driver.find_element(
                        By.CSS_SELECTOR, "input[data-testid='ocfEnterTextTextInput']"
                    )
                    if email_verify:
                        print("\n⚠ メール/電話番号認証が必要です")
                        print("手動で入力してください")
                        print("入力完了後、15秒待機します...")
                        time.sleep(15)
                except:
                    print("追加認証はありませんでした")

                # 2FA入力画面の確認と自動入力
                if account.get("totp_secret"):
                    try:
                        # 2FA入力フィールドを待機（最大10秒）
                        totp_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (
                                    By.CSS_SELECTOR,
                                    "input[inputmode='numeric'], input[name='text'][data-testid='ocfEnterTextTextInput']",
                                )
                            )
                        )

                        # TOTPコード生成と入力
                        code = self.totp_handler.get_totp_code(account["totp_secret"])
                        if code:
                            totp_input.clear()
                            totp_input.send_keys(code)
                            print(f"  ✓ 2FAコード自動入力: {code}")
                            time.sleep(1)
                            totp_input.send_keys(Keys.RETURN)

                            # 2FA認証後の画面遷移を確認
                            print("\n2FA認証処理中...")
                            time.sleep(5)

                            print("\n【確認してください】")
                            print("1. 2FAコードが正しく入力されたか")
                            print("2. ホーム画面に遷移したか")
                            print("\n確認後、Enterキーを押してください...")
                            input()

                    except Exception as e:
                        print(f"  → 2FA入力画面が見つかりません: {str(e)[:50]}")
                        print("\n手動で続行してください")
                        print("完了後、Enterキーを押してください...")
                        input()
                else:
                    print("\n2FAシークレットキーが設定されていません")
                    print("ログイン完了後、Enterキーを押してください...")
                    input()

            except Exception as e:
                print(f"自動ログインエラー: {str(e)[:50]}")
                print("\n手動でログインしてください")
                print(f"ユーザー名: {account['email']}")
                print(f"パスワード: {account['password']}")
                if account.get("totp_secret"):
                    code = self.totp_handler.get_totp_code(account["totp_secret"])
                    print(f"2FAコード: {code}")
                print("\nログイン完了後、Enterキーを押してください...")
                input()

            # ログイン状態確認
            driver.get("https://x.com/home")
            time.sleep(3)

            if "home" in driver.current_url.lower():
                print("✓ ログイン成功！プロファイル保存中...")

                # プロファイル情報保存
                self.profile_manager.save_profile_info(
                    account["email"],
                    {
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "login_status": "logged_in",
                        "has_2fa": bool(account.get("totp_secret")),
                    },
                )

                driver.quit()
                return True
            else:
                print("✗ ログイン失敗")
                driver.quit()
                return False

        except Exception as e:
            print(f"エラー: {str(e)[:100]}")
            return False

    def batch_login_with_2fa(self, account_ids: list):
        """複数アカウントの順次ログイン（2FA対応）"""
        print("\n複数アカウントのログイン開始（2FA自動入力対応）")
        print("=" * 50)

        success = 0
        failed = 0

        for i, account_id in enumerate(account_ids, 1):
            print(f"\n進捗: {i}/{len(account_ids)}")

            if self.login_with_2fa(account_id):
                success += 1
            else:
                failed += 1

            if i < len(account_ids):
                print("\n次のアカウントに進みますか？ (y/n): ", end="")
                if input().lower() != "y":
                    break
                time.sleep(2)

        print(f"\n{'='*50}")
        print(f"完了: 成功 {success} / 失敗 {failed}")
        print(f"{'='*50}")


if __name__ == "__main__":
    login = ManualProxyLoginWith2FA()

    print("2FA対応ログイン")
    print("1. 単一アカウント")
    print("2. 複数アカウント（カンマ区切り）")
    print("3. 複数アカウント（範囲選択）")

    choice = input("選択: ")

    if choice == "1":
        account_id = int(input("アカウント番号: "))
        login.login_with_2fa(account_id)
    elif choice == "2":
        ids_str = input("アカウント番号（カンマ区切り）: ")
        account_ids = [int(x.strip()) for x in ids_str.split(",")]
        login.batch_login_with_2fa(account_ids)
    elif choice == "3":
        try:
            start = int(input("開始番号: "))
            end = int(input("終了番号: "))

            if start > end:
                print("開始番号は終了番号以下にしてください")
            else:
                account_ids = list(range(start, end + 1))
                print(f"対象アカウント: {start}〜{end}（{len(account_ids)}件）")
                confirm = input("実行しますか？ (y/n): ")
                if confirm.lower() == "y":
                    login.batch_login_with_2fa(account_ids)
                else:
                    print("キャンセルしました")
        except ValueError:
            print("数値を入力してください")
