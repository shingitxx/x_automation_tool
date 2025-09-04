import os
import time
import json
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
# undetected_chromedriverのみ使用
from account_manager import AccountManager

class LoginManager:
    """ログイン管理システム"""
    
    def __init__(self):
        self.manager = AccountManager()
    
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
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(f'--user-data-dir={profile_dir}')
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # プロキシ設定
            proxy = account.get("proxy", {})
            if proxy and proxy.get("host") and proxy.get("port"):
                proxy_url = f"{proxy['host']}:{proxy['port']}"
                chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
            
            driver = uc.Chrome( options=chrome_options)
            try:
                driver.get("https://x.com/home")
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
        print(f"\n{'='*50}")
        print(f" 手動ログイン - スマートモード")
        print(f"{'='*50}")
        print(f"対象アカウント: {len(account_ids)}個")
        
        # プロファイルディレクトリ作成
        os.makedirs("profiles", exist_ok=True)

        # 1. 事前チェック：ログイン状態確認
        need_login = []
        already_logged = []
        
        print("\n1. ログイン状態を確認中...")
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
        print(f"\n{'='*50}")
        print("ログイン状態確認結果:")
        print(f"{'='*50}")
        print(f"✅ ログイン済み: {len(already_logged)}個")
        if already_logged:
            for acc_id in already_logged:
                acc = self.manager.get_account_by_id(acc_id)
                print(f"    [{acc_id}] {acc['email']}")
        
        print(f"\n❌ ログイン必要: {len(need_login)}個")
        if need_login:
            for acc_id in need_login:
                acc = self.manager.get_account_by_id(acc_id)
                print(f"    [{acc_id}] {acc['email']}")
        
        # 3. ログイン不要の場合は終了
        if not need_login:
            print(f"\n✅ 全てのアカウントが既にログイン済みです")
            input("Enterキーでメニューに戻る...")
            return
        
        # 4. 手動ログイン実行確認
        print(f"\n{'='*50}")
        print("手動ログインが必要なアカウントのみ処理します")
        print(f"処理対象: {len(need_login)}個")
        response = input("続行しますか？ (y/n): ").strip().lower()
        if response != 'y':
            print("キャンセルしました")
            return
        
        # 5. 未ログインアカウントのみ処理
        print(f"\n手動ログインを開始します...")
        
        for i, account_id in enumerate(need_login):
            account = self.manager.get_account_by_id(account_id)
            profile_dir = f"profiles/account_{account_id}"
            os.makedirs(profile_dir, exist_ok=True)

            print(f"\n{'='*50}")
            print(f"[{account_id}] {account['email']} ({i+1}/{len(need_login)})")
            print(f"プロファイル: {profile_dir}")
            print(f"{'='*50}")

            driver = None
            try:
                # プロセス完全分離のドライバー起動
                import tempfile
                import random
                
                # 各アカウント専用の一時ディレクトリ
                temp_profile = tempfile.mkdtemp(prefix=f'chrome_profile_{account_id}_')
                
                # プロキシ情報を事前に取得
                proxy = account.get("proxy", {})
                proxy_url = f"{proxy['host']}:{proxy['port']}" if proxy.get("host") and proxy.get("port") else None
                
                # プロセス分離とポート競合回避
                debug_port = 9000 + account_id + random.randint(0, 100)
                print(f"Chrome起動中... (ポート: {debug_port})")
                print(f"プロキシ設定: {proxy_url}" if proxy_url else "プロキシなし")
                
                # 複数回試行でドライバー作成（オプション毎回新規作成）
                driver = None
                for attempt in range(3):
                    try:
                        # 試行ごとに新しいChromeOptionsを作成
                        retry_options = webdriver.ChromeOptions()
                        retry_options.add_argument(f'--user-data-dir={temp_profile}')
                        retry_options.add_argument(f'--profile-directory=Profile_{account_id}')
                        retry_options.add_argument(f'--remote-debugging-port={debug_port}')
                        
                        # Chrome安定化オプション
                        retry_options.add_argument('--no-sandbox')
                        retry_options.add_argument('--disable-dev-shm-usage')
                        retry_options.add_argument('--disable-gpu')
                        retry_options.add_argument('--disable-extensions')
                        retry_options.add_argument('--no-first-run')
                        retry_options.add_argument('--disable-default-apps')
                        retry_options.add_argument('--disable-background-timer-throttling')
                        retry_options.add_argument('--disable-backgrounding-occluded-windows')
                        retry_options.add_argument('--disable-renderer-backgrounding')
                        retry_options.add_argument('--disable-hang-monitor')
                        retry_options.add_argument('--disable-prompt-on-repost')
                        retry_options.add_argument('--start-maximized')
                        retry_options.add_argument('--force-device-scale-factor=1')
                        
                        # プロキシ設定（既に定義済みの変数を使用）
                        if proxy_url:
                            retry_options.add_argument(f'--proxy-server=http://{proxy_url}')
                        
                        driver = uc.Chrome( 
                            options=retry_options,
                            
                            
                        )
                        driver.maximize_window()
                        print(f"  ✓ Chrome起動成功（試行{attempt+1}回目）")
                        break
                    except Exception as e:
                        print(f"  試行{attempt+1}失敗: {str(e)[:50]}")
                        if attempt < 2:  # 最後の試行でなければ待機
                            import time
                            time.sleep(3)
                            debug_port += 1  # ポートを変更してリトライ
                        else:
                            raise Exception(f"Chrome起動に3回失敗: {str(e)}")

                # 段階的ページ読み込み
                print("ブラウザを準備中...")
                driver.get("about:blank")
                import time
                time.sleep(2)
                
                print("Xトップページを開いています...")
                driver.get("https://x.com")
                time.sleep(3)
                
                print("Xのログインページに移動...")
                driver.get("https://x.com/i/flow/login")
                time.sleep(3)

                print("\n" + "="*40)
                print("【手動ログイン手順】")
                print("1. Xアカウントにログイン")
                print("2. ホーム画面表示を確認") 
                print("3. Enterキーを押す")
                print("="*40)

                input("ログイン完了後、Enterキーを押してください...")

                # ログイン確認
                current_url = driver.current_url
                if "home" in current_url.lower():
                    print(f"  ✅ [{account_id}] ログイン成功")
                    
                    # Cookieを手動保存（プロファイル代替）
                    cookies = driver.get_cookies()
                    cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                    os.makedirs("cache/cookies", exist_ok=True)
                    
                    import json
                    from datetime import datetime
                    cookie_data = {
                        "cookies": cookies,
                        "saved_at": datetime.now().isoformat(),
                        "account_id": account_id,
                        "email": account['email']
                    }
                    
                    with open(cookie_file, 'w', encoding='utf-8') as f:
                        json.dump(cookie_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"  ✓ Cookie保存完了: {cookie_file}")
                else:
                    print(f"  ⚠ [{account_id}] ログイン未完了の可能性があります")

                # 次のアカウントがある場合の確認
                if i < len(need_login) - 1:
                    print(f"\n次のアカウント: [{need_login[i+1]}] の処理に進みます")
                    input("準備ができたらEnterキーを押してください...")

            except Exception as e:
                print(f"  ✗ [{account_id}] エラー: {str(e)}")
            finally:
                if driver:
                    driver.quit()

        print(f"\n{'='*50}")
        print("手動ログイン完了")
        print(f"{'='*50}")
        print(f"処理済み: {len(need_login)}個")
        print("\n次回からは自動操作で高速実行可能です")
        input("Enterキーでメニューに戻る...")
