import os
import sys
from typing import List, Optional
from account_manager import AccountManager, create_sample_csv


class CLIInterface:
    """X自動化ツールのCLIインターフェース"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.running = True
    
    def clear_screen(self):
        """画面をクリア"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """ヘッダーを表示"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def print_menu(self, options: List[str], title: str = "メニュー"):
        """メニューを表示"""
        self.print_header(title)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("-"*60)
    
    def get_user_input(self, prompt: str, input_type=str, allow_empty: bool = False):
        """ユーザー入力を取得"""
        while True:
            try:
                user_input = input(f"\n{prompt}: ").strip()
                
                if not user_input and allow_empty:
                    return None
                
                if not user_input:
                    print("入力が必要です。")
                    continue
                
                if input_type == int:
                    return int(user_input)
                elif input_type == list:
                    # カンマ区切りの数値リスト
                    return [int(x.strip()) for x in user_input.split(',')]
                else:
                    return user_input
                    
            except ValueError:
                print(f"無効な入力です。{input_type.__name__}形式で入力してください。")
            except KeyboardInterrupt:
                print("\n\n操作がキャンセルされました。")
                return None
    
    def confirm_action(self, message: str = "実行しますか？") -> bool:
        """確認プロンプト"""
        response = self.get_user_input(f"{message} (y/n)", str)
        return response and response.lower() == 'y'
    
    def main_menu(self):
        """メインメニュー"""
        while self.running:
            self.clear_screen()
            options = [
                "アカウント管理",
                "プロキシ設定確認",
                "CSVインポート",
                "アカウント追加（手動）",
                "アカウント一覧表示",
                "サンプルCSV生成",
                "終了"
            ]
            
            self.print_menu(options, "X自動化ツール - メインメニュー")
            choice = self.get_user_input("選択番号を入力", int)
            
            if choice == 1:
                self.account_management_menu()
            elif choice == 2:
                self.show_proxy_settings()
            elif choice == 3:
                self.import_csv()
            elif choice == 4:
                self.add_account_manually()
            elif choice == 5:
                self.show_accounts()
            elif choice == 6:
                self.generate_sample_csv()
            elif choice == 7:
                if self.confirm_action("終了しますか？"):
                    self.running = False
                    print("\nプログラムを終了します。")
            else:
                print("無効な選択です。")
                input("\nEnterキーを押して続行...")
    
    def account_management_menu(self):
        """アカウント管理メニュー"""
        while True:
            self.clear_screen()
            
            # アカウント一覧を表示
            accounts = self.manager.display_accounts()
            
            if not accounts:
                print("\nアカウントが登録されていません。")
                input("\nEnterキーを押してメインメニューに戻る...")
                return
            
            options = [
                "特定の番号を選択",
                "複数選択（カンマ区切り）",
                "範囲指定",
                "未ログインのみ表示",
                "ログイン済みのみ表示",
                "メインメニューに戻る"
            ]
            
            self.print_menu(options, "アカウント選択")
            choice = self.get_user_input("選択番号を入力", int)
            
            if choice == 1:
                self.select_single_account()
            elif choice == 2:
                self.select_multiple_accounts()
            elif choice == 3:
                self.select_range_accounts()
            elif choice == 4:
                self.show_filtered_accounts("not_logged_in")
            elif choice == 5:
                self.show_filtered_accounts("logged_in")
            elif choice == 6:
                return
            else:
                print("無効な選択です。")
            
            input("\nEnterキーを押して続行...")
    
    def select_single_account(self):
        """単一アカウント選択"""
        account_id = self.get_user_input("アカウント番号を入力", int)
        account = self.manager.get_account_by_id(account_id)
        
        if account:
            self.show_account_details(account)
        else:
            print(f"\nアカウント番号 {account_id} は存在しません。")
    
    def select_multiple_accounts(self):
        """複数アカウント選択"""
        print("例: 1,3,5,7")
        ids = self.get_user_input("アカウント番号をカンマ区切りで入力", list)
        
        if ids:
            accounts = self.manager.get_accounts_by_ids(ids)
            if accounts:
                print(f"\n{len(accounts)}件のアカウントを選択しました：")
                for account in accounts:
                    print(f"[{account['id']}] {account['email']}")
            else:
                print("\n指定されたアカウントが見つかりません。")
    
    def select_range_accounts(self):
        """範囲指定でアカウント選択"""
        start_id = self.get_user_input("開始番号を入力", int)
        end_id = self.get_user_input("終了番号を入力", int)
        
        if start_id and end_id:
            accounts = self.manager.get_accounts_by_range(start_id, end_id)
            if accounts:
                print(f"\n[{start_id}]から[{end_id}]までの{len(accounts)}件を選択しました：")
                for account in accounts:
                    print(f"[{account['id']}] {account['email']}")
            else:
                print("\n指定範囲にアカウントが見つかりません。")
    
    def show_filtered_accounts(self, status_filter: str):
        """フィルタリングされたアカウント表示"""
        status_text = "未ログイン" if status_filter == "not_logged_in" else "ログイン済み"
        print(f"\n{status_text}のアカウント：")
        
        filtered = []
        for account in self.manager.accounts["accounts"]:
            account_status = self.manager._get_account_status(account)
            if (status_filter == "not_logged_in" and "✗" in account_status) or \
               (status_filter == "logged_in" and "✓" in account_status):
                filtered.append(account)
                print(f"[{account['id']}] {account['email']} - {account_status}")
        
        if not filtered:
            print(f"{status_text}のアカウントはありません。")
    
    def show_account_details(self, account: dict):
        """アカウント詳細表示"""
        print("\n" + "-"*60)
        print(f"アカウント詳細: [{account['id']}] {account['email']}")
        print("-"*60)
        print(f"ステータス: {self.manager._get_account_status(account)}")
        print(f"プロキシ: {account['proxy']['host']}:{account['proxy']['port']}")
        print(f"プロキシユーザー: {account['proxy']['username']}")
        print(f"最終ログイン: {account.get('last_login', '未ログイン')}")
        print(f"Cookie期限: {account.get('cookie_expires', 'なし')}")
        print("-"*60)
    
    def show_proxy_settings(self):
        """プロキシ設定一覧表示"""
        self.clear_screen()
        self.print_header("プロキシ設定一覧")
        
        accounts = self.manager.get_account_list()
        if not accounts:
            print("アカウントが登録されていません。")
        else:
            for account in accounts:
                acc_data = self.manager.get_account_by_id(account['id'])
                if acc_data:
                    print(f"\n[{account['id']}] {account['email']}")
                    print(f"  ホスト: {acc_data['proxy']['host']}")
                    print(f"  ポート: {acc_data['proxy']['port']}")
                    print(f"  ユーザー: {acc_data['proxy']['username']}")
                    print(f"  完全URL: {self.manager.get_proxy_url(account['id'])}")
        
        input("\nEnterキーを押して続行...")
    
    def import_csv(self):
        """CSVファイルインポート"""
        self.clear_screen()
        self.print_header("CSVインポート")
        
        csv_path = self.get_user_input(
            "CSVファイルパスを入力（Enterでデフォルト: config/accounts.csv）",
            str,
            allow_empty=True
        )
        
        if csv_path is None:
            csv_path = "config/accounts.csv"
        
        if not os.path.exists(csv_path):
            print(f"\nファイルが見つかりません: {csv_path}")
            if self.confirm_action("サンプルCSVを生成しますか？"):
                create_sample_csv(csv_path)
            return
        
        print(f"\nインポート対象: {csv_path}")
        if self.confirm_action("インポートを実行しますか？"):
            result = self.manager.import_accounts_from_csv(csv_path)
            
            if result["success"]:
                print(f"\n✓ {result['message']}")
                print(f"  新規インポート: {result['imported']}件")
                print(f"  スキップ（既存）: {result['skipped']}件")
                
                if "errors" in result:
                    print("\n⚠ エラー:")
                    for error in result["errors"]:
                        print(f"  - {error}")
            else:
                print(f"\n✗ エラー: {result['message']}")
        
        input("\nEnterキーを押して続行...")
    
    def add_account_manually(self):
        """手動でアカウント追加"""
        self.clear_screen()
        self.print_header("アカウント手動追加")
        
        print("\nアカウント情報を入力してください：")
        
        email = self.get_user_input("メールアドレス", str)
        if not email:
            return
        
        password = self.get_user_input("パスワード", str)
        if not password:
            return
        
        print("\nプロキシ情報を入力してください：")
        proxy_host = self.get_user_input("プロキシホスト（例: iproyalfast.hellworld.io）", str)
        proxy_port = self.get_user_input("プロキシポート（例: 12321）", str)
        proxy_user = self.get_user_input("プロキシユーザー", str)
        proxy_pass = self.get_user_input("プロキシパスワード", str)
        
        proxy_info = {
            "host": proxy_host,
            "port": proxy_port,
            "username": proxy_user,
            "password": proxy_pass
        }
        
        print("\n入力内容：")
        print(f"  メール: {email}")
        print(f"  プロキシ: {proxy_host}:{proxy_port}")
        
        if self.confirm_action("このアカウントを追加しますか？"):
            result = self.manager.add_single_account(email, password, proxy_info)
            
            if result["success"]:
                print(f"\n✓ {result['message']}")
                print(f"  アカウントID: {result['id']}")
            else:
                print(f"\n✗ {result['message']}")
        
        input("\nEnterキーを押して続行...")
    
    def show_accounts(self):
        """アカウント一覧表示"""
        self.clear_screen()
        self.manager.display_accounts()
        input("\nEnterキーを押して続行...")
    
    def generate_sample_csv(self):
        """サンプルCSV生成"""
        self.clear_screen()
        self.print_header("サンプルCSV生成")
        
        filepath = self.get_user_input(
            "保存先パスを入力（Enterでデフォルト: config/accounts.csv）",
            str,
            allow_empty=True
        )
        
        if filepath is None:
            filepath = "config/accounts.csv"
        
        if os.path.exists(filepath):
            if not self.confirm_action(f"{filepath} は既に存在します。上書きしますか？"):
                return
        
        create_sample_csv(filepath)
        print(f"\n✓ サンプルCSVを生成しました: {filepath}")
        input("\nEnterキーを押して続行...")


def main():
    """メインエントリーポイント"""
    try:
        cli = CLIInterface()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n\nプログラムを終了します。")
        sys.exit(0)
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
