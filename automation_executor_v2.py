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
from concurrent.futures import ThreadPoolExecutor, as_completed
from account_manager import AccountManager
from profile_manager import ProfileManager
import threading


class AutomationExecutorV2:
    """X自動操作実行エンジン（プロファイル対応版）"""

    def __init__(self):
        self.account_manager = AccountManager()
        self.profile_manager = ProfileManager()
        self.reply_texts = []
        self.used_replies = set()
        self.results = []
        self.driver_lock = threading.Lock()

    def setup_driver_with_profile(self, account_id: int) -> Optional[webdriver.Chrome]:
        """プロファイル付きドライバーセットアップ"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None

        # プロファイル存在確認
        if not self.profile_manager.profile_exists(account["email"]):
            print(f"  ⚠ プロファイルが存在しません。先にログインしてください。")
            return None

        try:
            proxy_url = self.account_manager.get_proxy_url(account_id)

            # プロファイル付きドライバー作成
            with self.driver_lock:
                driver = self.profile_manager.create_driver_with_profile(
                    account["email"],
                    proxy_url=proxy_url,
                    use_temp=False,  # 永続プロファイル使用
                )

            if not driver:
                print(f"  ✗ ドライバー起動失敗")
                return None

            return driver

        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            return None

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
            with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    text = row.get("リプライテキスト", "").strip()
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
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", like_button
            )
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

            bookmark_button = driver.find_element(
                By.CSS_SELECTOR, "[data-testid='bookmark']"
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", bookmark_button
            )
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

            retweet_button = driver.find_element(
                By.CSS_SELECTOR, "[data-testid='retweet']"
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", retweet_button
            )
            time.sleep(1)
            driver.execute_script("arguments[0].click();", retweet_button)
            time.sleep(2)

            try:
                confirm_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "[data-testid='retweetConfirm']")
                    )
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

    def execute_reply(
        self, driver: webdriver.Chrome, url: str, reply_text: str
    ) -> bool:
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
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']")
                )
            )
            text_area.send_keys(reply_text)
            time.sleep(2)

            # 送信ボタン（複数セレクタ対応）
            send_button_selectors = [
                "[data-testid='tweetButtonInline']",
                "[data-testid='tweetButton']",
                "button[data-testid='tweetButtonInline']",
                "div[data-testid='tweetButtonInline']",
                "[role='button'][data-testid='tweetButtonInline']",
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

    def process_single_account(
        self,
        account_id: int,
        target_url: str,
        actions: Dict[str, bool],
        wait_range: Tuple[int, int],
    ) -> Dict:
        """単一アカウント処理（プロファイル対応）"""
        result = {
            "account_id": account_id,
            "email": "",
            "url": target_url,
            "success": False,
            "actions_performed": [],
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }

        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            result["errors"].append("アカウントが見つかりません")
            return result

        result["email"] = account["email"]
        driver = None

        try:
            print(f"\n[{account_id}] {account['email']} - 処理開始")

            # プロファイル付きドライバー起動
            driver = self.setup_driver_with_profile(account_id)
            if not driver:
                result["errors"].append("ドライバー起動失敗")
                return result

            # ログイン状態確認（プロファイル使用のため通常はログイン済み）
            if not self.check_login_status(driver):
                result["errors"].append("ログイン状態確認失敗")
                return result

            print("  ✓ ログイン確認完了")

            # 各アクション実行
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
                    print(f"  実行: リプライ「{reply_text[:20]}...」")
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

    def execute_parallel(
        self,
        account_ids: List[int],
        target_url: str,
        actions: Dict[str, bool],
        wait_range: Tuple[int, int],
        max_workers: int = 1,
    ) -> List[Dict]:
        """並列実行（プロファイル対応）"""
        results = []
        total_accounts = len(account_ids)

        print(f"\n{'='*60}")
        print(f" 自動操作実行（プロファイル版）")
        print(f"{'='*60}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"アカウント数: {total_accounts}")
        print(f"同時実行数: {max_workers}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print(f"{'='*60}")

        # プロファイル存在チェック
        missing_profiles = []
        for account_id in account_ids:
            account = self.account_manager.get_account_by_id(account_id)
            if account and not self.profile_manager.profile_exists(account["email"]):
                missing_profiles.append(account_id)

        if missing_profiles:
            print(
                f"\n⚠ 以下のアカウントはプロファイルがありません（先にログインしてください）:"
            )
            for account_id in missing_profiles:
                account = self.account_manager.get_account_by_id(account_id)
                if account:
                    print(f"  [{account_id}] {account['email']}")

            # プロファイルがあるアカウントのみ実行
            account_ids = [id for id in account_ids if id not in missing_profiles]
            if not account_ids:
                print("\n実行可能なアカウントがありません。")
                return results

        # 並列実行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_account = {
                executor.submit(
                    self.process_single_account,
                    account_id,
                    target_url,
                    actions,
                    wait_range,
                ): account_id
                for account_id in account_ids
            }

            completed = 0
            for future in as_completed(future_to_account):
                completed += 1
                account_id = future_to_account[future]
                try:
                    result = future.result()
                    results.append(result)

                    status = "成功" if result.get("success", False) else "失敗"
                    print(
                        f"\n進捗: {completed}/{len(account_ids)} 完了 - [{account_id}] {status}"
                    )

                except Exception as e:
                    print(
                        f"\n進捗: {completed}/{len(account_ids)} - [{account_id}] エラー: {str(e)[:50]}"
                    )
                    results.append(
                        {
                            "account_id": account_id,
                            "success": False,
                            "errors": [str(e)[:100]],
                        }
                    )

        self.print_summary(results)
        self.save_results(results)
        return results

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

        # アクション別集計
        action_counts = {}
        for result in results:
            for action in result.get("actions_performed", []):
                action_counts[action] = action_counts.get(action, 0) + 1

        if action_counts:
            print(f"\n実行されたアクション:")
            for action, count in action_counts.items():
                print(f"  {action}: {count}件")

        if failed > 0:
            print(f"\n失敗したアカウント:")
            for result in results:
                if not result.get("success", False):
                    errors = ", ".join(result.get("errors", ["不明なエラー"]))
                    print(
                        f"  [{result['account_id']}] {result.get('email', 'N/A')}: {errors}"
                    )

        print(f"{'='*60}")

    def save_results(self, results: List[Dict]):
        """結果保存"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"execution_{timestamp}.json")

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n実行ログ保存: {log_file}")


def create_sample_reply_csv(filepath: str = "config/reply_texts.csv"):
    """サンプルリプライCSV作成"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    sample_data = [
        {"リプライテキスト": "興味深い内容ですね"},
        {"リプライテキスト": "シェアしてくださってありがとう"},
        {"リプライテキスト": "これは知らなかったです！"},
        {"リプライテキスト": "めちゃくちゃ良いですね"},
        {"リプライテキスト": "最高の投稿です"},
    ]

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["リプライテキスト"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
