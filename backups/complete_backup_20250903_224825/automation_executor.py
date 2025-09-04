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
            self.reply_texts = []
            
            encodings = ['utf-8-sig', 'utf-8']
            
            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding, newline='') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            text = row.get('リプライテキスト') or row.get('reply_text') or ''
                            if text and text.strip():
                                self.reply_texts.append(text.strip())
                    
                    if self.reply_texts:
                        break
                except:
                    continue
            
            if self.reply_texts:
                print(f"  ✓ {len(self.reply_texts)}件のリプライテキストを読み込みました")
                return True
            else:
                print(f"  ✗ リプライテキストが空です")
                return False
                
        except Exception as e:
            print(f"  ✗ 読み込みエラー: {e}")
            return False
    
    def get_random_reply(self) -> Optional[str]:
        if not self.reply_texts:
            return None
            
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
            time.sleep(5)
            
            try:
                like_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='like']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", like_button)
                time.sleep(2)
                print("  ✓ いいね完了")
                return True
            except:
                try:
                    unlike_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='unlike']")
                    print("  → 既にいいね済み")
                    return True
                except:
                    print("  ✗ いいねボタンが見つかりません")
                    return False
        except Exception as e:
            print(f"  ✗ いいねエラー: {str(e)[:50]}")
            return False
    
    def execute_bookmark(self, driver: webdriver.Chrome, url: str) -> bool:
        try:
            if url not in driver.current_url:
                driver.get(url)
                time.sleep(5)
            else:
                time.sleep(2)
            
            try:
                bookmark_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='bookmark']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bookmark_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", bookmark_button)
                time.sleep(2)
                print("  ✓ ブックマーク完了")
                return True
            except:
                try:
                    remove_bookmark = driver.find_element(By.CSS_SELECTOR, "[data-testid='removeBookmark']")
                    print("  → 既にブックマーク済み")
                    return True
                except:
                    print("  ✗ ブックマークボタンが見つかりません")
                    return False
        except Exception as e:
            print(f"  ✗ ブックマークエラー: {str(e)[:50]}")
            return False
    
    def execute_retweet(self, driver: webdriver.Chrome, url: str) -> bool:
        try:
            if url not in driver.current_url:
                driver.get(url)
                time.sleep(5)
            else:
                time.sleep(2)
            
            retweet_selectors = [
                "[data-testid='retweet']",
                "[data-testid='unretweet']"
            ]
            
            for selector in retweet_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        button = elements[0]
                        
                        if button.is_displayed():
                            testid = button.get_attribute("data-testid")
                            if testid == "unretweet":
                                print("  → 既にリツイート済み")
                                return True
                            
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            
                            try:
                                confirm_selectors = [
                                    "[data-testid='retweetConfirm']",
                                    "div[role='menuitem'][data-testid='retweetConfirm']",
                                    "//span[text()='リポスト']/..",
                                    "//span[text()='Repost']/.."
                                ]
                                
                                for conf_sel in confirm_selectors:
                                    try:
                                        if conf_sel.startswith("//"):
                                            conf_btn = driver.find_element(By.XPATH, conf_sel)
                                        else:
                                            conf_btn = driver.find_element(By.CSS_SELECTOR, conf_sel)
                                        
                                        driver.execute_script("arguments[0].click();", conf_btn)
                                        time.sleep(2)
                                        print("  ✓ リツイート完了")
                                        return True
                                    except:
                                        continue
                                
                                print("  ✓ リツイート完了")
                                return True
                                
                            except:
                                print("  ✓ リツイート完了")
                                return True
                                
                except Exception as e:
                    continue
            
            print(f"  ✗ リツイートボタンが見つかりません")
            return False
            
        except Exception as e:
            print(f"  ✗ リツイートエラー: {str(e)[:50]}")
            return False
    
    def execute_reply(self, driver: webdriver.Chrome, url: str, reply_text: str) -> bool:
        try:
            driver.get(url)
            time.sleep(5)
            
            if "x.com" not in driver.current_url and "twitter.com" not in driver.current_url:
                print(f"  ✗ ページ読み込みエラー: {driver.current_url}")
                return False
            
            print(f"  リプライテキスト: {reply_text}")
            
            reply_button_selectors = [
                "[data-testid='reply']",
                "div[role='button'][aria-label*='Reply']",
                "div[role='button'][aria-label*='返信']",
                "button[aria-label*='Reply']"
            ]
            
            clicked = False
            for selector in reply_button_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        button = elements[0]
                        if button.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            clicked = True
                            print("  ✓ リプライボタンをクリック")
                            break
                except:
                    continue
            
            reply_input_selectors = [
                "[data-testid='tweetTextarea_0']",
                "div[role='textbox']",
                "div[contenteditable='true'][role='textbox']",
                "div[aria-label*='Post text']",
                "div[aria-label*='ポストのテキスト']"
            ]
            
            input_found = False
            for selector in reply_input_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(1)
                            
                            element.send_keys(reply_text)
                            time.sleep(2)
                            
                            input_found = True
                            print("  ✓ リプライテキストを入力")
                            break
                    
                    if input_found:
                        break
                except:
                    continue
            
            if not input_found:
                print("  ✗ リプライ入力欄が見つかりません")
                return False
            
            send_button_selectors = [
                "[data-testid='tweetButtonInline']",
                "[data-testid='tweetButton']",
                "button[data-testid='tweetButton']",
                "div[role='button'][data-testid='tweetButtonInline']",
                "//span[text()='返信']/..",
                "//span[text()='Reply']/..",
                "//span[text()='Post']/.."
            ]
            
            for selector in send_button_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)
                            print("  ✓ リプライを送信")
                            return True
                except:
                    continue
            
            print("  ✗ 送信ボタンが見つかりません")
            return False
            
        except Exception as e:
            print(f"  ✗ リプライエラー: {str(e)[:100]}")
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
                print("  実行: リプライ")
                reply_text = self.get_random_reply()
                if reply_text:
                    print(f"    使用テキスト: {reply_text}")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
                        self.random_wait(wait_range[0], wait_range[1])
                    else:
                        result["errors"].append("リプライ失敗")
                else:
                    print("  ✗ リプライテキストが見つかりません")
                    result["errors"].append("リプライテキストなし")
            
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
        {"リプライテキスト": "興味深い内容ですね"},
        {"リプライテキスト": "シェアしてくださってありがとう"},
        {"リプライテキスト": "これは知らなかったです！"},
        {"リプライテキスト": "めちゃくちゃ良いですね"},
        {"リプライテキスト": "最高の投稿です"},
        {"リプライテキスト": "この情報は助かります"},
        {"リプライテキスト": "またひとつ学びました"},
        {"リプライテキスト": "すごく役立つ情報です"},
        {"リプライテキスト": "これからも投稿楽しみにしてます"},
        {"リプライテキスト": "有益な情報をありがとう！"}
    ]
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ["リプライテキスト"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
