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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from login_manager import LoginManager
from account_manager import AccountManager

class AutomationExecutor:
    """X(Twitter)の自動操作を実行するクラス（プロキシ認証対応版）"""
    
    def __init__(self):
        self.login_manager = LoginManager()
        self.account_manager = AccountManager()
        self.reply_texts = []
        self.used_replies = set()
        self.results = []
        
    def handle_proxy_auth(self, driver: webdriver.Chrome, account_id: int) -> bool:
        """プロキシ認証ダイアログを処理"""
        try:
            # アカウント情報を取得
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                return False
            
            proxy_username = account['proxy']['username']
            proxy_password = account['proxy']['password']
            
            # アラート（認証ダイアログ）の存在を確認
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = Alert(driver)
                
                # 認証情報を送信（Selenium 4の場合）
                alert.send_keys(proxy_username)
                alert.send_keys(Keys.TAB)
                alert.send_keys(proxy_password)
                alert.accept()
                
                print(f"  ✓ プロキシ認証を入力しました")
                return True
                
            except TimeoutException:
                # アラートがない場合は、別の方法を試す
                pass
            
            # 代替方法：JavaScriptで認証情報を設定
            auth_script = f"""
            var username = '{proxy_username}';
            var password = '{proxy_password}';
            window.location.href = 'http://' + username + ':' + password + '@' + window.location.host + window.location.pathname;
            """
            
            try:
                driver.execute_script(auth_script)
                time.sleep(2)
                return True
            except:
                pass
                
            return False
            
        except Exception as e:
            print(f"  ⚠ プロキシ認証処理エラー: {e}")
            return False
    
    def setup_driver_with_auth(self, account_id: int) -> Optional[webdriver.Chrome]:
        """認証付きでドライバーをセットアップ"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        # プロキシ情報を取得
        proxy_host = account['proxy']['host']
        proxy_port = account['proxy']['port']
        proxy_username = account['proxy']['username']
        proxy_password = account['proxy']['password']
        
        # 認証付きプロキシURLを構築
        proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
        
        # Chrome拡張機能でプロキシ認証を処理
        from selenium.webdriver.chrome.options import Options
        import zipfile
        
        # プロキシ認証用の拡張機能を作成
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = f"""
        var config = {{
                mode: "fixed_servers",
                rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                }},
                bypassList: ["localhost"]
                }}
            }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_username}",
                    password: "{proxy_password}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {{urls: ["<all_urls>"]}},
                    ['blocking']
        );
        """
        
        # 拡張機能のディレクトリを作成
        import tempfile
        extension_dir = tempfile.mkdtemp()
        
        # ファイルを作成
        with open(os.path.join(extension_dir, "manifest.json"), 'w') as f:
            f.write(manifest_json)
        
        with open(os.path.join(extension_dir, "background.js"), 'w') as f:
            f.write(background_js)
        
        # ZIPファイルを作成
        extension_path = os.path.join(extension_dir, "proxy_auth.zip")
        with zipfile.ZipFile(extension_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        
        # Chromeオプションを設定
        chrome_options = Options()
        chrome_options.add_extension(extension_path)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            # undetected-chromedriverを使用
            import undetected_chromedriver as uc
            driver = uc.Chrome(options=chrome_options, version_main=None)
            driver.implicitly_wait(10)
            
            print(f"  ✓ プロキシ認証付きドライバーを起動しました")
            return driver
            
        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {e}")
            
            # 通常のSeleniumで再試行
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.implicitly_wait(10)
                
                return driver
            except:
                return None
    
    def load_reply_texts(self, csv_path: str = "config/reply_texts.csv") -> bool:
        """リプライテキストをCSVから読み込み"""
        if not os.path.exists(csv_path):
            print(f"⚠ リプライテキストファイルが見つかりません: {csv_path}")
            return False
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.reply_texts = []
                for row in reader:
                    if 'リプライテキスト' in row:
                        self.reply_texts.append(row['リプライテキスト'])
            
            print(f"✓ {len(self.reply_texts)}件のリプライテキストを読み込みました")
            return True
        except Exception as e:
            print(f"✗ リプライテキスト読み込みエラー: {e}")
            return False
    
    def get_random_reply(self) -> Optional[str]:
        """未使用のランダムなリプライテキストを取得"""
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
        """ランダムな待機時間"""
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)
    
    def human_like_action(self):
        """人間らしい動作のための短い待機"""
        time.sleep(random.uniform(0.5, 1.5))
    
    def execute_like(self, driver: webdriver.Chrome, url: str) -> bool:
        """いいねを実行"""
        try:
            driver.get(url)
            self.human_like_action()
            
            like_selectors = [
                "//div[@data-testid='like']",
                "//div[@data-testid='unlike']",
                "//button[contains(@aria-label, 'Like')]",
                "//div[@role='button' and contains(@aria-label, 'いいね')]"
            ]
            
            for selector in like_selectors:
                try:
                    like_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    aria_label = like_button.get_attribute("aria-label") or ""
                    if "unlike" in aria_label.lower() or "いいね済み" in aria_label:
                        print("  → 既にいいね済み")
                        return True
                    
                    like_button.click()
                    self.human_like_action()
                    print("  ✓ いいね完了")
                    return True
                except:
                    continue
            
            print("  ✗ いいねボタンが見つかりません")
            return False
            
        except Exception as e:
            print(f"  ✗ いいねエラー: {str(e)[:50]}")
            return False
    
    def execute_bookmark(self, driver: webdriver.Chrome, url: str) -> bool:
        """ブックマークを実行"""
        try:
            driver.get(url)
            self.human_like_action()
            
            bookmark_selectors = [
                "//div[@data-testid='bookmark']",
                "//div[@data-testid='removeBookmark']",
                "//button[contains(@aria-label, 'Bookmark')]",
                "//div[@role='button' and contains(@aria-label, 'ブックマーク')]"
            ]
            
            for selector in bookmark_selectors:
                try:
                    bookmark_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    aria_label = bookmark_button.get_attribute("aria-label") or ""
                    if "remove" in aria_label.lower() or "削除" in aria_label:
                        print("  → 既にブックマーク済み")
                        return True
                    
                    bookmark_button.click()
                    self.human_like_action()
                    print("  ✓ ブックマーク完了")
                    return True
                except:
                    continue
            
            print("  ✗ ブックマークボタンが見つかりません")
            return False
            
        except Exception as e:
            print(f"  ✗ ブックマークエラー: {str(e)[:50]}")
            return False
    
    def execute_retweet(self, driver: webdriver.Chrome, url: str) -> bool:
        """リツイートを実行"""
        try:
            driver.get(url)
            self.human_like_action()
            
            retweet_selectors = [
                "//div[@data-testid='retweet']",
                "//div[@data-testid='unretweet']",
                "//button[contains(@aria-label, 'Retweet')]",
                "//div[@role='button' and contains(@aria-label, 'リツイート')]"
            ]
            
            for selector in retweet_selectors:
                try:
                    retweet_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    aria_label = retweet_button.get_attribute("aria-label") or ""
                    if "undo" in aria_label.lower() or "取り消" in aria_label:
                        print("  → 既にリツイート済み")
                        return True
                    
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
            
            print("  ✗ リツイートボタンが見つかりません")
            return False
            
        except Exception as e:
            print(f"  ✗ リツイートエラー: {str(e)[:50]}")
            return False
    
    def execute_reply(self, driver: webdriver.Chrome, url: str, reply_text: str) -> bool:
        """リプライを実行"""
        try:
            driver.get(url)
            self.human_like_action()
            
            reply_selectors = [
                "//div[@data-testid='tweetTextarea_0']",
                "//div[@role='textbox']",
                "//textarea[@placeholder='Post your reply']",
                "//div[contains(@aria-label, '返信')]"
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
                        "//button[@data-testid='tweetButton']",
                        "//button[contains(text(), 'Reply')]",
                        "//button[contains(text(), '返信')]"
                    ]
                    
                    for send_sel in send_selectors:
                        try:
                            send_button = driver.find_element(By.XPATH, send_sel)
                            if send_button.is_enabled():
                                send_button.click()
                                self.human_like_action()
                                print(f"  ✓ リプライ完了: {reply_text[:30]}...")
                                return True
                        except:
                            continue
                    
                except:
                    continue
            
            print("  ✗ リプライ入力欄が見つかりません")
            return False
            
        except Exception as e:
            print(f"  ✗ リプライエラー: {str(e)[:50]}")
            return False
    
    def process_single_account(self, account_id: int, target_url: str, 
                             actions: Dict[str, bool], wait_range: Tuple[int, int]) -> Dict:
        """単一アカウントで操作を実行（プロキシ認証対応）"""
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
            
            # プロキシ認証付きドライバーをセットアップ
            driver = self.setup_driver_with_auth(account_id)
            if not driver:
                # 通常のドライバーで再試行
                proxy_url = self.account_manager.get_proxy_url(account_id)
                driver = self.login_manager.setup_driver(proxy_url=proxy_url, headless=False)
            
            # Cookieを読み込んでログイン
            if not self.login_manager.load_cookies(driver, account_id):
                result["errors"].append("Cookie読み込み失敗")
                print("  ✗ Cookie読み込み失敗 - 初回ログインが必要です")
                return result
            
            # ログイン状態を確認
            if not self.login_manager.check_login_status(driver):
                result["errors"].append("ログイン状態確認失敗")
                print("  ✗ ログイン状態の確認に失敗しました")
                return result
            
            print("  ✓ ログイン成功")
            
            # 各アクションを実行
            if actions.get("like", False):
                print("  実行: いいね")
                if self.execute_like(driver, target_url):
                    result["actions_performed"].append("like")
                    self.random_wait(wait_range[0], wait_range[1])
                else:
                    result["errors"].append("いいね失敗")
            
            if actions.get("bookmark", False):
                print("  実行: ブックマーク")
                if self.execute_bookmark(driver, target_url):
                    result["actions_performed"].append("bookmark")
                    self.random_wait(wait_range[0], wait_range[1])
                else:
                    result["errors"].append("ブックマーク失敗")
            
            if actions.get("retweet", False):
                print("  実行: リツイート")
                if self.execute_retweet(driver, target_url):
                    result["actions_performed"].append("retweet")
                    self.random_wait(wait_range[0], wait_range[1])
                else:
                    result["errors"].append("リツイート失敗")
            
            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
                    print("  実行: リプライ")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
                    else:
                        result["errors"].append("リプライ失敗")
                else:
                    result["errors"].append("リプライテキストがありません")
            
            result["success"] = len(result["actions_performed"]) > 0
            
            if result["success"]:
                print(f"  ✅ 完了: {', '.join(result['actions_performed'])}")
            else:
                print(f"  ⚠️ 一部失敗: {', '.join(result['errors'])}")
            
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
        """複数アカウントで並列実行（キュー方式）"""
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
        """実行結果のサマリーを表示"""
        print(f"\n{'='*60}")
        print(f" 実行結果サマリー")
        print(f"{'='*60}")
        
        total = len(results)
        success = sum(1 for r in results if r.get("success", False))
        failed = total - success
        
        print(f"総アカウント数: {total}")
        print(f"成功: {success}")
        print(f"失敗: {failed}")
        
        action_stats = {}
        for result in results:
            for action in result.get("actions_performed", []):
                action_stats[action] = action_stats.get(action, 0) + 1
        
        if action_stats:
            print(f"\nアクション別実行数:")
            for action, count in action_stats.items():
                print(f"  {action}: {count}件")
        
        if failed > 0:
            print(f"\n失敗したアカウント:")
            for result in results:
                if not result.get("success", False):
                    errors = ", ".join(result.get("errors", ["不明なエラー"]))
                    print(f"  [{result['account_id']}] {result.get('email', 'N/A')}: {errors}")
        
        print(f"{'='*60}")
    
    def save_results(self, results: List[Dict]):
        """実行結果をログファイルに保存"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"execution_{timestamp}.json")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nログファイル: {log_file}")

def create_sample_reply_csv(filepath: str = "config/reply_texts.csv"):
    """サンプルのリプライテキストCSVを生成"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    sample_data = [
        {"リプライテキスト": "素晴らしい投稿ですね！"},
        {"リプライテキスト": "とても参考になりました"},
        {"リプライテキスト": "ありがとうございます"},
        {"リプライテキスト": "勉強になります"},
        {"リプライテキスト": "いいですね！"},
    ]
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["リプライテキスト"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"サンプルリプライCSVを作成しました: {filepath}")
