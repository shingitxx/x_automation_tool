# compare_test.py - 動作比較テスト（新規作成）
import os
import time

os.chdir(r"C:\Users\nextS\MyApps\x_automation_tool")

from automation_executor import AutomationExecutor


def test_direct_call():
    """optimal_parallel.pyと同じ方式"""
    print("\n【テスト1】直接呼び出し（optimal_parallel方式）")
    executor = AutomationExecutor()

    result = executor.process_single_account(
        account_id=1,
        target_url="https://x.com/X/status/1854720980188504557",
        actions={"like": True, "bookmark": True},
        wait_range=(2, 3),
    )
    print(f"結果: {result.get('success')}")
    return result


def test_sequential_call():
    """CLIメニュー8と同じ方式"""
    print("\n【テスト2】execute_sequential経由")
    executor = AutomationExecutor()

    results = executor.execute_sequential(
        account_ids=[1],
        target_url="https://x.com/X/status/1854720980188504557",
        actions={"like": True, "bookmark": True},
        wait_range=(2, 3),
    )
    print(f"結果: {len(results)}件")
    return results


if __name__ == "__main__":
    print("動作比較テスト")
    print("=" * 50)

    # テスト1
    test_direct_call()

    time.sleep(5)

    # テスト2
    test_sequential_call()
