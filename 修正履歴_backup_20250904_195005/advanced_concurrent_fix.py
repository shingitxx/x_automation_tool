#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高度な同時実行競合回避システム
"""

import os
import random
import time


def main():
    print("=" * 60)
    print(" 高度な同時実行競合回避")
    print("=" * 60)

    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 新しいsetup_driver_with_proxyメソッド（完全競合回避版）
    new_setup_method = '''    def setup_driver_with_proxy(self, account_id: int) -> Optional[webdriver.Chrome]:
        """プロキシ設定付きドライバー（完全競合回避版）"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        import tempfile
        import shutil
        import random
        import time
        
        # 完全に独立したディレクトリ構成
        base_dir = f"chrome_sessions/account_{account_id}"
        timestamp = int(time.time() * 1000)  # ミリ秒タイムスタンプ
        random_id = random.randint(1000, 9999)
        unique_suffix = f"{timestamp}_{random_id}"
        
        user_data_dir = f"{base_dir}/userdata_{unique_suffix}"
        cache_dir = f"{base_dir}/cache_{unique_suffix}"
        temp_dir = f"{base_dir}/temp_{unique_suffix}"
        
        # ディレクトリ作成
        for directory in [user_data_dir, cache_dir, temp_dir]:
            os.makedirs(directory, exist_ok=True)
        
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        
        # 完全に独立したディレクトリ設定
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        chrome_options.add_argument(f'--disk-cache-dir={cache_dir}')
        chrome_options.add_argument(f'--temp-profile={temp_dir}')
        
        # 動的ポート割り当て（競合回避）
        base_port = 9000 + (account_id * 10) + random.randint(0, 9)
        chrome_options.add_argument(f'--remote-debugging-port={base_port}')
        
        # プロセス分離
        chrome_options.add_argument(f'--process-per-site')
        chrome_options.add_argument(f'--site-per-process')
        
        # プロキシ設定
        proxy = account.get("proxy", {})
        if proxy and proxy.get("host") and proxy.get("port"):
            proxy_url = f"{proxy['host']}:{proxy['port']}"
            chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
            print(f"  プロキシ設定: {proxy_url}")
        
        # ドライバー起動の排他制御
        import threading
        if not hasattr(self, '_driver_lock'):
            self._driver_lock = threading.Lock()
        
        with self._driver_lock:
            try:
                # 起動前に短時間待機（スタガード起動）
                wait_time = random.uniform(0.5, 2.0)
                time.sleep(wait_time)
                
                # version_mainを指定してドライバー作成
                driver = uc.Chrome(
                    options=chrome_options,
                    version_main=None,  # 自動検出
                    driver_executable_path=None
                )
                
                driver.implicitly_wait(10)
                print(f"  ✓ ドライバー起動成功（アカウント: {account['email']}, ポート: {base_port}）")
                
                # ドライバー情報を保存（クリーンアップ用）
                if not hasattr(self, '_active_drivers'):
                    self._active_drivers = {}
                self._active_drivers[account_id] = {
                    'driver': driver,
                    'directories': [user_data_dir, cache_dir, temp_dir],
                    'base_dir': base_dir
                }
                
                return driver
                
            except Exception as e:
                error_msg = str(e)
                print(f"  ✗ ドライバー起動エラー（アカウント{account_id}）: {error_msg[:100]}")
                
                # エラー時のクリーンアップ
                try:
                    for directory in [user_data_dir, cache_dir, temp_dir]:
                        if os.path.exists(directory):
                            shutil.rmtree(directory, ignore_errors=True)
                except:
                    pass
                
                return None'''

    # 新しいクリーンアップメソッドを追加
    cleanup_method = '''
    def cleanup_driver(self, account_id: int, driver: webdriver.Chrome):
        """ドライバーと関連ファイルのクリーンアップ"""
        try:
            if driver:
                driver.quit()
        except:
            pass
        
        # 関連ディレクトリのクリーンアップ
        if hasattr(self, '_active_drivers') and account_id in self._active_drivers:
            driver_info = self._active_drivers[account_id]
            import shutil
            
            try:
                # 各ディレクトリを削除
                for directory in driver_info.get('directories', []):
                    if os.path.exists(directory):
                        shutil.rmtree(directory, ignore_errors=True)
                
                # ベースディレクトリが空なら削除
                base_dir = driver_info.get('base_dir', '')
                if os.path.exists(base_dir) and not os.listdir(base_dir):
                    os.rmdir(base_dir)
                    
            except Exception as e:
                print(f"  クリーンアップエラー（アカウント{account_id}）: {str(e)[:50]}")
            
            # 記録から削除
            del self._active_drivers[account_id]'''

    # process_single_accountメソッドの修正（クリーンアップ呼び出し）
    new_process_method = '''    def process_single_account(self, account_id: int, target_url: str, 
                             actions: Dict[str, bool], wait_range: Tuple[int, int]) -> Dict:
        """単一アカウント処理（クリーンアップ強化版）"""
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
            
            # 各操作の実行
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
            # 強化されたクリーンアップ
            if driver:
                self.cleanup_driver(account_id, driver)
                print(f"  ✓ ドライバークリーンアップ完了")
        
        return result'''

    # メソッドの置換
    import re

    # setup_driver_with_proxyの置換
    pattern1 = r"def setup_driver_with_proxy\(self, account_id.*?(?=\n    def|\nclass|\nif __name__|\Z)"
    match1 = re.search(pattern1, content, re.DOTALL)
    if match1:
        content = content.replace(match1.group(0), new_setup_method.strip())
        print("  ✓ setup_driver_with_proxyメソッドを修正しました")

    # process_single_accountの置換
    pattern2 = r"def process_single_account\(self, account_id.*?return result"
    match2 = re.search(pattern2, content, re.DOTALL)
    if match2:
        content = content.replace(
            match2.group(0), new_process_method.strip() + "\n        return result"
        )
        print("  ✓ process_single_accountメソッドを修正しました")

    # cleanup_methodを追加
    # クラス内の最後に追加
    if "class AutomationExecutor:" in content:
        # クラスの最後にメソッドを挿入
        class_end_pattern = r"(class AutomationExecutor:.*?)(\n\ndef create_sample_reply_csv|\nclass |\nif __name__|\Z)"
        match = re.search(class_end_pattern, content, re.DOTALL)
        if match:
            content = content.replace(match.group(1), match.group(1) + cleanup_method)
            print("  ✓ cleanup_driverメソッドを追加しました")

    # chrome_sessionsディレクトリ作成
    os.makedirs("chrome_sessions", exist_ok=True)
    print("  ✓ chrome_sessionsディレクトリを作成しました")

    # ファイル保存
    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ ファイル保存完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n高度な改善点:")
    print("✓ タイムスタンプ+ランダムIDによる完全独立ディレクトリ")
    print("✓ 動的ポート割り当て（9000番台使用）")
    print("✓ スタガード起動（0.5-2秒のランダム間隔）")
    print("✓ 排他制御によるドライバー起動管理")
    print("✓ 強化されたクリーンアップシステム")
    print("✓ プロセス分離とキャッシュ分離")
    print("\n4桁アカウント対応:")
    print("• 同時実行数は5-10程度を推奨")
    print("• 各アカウントが完全に独立して動作")
    print("• メモリとディスク使用量に注意")

    print("\n次のテスト:")
    print("同時実行数2で再度テストしてください")
    print("py -3.10 cli_interface.py")


if __name__ == "__main__":
    main()
