# single_account_test.py - 単一アカウントテスト（新規作成）
import os
import sys
import time

os.chdir(r"C:\Users\nextS\MyApps\x_automation_tool")
sys.path.append(os.getcwd())

from automation_executor import AutomationExecutor


def test_single_account(account_id: int, target_url: str):
    """単一アカウントのテスト実行"""
    print(f"\nアカウント {account_id} のテスト開始")
    print("=" * 50)

    executor = AutomationExecutor()

    print("ブラウザが起動します...")
    print("プロキシ認証ダイアログが出たら入力してください")
    print("\n20秒待機中...")

    # プロキシ認証用の待機
    for i in range(20, 0, -1):
        print(f"\r残り {i} 秒...", end="")
        time.sleep(1)

    print("\n\n処理開始")

    result = executor.process_single_account(
        account_id=account_id,
        target_url=target_url,
        actions={"like": True, "bookmark": True},
        wait_range=(2, 3),
    )

    print("\n結果:")
    print(f"成功: {result.get('success', False)}")
    print(f"実行されたアクション: {result.get('actions_performed', [])}")

    return result


if __name__ == "__main__":
    # テスト用URL
    url = input("ツイートURL: ").strip()
    if not url:
        url = "https://x.com/77_nanasi_4/status/1963211107155546282"

    # アカウント1でテスト
    test_single_account(1, url)
