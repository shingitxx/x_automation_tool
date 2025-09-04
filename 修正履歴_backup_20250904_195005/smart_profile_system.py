#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログイン状態チェック付きプロファイル管理システム
"""

import os


def main():
    print("=" * 60)
    print(" ログイン状態チェック付きプロファイル管理")
    print("=" * 60)

    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 新しいログイン状態チェック機能付きmanual_loginメソッド
    new_manual_login = '''    def check_login_status(self, account_id: int) -> bool:
        """プロファイルのログイン状態確認"""
        profile_dir = f"profiles/account_{account_id}"
        
        if not os.path.exists(profile_dir):
            return False
        
        # プロファイルディレクトリ内にログイン情報があるかチェック
        login_indicators = [
            "Default/Cookies",
            "Default/Local Storage",
            "Default/Session Storage"
        ]
        
        for indicator in login_indicators:
            if os.path.exists(os.path.join(profile_dir, indicator)):
                return True
        return False

    def quick_login_test(self, account_id: int) -> bool:
        """簡単なログイン状態テスト"""
        account = self.manager.get_account_by_id(account_id)
        if not account:
            return False
        
        profile_dir = f"profiles/account_{account_id}"
        if not self.check_login_status(account_id):
            return False
        
        print(f"  [{account_id}] ログイン状態をテスト中...")
        
        try:
            chrome_options = uc.ChromeOptions()
            chrome_options.add_argument(f'--user-data-dir={profile_dir}')
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # プロキシ設定
            proxy = account.get("proxy", {})
            if proxy and proxy.get("host") and proxy.get("port"):
                proxy_url = f"{proxy['host']}:{proxy['port']}"
                chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
            
            driver = uc.Chrome(options=chrome_options)
            try:
                driver.get("https://x.com/home")
                import time
                time.sleep(3)
                
                # URLでログイン状態判定
                current_url = driver.current_url
                if "home" in current_url.lower():
                    print(f"  ✓ [{account_id}] ログイン確認済み")
                    return True
                else:
                    print(f"  ✗ [{account_id}] ログアウト状態")
                    return False
            finally:
                driver.quit()
        except Exception as e:
            print(f"  ✗ [{account_id}] テストエラー: {str(e)[:50]}")
            return False

    def manual_login(self, account_ids: List[int], max_concurrent: int = 1):
        """手動ログイン（ログイン状態チェック付き）"""
        print(f"\\n{'='*50}")
        print(f" 手動ログイン - スマートモード")
        print(f"{'='*50}")
        print(f"対象アカウント: {len(account_ids)}個")
        
        # プロファイルディレクトリ作成
        os.makedirs("profiles", exist_ok=True)

        # 1. 事前チェック：ログイン状態確認
        need_login = []
        already_logged = []
        
        print("\\n1. ログイン状態を確認中...")
        for account_id in account_ids:
            account = self.manager.get_account_by_id(account_id)
            if not account:
                print(f"  ✗ [{account_id}] アカウントが見つかりません")
                continue
                
            if self.quick_login_test(account_id):
                already_logged.append(account_id)
            else:
                need_login.append(account_id)
        
        # 2. 結果表示
        print(f"\\n{'='*50}")
        print("ログイン状態確認結果:")
        print(f"{'='*50}")
        print(f"✅ ログイン済み: {len(already_logged)}個")
        if already_logged:
            for acc_id in already_logged:
                acc = self.manager.get_account_by_id(acc_id)
                print(f"    [{acc_id}] {acc['email']}")
        
        print(f"\\n❌ ログイン必要: {len(need_login)}個")
        if need_login:
            for acc_id in need_login:
                acc = self.manager.get_account_by_id(acc_id)
                print(f"    [{acc_id}] {acc['email']}")
        
        # 3. ログイン不要の場合は終了
        if not need_login:
            print(f"\\n✅ 全てのアカウントが既にログイン済みです")
            input("Enterキーでメニューに戻る...")
            return
        
        # 4. 手動ログイン実行確認
        print(f"\\n{'='*50}")
        print("手動ログインが必要なアカウントのみ処理します")
        print(f"処理対象: {len(need_login)}個")
        response = input("続行しますか？ (y/n): ").strip().lower()
        if response != 'y':
            print("キャンセルしました")
            return
        
        # 5. 未ログインアカウントのみ処理
        print(f"\\n手動ログインを開始します...")
        
        for i, account_id in enumerate(need_login):
            account = self.manager.get_account_by_id(account_id)
            profile_dir = f"profiles/account_{account_id}"
            os.makedirs(profile_dir, exist_ok=True)

            print(f"\\n{'='*50}")
            print(f"[{account_id}] {account['email']} ({i+1}/{len(need_login)})")
            print(f"プロファイル: {profile_dir}")
            print(f"{'='*50}")

            driver = None
            try:
                # プロファイル固定のドライバー起動
                chrome_options = uc.ChromeOptions()
                chrome_options.add_argument(f'--user-data-dir={profile_dir}')
                chrome_options.add_argument('--no-first-run')
                chrome_options.add_argument('--disable-default-apps')
                
                # プロキシ設定
                proxy = account.get("proxy", {})
                if proxy and proxy.get("host") and proxy.get("port"):
                    proxy_url = f"{proxy['host']}:{proxy['port']}"
                    chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
                    print(f"プロキシ設定: {proxy_url}")

                driver = uc.Chrome(options=chrome_options)
                driver.maximize_window()

                # Xのログインページを開く
                print("Xのログインページを開いています...")
                driver.get("https://x.com/login")

                print("\\n" + "="*40)
                print("【手動ログイン手順】")
                print("1. Xアカウントにログイン")
                print("2. ホーム画面表示を確認") 
                print("3. Enterキーを押す")
                print("="*40)

                input("ログイン完了後、Enterキーを押してください...")

                # ログイン確認
                current_url = driver.current_url
                if "home" in current_url.lower():
                    print(f"  ✅ [{account_id}] ログイン成功 - プロファイル保存済み")
                else:
                    print(f"  ⚠ [{account_id}] ログイン未完了の可能性があります")

                # 次のアカウントがある場合の確認
                if i < len(need_login) - 1:
                    print(f"\\n次のアカウント: [{need_login[i+1]}] の処理に進みます")
                    input("準備ができたらEnterキーを押してください...")

            except Exception as e:
                print(f"  ✗ [{account_id}] エラー: {str(e)}")
            finally:
                if driver:
                    driver.quit()

        print(f"\\n{'='*50}")
        print("手動ログイン完了")
        print(f"{'='*50}")
        print(f"処理済み: {len(need_login)}個")
        print("\\n次回からは自動操作で高速実行可能です")
        input("Enterキーでメニューに戻る...")'''

    # 既存のmanual_loginメソッドを置換
    import re

    pattern = (
        r"def manual_login\(self, account_ids.*?(?=\n    def|\nclass|\nif __name__|\Z)"
    )
    match = re.search(pattern, content, re.DOTALL)

    if match:
        # check_login_statusとquick_login_testメソッドを先に追加
        methods_to_add = '''
    def check_login_status(self, account_id: int) -> bool:
        """プロファイルのログイン状態確認"""
        profile_dir = f"profiles/account_{account_id}"
        
        if not os.path.exists(profile_dir):
            return False
        
        # プロファイルディレクトリ内にログイン情報があるかチェック
        login_indicators = [
            "Default/Cookies",
            "Default/Local Storage",
            "Default/Session Storage"
        ]
        
        for indicator in login_indicators:
            if os.path.exists(os.path.join(profile_dir, indicator)):
                return True
        return False

    def quick_login_test(self, account_id: int) -> bool:
        """簡単なログイン状態テスト"""
        account = self.manager.get_account_by_id(account_id)
        if not account:
            return False
        
        profile_dir = f"profiles/account_{account_id}"
        if not self.check_login_status(account_id):
            return False
        
        print(f"  [{account_id}] ログイン状態をテスト中...")
        
        try:
            chrome_options = uc.ChromeOptions()
            chrome_options.add_argument(f'--user-data-dir={profile_dir}')
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # プロキシ設定
            proxy = account.get("proxy", {})
            if proxy and proxy.get("host") and proxy.get("port"):
                proxy_url = f"{proxy['host']}:{proxy['port']}"
                chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
            
            driver = uc.Chrome(options=chrome_options)
            try:
                driver.get("https://x.com/home")
                import time
                time.sleep(3)
                
                # URLでログイン状態判定
                current_url = driver.current_url
                if "home" in current_url.lower():
                    print(f"  ✓ [{account_id}] ログイン確認済み")
                    return True
                else:
                    print(f"  ✗ [{account_id}] ログアウト状態")
                    return False
            finally:
                driver.quit()
        except Exception as e:
            print(f"  ✗ [{account_id}] テストエラー: {str(e)[:50]}")
            return False
'''

        # 既存のmanual_loginメソッドを新しいものに置換
        content = content.replace(
            match.group(0), methods_to_add + new_manual_login.strip()
        )
        print("  ✓ login_manager.py にログイン状態チェック機能を追加しました")
    else:
        print("  ✗ manual_loginメソッドが見つかりませんでした")
        return

    # ファイル保存
    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ ファイル保存完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n新機能:")
    print("✓ ログイン済みアカウントの自動検出")
    print("✓ 未ログインアカウントのみ手動処理")
    print("✓ プロファイルディレクトリの自動管理")
    print("✓ ログイン状態の事前テスト機能")
    print("\n効果:")
    print("• 既にログイン済み → 即座にスキップ")
    print("• 未ログインのみ → 手動ログイン実行")
    print("• 効率的な大量アカウント管理")

    print("\n次のテスト:")
    print("py -3.10 cli_interface.py")
    print("メニュー「2. 初回ログイン」でテストしてください")


if __name__ == "__main__":
    main()
