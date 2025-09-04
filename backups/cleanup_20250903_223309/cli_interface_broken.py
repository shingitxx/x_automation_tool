from cli_automation import AutomationCLI
import os
import sys
from typing import List, Optional
from account_manager import AccountManager, create_sample_csv
from proxy_tester import ProxyTester
from login_manager import LoginManager


class CLIInterface:
    """X自動化ツールのCLIインターフェース（拡張版）"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.proxy_tester = ProxyTester()
        self.login_manager = LoginManager()
        self.running = True
    
    def display_accounts_with_status(self):
        """ステータス付きアカウント一覧表示"""
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
        """メインメニュー（拡張版）"""
        while self.running:
            self.clear_screen()
            options = [
                "アカウント管理",
                "初回ログイン",
                "プロキシテスト",
                "プロキシ設定確認",
                "CSVインポート",
                "アカウント追加（手動）",
                "アカウント一覧表示",
                "サンプルCSV生成",
                "自動操作実行",
                "終了"
            ]
            
            self.print_menu(options, "X自動化ツール - メインメニュー v2.0")
            choice = self.get_user_input("選択番号を入力", int)
            
            if choice == 1:
                self.account_management_menu()
            elif choice == 2:
                self.initial_login_menu()
            elif choice == 3:
                self.proxy_test_menu()
            elif choice == 4:
                self.show_proxy_settings()
            elif choice == 5:
                self.import_csv()
            elif choice == 6:
                self.add_account_manually()
            elif choice == 7:
                self.show_accounts()
            elif choice == 8:
                self.generate_sample_csv()
            elif choice == 9:
                self.run_automation()
            elif choice == 10:
                if self.confirm_action("終了しますか？"):
                    self.running = False
                    print("\nプログラムを終了します。")
            else:
                print("無効な選択です。")
                input("\nEnterキーを押して続行...")
    
    def proxy_test_menu(self):
        """プロキシテストメニュー"""
        while True:
            self.clear_screen()
            self.print_header("プロキシテスト")
            
            options = [
                "特定アカウントのプロキシをテスト",
                "全アカウントのプロキシをテスト",
                "手動でプロキシ情報を入力してテスト",
                "メインメニューに戻る"
            ]
            
            self.print_menu(options, "プロキシテスト")
            choice = self.get_user_input("選択番号を入力", int)
            
            if choice == 1:
                self.test_single_account_proxy()
            elif choice == 2:
                self.test_all_proxies()
            elif choice == 3:
                self.test_manual_proxy()
            elif choice == 4:
                return
            else:
                print("無効な選択です。")
            
            input("\nEnterキーを押して続行...")
    
    def test_single_account_proxy(self):
        """特定アカウントのプロキシをテスト"""
        accounts = self.manager.display_accounts()
        if not accounts:
            print("\nアカウントが登録されていません。")
            return
        
        account_id = self.get_user_input("テストするアカウント番号を入力", int)
        result = self.proxy_tester.test_account_proxy(account_id)
        
        if result['status'] == 'success':
            print(f"\n✅ プロキシは正常に動作しています")
            print(f"接続IP: {result['ip_address']}")
            print(f"応答時間: {result['response_time']}秒")
        else:
            print(f"\n❌ プロキシテストに失敗しました")
            if result.get('error'):
                print(f"エラー: {result['error']}")
    
    def test_all_proxies(self):
        """全アカウントのプロキシをテスト"""
        if self.confirm_action("全アカウントのプロキシをテストしますか？"):
            self.proxy_tester.test_all_accounts()
    
    def test_manual_proxy(self):
        """手動入力でプロキシをテスト"""
        print("\nプロキシ情報を入力してください:")
        host = self.get_user_input("ホスト", str)
        port = self.get_user_input("ポート", str)
        username = self.get_user_input("ユーザー名", str)
        password = self.get_user_input("パスワード", str)
        
        proxy_url = f"http://{username}:{password}@{host}:{port}"
        
        result = self.proxy_tester.test_proxy(proxy_url)
        
        if result['status'] == 'success':
            print(f"\n✅ プロキシは正常に動作しています")
            print(f"接続IP: {result['ip_address']}")
            print(f"応答時間: {result['response_time']}秒")
        else:
            print(f"\n❌ プロキシテストに失敗しました")
            if result.get('error'):
                print(f"エラー: {result['error']}")
    
    def initial_login_menu(self):
        """初回ログインメニュー"""
        self.clear_screen()
        
        # アカウント一覧を表示
        accounts = self.manager.display_accounts()
        
        if not accounts:
            print("\nアカウントが登録されていません。")
            input("\nEnterキーを押してメインメニューに戻る...")
            return
        
        options = [
            "特定の番号を選択してログイン",
            "複数選択してログイン（カンマ区切り）",
            "範囲指定でログイン",
            "未ログインのみ全てログイン",
            "自動ログイン（ID/パスワード自動入力）",
            "メインメニューに戻る"
        ]
        
        self.print_menu(options, "初回ログイン")
        choice = self.get_user_input("選択番号を入力", int)
        
        account_ids = []
        
        if choice == 1:
            account_id = self.get_user_input("アカウント番号を入力", int)
            account_ids = [account_id]
        elif choice == 2:
            print("例: 1,3,5,7")
            account_ids = self.get_user_input("アカウント番号をカンマ区切りで入力", list)
        elif choice == 3:
            start_id = self.get_user_input("開始番号を入力", int)
            end_id = self.get_user_input("終了番号を入力", int)
            account_ids = list(range(start_id, end_id + 1))
        elif choice == 4:
            # 未ログインアカウントを取得
            for account in self.manager.accounts["accounts"]:
                status = self.manager._get_account_status(account)
                if "✗" in status:
                    account_ids.append(account["id"])
        elif choice == 5:
            # 自動ログインモード（アカウント選択機能付き）
            print("\n自動ログインモード（ID/パスワードまで自動入力）")
            print("2FA認証は手動で入力が必要です")
            
            # アカウント選択
            selected_ids = self.select_accounts_for_login()
            if not selected_ids:
                print("アカウントが選択されませんでした")
                return
            
            # 同時実行数設定
            max_concurrent = self.get_user_input(
                f"同時に開くブラウザ数を入力（1-{min(5, len(selected_ids))}）",
                int
            )
            
            if self.confirm_action(f"{len(selected_ids)}個のアカウントで自動ログインを開始しますか？"):
                self.login_manager.auto_login_until_2fa(selected_ids, max_concurrent)
                
        elif choice == 6:
            return
        else:
            print("無効な選択です。")
            input("\nEnterキーを押して続行...")
            return
        
        if account_ids:
            # 有効なアカウントIDのみフィルタ
            valid_ids = []
            for aid in account_ids:
                if self.manager.get_account_by_id(aid):
                    valid_ids.append(aid)
            
            if valid_ids:
                max_concurrent = self.get_user_input(
                    f"同時に開くブラウザ数を入力（1-{min(10, len(valid_ids))}）",
                    int
                )
                
                if self.confirm_action(f"{len(valid_ids)}個のアカウントでログインを開始しますか？"):
                    self.login_manager.manual_login(valid_ids, max_concurrent)
            else:
                print("有効なアカウントが見つかりません。")
        
        input("\nEnterキーを押して続行...")
    
    def select_accounts_for_login(self):
        """ログイン用のアカウント選択"""
        try:
            self.display_accounts_with_status()
        except:
            print("
登録アカウント:")
            for account in self.manager.accounts.get("accounts", []):
                print(f"[{account['id']}] {account['email']}")
        
        print("
ログイン方法を選択してください:")
        print("1. 特定の番号を選択してログイン")
        print("2. 複数選択してログイン（カンマ区切り）")
        print("3. 範囲指定でログイン")
        print("4. 未ログインのみ全てログイン")
        print("5. 戻る")
        
        while True:
            try:
                choice = int(input("選択 (1-5): "))
                if 1 <= choice <= 5:
                    break
                else:
                    print("1-5の範囲で入力してください")
            except ValueError:
                print("数字を入力してください")
        
        if choice == 1:
            while True:
                try:
                    account_id = int(input("ログインするアカウント番号を入力: "))
                    if self.manager.get_account_by_id(account_id):
                        return [account_id]
                    else:
                        print("存在しないアカウント番号です")
                except ValueError:
                    print("数字を入力してください")
                    
        elif choice == 2:
            try:
                ids_str = input("ログインするアカウント番号をカンマ区切りで入力: ")
                account_ids = [int(x.strip()) for x in ids_str.split(",")]
                valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
                if valid_ids:
                    return valid_ids
                else:
                    print("有効なアカウントが見つかりませんでした")
            except ValueError:
                print("正しい形式で入力してください（例: 1,2,3）")
                
        elif choice == 3:
            try:
                start_id = int(input("開始アカウント番号: "))
                end_id = int(input("終了アカウント番号: "))
                if start_id <= end_id:
                    account_ids = list(range(start_id, end_id + 1))
                    valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
                    if valid_ids:
                        return valid_ids
                    else:
                        print("指定範囲に有効なアカウントが見つかりませんでした")
                else:
                    print("開始番号は終了番号以下にしてください")
            except ValueError:
                print("数字を入力してください")
                
        elif choice == 4:
            not_logged_ids = []
            try:
                for account in self.manager.accounts.get("accounts", []):
                    cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                    if not os.path.exists(cookie_file):
                        not_logged_ids.append(account["id"])
                
                if not_logged_ids:
                    print(f"未ログインアカウント: {not_logged_ids}")
                    return not_logged_ids
                else:
                    print("未ログインのアカウントがありません")
            except Exception as e:
                print(f"アカウント状態の確認エラー: {e}")
        
        return []

    
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



    def run_automation(self):
        """自動操作を実行"""
        from cli_automation import AutomationCLI
        automation_cli = AutomationCLI()
        automation_cli.run_automation()

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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
