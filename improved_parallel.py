# improved_parallel.py - CLI方式を参考にした改良版並列実行（新規作成）
import os
import time
import threading
from datetime import datetime
from typing import List, Dict

os.chdir(r"C:\Users\nextS\MyApps\x_automation_tool")

from automation_executor import AutomationExecutor
from account_manager import AccountManager
from profile_manager import ProfileManager


class ImprovedParallelExecutor:
    """CLI方式を参考にした並列実行"""

    def __init__(self):
        self.executor = AutomationExecutor()
        self.account_manager = AccountManager()
        self.profile_manager = ProfileManager()
        self.results = []
        self.lock = threading.Lock()

    def process_account_wrapper(
        self, account_id: int, target_url: str, actions: dict, delay: int
    ):
        """アカウント処理のラッパー（execute_sequentialの単体版）"""
        # 遅延起動
        time.sleep(delay)

        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            print(f"[{account_id}] アカウントが見つかりません")
            return

        # プロファイル存在確認（重要）
        if not self.profile_manager.profile_exists(account["email"]):
            print(f"[{account_id}] プロファイルがありません")
            return

        print(f"\n[{account_id}] {account['email']} - 開始")

        # execute_sequentialと同じ方法で実行
        result = self.executor.process_single_account(
            account_id=account_id,
            target_url=target_url,
            actions=actions,
            wait_range=(2, 3),
        )

        with self.lock:
            self.results.append(result)

        if result.get("success"):
            print(f"[{account_id}] ✓ 成功")
        else:
            print(f"[{account_id}] ✗ 失敗")

    def run_parallel(
        self, account_ids: List[int], target_url: str, actions: Dict[str, bool]
    ):
        """並列実行（メイン）"""
        print(f"\n{'='*60}")
        print(f" 改良版並列実行")
        print(f"{'='*60}")
        print(f"対象URL: {target_url}")
        print(f"アカウント: {account_ids}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"{'='*60}")

        # プロファイル確認
        for account_id in account_ids:
            account = self.account_manager.get_account_by_id(account_id)
            if account and self.profile_manager.profile_exists(account["email"]):
                print(f"[{account_id}] プロファイル確認 ✓")
            else:
                print(f"[{account_id}] プロファイル確認 ✗")

        threads = []

        # 各アカウントを遅延起動
        for i, account_id in enumerate(account_ids):
            delay = i * 8  # 8秒間隔
            thread = threading.Thread(
                target=self.process_account_wrapper,
                args=(account_id, target_url, actions, delay),
            )
            thread.start()
            threads.append(thread)

            if delay == 0:
                print(f"[{account_id}] 即座に起動")
            else:
                print(f"[{account_id}] {delay}秒後に起動")

        # 全スレッド完了待ち
        for thread in threads:
            thread.join()

        # 結果サマリー
        self.print_summary()

    def print_summary(self):
        """結果サマリー表示"""
        print(f"\n{'='*60}")
        print(f" 実行結果")
        print(f"{'='*60}")

        total = len(self.results)
        success = sum(1 for r in self.results if r.get("success", False))
        failed = total - success

        print(f"総数: {total}")
        print(f"成功: {success}")
        print(f"失敗: {failed}")

        for result in self.results:
            account_id = result.get("account_id")
            actions = result.get("actions_performed", [])
            if actions:
                print(f"[{account_id}]: {', '.join(actions)}")
            else:
                print(f"[{account_id}]: 失敗")

        print(f"{'='*60}")


def main():
    """メイン実行"""
    executor = ImprovedParallelExecutor()

    # URL入力
    print("\nツイートURLを入力してください")
    url = input("URL (Enterでデフォルト): ").strip()
    if not url:
        url = "https://x.com/X/status/1854720980188504557"

    # アクション設定
    actions = {"like": True, "bookmark": True, "retweet": False, "reply": False}

    # 2アカウントでテスト
    account_ids = [1, 2]

    print(f"\n実行アカウント: {account_ids}")
    confirm = input("実行しますか？ (y/n): ")

    if confirm.lower() == "y":
        executor.run_parallel(account_ids, url, actions)
    else:
        print("キャンセルしました")


if __name__ == "__main__":
    main()
