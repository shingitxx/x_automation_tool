import os
import sys
from typing import List
from account_manager import AccountManager
from login_manager_v2 import LoginManagerV2
from profile_manager import ProfileManager
from automation_executor_v2 import AutomationExecutorV2
from proxy_tester import ProxyTester
from cli_automation_v2 import AutomationCLIV2


class CLIInterfaceV2:
    """改良版メインCLIインターフェース（プロファイル管理対応）"""

    def __init__(self):
        self.manager = AccountManager()
        self.login_manager = LoginManagerV2()
        self.profile_manager = ProfileManager()
        self.automation_executor = AutomationExecutorV2()
        self.proxy_tester = ProxyTester()
        self.automation_cli = AutomationCLIV2()

    def display_accounts_with_status(self):
        """アカウント一覧表示（プロファイル状態付き）"""
        print("\n" + "=" * 70)
        print(" 登録アカウント一覧")
        print("=" * 70)

        if not self.manager.accounts.get("accounts"):
            print("登録されているアカウントがありません。")
            return

        for account in self.manager.accounts["accounts"]:
            # プロファイル状態確認
            profile_status = (
                "✓" if self.profile_manager.profile_exists(account["email"]) else "✗"
            )

            # Cookie状態確認
            cookie_status = self.manager._get_account_status(account)

            proxy_info = f"{account['proxy']['host']}:{account['proxy']['port']}"

            print(
                f"[{account['id']:2}] {account['email']:25} "
                f"プロファイル:{profile_status} {cookie_status:12} "
                f"プロキシ:{proxy_info}"
            )

        print("=" * 70)

    def get_concurrent_count(self, total_accounts: int) -> int:
        """同時実行数を取得"""
        max_recommended = min(5, total_accounts)  # プロファイル使用時は5まで推奨

        print(f"\n対象アカウント数: {total_accounts}")
        print(f"推奨同時実行数: 1-{max_recommended}")

        while True:
            try:
                concurrent = int(
                    input(f"同時に開くブラウザ数を入力 (1-{max_recommended}): ")
                )
                if 1 <= concurrent <= max_recommended:
                    return concurrent
                else:
                    print(f"1-{max_recommended}の範囲で入力してください")
            except ValueError:
                print("数字を入力してください")

    def main_menu(self):
        """メインメニュー"""
        while True:
            print("\n" + "=" * 60)
            print(" X自動化ツール v2.0 - メインメニュー")
            print("=" * 60)
            print("1. プロファイル管理")
            print("2. 初回ログイン（プロファイル作成）")
            print("3. プロファイル状態確認")
            print("4. プロキシテスト")
            print("5. CSVインポート")
            print("6. アカウント一覧表示")
            print("7. サンプルCSV生成")
            print("8. 自動操作実行（プロファイル版）")
            print("9. プロファイルクリーンアップ")
            print("10. 終了")
            print("-" * 60)

            try:
                choice = int(input("選択番号を入力: "))
            except ValueError:
                print("数字を入力してください")
                continue

            if choice == 1:
                self.profile_management_menu()
            elif choice == 2:
                self.initial_login_menu()
            elif choice == 3:
                self.check_profile_status()
            elif choice == 4:
                self.proxy_test_menu()
            elif choice == 5:
                self.csv_import_menu()
            elif choice == 6:
                self.display_accounts()
            elif choice == 7:
                self.generate_sample_csv()
            elif choice == 8:
                self.automation_execution_menu()
            elif choice == 9:
                self.cleanup_profiles()
            elif choice == 10:
                print("プログラムを終了します")
                break
            else:
                print("1-10の範囲で入力してください")

    def profile_management_menu(self):
        """プロファイル管理メニュー"""
        while True:
            print("\n" + "=" * 50)
            print(" プロファイル管理")
            print("=" * 50)
            print("1. 全プロファイル一覧")
            print("2. プロファイル削除")
            print("3. プロファイルログイン状態確認")
            print("4. メインメニューに戻る")

            try:
                choice = int(input("選択: "))
            except ValueError:
                print("数字を入力してください")
                continue

            if choice == 1:
                self.show_all_profiles()
            elif choice == 2:
                self.delete_profile()
            elif choice == 3:
                self.check_profile_login()
            elif choice == 4:
                break
            else:
                print("1-4の範囲で入力してください")

    def show_all_profiles(self):
        """全プロファイル表示"""
        profiles = self.profile_manager.get_all_profiles()

        print("\n" + "=" * 70)
        print(" プロファイル一覧")
        print("=" * 70)

        if not profiles:
            print("プロファイルがありません。")
        else:
            for profile in profiles:
                status = "存在" if profile.get("exists", False) else "削除済み"
                print(
                    f"メール: {profile['email']:30} "
                    f"状態: {status:8} "
                    f"最終使用: {profile.get('last_used', 'N/A')[:19]}"
                )

        print("=" * 70)
        input("Enterキーで戻る...")

    def delete_profile(self):
        """プロファイル削除"""
        self.display_accounts_with_status()
        try:
            account_id = int(input("\n削除するアカウント番号: "))
            account = self.manager.get_account_by_id(account_id)

            if account:
                confirm = input(
                    f"{account['email']} のプロファイルを削除しますか？ (y/n): "
                )
                if confirm.lower() == "y":
                    if self.profile_manager.delete_profile(account["email"]):
                        print("✓ プロファイル削除完了")
                    else:
                        print("✗ プロファイル削除失敗")
            else:
                print("アカウントが見つかりません")
        except ValueError:
            print("数字を入力してください")
        input("Enterキーで戻る...")

    def check_profile_login(self):
        """プロファイルログイン状態確認"""
        self.display_accounts_with_status()
        try:
            account_id = int(input("\n確認するアカウント番号: "))
            account = self.manager.get_account_by_id(account_id)

            if account:
                print(f"\n{account['email']} のログイン状態を確認中...")
                if self.profile_manager.check_profile_login_status(account["email"]):
                    print("✓ ログイン済み")
                else:
                    print("✗ 未ログイン")
            else:
                print("アカウントが見つかりません")
        except ValueError:
            print("数字を入力してください")
        input("Enterキーで戻る...")

    def initial_login_menu(self):
        """初回ログインメニュー（プロファイル作成）"""
        while True:
            print("\n" + "=" * 50)
            print(" 初回ログイン（プロファイル作成）")
            print("=" * 50)
            print("1. 特定の番号を選択してログイン")
            print("2. 複数選択してログイン（カンマ区切り）")
            print("3. 範囲指定でログイン")
            print("4. プロファイルがないアカウント全てログイン")
            print("5. メインメニューに戻る")

            try:
                choice = int(input("選択: "))
            except ValueError:
                print("数字を入力してください")
                continue

            if choice == 1:
                self.display_accounts_with_status()
                try:
                    account_id = int(input("ログインするアカウント番号: "))
                    if self.manager.get_account_by_id(account_id):
                        self.login_manager.manual_login([account_id], 1)
                    else:
                        print("存在しないアカウントです")
                except ValueError:
                    print("数字を入力してください")

            elif choice == 2:
                self.display_accounts_with_status()
                try:
                    ids_str = input("ログインするアカウント番号をカンマ区切りで入力: ")
                    account_ids = [int(x.strip()) for x in ids_str.split(",")]
                    valid_ids = [
                        id for id in account_ids if self.manager.get_account_by_id(id)
                    ]
                    if valid_ids:
                        max_concurrent = self.get_concurrent_count(len(valid_ids))
                        self.login_manager.manual_login(valid_ids, max_concurrent)
                    else:
                        print("有効なアカウントがありません")
                except ValueError:
                    print("正しい形式で入力してください")

            elif choice == 3:
                self.display_accounts_with_status()
                try:
                    start = int(input("開始番号: "))
                    end = int(input("終了番号: "))
                    account_ids = list(range(start, end + 1))
                    valid_ids = [
                        id for id in account_ids if self.manager.get_account_by_id(id)
                    ]
                    if valid_ids:
                        max_concurrent = self.get_concurrent_count(len(valid_ids))
                        self.login_manager.manual_login(valid_ids, max_concurrent)
                    else:
                        print("指定範囲に有効なアカウントがありません")
                except ValueError:
                    print("数字を入力してください")

            elif choice == 4:
                no_profile = []
                for account in self.manager.accounts.get("accounts", []):
                    if not self.profile_manager.profile_exists(account["email"]):
                        no_profile.append(account["id"])

                if no_profile:
                    print(f"プロファイルがないアカウント: {no_profile}")
                    max_concurrent = self.get_concurrent_count(len(no_profile))
                    self.login_manager.manual_login(no_profile, max_concurrent)
                else:
                    print("プロファイルがないアカウントがありません")

            elif choice == 5:
                break
            else:
                print("1-5の範囲で入力してください")

    def check_profile_status(self):
        """プロファイル状態確認"""
        self.display_accounts_with_status()
        input("Enterキーで戻る...")

    def proxy_test_menu(self):
        """プロキシテストメニュー"""
        print("\nプロキシテストを実行します")
        self.display_accounts_with_status()
        try:
            account_id = int(input("テストするアカウント番号: "))
            result = self.proxy_tester.test_account_proxy(account_id)
            print(f"\nテスト結果: {result.get('status', 'unknown')}")
        except ValueError:
            print("数字を入力してください")
        input("Enterキーで戻る...")

    def csv_import_menu(self):
        """CSVインポートメニュー"""
        csv_path = input(
            "CSVファイルのパスを入力（デフォルト: config/accounts.csv）: "
        ).strip()
        if not csv_path:
            csv_path = "config/accounts.csv"

        if os.path.exists(csv_path):
            result = self.manager.import_from_csv(csv_path)
            print(f"\nインポート結果:")
            if "error" in result:
                print(f"エラー: {result['error']}")
            else:
                print(f"インポート: {result.get('imported', 0)}件")
                print(f"スキップ: {result.get('skipped', 0)}件")
                print(f"エラー: {result.get('errors', 0)}件")
        else:
            print(f"ファイルが見つかりません: {csv_path}")
        input("Enterキーで戻る...")

    def display_accounts(self):
        """アカウント一覧表示"""
        self.display_accounts_with_status()
        input("Enterキーで戻る...")

    def generate_sample_csv(self):
        """サンプルCSV生成"""
        csv_path = "config/accounts_sample.csv"
        os.makedirs("config", exist_ok=True)

        import csv

        sample_data = [
            {
                "アカウントID": "user1@example.com",
                "パスワード": "password123",
                "プロキシホスト": "proxy.example.com",
                "プロキシポート": "8080",
                "プロキシユーザー": "proxy_user",
                "プロキシパスワード": "proxy_pass",
            }
        ]

        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            fieldnames = [
                "アカウントID",
                "パスワード",
                "プロキシホスト",
                "プロキシポート",
                "プロキシユーザー",
                "プロキシパスワード",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)

        print(f"\n✓ サンプルCSVを作成しました: {csv_path}")
        print("実際のアカウント情報に書き換えてからインポートしてください")
        input("Enterキーで戻る...")

    def automation_execution_menu(self):
        """自動操作実行メニュー（プロファイル版）"""
        # 既存のAutomationCLIを使用するか、新しい実装を追加
        print("\n自動操作実行（プロファイル版）を開始します")
        self.automation_cli.run_automation()

    def cleanup_profiles(self):
        """プロファイルクリーンアップ"""
        print("\n一時プロファイルをクリーンアップします...")
        self.profile_manager.cleanup_temp_profiles()
        print("✓ クリーンアップ完了")
        input("Enterキーで戻る...")


def main():
    """メイン関数"""
    try:
        cli = CLIInterfaceV2()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n\nプログラムが中断されました")
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
