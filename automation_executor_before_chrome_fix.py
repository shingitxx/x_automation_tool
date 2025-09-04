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
    """X自動操作実行エンジン"""
    
    def __init__(self):
        self.account_manager = AccountManager()
        self.reply_texts = []
        self.used_replies = set()
        self.results = []
        
    def setup_driver_with_proxy(self, account_id: int) -> Optional[webdriver.Chrome]:
        """プロキシ設定付きドライバー"""
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
            return driver
        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            return None
    
    def load_cookies(self, driver: webdriver.Chrome, account_id: int) -> bool:
        """Cookie読み込み"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return False
        
        cookie_file = os.path.join(
            self.account_manager.cookies_dir,
            f"{account['email']}_cookies.json"
        )
        
        if not os.path.exists(cookie_file):
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
            return True
        except:
            return False
    
    def check_login_status(self, driver: webdriver.Chrome) -> bool:
        """ログイン状態確認"""
        try:
            driver.get("https://x.com/home")
            time.sleep(3)
            return "home" in driver.current_url.lower()
        except:
            return False
    
    def load_reply_texts(self, csv_path: str = "config/reply_texts.csv") -> bool:
        """リプライテキスト読み込み"""
        if not os.path.exists(csv_path):
            return False
        
        try:
            self.reply_texts = []
            with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    text = row.get('リプライテキスト', '').strip()
                    if text:
                        self.reply_texts.append(text)
            return len(self.reply_texts) > 0
        except:
            return False
    
    def get_random_reply(self) -> Optional[str]:
        """ランダムリプライ取得"""
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
    
    def execute_like(self, driver: webdriver.Chrome, url: str) -> bool:
        """いいね実行"""
        try:
            driver.get(url)
            time.sleep(5)
            
            like_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='like']")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", like_button)
            time.sleep(2)
            return True
        except:
            try:
                driver.find_element(By.CSS_SELECTOR, "[data-testid='unlike']")
                return True  # 既にいいね済み
            except:
                return False
    
    def execute_bookmark(self, driver: webdriver.Chrome, url: str) -> bool:
        """ブックマーク実行"""
        try:
            if url not in driver.current_url:
                driver.get(url)
                time.sleep(5)
            
            bookmark_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='bookmark']")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bookmark_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", bookmark_button)
            time.sleep(2)
            return True
        except:
            try:
                driver.find_element(By.CSS_SELECTOR, "[data-testid='removeBookmark']")
                return True  # 既にブックマーク済み
            except:
                return False
    
    def execute_retweet(self, driver: webdriver.Chrome, url: str) -> bool:
        """リツイート実行"""
        try:
            if url not in driver.current_url:
                driver.get(url)
                time.sleep(5)
            
            retweet_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='retweet']")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", retweet_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", retweet_button)
            time.sleep(2)
            
            try:
                confirm_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='retweetConfirm']"))
                )
                driver.execute_script("arguments[0].click();", confirm_button)
                time.sleep(2)
            except:
                pass
            
            return True
        except:
            try:
                driver.find_element(By.CSS_SELECTOR, "[data-testid='unretweet']")
                return True  # 既にリツイート済み
            except:
                return False
    
    def execute_reply(self, driver: webdriver.Chrome, url: str, reply_text: str) -> bool:
        """リプライ実行"""
        try:
            driver.get(url)
            time.sleep(5)
            
            # リプライボタンクリック
            reply_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='reply']")
            driver.execute_script("arguments[0].click();", reply_button)
            time.sleep(2)
            
            # テキスト入力
            text_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']"))
            )
            text_area.send_keys(reply_text)
            time.sleep(2)
            
            # 送信ボタンを複数のセレクタで試行
            send_button_selectors = [
                "[data-testid='tweetButtonInline']",
                "[data-testid='tweetButton']", 
                "button[data-testid='tweetButtonInline']",
                "div[data-testid='tweetButtonInline']",
                "[role='button'][data-testid='tweetButtonInline']"
            ]
            
            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_enabled():
                        break
                except:
                    continue
            
            if not send_button:
                return False
            
            # ボタンが有効になるまで待機
            for i in range(5):
                if send_button.is_enabled():
                    break
                time.sleep(1)
            
            if not send_button.is_enabled():
                return False
            
            # 送信実行
            driver.execute_script("arguments[0].click();", send_button)
            time.sleep(3)
            return True
            
        except Exception as e:
            return False
    
    def process_single_account(self, account_id: int, target_url: str, 
                             actions: Dict[str, bool], wait_range: Tuple[int, int]) -> Dict:
        """単一アカウント処理"""
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
                    print("  ✓ いいね完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("bookmark", False):
                print("  実行: ブックマーク")
                if self.execute_bookmark(driver, target_url):
                    result["actions_performed"].append("bookmark")
                    print("  ✓ ブックマーク完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("retweet", False):
                print("  実行: リツイート")
                if self.execute_retweet(driver, target_url):
                    result["actions_performed"].append("retweet")
                    print("  ✓ リツイート完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
                    print("  実行: リプライ")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
                        print("  ✓ リプライ完了")
            
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
        """真の並列実行（プロファイル分離版）"""
        results = []
        total_accounts = len(account_ids)
        
        print(f"\n{'='*60}")
        print(f" 自動操作実行（並列処理）")
        print(f"{'='*60}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"アカウント数: {total_accounts}")
        print(f"同時実行数: {max_workers}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print(f"{'='*60}")
        
        completed = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 各アカウントに対してタスクを投入（スタガード起動）
            futures = {}
            for i, account_id in enumerate(account_ids):
                # 起動タイミングをずらして競合回避
                import time
                if i > 0:
                    time.sleep(1)  # 1秒間隔でタスク投入
                
                future = executor.submit(
                    self.process_single_account_isolated,
                    account_id,
                    target_url,
                    actions,
                    wait_range
                )
                futures[future] = account_id
            
            # 完了したタスクから順次結果を取得
            for future in as_completed(futures):
                account_id = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    status = "成功" if result.get("success", False) else "失敗"
                    actions_done = ", ".join(result.get("actions_performed", []))
                    
                    print(f"\n[{account_id}] {status} - {actions_done}")
                    print(f"進捗: {completed}/{total_accounts} 完了")
                    
                except Exception as e:
                    print(f"\n[{account_id}] 実行エラー: {e}")
                    results.append({
                        "account_id": account_id,
                        "success": False,
                        "errors": [str(e)],
                        "email": "unknown"
                    })
                    completed += 1
        
        self.print_summary(results)
        self.save_results(results)
        return results
    

    def process_single_account_isolated(self, account_id: int, target_url: str, 
                                       actions: Dict[str, bool], wait_range: Tuple[int, int]) -> Dict:
        """完全分離された単一アカウント処理"""
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
            
            # 完全分離されたドライバー作成
            driver = self.setup_driver_isolated(account_id)
            if not driver:
                result["errors"].append("ドライバー起動失敗")
                return result
            
            if not self.load_cookies(driver, account_id):
                result["errors"].append("Cookie読み込み失敗")
                return result
            
            if not self.check_login_status(driver):
                result["errors"].append("ログイン状態確認失敗")
                return result
            
            print(f"  [{account_id}] ✓ ログイン成功")
            
            if actions.get("like", False):
                print(f"  [{account_id}] 実行: いいね")
                if self.execute_like(driver, target_url):
                    result["actions_performed"].append("like")
                    print(f"  [{account_id}] ✓ いいね完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("bookmark", False):
                print(f"  [{account_id}] 実行: ブックマーク")
                if self.execute_bookmark(driver, target_url):
                    result["actions_performed"].append("bookmark")
                    print(f"  [{account_id}] ✓ ブックマーク完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("retweet", False):
                print(f"  [{account_id}] 実行: リツイート")
                if self.execute_retweet(driver, target_url):
                    result["actions_performed"].append("retweet")
                    print(f"  [{account_id}] ✓ リツイート完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
                    print(f"  [{account_id}] 実行: リプライ")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
                        print(f"  [{account_id}] ✓ リプライ完了")
            
            result["success"] = len(result["actions_performed"]) > 0
            
        except Exception as e:
            result["errors"].append(f"実行エラー: {str(e)[:100]}")
            print(f"  [{account_id}] ✗ エラー: {str(e)[:50]}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return result
    
    def setup_driver_isolated(self, account_id: int) -> Optional[webdriver.Chrome]:
        """Windows対応完全分離ドライバー作成"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        import tempfile
        import threading
        import uuid
        import time
        
        # 完全ユニークな識別子生成
        thread_id = threading.current_thread().ident
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time() * 1000))
        
        # Windows対応の安全な一時ディレクトリ作成
        temp_suffix = f"chrome_{account_id}_{thread_id}_{unique_id}_{timestamp}"
        
        # 最大10回リトライで一意ディレクトリ作成
        temp_dir = None
        for attempt in range(10):
            try:
                temp_dir = tempfile.mkdtemp(
                    prefix=f"{temp_suffix}_{attempt}_",
                    dir=tempfile.gettempdir()
                )
                break
            except (FileExistsError, OSError) as e:
                if attempt == 9:
                    print(f"  [{account_id}] ✗ 一時ディレクトリ作成失敗: {str(e)}")
                    return None
                time.sleep(0.1)
        
        if not temp_dir:
            return None
        
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-popup-blocking')
        
        # 完全分離設定
        chrome_options.add_argument(f'--user-data-dir={temp_dir}')
        
        # ポート競合回避（より広い範囲）
        debug_port = 9000 + (account_id * 100) + random.randint(0, 99)
        chrome_options.add_argument(f'--remote-debugging-port={debug_port}')
        
        # プロキシ設定
        proxy = account.get("proxy", {})
        if proxy and proxy.get("host") and proxy.get("port"):
            proxy_url = f"{proxy['host']}:{proxy['port']}"
            chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
        
        try:
            driver = uc.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            
            # 成功時は一時ディレクトリを記録（後でクリーンアップ用）
            if not hasattr(self, 'temp_dirs'):
                self.temp_dirs = []
            self.temp_dirs.append(temp_dir)
            
            print(f"  [{account_id}] ✓ Windows対応ドライバー起動成功")
            return driver
            
        except Exception as e:
            print(f"  [{account_id}] ✗ ドライバー起動エラー: {str(e)[:100]}")
            # 失敗時は一時ディレクトリをクリーンアップ
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            return None
    def print_summary(self, results: List[Dict]):
        """結果サマリー表示"""
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
        """結果保存"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"execution_{timestamp}.json")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

def create_sample_reply_csv(filepath: str = "config/reply_texts.csv"):
    """サンプルリプライCSV作成"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    sample_data = [
        {"リプライテキスト": "興味深い内容ですね"},
        {"リプライテキスト": "シェアしてくださってありがとう"},
        {"リプライテキスト": "これは知らなかったです！"},
        {"リプライテキスト": "めちゃくちゃ良いですね"},
        {"リプライテキスト": "最高の投稿です"}
    ]
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ["リプライテキスト"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
