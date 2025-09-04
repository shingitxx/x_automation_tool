import os
import time
import random
import json
import csv
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from account_manager import AccountManager
import undetected_chromedriver as uc

class AutomationExecutor:
    def __init__(self):
        self.account_manager = AccountManager()
        self.reply_texts = []
        self.used_replies = set()
        self.results = []
        
    def setup_driver_with_proxy(self, account_id: int) -> Optional[webdriver.Chrome]:
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            driver = uc.Chrome(options=chrome_options, version_main=139)
            driver.implicitly_wait(10)
            print(f"  ✓ ドライバーを起動（アカウント: {account['email']}）")
            return driver
        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            return None
    
    def load_cookies(self, driver: webdriver.Chrome, account_id: int) -> bool:
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return False
        
        cookie_file = os.path.join(
            self.account_manager.cookies_dir,
            f"{account['email']}_cookies.json"
        )
        
        if not os.path.exists(cookie_file):
            print(f"  ⚠ Cookieファイルが見つかりません")
            return False
        
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            driver.get("https://x.com")
            time.sleep(3)
            
            for cookie in cookie_data.get("cookies", []):
                try:
                    driver.add_cookie(cookie)
                except:
                    pass
            
            driver.refresh()
            time.sleep(3)
            print(f"  ✓ Cookieを読み込みました")
            return True
            
        except Exception as e:
            print(f"  ✗ Cookie読み込みエラー: {str(e)[:50]}")
            return False
    
    def check_login_status(self, driver: webdriver.Chrome) -> bool:
        try:
            driver.get("https://x.com/home")
            time.sleep(3)
            if "home" in driver.current_url.lower():
                return True
            return False
        except:
            return False
    
    def load_reply_texts(self, csv_path: str = "config/reply_texts.csv") -> bool:
        if not os.path.exists(csv_path):
            return False
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.reply_texts = []
                for row in reader:
                    if 'リプライテキスト' in row:
                        self.reply_texts.append(row['リプライテキスト'])
            return True
        except:
            return False
    
    def get_random_reply(self) -> Optional[str]:
        available_texts = [t for t in self.reply_texts if t not in self.used_replies]
        if not available_texts:
            self.used_replies.clear()
            available_texts = self.reply_texts
        if available_texts:
            selected = random.choice(available_texts)
            self.used_replies.add(selected)
            return selected
        return None
    
    def random_wait(self, min_seconds: float, max_seconds: float):
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def human_like_action(self):
        time.sleep(random.uniform(0.5, 1.5))
    
    def execute_like(self, driver: webdriver.Chrome, url: str) -> bool:
        try:
            driver.get(url)
            self.human_like_action()
            
            like_selectors = [
                "//div[@data-testid='like']",
                "//div[@data-testid='unlike']"
            ]
            
            for selector in like_selectors:
                try:
                    like_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    like_button.click()
                    self.human_like_action()
                    print("  ✓ いいね完了")
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    def execute_bookmark(self, driver: webdriver.Chrome, url: str) -> bool:
        try:
            driver.get(url)
            self.human_like_action()
            
            bookmark_selectors = [
                "//div[@data-testid='bookmark']",
                "//div[@data-testid='removeBookmark']"
            ]
            
            for selector in bookmark_selectors:
                try:
                    bookmark_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    bookmark_button.click()
                    self.human_like_action()
                    print("  ✓ ブックマーク完了")
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    def execute_retweet(self, driver: webdriver.Chrome, url: str) -> bool:
        try:
            driver.get(url)
            self.human_like_action()
            
            retweet_selectors = [
                "//div[@data-testid='retweet']",
                "//div[@data-testid='unretweet']"
            ]
            
            for selector in retweet_selectors:
                try:
                    retweet_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    retweet_button.click()
                    self.human_like_action()
                    
                    try:
                        confirm_button = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='retweetConfirm']"))
                        )
                        confirm_button.click()
                    except:
                        pass
                    
                    print("  ✓ リツイート完了")
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    def execute_reply(self, driver: webdriver.Chrome, url: str, reply_text: str) -> bool:
        try:
            driver.get(url)
            self.human_like_action()
            
            reply_selectors = [
                "//div[@data-testid='tweetTextarea_0']",
                "//div[@role='textbox']"
            ]
            
            for selector in reply_selectors:
                try:
                    reply_box = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    reply_box.click()
                    self.human_like_action()
                    reply_box.send_keys(reply_text)
                    self.human_like_action()
                    
                    send_selectors = [
                        "//div[@data-testid='tweetButtonInline']",
                        "//button[@data-testid='tweetButton']"
                    ]
                    
                    for send_sel in send_selectors:
                        try:
                            send_button = driver.find_element(By.XPATH, send_sel)
                            if send_button.is_enabled():
                                send_button.click()
                                self.human_like_action()
                                print(f"  ✓ リプライ完了")
                                return True
                        except:
                            continue
                except:
                    continue
            return False
        except:
            return False
    
    def process_single_account(self, account_id: int, target_url: str, 
                             actions: Dict[str, bool], wait_range: Tuple[int, int]) -> Dict:
        result = {
            "account_id": account_id,
            "email": "",
            "url": target_url,
            "success": False,
            "actions_performed": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
        
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            result["errors"].append("アカウントが見つかりません")
            return result
        
        result["email"] = account["email"]
        driver = None
        
        try:
            print(f"\n[{account_id}] {account['email']} - 処理開始")
            
            driver = self.setup_driver_with_proxy(account_id)
            if not driver:
                result["errors"].append("ドライバー起動失敗")
                return result
            
            if not self.load_cookies(driver, account_id):
                result["errors"].append("Cookie読み込み失敗")
                return result
            
            if not self.check_login_status(driver):
                result["errors"].append("ログイン状態確認失敗")
                return result
            
            print("  ✓ ログイン成功")
            
            if actions.get("like", False):
                print("  実行: いいね")
                if self.execute_like(driver, target_url):
                    result["actions_performed"].append("like")
                    self.random_wait(wait_range[0], wait_range[1])
            
            if actions.get("bookmark", False):
                print("  実行: ブックマーク")
                if self.execute_bookmark(driver, target_url):
                    result["actions_performed"].append("bookmark")
                    self.random_wait(wait_range[0], wait_range[1])
            
            if actions.get("retweet", False):
                print("  実行: リツイート")
                if self.execute_retweet(driver, target_url):
                    result["actions_performed"].append("retweet")
                    self.random_wait(wait_range[0], wait_range[1])
            
            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
                    print("  実行: リプライ")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
            
            result["success"] = len(result["actions_performed"]) > 0
            
            if result["success"]:
                print(f"  ✅ 完了: {', '.join(result['actions_performed'])}")
            
        except Exception as e:
            result["errors"].append(f"実行エラー: {str(e)[:100]}")
            print(f"  ✗ エラー: {str(e)[:50]}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return result
    
    def execute_parallel(self, account_ids: List[int], target_url: str,
                        actions: Dict[str, bool], wait_range: Tuple[int, int],
                        max_workers: int = 5) -> List[Dict]:
        results = []
        total_accounts = len(account_ids)
        completed = 0
        
        print(f"\n{'='*60}")
        print(f" 自動操作実行")
        print(f"{'='*60}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"アカウント数: {total_accounts}")
        print(f"同時実行数: {max_workers}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print(f"{'='*60}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.process_single_account,
                    account_id,
                    target_url,
                    actions,
                    wait_range
                ): account_id
                for account_id in account_ids
            }
            
            for future in as_completed(futures):
                account_id = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    print(f"\n進捗: {completed}/{total_accounts} 完了")
                except Exception as e:
                    print(f"\n[{account_id}] 実行エラー: {e}")
                    results.append({
                        "account_id": account_id,
                        "success": False,
                        "errors": [str(e)]
                    })
                    completed += 1
        
        self.print_summary(results)
        self.save_results(results)
        return results
    
    def print_summary(self, results: List[Dict]):
        print(f"\n{'='*60}")
        print(f" 実行結果サマリー")
        print(f"{'='*60}")
        
        total = len(results)
        success = sum(1 for r in results if r.get("success", False))
        failed = total - success
        
        print(f"総アカウント数: {total}")
        print(f"成功: {success}")
        print(f"失敗: {failed}")
        
        if failed > 0:
            print(f"\n失敗したアカウント:")
            for result in results:
                if not result.get("success", False):
                    errors = ", ".join(result.get("errors", ["不明なエラー"]))
                    print(f"  [{result['account_id']}] {result.get('email', 'N/A')}: {errors}")
        
        print(f"{'='*60}")
    
    def save_results(self, results: List[Dict]):
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"execution_{timestamp}.json")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nログファイル: {log_file}")

def create_sample_reply_csv(filepath: str = "config/reply_texts.csv"):
    import os
    import csv
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    sample_data = [
        {"リプライテキスト": "素晴らしい投稿ですね！"},
        {"リプライテキスト": "とても参考になりました"},
        {"リプライテキスト": "ありがとうございます"},
    ]
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["リプライテキスト"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
