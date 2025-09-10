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
    """ログイン管理クラス"""
    
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
            print(f"⚠ ドライバー起動エラー: {e}")
            return None
    
    def manual_login(self, account_ids: List[int], max_concurrent: int = 10):
        """手動ログイン"""
        drivers = []
        
        try:
            for account_id in account_ids:
                account = self.manager.get_account_by_id(account_id)
                if not account:
                    continue
                
                print(f"アカウント [{account_id}] {account['email']} のブラウザを起動中...")
                
                proxy_url = self.manager.get_proxy_url(account_id)
                driver = self.setup_driver(proxy_url=proxy_url)
                
                if driver:
                    driver.get(self.x_login_url)
                    drivers.append((driver, account_id, account['email']))
            
            if drivers:
                print(f"\n{len(drivers)}個のブラウザが起動しました。")
                print("各ブラウザでログインを完了してください。")
                input("全てのログインが完了したらEnterキーを押してください...")
                
                for driver, account_id, email in drivers:
                    try:
                        self.save_cookies(driver, account_id)
                        print(f"✓ [{account_id}] {email} - Cookie保存完了")
                    except Exception as e:
                        print(f"✗ [{account_id}] {email} - エラー: {e}")
                    finally:
                        driver.quit()
        
        except Exception as e:
            print(f"手動ログインエラー: {e}")
    
    def auto_login_until_2fa(self, account_ids: List[int], max_concurrent: int = 5):
        """初回ログインフォーム自動入力（要素選択改善版）"""
        
        print("
" + "="*60)
        print(" 自動フォーム入力開始")
        print("="*60)
        
        for i in range(0, len(account_ids), max_concurrent):
            batch = account_ids[i:i+max_concurrent]
            batch_drivers = []
            
            for account_id in batch:
                account = self.manager.get_account_by_id(account_id)
                if not account:
                    continue
                
                print(f"
[{account_id}] {account['email']} - 自動入力開始")
                
                try:
                    driver = self.setup_driver(headless=False)
                    driver.execute_script(f"document.title = '[{account_id}] {account['email']}'")
                    
                    driver.get("https://x.com/i/flow/login")
                    time.sleep(8)  # ページ読み込みを十分に待機
                    
                    # Step 1: メールアドレス入力（より確実な方法）
                    try:
                        # 複数の方法で入力欄を探す
                        input_found = False
                        
                        # 方法1: 最初のinput要素
                        inputs = driver.find_elements(By.TAG_NAME, "input")
                        for input_elem in inputs:
                            if input_elem.is_displayed() and input_elem.is_enabled():
                                try:
                                    input_elem.clear()
                                    input_elem.send_keys(account['email'])
                                    time.sleep(2)
                                    
                                    # Enterキーまたは次へボタン
                                    from selenium.webdriver.common.keys import Keys
                                    input_elem.send_keys(Keys.TAB)
                                    time.sleep(1)
                                    
                                    # 次へボタンを探してクリック
                                    buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
                                    for button in buttons:
                                        if button.is_displayed() and ('次へ' in button.text or 'Next' in button.text):
                                            driver.execute_script("arguments[0].click();", button)
                                            time.sleep(5)
                                            input_found = True
                                            break
                                    
                                    if input_found:
                                        break
                                        
                                except Exception:
                                    continue
                        
                        if not input_found:
                            print(f"  ✗ メールアドレス入力欄が見つかりません")
                            driver.quit()
                            continue
                        
                        print(f"  ✓ メールアドレス入力完了")
                        
                    except Exception as e:
                        print(f"  ✗ メールアドレス入力エラー: {str(e)[:50]}")
                        driver.quit()
                        continue
                    
                    # Step 2: パスワード入力
                    try:
                        password_found = False
                        
                        # パスワード入力欄を待機
                        password_inputs = WebDriverWait(driver, 15).until(
                            lambda d: d.find_elements(By.CSS_SELECTOR, "input[type='password']")
                        )
                        
                        for password_input in password_inputs:
                            if password_input.is_displayed() and password_input.is_enabled():
                                try:
                                    password_input.clear()
                                    password_input.send_keys(account['password'])
                                    time.sleep(2)
                                    
                                    # ログインボタンをクリック
                                    login_buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
                                    for button in login_buttons:
                                        if button.is_displayed() and ('ログイン' in button.text or 'Log in' in button.text or 'login' in button.text.lower()):
                                            driver.execute_script("arguments[0].click();", button)
                                            time.sleep(8)
                                            password_found = True
                                            break
                                    
                                    if password_found:
                                        break
                                        
                                except Exception:
                                    continue
                        
                        if not password_found:
                            print(f"  ✗ パスワード入力失敗")
                            driver.quit()
                            continue
                        
                        print(f"  ✓ パスワード入力完了")
                        
                    except Exception as e:
                        print(f"  ✗ パスワード入力エラー: {str(e)[:50]}")
                        driver.quit()
                        continue
                    
                    # 2FA待機
                    driver.execute_script(f"document.title = '[{account_id}] {account['email']} - 2FA待機'")
                    print(f"  ⏸ 2FA認証待機")
                    
                    batch_drivers.append({
                        "driver": driver,
                        "account_id": account_id,
                        "email": account['email']
                    })
                
                except Exception as e:
                    print(f"  ✗ 全体エラー: {str(e)[:50]}")
                    try:
                        driver.quit()
                    except:
                        pass
            
            # 2FA認証待機（既存の処理）
            if batch_drivers:
                print("
" + "-"*60)
                print("各ウィンドウで2FA認証を手動入力してください")
                print("-"*60)
                
                for item in batch_drivers:
                    print(f"  [{item['account_id']}] {item['email']}")
                
                print("
全ての2FA認証完了後、Enterキーを押してください...")
                input()
                
                # Cookie保存
                for item in batch_drivers:
                    try:
                        self.save_cookies(item["driver"], item["account_id"])
                        print(f"✓ [{item['account_id']}] Cookie保存完了")
                        item["driver"].quit()
                    except Exception as e:
                        print(f"✗ [{item['account_id']}] エラー: {str(e)[:30]}")
                        try:
                            item["driver"].quit()
                        except:
                            pass
            
            # 次のバッチ確認
            if i + max_concurrent < len(account_ids):
                if input("
次のバッチに進みますか？ (y/n): ").lower() != 'y':
                    break
        
        print("
初回ログイン完了")
    
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
