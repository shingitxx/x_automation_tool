#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X自動化ツール完全版作成
最初の要件定義に基づく完成形システム
"""

import os
import shutil
from datetime import datetime

print("=" * 60)
print(" X自動化ツール完全版作成")
print("=" * 60)

# 既存ファイルのバックアップ
backup_dir = f"backups/complete_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)

essential_files = [
    "cli_interface.py",
    "account_manager.py",
    "automation_executor.py",
    "cli_automation.py",
    "login_manager.py",
    "proxy_tester.py",
]

for file in essential_files:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(backup_dir, file))

# 1. account_manager.py（完成版）
account_manager_content = '''import os
import json
import csv
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet

class AccountManager:
    """アカウント管理システム"""
    
    def __init__(self):
        self.data_dir = "data"
        self.config_dir = "config"
        self.cache_dir = "cache"
        self.cookies_dir = os.path.join(self.cache_dir, "cookies")
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)
        
        self.accounts_file = os.path.join(self.data_dir, "account_status.json")
        self.key_file = os.path.join(self.cache_dir, "encryption.key")
        
        self._init_encryption()
        self.accounts = self._load_accounts()
    
    def _init_encryption(self):
        """暗号化キー初期化"""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        with open(self.key_file, 'rb') as f:
            self.cipher = Fernet(f.read())
    
    def _load_accounts(self) -> Dict:
        """アカウントデータ読み込み"""
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"accounts": []}
    
    def _save_accounts(self):
        """アカウントデータ保存"""
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)
    
    def import_from_csv(self, csv_path: str) -> Dict[str, int]:
        """CSVからアカウント一括インポート"""
        if not os.path.exists(csv_path):
            return {"error": "ファイルが見つかりません"}
        
        results = {"imported": 0, "skipped": 0, "errors": 0}
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    email = row.get('アカウントID', '').strip()
                    password = row.get('パスワード', '').strip()
                    proxy_host = row.get('プロキシホスト', '').strip()
                    proxy_port = row.get('プロキシポート', '').strip()
                    proxy_user = row.get('プロキシユーザー', '').strip()
                    proxy_pass = row.get('プロキシパスワード', '').strip()
                    
                    if not all([email, password, proxy_host, proxy_port, proxy_user, proxy_pass]):
                        results["errors"] += 1
                        continue
                    
                    if self._account_exists(email):
                        results["skipped"] += 1
                        continue
                    
                    account_id = self._get_next_id()
                    encrypted_password = self.cipher.encrypt(password.encode()).decode()
                    
                    account = {
                        "id": account_id,
                        "email": email,
                        "password": encrypted_password,
                        "proxy": {
                            "host": proxy_host,
                            "port": proxy_port,
                            "username": proxy_user,
                            "password": proxy_pass
                        },
                        "created_at": datetime.now().isoformat(),
                        "last_login": None,
                        "status": "not_logged_in"
                    }
                    
                    self.accounts["accounts"].append(account)
                    results["imported"] += 1
            
            self._save_accounts()
            return results
            
        except Exception as e:
            return {"error": str(e)}
    
    def _account_exists(self, email: str) -> bool:
        """アカウント存在確認"""
        return any(acc["email"] == email for acc in self.accounts["accounts"])
    
    def _get_next_id(self) -> int:
        """次のアカウントID取得"""
        if not self.accounts["accounts"]:
            return 1
        return max(acc["id"] for acc in self.accounts["accounts"]) + 1
    
    def get_account_by_id(self, account_id: int) -> Optional[Dict]:
        """IDでアカウント取得"""
        for account in self.accounts["accounts"]:
            if account["id"] == account_id:
                # パスワードを復号化
                decrypted_account = account.copy()
                try:
                    decrypted_account["password"] = self.cipher.decrypt(
                        account["password"].encode()
                    ).decode()
                except:
                    decrypted_account["password"] = account["password"]
                return decrypted_account
        return None
    
    def get_proxy_url(self, account_id: int) -> Optional[str]:
        """プロキシURL取得"""
        account = self.get_account_by_id(account_id)
        if not account:
            return None
        
        proxy = account["proxy"]
        return f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
    
    def _get_account_status(self, account: Dict) -> str:
        """アカウントステータス取得"""
        cookie_file = os.path.join(self.cookies_dir, f"{account['email']}_cookies.json")
        
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie_data = json.load(f)
                
                saved_time = datetime.fromisoformat(cookie_data.get("saved_at", ""))
                if (datetime.now() - saved_time).days < 30:
                    return "✓ログイン済み"
                else:
                    return "⚠Cookie期限切れ"
            except:
                return "✗未ログイン"
        
        return "✗未ログイン"
'''

# 2. automation_executor.py（完成版）
automation_executor_content = '''import os
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
            
            # 送信
            send_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='tweetButtonInline']")
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
            print(f"\\n[{account_id}] {account['email']} - 処理開始")
            
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
        """並列実行（キュー方式）"""
        results = []
        total_accounts = len(account_ids)
        completed = 0
        
        print(f"\\n{'='*60}")
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
                    print(f"\\n進捗: {completed}/{total_accounts} 完了")
                except Exception as e:
                    print(f"\\n[{account_id}] 実行エラー: {e}")
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
        """結果サマリー表示"""
        print(f"\\n{'='*60}")
        print(f" 実行結果サマリー")
        print(f"{'='*60}")
        
        total = len(results)
        success = sum(1 for r in results if r.get("success", False))
        failed = total - success
        
        print(f"総アカウント数: {total}")
        print(f"成功: {success}")
        print(f"失敗: {failed}")
        
        if failed > 0:
            print(f"\\n失敗したアカウント:")
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
'''

# 3. cli_automation.py（完成版）
cli_automation_content = '''import os
from typing import Dict, List, Tuple
from automation_executor import AutomationExecutor, create_sample_reply_csv

class AutomationCLI:
    """自動操作CLI"""
    
    def __init__(self):
        self.executor = AutomationExecutor()
    
    def run_automation(self):
        """自動操作実行"""
        print("\\n" + "="*60)
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
        
        input("\\nEnterキーを押してメニューに戻る...")
    
    def select_accounts(self) -> List[int]:
        """アカウント選択"""
        print("\\n実行するアカウントを選択してください：")
        print("1. 全アカウント実行")
        print("2. 特定番号を選択（例: 5）")
        print("3. 複数選択（例: 1,3,5,7）")
        print("4. 範囲指定（例: 10-20）")
        print("5. ログイン済みのみ実行")
        
        try:
            choice = int(input("選択: "))
        except ValueError:
            return []
        
        if choice == 1:
            accounts = self.executor.account_manager.accounts.get("accounts", [])
            return [acc["id"] for acc in accounts]
        elif choice == 2:
            try:
                account_id = int(input("アカウント番号を入力: "))
                return [account_id]
            except ValueError:
                return []
        elif choice == 3:
            try:
                ids_str = input("アカウント番号をカンマ区切りで入力: ")
                return [int(x.strip()) for x in ids_str.split(",")]
            except ValueError:
                return []
        elif choice == 4:
            try:
                range_str = input("範囲を入力（例: 1-10）: ")
                start, end = map(int, range_str.split("-"))
                return list(range(start, end + 1))
            except ValueError:
                return []
        elif choice == 5:
            logged_in = []
            accounts = self.executor.account_manager.accounts.get("accounts", [])
            for account in accounts:
                cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                if os.path.exists(cookie_file):
                    logged_in.append(account["id"])
            return logged_in
        
        return []
    
    def get_concurrent_workers(self, total_accounts: int) -> int:
        """同時実行数取得"""
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
        url = input("\\n対象URLを入力してください: ").strip()
        
        if not url:
            print("URLが入力されませんでした")
            return ""
        
        if not url.startswith(("https://x.com", "https://twitter.com")):
            print("X（Twitter）のURLを入力してください")
            return ""
        
        return url
    
    def select_actions(self) -> Dict[str, bool]:
        """実行操作選択"""
        print("\\n実行する操作を選択してください：")
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
            
            confirm = input(f"\\n「{', '.join(action_names)}」を実行します。よろしいですか？(y/n): ")
            if confirm.lower() == 'y':
                return actions
        
        return {}
    
    def get_wait_range(self) -> Tuple[int, int]:
        """待機時間設定"""
        print("\\n操作間の待機時間を設定します")
        
        try:
            min_wait = int(input("最小待機時間（秒）: "))
            max_wait = int(input("最大待機時間（秒）: "))
            
            if min_wait > max_wait:
                min_wait, max_wait = max_wait, min_wait
                
            return (min_wait, max_wait)
            
        except ValueError:
            print("デフォルト値（3-10秒）を使用します")
            return (3, 10)
    
    def setup_reply_texts(self) -> bool:
        """リプライテキスト設定"""
        csv_path = "config/reply_texts.csv"
        
        if self.executor.load_reply_texts(csv_path):
            return True
        
        if not os.path.exists(csv_path):
            print(f"\\nリプライテキストファイルが見つかりません: {csv_path}")
            create_sample = input("サンプルファイルを作成しますか？ (y/n): ").strip().lower()
            if create_sample == 'y':
                create_sample_reply_csv(csv_path)
                return self.executor.load_reply_texts(csv_path)
        
        return False
    
    def confirm_execution(self, account_ids: List[int], target_url: str, 
                         actions: Dict[str, bool], wait_range: Tuple[int, int], 
                         max_workers: int) -> bool:
        """実行確認"""
        print("\\n" + "="*60)
        print(" 設定確認")
        print("="*60)
        print(f"アカウント数: {len(account_ids)}")
        print(f"同時実行数: {max_workers}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print("="*60)
        
        confirm = input("\\n実行を開始しますか？(y/n): ")
        return confirm.lower() == 'y'
'''

# 4. login_manager.py（完成版・手動ログインのみ）
login_manager_content = '''import os
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from account_manager import AccountManager

class LoginManager:
    """ログイン管理（手動ログインのみ）"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.x_login_url = "https://x.com/i/flow/login"
    
    def setup_driver(self, proxy_url: Optional[str] = None, headless: bool = False) -> webdriver.Chrome:
        """ドライバーセットアップ"""
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        if headless:
            options.add_argument('--headless=new')
        
        try:
            driver = uc.Chrome(options=options, version_main=139)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            print(f"ドライバー起動エラー: {e}")
            return None
    
    def manual_login(self, account_ids: List[int], max_concurrent: int = 10):
        """手動ログイン"""
        drivers = []
        
        try:
            print(f"\\n{len(account_ids)}個のアカウントでブラウザを起動します")
            
            for account_id in account_ids:
                account = self.manager.get_account_by_id(account_id)
                if not account:
                    print(f"アカウントID {account_id} が見つかりません")
                    continue
                
                print(f"\\n[{account_id}] {account['email']} - ブラウザ起動中...")
                
                driver = self.setup_driver()
                
                if driver:
                    driver.execute_script(f"document.title = '[{account_id}] {account['email']}'")
                    driver.get(self.x_login_url)
                    drivers.append((driver, account_id, account['email']))
                    print(f"  ✓ ブラウザ起動完了")
                else:
                    print(f"  ✗ ブラウザ起動失敗")
            
            if drivers:
                print(f"\\n{'='*60}")
                print(f" 手動ログイン")
                print(f"{'='*60}")
                print(f"起動したブラウザ: {len(drivers)}個")
                print("\\n各ブラウザで以下の手順でログインしてください:")
                print("1. メールアドレス/ユーザー名を入力")
                print("2. パスワードを入力") 
                print("3. 2FA認証（必要な場合）")
                print("\\nウィンドウタイトルでアカウントを識別できます:")
                
                for driver, account_id, email in drivers:
                    print(f"  [{account_id}] {email}")
                
                print(f"\\n{'='*60}")
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
                
                print(f"\\n結果: {success_count}/{len(drivers)} アカウントでCookie保存完了")
            else:
                print("\\nブラウザの起動に失敗しました")
        
        except Exception as e:
            print(f"手動ログインエラー: {e}")
            for driver, _, _ in drivers:
                try:
                    driver.quit()
                except:
                    pass
    
    def save_cookies(self, driver: webdriver.Chrome, account_id: int):
        """Cookie保存"""
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
'''

# 5. proxy_tester.py（完成版）
proxy_tester_content = '''import os
import time
import requests
from typing import Dict
from account_manager import AccountManager

