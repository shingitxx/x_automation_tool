import os
from typing import Dict, List, Tuple
from automation_executor import AutomationExecutor, create_sample_reply_csv

class AutomationCLI:
    """自動操作のCLIインターフェース"""
    
    def __init__(self):
        self.executor = AutomationExecutor()
    
    def run_automation(self):
        """自動操作を実行"""
        print("\n" + "="*60)
        print(" 自動操作実行")
        print("="*60)
        
        # アカウント選択
        selected_accounts = self.select_accounts()
        if not selected_accounts:
            print("アカウントが選択されませんでした")
            return
        
        # 同時実行数設定
        max_workers = self.get_concurrent_workers(len(selected_accounts))
        
        # 対象URL入力
        target_url = self.get_target_url()
        if not target_url:
            return
        
        # 実行操作選択
        actions = self.select_actions()
        if not any(actions.values()):
            print("実行する操作が選択されませんでした")
            return
        
        # 待機時間設定
        wait_range = self.get_wait_range()
        
        # リプライテキストの確認
        if actions.get("reply", False):
            if not self.setup_reply_texts():
                actions["reply"] = False
        
        # 確認
        if not self.confirm_execution(selected_accounts, target_url, actions, wait_range, max_workers):
            return
        
        # 実行
        results = self.executor.execute_parallel(
            selected_accounts, target_url, actions, wait_range, max_workers
        )
        
        input("\nEnterキーを押してメニューに戻る...")
    
    def select_accounts(self) -> List[int]:
        """アカウント選択"""
        print("\n実行するアカウントを選択してください：")
        print("1. 全アカウント実行")
        print("2. 特定番号を選択（例: 5）")
        print("3. 複数選択（例: 1,3,5,7）")
        print("4. 範囲指定（例: 10-20）")
        print("5. ログイン済みのみ実行")
        
        try:
            choice = int(input("選択: "))
        except ValueError:
            print("数字を入力してください")
            return []
        
        if choice == 1:
            # 全アカウント
            accounts = self.executor.account_manager.accounts.get("accounts", [])
            return [acc["id"] for acc in accounts]
            
        elif choice == 2:
            # 特定番号
            try:
                account_id = int(input("アカウント番号を入力: "))
                return [account_id]
            except ValueError:
                print("数字を入力してください")
                return []
                
        elif choice == 3:
            # 複数選択
            try:
                ids_str = input("アカウント番号をカンマ区切りで入力: ")
                return [int(x.strip()) for x in ids_str.split(",")]
            except ValueError:
                print("正しい形式で入力してください")
                return []
                
        elif choice == 4:
            # 範囲指定
            try:
                range_str = input("範囲を入力（例: 1-10）: ")
                start, end = map(int, range_str.split("-"))
                return list(range(start, end + 1))
            except ValueError:
                print("正しい形式で入力してください（例: 1-10）")
                return []
                
        elif choice == 5:
            # ログイン済みのみ
            logged_in = []
            accounts = self.executor.account_manager.accounts.get("accounts", [])
            for account in accounts:
                cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                if os.path.exists(cookie_file):
                    logged_in.append(account["id"])
            return logged_in
        
        return []
    
    def get_concurrent_workers(self, total_accounts: int) -> int:
        """同時実行数を取得"""
        max_workers = min(10, total_accounts)
        
        while True:
            try:
                workers = int(input(f"同時実行数を入力（1-{max_workers}）: "))
                if 1 <= workers <= max_workers:
                    return workers
                else:
                    print(f"1-{max_workers}の範囲で入力してください")
            except ValueError:
                print("数字を入力してください")
    
    def get_target_url(self) -> str:
        """対象URL取得"""
        url = input("\n対象URLを入力してください: ").strip()
        
        if not url:
            print("URLが入力されませんでした")
            return ""
        
        if not url.startswith(("https://x.com", "https://twitter.com")):
            print("X（Twitter）のURLを入力してください")
            return ""
        
        return url
    
    def select_actions(self) -> Dict[str, bool]:
        """実行操作選択"""
        print("\n実行する操作を選択してください：")
        print("1. いいね")
        print("2. ブックマーク")
        print("3. いいね、ブックマーク")
        print("4. いいね、ブックマーク、リツイート")
        print("5. リツイート")
        print("6. リプライ")
        print("7. いいね、リプライ")
        print("8. いいね、ブックマーク、リプライ")
        print("9. すべて（いいね、ブックマーク、リツイート、リプライ）")
        
        try:
            choice = int(input("選択番号を入力: "))
        except ValueError:
            print("数字を入力してください")
            return {}
        
        action_map = {
            1: {"like": True},
            2: {"bookmark": True},
            3: {"like": True, "bookmark": True},
            4: {"like": True, "bookmark": True, "retweet": True},
            5: {"retweet": True},
            6: {"reply": True},
            7: {"like": True, "reply": True},
            8: {"like": True, "bookmark": True, "reply": True},
            9: {"like": True, "bookmark": True, "retweet": True, "reply": True}
        }
        
        if choice in action_map:
            actions = action_map[choice]
            action_names = [k for k, v in actions.items() if v]
            
            confirm = input(f"\n「{', '.join(action_names)}」を実行します。よろしいですか？(y/n): ")
            if confirm.lower() == 'y':
                return actions
        
        print("選択がキャンセルされました")
        return {}
    
    def get_wait_range(self) -> Tuple[int, int]:
        """待機時間設定"""
        print("\n操作間の待機時間を設定します")
        
        try:
            min_wait = int(input("最小待機時間（秒）: "))
            max_wait = int(input("最大待機時間（秒）: "))
            
            if min_wait > max_wait:
                min_wait, max_wait = max_wait, min_wait
                
            return (min_wait, max_wait)
            
        except ValueError:
            print("数字を入力してください。デフォルト値（3-10秒）を使用します")
            return (3, 10)
    
    def setup_reply_texts(self) -> bool:
        """リプライテキスト設定"""
        csv_path = "config/reply_texts.csv"
        
        if self.executor.load_reply_texts(csv_path):
            print(f"  ✓ リプライテキストを読み込みました")
            return True
        
        if not os.path.exists(csv_path):
            print(f"\nリプライテキストファイルが見つかりません: {csv_path}")
            create_sample = input("サンプルファイルを作成しますか？ (y/n): ").strip().lower()
            if create_sample == 'y':
                create_sample_reply_csv(csv_path)
                return self.executor.load_reply_texts(csv_path)
            else:
                return False
        
        return self.executor.load_reply_texts(csv_path)
    
    def confirm_execution(self, account_ids: List[int], target_url: str, 
                         actions: Dict[str, bool], wait_range: Tuple[int, int], 
                         max_workers: int) -> bool:
        """実行確認"""
        print("\n" + "="*60)
        print(" 設定確認")
        print("="*60)
        print(f"アカウント数: {len(account_ids)}")
        print(f"同時実行数: {max_workers}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print("="*60)
        
        confirm = input("\n実行を開始しますか？(y/n): ")
        return confirm.lower() == 'y'
