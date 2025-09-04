import os
from typing import List, Dict, Tuple
from automation_executor_v2 import AutomationExecutorV2, create_sample_reply_csv
from account_manager import AccountManager


class AutomationCLIV2:
    """自動操作用CLIインターフェース（プロファイル版）"""

    def __init__(self):
        self.executor = AutomationExecutorV2()
        self.account_manager = AccountManager()

    def run_automation(self):
        """自動操作実行メニュー"""
        print("\n" + "=" * 60)
        print(" 自動操作設定")
        print("=" * 60)

        # アカウント選択
        account_ids = self.select_accounts()
        if not account_ids:
            print("実行をキャンセルしました")
            return

        # 同時実行数設定
        max_workers = self.get_concurrent_count(len(account_ids))

        # URL入力
        target_url = self.get_target_url()

        # アクション選択
        actions = self.select_actions()

        # リプライテキスト読み込み（必要な場合）
        if actions.get("reply", False):
            if not self.executor.load_reply_texts():
                print("\nリプライテキストCSVが見つかりません")
                create_csv = input("サンプルCSVを作成しますか？ (y/n): ")
                if create_csv.lower() == "y":
                    create_sample_reply_csv()
                    print(
                        "config/reply_texts.csvを作成しました。編集してから再実行してください"
                    )
                    return
                else:
                    print("リプライをスキップします")
                    actions["reply"] = False

        # 待機時間設定
        wait_range = self.get_wait_range()

        # 設定確認
        print("\n" + "=" * 60)
        print(" 設定確認")
        print("=" * 60)
        print(f"アカウント数: {len(account_ids)}")
        print(f"同時実行数: {max_workers}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print("=" * 60)

        confirm = input("実行を開始しますか？(y/n): ")
        if confirm.lower() != "y":
            print("実行をキャンセルしました")
            return

        # 並列実行（改良版）
        results = self.executor.execute_parallel(
            account_ids=account_ids,
            target_url=target_url,
            actions=actions,
            wait_range=wait_range,
            max_workers=max_workers,
        )

        input("\nEnterキーで戻る...")

    def select_accounts(self) -> List[int]:
        """アカウント選択"""
        self.display_accounts()

        print("\n" + "=" * 50)
        print(" アカウント選択")
        print("=" * 50)
        print("1. 特定の番号を選択")
        print("2. 複数選択（カンマ区切り）")
        print("3. 範囲指定")
        print("4. 全アカウント")
        print("5. キャンセル")

        try:
            choice = int(input("選択: "))
        except ValueError:
            return []

        if choice == 1:
            try:
                account_id = int(input("アカウント番号: "))
                if self.account_manager.get_account_by_id(account_id):
                    return [account_id]
            except ValueError:
                pass
            return []

        elif choice == 2:
            try:
                ids_str = input("アカウント番号（カンマ区切り）: ")
                account_ids = [int(x.strip()) for x in ids_str.split(",")]
                valid_ids = [
                    id
                    for id in account_ids
                    if self.account_manager.get_account_by_id(id)
                ]
                return valid_ids
            except ValueError:
                return []

        elif choice == 3:
            try:
                start = int(input("開始番号: "))
                end = int(input("終了番号: "))
                account_ids = list(range(start, end + 1))
                valid_ids = [
                    id
                    for id in account_ids
                    if self.account_manager.get_account_by_id(id)
                ]
                return valid_ids
            except ValueError:
                return []

        elif choice == 4:
            return [
                acc["id"] for acc in self.account_manager.accounts.get("accounts", [])
            ]

        return []

    def get_concurrent_count(self, total_accounts: int) -> int:
        """同時実行数取得"""
        max_recommended = min(5, total_accounts)

        print(f"\n同時実行数設定")
        print(f"推奨: 1-{max_recommended}")

        while True:
            try:
                concurrent = int(input(f"同時実行数 (1-{max_recommended}): "))
                if 1 <= concurrent <= max_recommended:
                    return concurrent
                else:
                    print(f"1-{max_recommended}の範囲で入力してください")
            except ValueError:
                print("数字を入力してください")

    def get_target_url(self) -> str:
        """対象URL取得"""
        print("\n対象のツイートURL入力")
        print("例: https://x.com/username/status/1234567890")

        while True:
            url = input("URL: ").strip()
            if "x.com" in url or "twitter.com" in url:
                return url
            print("有効なX(Twitter)のURLを入力してください")

    def select_actions(self) -> Dict[str, bool]:
        """実行アクション選択"""
        print("\n実行する操作を選択")

        actions = {}
        actions["like"] = input("いいねを実行？ (y/n): ").lower() == "y"
        actions["bookmark"] = input("ブックマークを実行？ (y/n): ").lower() == "y"
        actions["retweet"] = input("リツイートを実行？ (y/n): ").lower() == "y"
        actions["reply"] = input("リプライを実行？ (y/n): ").lower() == "y"

        return actions

    def get_wait_range(self) -> Tuple[int, int]:
        """待機時間範囲取得"""
        print("\n操作間の待機時間を設定します")

        while True:
            try:
                min_wait = int(input("最小待機時間（秒）: "))
                max_wait = int(input("最大待機時間（秒）: "))

                if 0 <= min_wait <= max_wait:
                    return (min_wait, max_wait)
                else:
                    print("最小値 <= 最大値で入力してください")
            except ValueError:
                print("数字を入力してください")

    def display_accounts(self):
        """アカウント一覧表示"""
        print("\n" + "=" * 60)
        print(" 登録アカウント一覧")
        print("=" * 60)

        if not self.account_manager.accounts.get("accounts"):
            print("登録されているアカウントがありません")
            return

        for account in self.account_manager.accounts["accounts"]:
            status = self.account_manager._get_account_status(account)
            print(f"[{account['id']:2}] {account['email']:25} {status}")

        print("=" * 60)