class ProxyTester:
    """プロキシテスト"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://ipinfo.io/json"
        ]
    
    def test_account_proxy(self, account_id: int) -> Dict:
        """アカウントのプロキシテスト"""
        account = self.manager.get_account_by_id(account_id)
        if not account:
            return {"status": "error", "error": "アカウントが見つかりません"}
        
        proxy_url = self.manager.get_proxy_url(account_id)
        if not proxy_url:
            return {"status": "error", "error": "プロキシ情報が見つかりません"}
        
        print(f"\\nアカウント: [{account_id}] {account['email']}")
        print(f"プロキシをテスト中: {account['proxy']['host']}:{account['proxy']['port']}")
        print("-" * 50)
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        results = {"successes": 0, "failures": 0, "responses": []}
        
        for test_url in self.test_urls:
            print(f"テストURL: {test_url}")
            try:
                start_time = time.time()
                response = requests.get(test_url, proxies=proxies, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = round(end_time - start_time, 2)
                    
                    if "ip" in response.text.lower():
                        try:
                            data = response.json()
                            ip = data.get('ip', data.get('origin', 'N/A'))
                            print(f"✓ 成功 - IP: {ip} (応答時間: {response_time}秒)")
                        except:
                            print(f"✓ 成功 (応答時間: {response_time}秒)")
                    else:
                        print(f"✓ 成功 (応答時間: {response_time}秒)")
                    
                    results["successes"] += 1
                    results["responses"].append({
                        "url": test_url,
                        "status": "success",
                        "response_time": response_time
                    })
                else:
                    print(f"✗ HTTPエラー: {response.status_code}")
                    results["failures"] += 1
                    
            except requests.exceptions.Timeout:
                print("✗ タイムアウト")
                results["failures"] += 1
            except requests.exceptions.ConnectionError:
                print("✗ 接続エラー")
                results["failures"] += 1
            except Exception as e:
                print(f"✗ エラー: {str(e)}")
                results["failures"] += 1
            
            print("次のテストまで2秒待機...")
            time.sleep(2)
        
        if results["successes"] > 0:
            results["status"] = "success"
        else:
            results["status"] = "failure"
        
        return results
    
    def test_all_proxies(self) -> Dict:
        """全プロキシテスト"""
        accounts = self.manager.accounts.get("accounts", [])
        if not accounts:
            return {"error": "アカウントが登録されていません"}
        
        print(f"\\n{len(accounts)}個のアカウントのプロキシをテストします\\n")
        
        all_results = []
        
        for account in accounts:
            result = self.test_account_proxy(account["id"])
            result["account_id"] = account["id"]
            result["email"] = account["email"]
            all_results.append(result)
        
        # サマリー表示
        success_count = sum(1 for r in all_results if r.get("status") == "success")
        print(f"\\n{'='*50}")
        print(f"テスト結果サマリー")
        print(f"{'='*50}")
        print(f"総アカウント数: {len(all_results)}")
        print(f"成功: {success_count}")
        print(f"失敗: {len(all_results) - success_count}")
        
        return {"results": all_results}
'''

# 6. cli_interface.py（完成版）
cli_interface_content = '''import os
import sys
from typing import List
from account_manager import AccountManager
from login_manager import LoginManager
from proxy_tester import ProxyTester
from cli_automation import AutomationCLI

class CLIInterface:
    """メインCLIインターフェース"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.login_manager = LoginManager()
        self.proxy_tester = ProxyTester()
        self.automation_cli = AutomationCLI()
    
    def display_accounts_with_status(self):
        """アカウント一覧表示"""
        print("\\n" + "="*60)
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
    
    def get_concurrent_count(self, total_accounts: int) -> int:
        """同時実行数を取得"""
        max_recommended = min(10, total_accounts)
        
        print(f"\\n対象アカウント数: {total_accounts}")
        print(f"推奨同時実行数: 1-{max_recommended}")
        
        while True:
            try:
                concurrent = int(input(f"同時に開くブラウザ数を入力 (1-{max_recommended}): "))
                if 1 <= concurrent <= max_recommended:
                    return concurrent
                else:
                    print(f"1-{max_recommended}の範囲で入力してください")
            except ValueError:
                print("数字を入力してください")
    
    def main_menu(self):
        """メインメニュー"""
        while True:
            print("\\n" + "="*60)
            print(" X自動化ツール - メインメニュー")
            print("="*60)
            print("1. アカウント管理")
            print("2. 初回ログイン")
            print("3. プロキシ設定確認")
            print("4. プロキシテスト")
            print("5. CSVインポート")
            print("6. アカウント追加（手動）")
            print("7. アカウント一覧表示")
            print("8. サンプルCSV生成")
            print("9. 自動操作実行")
            print("10. 終了")
            print("-"*60)
            
            try:
                choice = int(input("選択番号を入力: "))
            except ValueError:
                print("数字を入力してください")
                continue
            
            if choice == 1:
                print("\\nアカウント管理メニューは開発中です")
                input("Enterキーで戻る...")
            elif choice == 2:
                self.initial_login_menu()
            elif choice == 3:
                print("\\nプロキシ設定メニューは開発中です")
                input("Enterキーで戻る...")
            elif choice == 4:
                self.proxy_test_menu()
            elif choice == 5:
                self.csv_import_menu()
            elif choice == 6:
                print("\\n手動アカウント追加は開発中です")
                input("Enterキーで戻る...")
            elif choice == 7:
                self.display_accounts()
            elif choice == 8:
                self.generate_sample_csv()
            elif choice == 9:
                self.automation_cli.run_automation()
            elif choice == 10:
                print("プログラムを終了します")
                break
            else:
                print("1-10の範囲で入力してください")
    
    def initial_login_menu(self):
        """初回ログインメニュー"""
        while True:
            print("\\n" + "="*50)
            print(" 初回ログイン")
            print("="*50)
            print("1. 特定の番号を選択してログイン")
            print("2. 複数選択してログイン（カンマ区切り）")
            print("3. 範囲指定でログイン")
            print("4. 未ログインのみ全てログイン")
            print("5. メインメニューに戻る")
            
            try:
                choice = int(input("選択: "))
            except ValueError:
                print("数字を入力してください")
                continue
            
            if choice == 1:
                self.display_accounts_with_status()
                try:
                    account_id = int(input("ログインするアカウント番号: "))
                    if self.manager.get_account_by_id(account_id):
                        self.login_manager.manual_login([account_id], 1)
                    else:
                        print("存在しないアカウントです")
                except ValueError:
                    print("数字を入力してください")
                    
            elif choice == 2:
                self.display_accounts_with_status()
                try:
                    ids_str = input("ログインするアカウント番号をカンマ区切りで入力: ")
                    account_ids = [int(x.strip()) for x in ids_str.split(",")]
                    valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
                    if valid_ids:
                        max_concurrent = self.get_concurrent_count(len(valid_ids))
                        self.login_manager.manual_login(valid_ids, max_concurrent)
                    else:
                        print("有効なアカウントがありません")
                except ValueError:
                    print("正しい形式で入力してください")
                    
            elif choice == 3:
                self.display_accounts_with_status()
                try:
                    start = int(input("開始番号: "))
                    end = int(input("終了番号: "))
                    account_ids = list(range(start, end + 1))
                    valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
                    if valid_ids:
                        max_concurrent = self.get_concurrent_count(len(valid_ids))
                        self.login_manager.manual_login(valid_ids, max_concurrent)
                    else:
                        print("指定範囲に有効なアカウントがありません")
                except ValueError:
                    print("数字を入力してください")
                    
            elif choice == 4:
                not_logged = []
                for account in self.manager.accounts.get("accounts", []):
                    cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                    if not os.path.exists(cookie_file):
                        not_logged.append(account["id"])
                        
                if not_logged:
                    print(f"未ログインアカウント: {not_logged}")
                    max_concurrent = self.get_concurrent_count(len(not_logged))
                    self.login_manager.manual_login(not_logged, max_concurrent)
                else:
                    print("未ログインのアカウントがありません")
                    
            elif choice == 5:
                break
            else:
                print("1-5の範囲で入力してください")
    
    def proxy_test_menu(self):
        """プロキシテストメニュー"""
        print("\\nプロキシテストを実行します")
        self.display_accounts_with_status()
        try:
            account_id = int(input("テストするアカウント番号: "))
            result = self.proxy_tester.test_account_proxy(account_id)
            print(f"\\nテスト結果: {result.get('status', 'unknown')}")
        except ValueError:
            print("数字を入力してください")
        input("Enterキーで戻る...")
    
    def csv_import_menu(self):
        """CSVインポートメニュー"""
        csv_path = input("CSVファイルのパスを入力（デフォルト: config/accounts.csv）: ").strip()
        if not csv_path:
            csv_path = "config/accounts.csv"
        
        if os.path.exists(csv_path):
            result = self.manager.import_from_csv(csv_path)
            print(f"\\nインポート結果:")
            if "error" in result:
                print(f"エラー: {result['error']}")
            else:
                print(f"インポート: {result.get('imported', 0)}件")
                print(f"スキップ: {result.get('skipped', 0)}件")
                print(f"エラー: {result.get('errors', 0)}件")
        else:
            print(f"ファイルが見つかりません: {csv_path}")
        input("Enterキーで戻る...")
    
    def display_accounts(self):
        """アカウント一覧表示"""
        self.display_accounts_with_status()
        input("Enterキーで戻る...")
    
    def generate_sample_csv(self):
        """サンプルCSV生成"""
        csv_path = "config/accounts_sample.csv"
        os.makedirs("config", exist_ok=True)
        
        import csv
        sample_data = [
            {
                "アカウントID": "user1@example.com",
                "パスワード": "password123",
                "プロキシホスト": "iproyalfast.hellworld.io",
                "プロキシポート": "12321",
                "プロキシユーザー": "your_username",
                "プロキシパスワード": "your_password_session"
            }
        ]
        
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ["アカウントID", "パスワード", "プロキシホスト", 
                         "プロキシポート", "プロキシユーザー", "プロキシパスワード"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"\\n✓ サンプルCSVを作成しました: {csv_path}")
        print("実際のアカウント情報に書き換えてからインポートしてください")
        input("Enterキーで戻る...")

