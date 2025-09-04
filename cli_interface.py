import os
import sys
from typing import List
from account_manager import AccountManager
from login_manager import LoginManager
from proxy_tester import ProxyTester
from cli_automation import AutomationCLI

class CLIInterface:
    """メインCLIインターフェース"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.login_manager = LoginManager()
        self.proxy_tester = ProxyTester()
        self.automation_cli = AutomationCLI()
    
    def display_accounts_with_status(self):
        """アカウント一覧表示"""
        print("\n" + "="*60)
        print(" 登録アカウント一覧")
        print("="*60)
        
        if not self.manager.accounts.get("accounts"):
            print("登録されているアカウントがありません。")
            return
        
        for account in self.manager.accounts["accounts"]:
            status = self.manager._get_account_status(account)
            proxy_info = f"{account['proxy']['host']}:{account['proxy']['port']}"
            print(f"[{account['id']:2}] {account['email']:25} {status} プロキシ: {proxy_info}")
        
        print("="*60)
    
    def get_concurrent_count(self, total_accounts: int) -> int:
        """同時実行数を取得"""
        max_recommended = min(10, total_accounts)
        
        print(f"\n対象アカウント数: {total_accounts}")
        print(f"推奨同時実行数: 1-{max_recommended}")
        
        while True:
            try:
                concurrent = int(input(f"同時に開くブラウザ数を入力 (1-{max_recommended}): "))
                if 1 <= concurrent <= max_recommended:
                    return concurrent
                else:
                    print(f"1-{max_recommended}の範囲で入力してください")
            except ValueError:
                print("数字を入力してください")
    
    def main_menu(self):
        """メインメニュー"""
        while True:
            print("\n" + "="*60)
            print(" X自動化ツール - メインメニュー")
            print("="*60)
            print("1. アカウント管理")
            print("2. 初回ログイン")
            print("3. プロキシ設定確認")
            print("4. プロキシテスト")
            print("5. CSVインポート")
            print("6. アカウント追加（手動）")
            print("7. アカウント一覧表示")
            print("8. サンプルCSV生成")
            print("9. 自動操作実行")
            print("10. 終了")
            print("-"*60)
            
            try:
                choice = int(input("選択番号を入力: "))
            except ValueError:
                print("数字を入力してください")
                continue
            
            if choice == 1:
                print("\nアカウント管理メニューは開発中です")
                input("Enterキーで戻る...")
            elif choice == 2:
                self.initial_login_menu()
            elif choice == 3:
                print("\nプロキシ設定メニューは開発中です")
                input("Enterキーで戻る...")
            elif choice == 4:
                self.proxy_test_menu()
            elif choice == 5:
                self.csv_import_menu()
            elif choice == 6:
                print("\n手動アカウント追加は開発中です")
                input("Enterキーで戻る...")
            elif choice == 7:
                self.display_accounts()
            elif choice == 8:
                self.generate_sample_csv()
            elif choice == 9:
                self.automation_cli.run_automation()
            elif choice == 10:
                print("プログラムを終了します")
                break
            else:
                print("1-10の範囲で入力してください")
    
    def initial_login_menu(self):
        """初回ログインメニュー"""
        while True:
            print("\n" + "="*50)
            print(" 初回ログイン")
            print("="*50)
            print("1. 特定の番号を選択してログイン")
            print("2. 複数選択してログイン（カンマ区切り）")
            print("3. 範囲指定でログイン")
            print("4. 未ログインのみ全てログイン")
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
                    valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
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
                    valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
                    if valid_ids:
                        max_concurrent = self.get_concurrent_count(len(valid_ids))
                        self.login_manager.manual_login(valid_ids, max_concurrent)
                    else:
                        print("指定範囲に有効なアカウントがありません")
                except ValueError:
                    print("数字を入力してください")
                    
            elif choice == 4:
                not_logged = []
                for account in self.manager.accounts.get("accounts", []):
                    cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                    if not os.path.exists(cookie_file):
                        not_logged.append(account["id"])
                        
                if not_logged:
                    print(f"未ログインアカウント: {not_logged}")
                    max_concurrent = self.get_concurrent_count(len(not_logged))
                    self.login_manager.manual_login(not_logged, max_concurrent)
                else:
                    print("未ログインのアカウントがありません")
                    
            elif choice == 5:
                break
            else:
                print("1-5の範囲で入力してください")
    
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
        csv_path = input("CSVファイルのパスを入力（デフォルト: config/accounts.csv）: ").strip()
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
                "プロキシホスト": "iproyalfast.hellworld.io",
                "プロキシポート": "12321",
                "プロキシユーザー": "your_username",
                "プロキシパスワード": "your_password_session"
            }
        ]
        
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ["アカウントID", "パスワード", "プロキシホスト", 
                         "プロキシポート", "プロキシユーザー", "プロキシパスワード"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"\n✓ サンプルCSVを作成しました: {csv_path}")
        print("実際のアカウント情報に書き換えてからインポートしてください")
        input("Enterキーで戻る...")

def main():
    """メイン関数"""
    try:
        cli = CLIInterface()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n\nプログラムが中断されました")
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
