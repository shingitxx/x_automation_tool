# trace_test.py - 処理追跡テスト（新規作成）
import os
import time

os.chdir(r"C:\Users\nextS\MyApps\x_automation_tool")

from account_manager import AccountManager
from profile_manager import ProfileManager


def trace_execution():
    """段階的に処理を追跡"""
    print("処理追跡テスト開始")
    print("=" * 50)

    # ステップ1: マネージャー初期化
    print("\n【ステップ1】マネージャー初期化")
    am = AccountManager()
    pm = ProfileManager()
    print("✓ 完了")

    # ステップ2: アカウント取得
    print("\n【ステップ2】アカウント取得")
    account = am.get_account_by_id(1)
    print(f"アカウント: {account['email']}")
    print("✓ 完了")

    # ステップ3: プロファイル確認
    print("\n【ステップ3】プロファイル確認")
    exists = pm.profile_exists(account["email"])
    print(f"プロファイル存在: {exists}")
    print("✓ 完了")

    # ステップ4: プロキシURL取得
    print("\n【ステップ4】プロキシURL取得")
    proxy_url = am.get_proxy_url(1)
    print(f"プロキシ: {proxy_url[:50]}...")
    print("✓ 完了")

    # ステップ5: ドライバー作成（ここが問題の可能性大）
    print("\n【ステップ5】ドライバー作成")
    print("10秒待機してから起動...")
    time.sleep(10)  # optimal_parallel.pyと同じ待機

    driver = pm.create_driver_with_profile(
        account["email"], proxy_url=proxy_url, use_temp=False
    )

    if driver:
        print("✓ ドライバー作成成功")
        driver.get("https://x.com/home")
        time.sleep(5)
        driver.quit()
    else:
        print("✗ ドライバー作成失敗")

    print("\n完了")


if __name__ == "__main__":
    trace_execution()
automation_executor