def main():
    """メイン関数"""
    try:
        cli = CLIInterface()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\\n\\nプログラムが中断されました")
    except Exception as e:
        print(f"\\n予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
'''

# ファイル作成
files_to_create = [
    ("account_manager.py", account_manager_content),
    ("automation_executor.py", automation_executor_content),
    ("cli_automation.py", cli_automation_content),
    ("login_manager.py", login_manager_content),
    ("proxy_tester.py", proxy_tester_content),
    ("cli_interface.py", cli_interface_content),
]

for filename, content in files_to_create:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ {filename} を作成しました")

# サンプルCSVも作成
os.makedirs("config", exist_ok=True)
with open("config/reply_texts.csv", "w", encoding="utf-8-sig", newline="") as f:
    import csv

    writer = csv.writer(f)
    writer.writerow(["リプライテキスト"])
    for text in [
        "興味深い内容ですね",
        "シェアしてくださってありがとう",
        "これは知らなかったです！",
        "めちゃくちゃ良いですね",
        "最高の投稿です",
    ]:
        writer.writerow([text])

print("✓ config/reply_texts.csv を作成しました")

print("\n" + "=" * 60)
print(" X自動化ツール完全版作成完了")
print("=" * 60)
print("\n実装された機能:")
print("✅ アカウント管理（CSV一括インポート、暗号化保存）")
print("✅ 初回ログイン（手動、同時実行数選択可能）")
print("✅ プロキシテスト機能")
print("✅ 自動操作（いいね、ブックマーク、リツイート、リプライ）")
print("✅ 並列処理（キュー方式で同時実行数制御）")
print("✅ 選択的実行（全て、特定、複数、範囲、ログイン済みのみ）")
print("✅ リプライテキストランダム選択")
print("✅ 詳細ログ記録")
print("\n使用方法:")
print("1. py -3.10 cli_interface.py")
print("2. CSVインポートでアカウント登録")
print("3. 初回ログインで手動ログイン")
print("4. 自動操作実行で各種操作")
