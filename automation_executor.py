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
from account_manager import AccountManager
from profile_manager import ProfileManager
import threading
from queue import Queue


class AutomationExecutor:
    """X自動操作実行エンジン（安定版・逐次処理）"""

    def __init__(self):
        self.startup_event = threading.Event()  # 起動完了通知用
        self.account_manager = AccountManager()
        self.profile_manager = ProfileManager()
        self.reply_texts = []
        self.used_replies = set()
        self.results = []

    def setup_driver_with_profile(self, account_id: int) -> Optional[webdriver.Chrome]:
        """プロファイル付きドライバーセットアップ（プロキシなし版）"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            print(f"  ✗ アカウントが見つかりません")
            return None

        # プロファイル存在確認
        if not self.profile_manager.profile_exists(account["email"]):
            print(f"  ⚠ プロファイルが存在しません。先にログインしてください。")
            return None

        try:
            # プロキシを一旦無効化してテスト
            proxy_url = self.account_manager.get_proxy_url(account_id)
            driver = self.profile_manager.create_driver_with_profile(
                account["email"],
                proxy_url=proxy_url,  # プロキシを有効化
                use_temp=False,
            )

            if not driver:
                print(f"  ✗ ドライバー起動失敗")
                return None

            return driver

        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            return None

    def check_login_status(self, driver: webdriver.Chrome) -> bool:
        """ログイン状態確認（改良版）"""
        try:
            driver.get("https://x.com/home")
            time.sleep(5)

            # ログインボタンが表示されていたら未ログイン
            try:
                login_button = driver.find_element(
                    By.XPATH, "//a[@href='/login']//span[text()='ログイン']"
                )
                if login_button:
                    return False  # 未ログイン
            except:
                pass

            # アカウント作成ボタンが表示されていたら未ログイン
            try:
                create_button = driver.find_element(
                    By.XPATH, "//span[text()='アカウント作成']"
                )
                if create_button:
                    return False  # 未ログイン
            except:
                pass

            # タイムラインが表示されているか確認
            try:
                timeline = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-testid='primaryColumn']")
                    )
                )
                if timeline:
                    return True  # ログイン済み
            except:
                pass

            return False  # デフォルトは未ログイン
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

    def wait_for_page_load(self, driver: webdriver.Chrome, timeout: int = 30) -> bool:
        """ページの完全読み込みを待機"""
        try:
            # JavaScriptの読み込み完了を確認
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # X(Twitter)の主要要素の読み込みを確認
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )

            # 動的コンテンツの安定化待機
            time.sleep(3)

            print("    ✓ ページ読み込み完了")
            return True

        except TimeoutException:
            print("    ⚠ ページ読み込みタイムアウト")
            return False
        except Exception as e:
            print(f"    ⚠ ページ読み込みエラー: {str(e)[:50]}")
            return False

    def execute_like(self, driver: webdriver.Chrome, url: str) -> bool:
        """いいね実行"""
        try:
            if url not in driver.current_url:
                driver.get(url)
                # ページ完全読み込み待機を追加
                if not self.wait_for_page_load(driver):
                    return False

            # 既にいいね済みチェック
            try:
                unlike_button = driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='unlike']"
                )
                print("    → 既にいいね済み")
                return True
            except:
                pass

            # いいねボタンクリック
            like_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='like']")
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", like_button
            )
            time.sleep(1)
            driver.execute_script("arguments[0].click();", like_button)
            time.sleep(2)
            return True

        except Exception as e:
            print(f"    ✗ いいねエラー: {str(e)[:50]}")
            return False

    def execute_bookmark(self, driver: webdriver.Chrome, url: str) -> bool:
        """ブックマーク実行（検証付き）"""
        try:
            if url not in driver.current_url:
                driver.get(url)
                if not self.wait_for_page_load(driver):
                    return False

            # 既にブックマーク済みチェック
            try:
                remove_bookmark = driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='removeBookmark']"
                )
                print("    → 既にブックマーク済み")
                return True
            except:
                pass

            bookmark_button = driver.find_element(
                By.CSS_SELECTOR, "[data-testid='bookmark']"
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", bookmark_button
            )
            time.sleep(1)
            driver.execute_script("arguments[0].click();", bookmark_button)
            time.sleep(3)

            # ログインモーダルが出たか確認
            if "login" in driver.current_url or "flow/login" in driver.current_url:
                print("    ✗ 未ログイン（ログイン画面にリダイレクト）")
                return False

            # ブックマークが成功したか確認（removeBookmark に変わったか）
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-testid='removeBookmark']")
                    )
                )
                return True
            except:
                print("    ✗ ブックマーク失敗（状態変化なし）")
                return False

        except Exception as e:
            print(f"    ✗ ブックマークエラー: {str(e)[:50]}")
            return False

    def execute_retweet(self, driver: webdriver.Chrome, url: str) -> bool:
        """リツイート実行"""
        try:
            if url not in driver.current_url:
                driver.get(url)
                # ページ完全読み込み待機を追加
                if not self.wait_for_page_load(driver):
                    return False

            # 既にリツイート済みチェック
            try:
                unretweet = driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='unretweet']"
                )
                print("    → 既にリツイート済み")
                return True
            except:
                pass

            retweet_button = driver.find_element(
                By.CSS_SELECTOR, "[data-testid='retweet']"
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", retweet_button
            )
            time.sleep(1)
            driver.execute_script("arguments[0].click();", retweet_button)
            time.sleep(2)

            # 確認ダイアログ処理
            try:
                confirm_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "[data-testid='retweetConfirm']")
                    )
                )
                driver.execute_script("arguments[0].click();", confirm_button)
                time.sleep(2)
            except:
                pass

            return True

        except Exception as e:
            print(f"    ✗ リツイートエラー: {str(e)[:50]}")
            return False

    def execute_reply(
        self, driver: webdriver.Chrome, url: str, reply_text: str
    ) -> bool:
        """リプライ実行"""
        try:
            if url not in driver.current_url:
                driver.get(url)
                # ページ完全読み込み待機を追加
                if not self.wait_for_page_load(driver):
                    return False

            # リプライボタンクリック
            reply_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='reply']")
            driver.execute_script("arguments[0].click();", reply_button)
            time.sleep(3)

            # テキスト入力
            text_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']")
                )
            )
            text_area.send_keys(reply_text)
            time.sleep(2)

            # 送信ボタン
            send_button_selectors = [
                "[data-testid='tweetButtonInline']",
                "[data-testid='tweetButton']",
            ]

            for selector in send_button_selectors:
                try:
                    send_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_enabled():
                        driver.execute_script("arguments[0].click();", send_button)
                        time.sleep(3)
                        return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"    ✗ リプライエラー: {str(e)[:50]}")
            return False

    def process_single_account(
        self,
        account_id: int,
        target_url: str,
        actions: Dict[str, bool],
        wait_range: Tuple[int, int],
    ) -> Dict:
        """単一アカウント処理（自動再ログイン機能付き）"""
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

            # X.comにアクセス
            driver.get("https://x.com/home")
            time.sleep(5)

            # Cloudflare手動解除処理
            try:
                from cloudflare_handler import CloudflareHandler

                if not CloudflareHandler.check_and_handle_cloudflare(driver):
                    result["errors"].append("Cloudflare解除タイムアウト")
                    return result
            except ImportError:
                # cloudflare_handler.pyがない場合はスキップ
                pass

            # ログイン状態確認と自動再ログイン
            login_required = False

            # ログインボタンの存在確認
            try:
                login_button = driver.find_element(
                    By.XPATH, "//a[@href='/login']//span[text()='ログイン']"
                )
                if login_button:
                    login_required = True
            except:
                pass

            # アカウント作成ボタンの存在確認
            if not login_required:
                try:
                    create_button = driver.find_element(
                        By.XPATH, "//span[text()='アカウント作成']"
                    )
                    if create_button:
                        login_required = True
                except:
                    pass

            # ログインが必要な場合
            if login_required:
                print(f"  → セッションが切れています。再ログインします...")

                # ログインページへ移動
                driver.get("https://x.com/login")
                time.sleep(3)

                # Cloudflareチェック
                try:
                    from cloudflare_handler import CloudflareHandler

                    if not CloudflareHandler.check_and_handle_cloudflare(driver):
                        result["errors"].append("Cloudflare解除タイムアウト")
                        return result
                except ImportError:
                    pass

                try:
                    # ユーザー名入力
                    username_input = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "input[autocomplete='username']")
                        )
                    )
                    username_input.clear()
                    username_input.send_keys(account["email"])
                    time.sleep(2)

                    # 次へボタン
                    next_button = driver.find_element(
                        By.XPATH, "//span[text()='次へ']/.."
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)

                    # パスワード入力
                    password_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "input[type='password']")
                        )
                    )
                    password_input.clear()
                    password_input.send_keys(account["password"])
                    time.sleep(2)

                    # ログインボタン
                    login_button = driver.find_element(
                        By.XPATH, "//span[text()='ログイン']/.."
                    )
                    driver.execute_script("arguments[0].click();", login_button)
                    time.sleep(5)

                    # 二段階認証のチェック
                    try:
                        auth_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "input[name='text']")
                            )
                        )
                        print(f"  → 二段階認証を検出")

                        secret_key = account.get("secret_key", "").strip()
                        if secret_key:
                            try:
                                import pyotp

                                totp = pyotp.TOTP(secret_key)
                                auth_code = totp.now()

                                print(f"  → 認証コード自動生成: {auth_code}")
                                auth_input.clear()
                                auth_input.send_keys(auth_code)
                                time.sleep(2)

                                next_button = driver.find_element(
                                    By.XPATH, "//span[text()='次へ']/.."
                                )
                                driver.execute_script(
                                    "arguments[0].click();", next_button
                                )
                                time.sleep(5)

                                print(f"  ✓ 二段階認証完了")
                            except:
                                print(f"  ⚠ 手動で認証コードを入力してください")
                                input("  認証完了後、Enterキーを押してください...")
                        else:
                            print(f"  ⚠ 手動で認証コードを入力してください")
                            input("  認証完了後、Enterキーを押してください...")

                    except TimeoutException:
                        pass  # 二段階認証なし

                    # ホームに戻る
                    time.sleep(5)
                    driver.get("https://x.com/home")
                    time.sleep(5)

                    # ログイン成功確認
                    if "home" in driver.current_url.lower():
                        print(f"  ✓ 再ログイン成功")
                    else:
                        print(f"  ✗ 再ログイン失敗")
                        result["errors"].append("再ログイン失敗")
                        return result

                except Exception as e:
                    print(f"  ✗ 再ログインエラー: {str(e)[:100]}")
                    result["errors"].append(f"再ログインエラー: {str(e)[:100]}")
                    return result
            else:
                print("  ✓ ログイン確認完了")

            # 各アクション実行
            if actions.get("like", False):
                print("  実行: いいね")
                if self.execute_like(driver, target_url):
                    result["actions_performed"].append("like")
                    print("    ✓ いいね完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
                else:
                    result["errors"].append("いいね失敗")

            if actions.get("bookmark", False):
                print("  実行: ブックマーク")
                if self.execute_bookmark(driver, target_url):
                    result["actions_performed"].append("bookmark")
                    print("    ✓ ブックマーク完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
                else:
                    result["errors"].append("ブックマーク失敗")

            if actions.get("retweet", False):
                print("  実行: リツイート")
                if self.execute_retweet(driver, target_url):
                    result["actions_performed"].append("retweet")
                    print("    ✓ リツイート完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
                else:
                    result["errors"].append("リツイート失敗")

            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
                    print(f"  実行: リプライ「{reply_text[:20]}...」")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
                        print("    ✓ リプライ完了")
                    else:
                        result["errors"].append("リプライ失敗")

            result["success"] = len(result["actions_performed"]) > 0

            if result["success"]:
                print(f"  ✅ 完了: {', '.join(result['actions_performed'])}")
            else:
                print(f"  ⚠ アクションが実行されませんでした")

        except Exception as e:
            result["errors"].append(f"実行エラー: {str(e)[:100]}")
            print(f"  ✗ エラー: {str(e)[:50]}")

        finally:
            if driver:
                try:
                    self.profile_manager.close_driver(driver)
                    time.sleep(2)  # ドライバー完全終了を待つ
                except:
                    pass

        return result

    def execute_sequential(
        self,
        account_ids: List[int],
        target_url: str,
        actions: Dict[str, bool],
        wait_range: Tuple[int, int],
    ) -> List[Dict]:
        """逐次実行（安定版）"""
        results = []
        total_accounts = len(account_ids)

        print(f"\n{'='*60}")
        print(f" 自動操作実行（逐次処理版）")
        print(f"{'='*60}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"アカウント数: {total_accounts}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print(f"{'='*60}")

        # プロファイル存在チェック
        for i, account_id in enumerate(account_ids, 1):
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                continue

            if not self.profile_manager.profile_exists(account["email"]):
                print(f"⚠ [{account_id}] {account['email']}: プロファイルがありません")
                continue

            # 単一アカウント処理
            result = self.process_single_account(
                account_id, target_url, actions, wait_range
            )
            results.append(result)

            status = "成功" if result.get("success", False) else "失敗"
            print(f"\n進捗: {i}/{total_accounts} - [{account_id}] {status}")

            # 次のアカウントまでの間隔（最後以外）
            if i < total_accounts:
                interval = random.uniform(3, 5)
                print(f"次のアカウントまで {interval:.1f} 秒待機...")
                time.sleep(interval)

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

    def execute_parallel(
        self,
        account_ids: List[int],
        target_url: str,
        actions: Dict[str, bool],
        wait_range: Tuple[int, int],
        max_workers: int = 3,
    ) -> List[Dict]:
        """並列実行（複数アカウント同時処理）"""
        results = []
        total_accounts = len(account_ids)

        print(f"\n{'='*60}")
        print(f" 自動操作実行（並列処理版）")
        print(f"{'='*60}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"アカウント数: {total_accounts}")
        print(f"同時実行数: {max_workers}")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print(f"{'='*60}")

        # プロファイル存在チェック
        valid_accounts = []
        for account_id in account_ids:
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                continue
            if not self.profile_manager.profile_exists(account["email"]):
                print(f"⚠ [{account_id}] {account['email']}: プロファイルがありません")
                continue
            valid_accounts.append(account_id)

        if not valid_accounts:
            print("実行可能なアカウントがありません")
            return results

        # バッチ処理
        for i in range(0, len(valid_accounts), max_workers):
            batch = valid_accounts[i : i + max_workers]
            batch_num = (i // max_workers) + 1
            total_batches = (len(valid_accounts) + max_workers - 1) // max_workers

            print(f"\nバッチ {batch_num}/{total_batches} 処理開始")
            print(f"アカウント: {batch}")

            # スレッドプールで並列実行（段階的起動）
            threads = []
            batch_results = []
            result_queue = Queue()

            for idx, account_id in enumerate(batch):
                thread = threading.Thread(
                    target=self._thread_worker,
                    args=(
                        account_id,
                        target_url,
                        actions,
                        wait_range,
                        result_queue,
                        idx,
                    ),
                )
                threads.append(thread)
                thread.start()

            # 全スレッド完了待機
            for thread in threads:
                thread.join()

            # 結果収集
            while not result_queue.empty():
                batch_results.append(result_queue.get())

            results.extend(batch_results)

            # 次のバッチまでの間隔
            if i + max_workers < len(valid_accounts):
                interval = random.uniform(5, 10)
                print(f"\n次のバッチまで {interval:.1f} 秒待機...")
                time.sleep(interval)

        self.print_summary(results)
        self.save_results(results)
        return results

    def _thread_worker(
        self,
        account_id: int,
        target_url: str,
        actions: Dict[str, bool],
        wait_range: Tuple[int, int],
        result_queue: Queue,
        batch_index: int = 0,
    ):
        """スレッドワーカー（並列実行用）"""

        # 2番目以降は前のアカウントの起動完了を待つ
        if batch_index > 0:
            print(f"[{account_id}] 前のアカウントの起動完了待機中...")
            if not hasattr(self, "startup_events"):
                self.startup_events = {}

            while batch_index - 1 not in self.startup_events:
                time.sleep(0.5)

            self.startup_events[batch_index - 1].wait()
            print(f"[{account_id}] 起動開始")

        # 自分用のイベントを作成
        if not hasattr(self, "startup_events"):
            self.startup_events = {}
        self.startup_events[batch_index] = threading.Event()

        # ドライバー起動部分だけを先に実行
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            result = {
                "account_id": account_id,
                "email": "",
                "url": target_url,
                "success": False,
                "actions_performed": [],
                "errors": ["アカウントが見つかりません"],
                "timestamp": datetime.now().isoformat(),
            }
            self.startup_events[batch_index].set()  # エラーでも通知
            result_queue.put(result)
            return

        print(f"[{account_id}] {account['email']} - 処理開始")

        # ドライバー起動
        driver = self.setup_driver_with_profile(account_id)

        # 起動完了したら即座に次のアカウントに通知
        if driver:
            print(f"[{account_id}] 起動完了 → 次のアカウントへ通知")
            self.startup_events[batch_index].set()

            # 以降のタスクは並列で実行
            result = self._execute_tasks(
                driver, account, account_id, target_url, actions, wait_range
            )
        else:
            # 起動失敗でも通知（無限待機防止）
            self.startup_events[batch_index].set()
            result = {
                "account_id": account_id,
                "email": account["email"],
                "url": target_url,
                "success": False,
                "actions_performed": [],
                "errors": ["ドライバー起動失敗"],
                "timestamp": datetime.now().isoformat(),
            }

        result_queue.put(result)

    def execute_like(self, driver: webdriver.Chrome, url: str) -> bool:
        """いいね実行（検証付き）"""
        try:
            if url not in driver.current_url:
                driver.get(url)
                if not self.wait_for_page_load(driver):
                    return False

            # 既にいいね済みチェック
            try:
                unlike_button = driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='unlike']"
                )
                print("    → 既にいいね済み")
                return True
            except:
                pass

            # いいねボタンクリック
            like_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='like']")
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", like_button
            )
            time.sleep(1)
            driver.execute_script("arguments[0].click();", like_button)
            time.sleep(3)

            # ログインモーダルが出たか確認
            if "login" in driver.current_url or "flow/login" in driver.current_url:
                print("    ✗ 未ログイン（ログイン画面にリダイレクト）")
                return False

            # いいねが成功したか確認（unlike に変わったか）
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-testid='unlike']")
                    )
                )
                return True
            except:
                print("    ✗ いいね失敗（状態変化なし）")
                return False

        except Exception as e:
            print(f"    ✗ いいねエラー: {str(e)[:50]}")
            return False

    def _execute_tasks(
        self,
        driver: webdriver.Chrome,
        account: Dict,
        account_id: int,
        target_url: str,
        actions: Dict[str, bool],
        wait_range: Tuple[int, int],
    ) -> Dict:
        """タスク実行部分（自動再ログイン機能付き）"""
        result = {
            "account_id": account_id,
            "email": account["email"],
            "url": target_url,
            "success": False,
            "actions_performed": [],
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # ホームページでログイン状態を確認
            driver.get("https://x.com/home")

            # ページ遷移完了を待機（最大30秒）
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # 追加の安定待機

            # URLをチェック - ログインページにリダイレクトされたか
            current_url = driver.current_url
            if "login" in current_url or "flow/login" in current_url:
                print(f"[{account_id}] → 未ログイン検出。ログインします...")

                try:
                    # ユーザー名入力
                    username_input = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "input[autocomplete='username']")
                        )
                    )
                    username_input.clear()
                    username_input.send_keys(account["email"])
                    time.sleep(2)

                    # 次へボタン
                    next_button = driver.find_element(
                        By.XPATH, "//span[text()='次へ']/.."
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)

                    # パスワード入力
                    password_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "input[type='password']")
                        )
                    )
                    password_input.clear()
                    password_input.send_keys(account["password"])
                    time.sleep(2)

                    # ログインボタン
                    login_button = driver.find_element(
                        By.XPATH, "//span[text()='ログイン']/.."
                    )
                    driver.execute_script("arguments[0].click();", login_button)
                    time.sleep(5)

                    # 二段階認証のチェック
                    try:
                        auth_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "input[name='text']")
                            )
                        )
                        print(f"[{account_id}] → 二段階認証を検出")

                        secret_key = account.get("secret_key", "").strip()
                        if secret_key:
                            try:
                                import pyotp

                                totp = pyotp.TOTP(secret_key)
                                auth_code = totp.now()

                                print(
                                    f"[{account_id}] → 認証コード自動生成: {auth_code}"
                                )
                                auth_input.clear()
                                auth_input.send_keys(auth_code)
                                time.sleep(2)

                                next_button = driver.find_element(
                                    By.XPATH, "//span[text()='次へ']/.."
                                )
                                driver.execute_script(
                                    "arguments[0].click();", next_button
                                )
                                time.sleep(5)

                                print(f"[{account_id}] ✓ 二段階認証完了")
                            except:
                                print(
                                    f"[{account_id}] ⚠ 手動で認証コードを入力してください"
                                )
                                input("  認証完了後、Enterキーを押してください...")
                        else:
                            print(
                                f"[{account_id}] ⚠ 手動で認証コードを入力してください"
                            )
                            input("  認証完了後、Enterキーを押してください...")

                    except TimeoutException:
                        pass  # 二段階認証なし

                    # ログイン完了を待機
                    WebDriverWait(driver, 30).until(
                        lambda d: "home" in d.current_url.lower()
                        and "login" not in d.current_url.lower()
                    )

                    print(f"[{account_id}] ✓ ログイン成功")

                except Exception as e:
                    print(f"[{account_id}] ✗ ログインエラー: {str(e)[:100]}")
                    result["errors"].append(f"ログインエラー: {str(e)[:100]}")
                    return result
            else:
                print(f"[{account_id}] ✓ ログイン確認完了")

            # 各アクション実行
            if actions.get("like", False):
                print(f"[{account_id}] 実行: いいね")
                if self.execute_like(driver, target_url):
                    result["actions_performed"].append("like")
                    print(f"[{account_id}] ✓ いいね完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))

            if actions.get("bookmark", False):
                print(f"[{account_id}] 実行: ブックマーク")
                if self.execute_bookmark(driver, target_url):
                    result["actions_performed"].append("bookmark")
                    print(f"[{account_id}] ✓ ブックマーク完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))

            if actions.get("retweet", False):
                print(f"[{account_id}] 実行: リツイート")
                if self.execute_retweet(driver, target_url):
                    result["actions_performed"].append("retweet")
                    print(f"[{account_id}] ✓ リツイート完了")
                    time.sleep(random.uniform(wait_range[0], wait_range[1]))

            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
                    print(f"[{account_id}] 実行: リプライ")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
                        print(f"[{account_id}] ✓ リプライ完了")

            result["success"] = len(result["actions_performed"]) > 0

            if result["success"]:
                print(
                    f"[{account_id}] ✅ 完了: {', '.join(result['actions_performed'])}"
                )

        except Exception as e:
            result["errors"].append(f"実行エラー: {str(e)[:100]}")
            print(f"[{account_id}] ✗ エラー: {str(e)[:50]}")

        finally:
            self.profile_manager.close_driver(driver)
            time.sleep(2)

        return result
