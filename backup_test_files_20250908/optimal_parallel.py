# optimal_parallel.py として保存
import os
import time
import threading
from automation_executor import AutomationExecutor


def run_parallel_optimized(account_ids, target_url, actions, delay_seconds=3):
    """最適化された並列実行"""
    executor = AutomationExecutor()
    threads = []

    def run_with_delay(account_id, delay):
        time.sleep(delay)
        print(f"[{account_id}] 起動")
        executor.process_single_account(account_id, target_url, actions, (2, 3))

    for i, account_id in enumerate(account_ids):
        thread = threading.Thread(
            target=run_with_delay, args=(account_id, i * delay_seconds)
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("全アカウント完了")


if __name__ == "__main__":
    os.chdir(r"C:\Users\nextS\MyApps\x_automation_tool")

    # 3秒間隔で4アカウント起動テスト
    run_parallel_optimized(
        account_ids=[1, 2],  # まず2つでテスト
        target_url="https://x.com/adotarou_/status/1806524402617757833",
        actions={"like": True, "bookmark": True},
        delay_seconds=3,  # 3秒に短縮
    )
