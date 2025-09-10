import os
import shutil
import tempfile
import time
import random
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 簡易ファイルロック実装
class SimpleFileLock:
    def __init__(self, path):
        self.path = path

    def acquire(self, timeout=30):
        start = time.time()
        while True:
            try:
                # 原子的に作成できたらロック獲得
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                return
            except FileExistsError:
                if timeout and time.time() - start > timeout:
                    raise TimeoutError(f"ロックタイムアウト: {self.path}")
                time.sleep(0.1)

    def release(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


@contextmanager
def account_lock(account_email: str):
    """アカウント単位の排他ロック"""
    os.makedirs("./profiles_lock", exist_ok=True)
    safe_email = account_email.replace("@", "_at_").replace(".", "_")
    lock = SimpleFileLock(f"./profiles_lock/{safe_email}.lock")
    lock.acquire(timeout=30)
    try:
        yield
    finally:
        lock.release()


def clean_stale_profile_locks(profile_dir: str):
    """前回の残骸ロックファイル削除"""
    for name in [
        "SingletonLock",
        "SingletonCookie",
        "SingletonSocket",
        "SingletonGpuLock",
    ]:
        lock_path = os.path.join(profile_dir, name)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print(f"  ✓ 残骸ロック削除: {name}")
            except:
                pass


def create_isolated_driver(
    account_email: str, profile_path: str, proxy_url: Optional[str] = None
) -> Tuple[webdriver.Chrome, str]:
    """分離環境でのドライバー作成"""
    # プロファイルディレクトリ準備
    os.makedirs(profile_path, exist_ok=True)
    os.makedirs(os.path.join(profile_path, "downloads"), exist_ok=True)

    # 残骸クリーンアップ
    clean_stale_profile_locks(profile_path)

    # 起動ごと固有の一時ディレクトリ
    safe_email = account_email.replace("@", "_at_").replace(".", "_")
    tmp_dir = tempfile.mkdtemp(prefix=f"uc_{safe_email}_")

    # 環境変数を一時的に変更
    old_env = {
        "TMPDIR": os.environ.get("TMPDIR"),
        "TEMP": os.environ.get("TEMP"),
        "TMP": os.environ.get("TMP"),
    }

    os.environ["TMPDIR"] = tmp_dir
    os.environ["TEMP"] = tmp_dir
    os.environ["TMP"] = tmp_dir

    try:
        # Chrome オプション設定
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # ダウンロードディレクトリ設定
        prefs = {"download.default_directory": os.path.join(profile_path, "downloads")}
        options.add_experimental_option("prefs", prefs)

        # プロキシ設定
        if proxy_url:
            if "@" in proxy_url:
                proxy_parts = proxy_url.split("@")
                proxy_server = f"http://{proxy_parts[1]}"
            else:
                proxy_server = proxy_url
            options.add_argument(f"--proxy-server={proxy_server}")
            print(f"  → プロキシ設定: {proxy_server}")

        # port=0 で空きポート自動割り当て
        driver = uc.Chrome(options=options, version_main=139)
        driver.implicitly_wait(10)

        print(f"  ✓ ドライバー起動成功（分離環境）")
        return driver, tmp_dir

    finally:
        # 環境変数を元に戻す
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def process_single_account_isolated(account_data: Dict) -> Dict:
    """単一アカウント処理（プロセス分離版）"""
    result = {
        "account_id": account_data["id"],
        "email": account_data["email"],
        "url": account_data["target_url"],
        "success": False,
        "actions_performed": [],
        "errors": [],
        "timestamp": datetime.now().isoformat(),
    }

    driver = None
    tmp_dir = None

    # アカウント単位で排他ロック
    with account_lock(account_data["email"]):
        try:
            print(f"\n[{account_data['id']}] {account_data['email']} - 処理開始")

            # プロファイルパス
            safe_email = account_data["email"].replace("@", "_at_").replace(".", "_")
            profile_path = os.path.abspath(f"./profiles/profile_{safe_email}")

            # ドライバー作成
            driver, tmp_dir = create_isolated_driver(
                account_data["email"], profile_path, account_data.get("proxy_url")
            )

            # ログイン状態確認
            driver.get("https://x.com/home")
            time.sleep(3)

            if "home" not in driver.current_url.lower():
                result["errors"].append("ログイン状態確認失敗")
                return result

            print("  ✓ ログイン確認完了")

            # 各アクション実行
            actions = account_data["actions"]
            wait_range = account_data["wait_range"]

            # ターゲットURLへ移動
            driver.get(account_data["target_url"])
            time.sleep(5)

            # いいね実行
            if actions.get("like", False):
                print("  実行: いいね")
                try:
                    # 既にいいね済みチェック
                    try:
                        unlike_button = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='unlike']"
                        )
                        print("    → 既にいいね済み")
                        result["actions_performed"].append("like")
                    except:
                        # いいねボタンクリック
                        like_button = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='like']"
                        )
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            like_button,
                        )
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", like_button)
                        result["actions_performed"].append("like")
                        print("    ✓ いいね完了")

                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
                except Exception as e:
                    result["errors"].append(f"いいね失敗: {str(e)[:50]}")

            # ブックマーク実行
            if actions.get("bookmark", False):
                print("  実行: ブックマーク")
                try:
                    # 既にブックマーク済みチェック
                    try:
                        remove_bookmark = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='removeBookmark']"
                        )
                        print("    → 既にブックマーク済み")
                        result["actions_performed"].append("bookmark")
                    except:
                        # ブックマークボタンクリック
                        bookmark_button = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='bookmark']"
                        )
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            bookmark_button,
                        )
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", bookmark_button)
                        result["actions_performed"].append("bookmark")
                        print("    ✓ ブックマーク完了")

                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
                except Exception as e:
                    result["errors"].append(f"ブックマーク失敗: {str(e)[:50]}")

            # リツイート実行
            if actions.get("retweet", False):
                print("  実行: リツイート")
                try:
                    # 既にリツイート済みチェック
                    try:
                        unretweet = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='unretweet']"
                        )
                        print("    → 既にリツイート済み")
                        result["actions_performed"].append("retweet")
                    except:
                        # リツイートボタンクリック
                        retweet_button = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='retweet']"
                        )
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            retweet_button,
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
                            driver.execute_script(
                                "arguments[0].click();", confirm_button
                            )
                        except:
                            pass

                        result["actions_performed"].append("retweet")
                        print("    ✓ リツイート完了")

                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
                except Exception as e:
                    result["errors"].append(f"リツイート失敗: {str(e)[:50]}")

            # リプライ実行
            if actions.get("reply", False) and account_data.get("reply_text"):
                print(f"  実行: リプライ「{account_data['reply_text'][:20]}...」")
                try:
                    # リプライボタンクリック
                    reply_button = driver.find_element(
                        By.CSS_SELECTOR, "[data-testid='reply']"
                    )
                    driver.execute_script("arguments[0].click();", reply_button)
                    time.sleep(3)

                    # テキスト入力
                    text_area = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "[data-testid='tweetTextarea_0']")
                        )
                    )
                    text_area.send_keys(account_data["reply_text"])
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
                                driver.execute_script(
                                    "arguments[0].click();", send_button
                                )
                                result["actions_performed"].append("reply")
                                print("    ✓ リプライ完了")
                                break
                        except:
                            continue

                    time.sleep(random.uniform(wait_range[0], wait_range[1]))
                except Exception as e:
                    result["errors"].append(f"リプライ失敗: {str(e)[:50]}")

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
                    driver.quit()
                    time.sleep(1)
                except:
                    pass

            if tmp_dir and os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                except:
                    pass

    return result


class ParallelExecutor:
    """並列実行エンジン（マルチプロセス版）"""

    def __init__(self):
        pass

    def execute_parallel_tasks(
        self, accounts_data: List[Dict], max_workers: int = 3
    ) -> List[Dict]:
        """並列タスク実行"""
        results = []
        total = len(accounts_data)

        print(f"\n{'='*60}")
        print(f" 並列処理実行（マルチプロセス版）")
        print(f"{'='*60}")
        print(f"総アカウント数: {total}")
        print(f"最大同時実行数: {max_workers}")
        print(f"{'='*60}")

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 起動タイミングをずらしてファイル競合を回避
            futures = []
            for i, account_data in enumerate(accounts_data):
                time.sleep(random.uniform(0.2, 0.5))
                future = executor.submit(process_single_account_isolated, account_data)
                futures.append(future)
                print(f"タスク投入 [{i+1}/{total}]: {account_data['email']}")

            # 結果収集
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=120)
                    results.append(result)
                    status = "成功" if result["success"] else "失敗"
                    print(
                        f"完了: [{result['account_id']}] {result['email']} - {status}"
                    )
                except Exception as e:
                    print(f"タスクエラー: {str(e)[:100]}")

        return results
