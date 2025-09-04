import os
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from account_manager import AccountManager

class LoginManager:
    """ログイン管理クラス（手動ログインのみ）"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.x_login_url = "https://x.com/i/flow/login"
    
    def setup_driver(self, proxy_url: Optional[str] = None, headless: bool = False) -> webdriver.Chrome:
        """Seleniumドライバーをセットアップ"""
        
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        
        if headless:
            options.add_argument('--headless=new')
        
        try:
            driver = uc.Chrome(options=options, version_main=139)
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            print(f"ドライバー起動エラー: {e}")
            return None
    
    def manual_login(self, account_ids: List[int], max_concurrent: int = 10):
        """手動ログイン"""
        drivers = []
        
        try:
            print(f"\n{len(account_ids)}個のアカウントでブラウザを起動します")
            
            for account_id in account_ids:
                account = self.manager.get_account_by_id(account_id)
                if not account:
                    print(f"アカウントID {account_id} が見つかりません")
                    continue
                
                print(f"\n[{account_id}] {account['email']} - ブラウザ起動中...")
                
                proxy_url = self.manager.get_proxy_url(account_id)
                driver = self.setup_driver(proxy_url=proxy_url)
                
                if driver:
                    # ウィンドウタイトルを設定
                    driver.execute_script(f"document.title = '[{account_id}] {account['email']}'")
                    driver.get(self.x_login_url)
                    drivers.append((driver, account_id, account['email']))
                    print(f"  ✓ ブラウザ起動完了")
                else:
                    print(f"  ✗ ブラウザ起動失敗")
            
            if drivers:
                print(f"\n{'='*60}")
                print(f" 手動ログイン")
                print(f"{'='*60}")
                print(f"起動したブラウザ: {len(drivers)}個")
                print("\n各ブラウザで以下の手順でログインしてください:")
                print("1. メールアドレス/ユーザー名を入力")
                print("2. パスワードを入力")
                print("3. 2FA認証（必要な場合）")
                print("\nウィンドウタイトルでアカウントを識別できます:")
                
                for driver, account_id, email in drivers:
                    print(f"  [{account_id}] {email}")
                
                print(f"\n{'='*60}")
                input("全てのログインが完了したらEnterキーを押してください...")
                
                # Cookie保存
                success_count = 0
                for driver, account_id, email in drivers:
                    try:
                        self.save_cookies(driver, account_id)
                        print(f"✓ [{account_id}] {email} - Cookie保存完了")
                        success_count += 1
                    except Exception as e:
                        print(f"✗ [{account_id}] {email} - Cookie保存エラー: {str(e)[:50]}")
                    finally:
                        try:
                            driver.quit()
                        except:
                            pass
                
                print(f"\n結果: {success_count}/{len(drivers)} アカウントでCookie保存完了")
            else:
                print("\nブラウザの起動に失敗しました")
        
        except Exception as e:
            print(f"手動ログインエラー: {e}")
            # エラー時は開いているブラウザを全て閉じる
            for driver, _, _ in drivers:
                try:
                    driver.quit()
                except:
                    pass
    
    def save_cookies(self, driver: webdriver.Chrome, account_id: int):
        """Cookieを保存"""
        account = self.manager.get_account_by_id(account_id)
        if not account:
            return
        
        cookie_file = os.path.join(
            self.manager.cookies_dir,
            f"{account['email']}_cookies.json"
        )
        
        cookies = driver.get_cookies()
        cookie_data = {
            "cookies": cookies,
            "saved_at": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookie_data, f, ensure_ascii=False, indent=2)
