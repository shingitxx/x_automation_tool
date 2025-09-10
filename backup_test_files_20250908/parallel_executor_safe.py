# parallel_executor_safe.py - 安全な並列実行（新規作成）
import os
import time
import subprocess
from threading import Thread, Lock


class SafeParallelExecutor:
    """プロキシ認証を考慮した安全な並列実行"""

    def __init__(self):
        self.lock = Lock()
        self.results = []

    def execute_single_account_subprocess(
        self, account_id: int, target_url: str, delay: int
    ):
        """単一アカウントをサブプロセスで実行"""
        # 遅延起動
        time.sleep(delay)

        print(f"\n[アカウント {account_id}] 起動開始")
        print(f"[アカウント {account_id}] 20秒後に処理を開始します...")

        # サブプロセスとして実行（完全に独立）
        script = f"""
import sys
import os
sys.path.append(r'C:\\Users\\nextS\\MyApps\\x_automation_tool')
os.chdir(r'C:\\Users\\nextS\\MyApps\\x_automation_tool')

import time
from automation_executor import AutomationExecutor

executor = AutomationExecutor()

# プロキシ認証の完了を待つ
print("[{account_id}] プロキシ認証待機中（20秒）...")
time.sleep(20)

print("[{account_id}] 自動操作開始")
result = executor.process_single_account(
    {account_id},
    "{target_url}",
    {{"like": True, "bookmark": True}},
    (2, 3)
)

print(f"[{account_id}] 完了: " + str(result.get("success", False)))
"""

        # Pythonサブプロセスとして実行
        try:
            result = subprocess.run(
                ["py", "-3.10", "-c", script],
                capture_output=True,
                text=True,
                timeout=120,  # 2分のタイムアウト
            )

            with self.lock:
                self.results.append(
                    {
                        "account_id": account_id,
                        "success": "完了: True" in result.stdout,
                        "output": result.stdout,
                        "error": result.stderr,
                    }
                )

            if result.returncode == 0:
                print(f"[アカウント {account_id}] ✓ 正常終了")
            else:
                print(f"[アカウント {account_id}] ✗ エラー終了")

        except subprocess.TimeoutExpired:
            print(f"[アカウント {account_id}] ✗ タイムアウト")
        except Exception as e:
            print(f"[アカウント {account_id}] ✗ 実行エラー: {str(e)[:50]}")

    def run_parallel(self, account_ids: list, target_url: str):
        """並列実行（メイン）"""
        print("\n" + "=" * 60)
        print(" 安全な並列実行モード")
        print("=" * 60)
        print("各ブラウザは20秒後に自動操作を開始します")
        print("プロキシ認証ダイアログが出たら手動で入力してください")
        print("=" * 60)

        threads = []

        # 各アカウントを15秒間隔で起動
        for i, account_id in enumerate(account_ids):
            delay = i * 15  # 15秒間隔
            thread = Thread(
                target=self.execute_single_account_subprocess,
                args=(account_id, target_url, delay),
            )
            thread.start()
            threads.append(thread)
            print(f"アカウント {account_id}: {delay}秒後に起動予定")

        # 全スレッド完了待ち
        for thread in threads:
            thread.join()

        # 結果表示
        print("\n" + "=" * 60)
        print(" 実行結果")
        print("=" * 60)
        success_count = sum(1 for r in self.results if r.get("success", False))
        print(f"成功: {success_count}/{len(self.results)}")
        print("=" * 60)


if __name__ == "__main__":
    executor = SafeParallelExecutor()

    # 対話式URL入力
    print("\nツイートURLを入力してください")
    url = input("URL (Enterでデフォルト): ").strip()
    if not url:
        url = "https://x.com/77_nanasi_4/status/1963211107155546282"

    # 2アカウントで実行
    executor.run_parallel(account_ids=[1, 2], target_url=url)
