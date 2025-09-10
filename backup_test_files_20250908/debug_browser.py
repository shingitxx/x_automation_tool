# debug_browser.py - ブラウザ起動デバッグ（新規作成）
import os
import sys
import time

os.chdir(r"C:\Users\nextS\MyApps\x_automation_tool")
sys.path.append(os.getcwd())

from profile_manager import ProfileManager
from account_manager import AccountManager
import undetected_chromedriver as uc


def debug_browser_launch(account_id: int):
    """ブラウザ起動のデバッグ"""
    print(f"\nアカウント {account_id} でブラウザ起動テスト")
    print("=" * 50)

    # マネージャー初期化
    pm = ProfileManager()
    am = AccountManager()

    # アカウント取得
    account = am.get_account_by_id(account_id)
    if not account:
        print("✗ アカウントが見つかりません")
        return False

    print(f"アカウント: {account['email']}")

    # プロファイル確認
    if pm.profile_exists(account["email"]):
        print("✓ プロファイル存在確認")
    else:
        print("✗ プロファイルが存在しません")
        return False

    # プロキシURL取得
    proxy_url = am.get_proxy_url(account_id)
    print(f"プロキシURL: {proxy_url[:50]}...")

    # ドライバー起動試行
    print("\n【方法1】profile_manager経由")
    driver1 = pm.create_driver_with_profile(
        account["email"], proxy_url=proxy_url, use_temp=False
    )

    if driver1:
        print("✓ ドライバー1起動成功")
        driver1.get("https://x.com/home")
        time.sleep(5)
        print(f"現在のURL: {driver1.current_url}")
        driver1.quit()
    else:
        print("✗ ドライバー1起動失敗")

    time.sleep(3)

    # 直接起動試行
    print("\n【方法2】直接起動")
    try:
        profile_path = pm.get_profile_path(account["email"])
        print(f"プロファイルパス: {profile_path}")

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--profile-directory=Default")

        # プロキシ設定
        if "@" in proxy_url:
            proxy_parts = proxy_url.split("@")
            proxy_server = f"http://{proxy_parts[1]}"
        else:
            proxy_server = proxy_url
        chrome_options.add_argument(f"--proxy-server={proxy_server}")

        driver2 = uc.Chrome(options=chrome_options, version_main=139)
        print("✓ ドライバー2起動成功")

        driver2.get("https://x.com/home")
        time.sleep(5)
        print(f"現在のURL: {driver2.current_url}")

        time.sleep(5)
        driver2.quit()

    except Exception as e:
        print(f"✗ ドライバー2起動失敗: {str(e)[:100]}")

    return True


if __name__ == "__main__":
    # アカウント1でテスト
    debug_browser_launch(1)

    print("\n続けてアカウント2もテストしますか？")
    if input("(y/n): ").lower() == "y":
        debug_browser_launch(2)
