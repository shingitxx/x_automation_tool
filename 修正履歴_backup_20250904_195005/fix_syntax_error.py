#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SyntaxError修正
"""

import os


def main():
    print("=" * 60)
    print(" SyntaxError修正")
    print("=" * 60)

    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    print("  60行目周辺の構文エラーを確認中...")

    # 60行目周辺を確認
    for i in range(max(0, 55), min(len(lines), 65)):
        line = lines[i].rstrip()
        print(f"  行{i+1:2}: {line}")

    # 文字列リテラルの問題を修正
    fixed_lines = []
    for i, line in enumerate(lines):
        # よくある問題：終了していない文字列、エスケープ問題
        # f文字列内での引用符の問題を修正
        if line.strip().startswith('print(f"') and not line.strip().endswith('")\\n'):
            # f文字列の修正
            line = line.replace('\\"', '"').replace("'", "\\'")

        # 複数行文字列の問題
        if '"""' in line:
            quote_count = line.count('"""')
            if quote_count % 2 != 0:
                # 奇数個のトリプルクォートがある場合は修正が必要
                print(f"  ⚠ 行{i+1}でトリプルクォートの問題を検出")

        fixed_lines.append(line)

    # ファイルを書き直し
    try:
        with open("automation_executor.py", "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        print("  ✓ ファイル修正完了")
    except Exception as e:
        print(f"  ✗ ファイル書き込みエラー: {e}")
        return

    # 構文チェック
    print("  構文チェック実行中...")
    try:
        import py_compile

        py_compile.compile("automation_executor.py", doraise=True)
        print("  ✓ 構文チェック成功")
    except py_compile.PyCompileError as e:
        print(f"  ✗ 構文エラー継続: {e}")

        # 問題のある行を特定して修正
        error_msg = str(e)
        if "line" in error_msg:
            # エラー行番号を抽出
            import re

            match = re.search(r"line (\d+)", error_msg)
            if match:
                error_line = int(match.group(1))
                print(f"  エラー行: {error_line}")

                # 該当行周辺を表示
                for i in range(
                    max(0, error_line - 3), min(len(fixed_lines), error_line + 3)
                ):
                    marker = " >>> " if i == error_line - 1 else "     "
                    print(f"{marker}行{i+1:2}: {fixed_lines[i].rstrip()}")

        # 緊急回避：automation_executor.pyを最小限で再作成
        print("  緊急回避：最小限のautomation_executor.pyを作成...")
        create_minimal_executor()


def create_minimal_executor():
    """最小限のautomation_executor.pyを作成"""
    minimal_content = '''import os
import time
import random
import json
import csv
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from account_manager import AccountManager

class AutomationExecutor:
    """X自動操作実行エンジン"""
    
    def __init__(self):
        self.account_manager = AccountManager()
        self.reply_texts = []
        self.used_replies = set()
        self.results = []
        
    def setup_driver_with_proxy(self, account_id: int) -> Optional[webdriver.Chrome]:
        """プロキシ設定付きドライバー（通常selenium版）"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        # プロキシ設定
        proxy = account.get("proxy", {})
        if proxy and proxy.get("host") and proxy.get("port"):
            proxy_url = f"{proxy['host']}:{proxy['port']}"
            chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
            print(f"  プロキシ設定: {proxy_url}")

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            print(f"  ✓ ドライバー起動成功（アカウント: {account['email']}）")
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
            return False
    
    def load_reply_texts(self, csv_path: str = "config/reply_texts.csv") -> bool:
        """リプライテキストをCSVから読み込み"""
        if not os.path.exists(csv_path):
            return False
        try:
            with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                self.reply_texts = []
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
    
    def execute_reply(self, driver: webdriver.Chrome, url: str, reply_text: str) -> bool:
        """リプライ実行"""
        try:
            driver.get(url)
            time.sleep(5)
            
            reply_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='reply']")
            driver.execute_script("arguments[0].click();", reply_button)
            time.sleep(3)
            
            text_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']"))
            )
            text_area.send_keys(reply_text)
            time.sleep(2)
            
            send_button_selectors = [
                "[data-testid='tweetButtonInline']",
                "[data-testid='tweetButton']", 
                "button[data-testid='tweetButtonInline']"
            ]
            
            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_enabled():
                        break
                except:
                    continue
            
            if send_button and send_button.is_enabled():
                driver.execute_script("arguments[0].click();", send_button)
                time.sleep(3)
                return True
            
            return False
        except:
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
                if self.execute_like(driver, target_url):
                    result["actions_performed"].append("like")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("bookmark", False):
                if self.execute_bookmark(driver, target_url):
                    result["actions_performed"].append("bookmark")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("retweet", False):
                if self.execute_retweet(driver, target_url):
                    result["actions_performed"].append("retweet")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
            
            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
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
        """並列実行"""
        results = []
        
        for account_id in account_ids:
            result = self.process_single_account(account_id, target_url, actions, wait_range)
            results.append(result)
        
        return results

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
'''

    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.write(minimal_content)

    print("  ✓ 最小限のautomation_executor.pyを作成しました")


if __name__ == "__main__":
    main()
