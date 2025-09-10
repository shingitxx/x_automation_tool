#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
複数同時実行の確実な実装
"""

import os


def main():
    print("=" * 60)
    print(" 複数同時実行の実装")
    print("=" * 60)

    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    # execute_parallelメソッドを真の並列処理に変更
    old_execute_parallel = '''    def execute_parallel(self, account_ids: List[int], target_url: str,
                        actions: Dict[str, bool], wait_range: Tuple[int, int],
                        max_workers: int = 1) -> List[Dict]:
        """順次実行（プロキシ競合回避）"""
        results = []
        total_accounts = len(account_ids)
        
        print(f"\\n{'='*60}")
        print(f" 自動操作実行")
        print(f"{'='*60}")
        print(f"対象URL: {target_url}")
        print(f"実行操作: {', '.join([k for k, v in actions.items() if v])}")
        print(f"アカウント数: {total_accounts}")
        print(f"処理方式: 順次実行")
        print(f"待機時間: {wait_range[0]}-{wait_range[1]}秒")
        print(f"{'='*60}")
        
        for i, account_id in enumerate(account_ids):
            try:
                result = self.process_single_account(
                    account_id,
                    target_url,
                    actions,
                    wait_range
                )
                results.append(result)
                
                completed = i + 1
                print(f"\\n進捗: {completed}/{total_accounts} 完了")
                
                if i < len(account_ids) - 1:  # 最後でなければ
                    time.sleep(2)  # アカウント間の間隔
                
            except Exception as e:
                print(f"\\n[{account_id}] 実行エラー: {e}")
                results.append({
                    "account_id": account_id,
                    "success": False,
                    "errors": [str(e)]
                })
        
        self.print_summary(results)
        self.save_results(results)
        return results'''

    new_execute_parallel = '''    def execute_parallel(self, account_ids: List[int], target_url: str,
                        actions: Dict[str, bool], wait_range: Tuple[int, int],
                        max_workers: int = 5) -> List[Dict]:
        """真の並列実行（プロファイル分離版）"""
        results = []
        total_accounts = len(account_ids)
        
        print(f"\\n{'='*60}")
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
                    
                    print(f"\\n[{account_id}] {status} - {actions_done}")
                    print(f"進捗: {completed}/{total_accounts} 完了")
                    
                except Exception as e:
                    print(f"\\n[{account_id}] 実行エラー: {e}")
                    results.append({
                        "account_id": account_id,
                        "success": False,
                        "errors": [str(e)],
                        "email": "unknown"
                    })
                    completed += 1
        
        self.print_summary(results)
        self.save_results(results)
        return results'''

    if old_execute_parallel in content:
        content = content.replace(old_execute_parallel, new_execute_parallel)
        print("  ✓ execute_parallelを並列処理版に変更しました")

    # 新しい分離処理メソッドを追加
    new_isolated_method = '''
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
            print(f"\\n[{account_id}] {account['email']} - 処理開始")
            
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
        """完全分離されたドライバー作成"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        import tempfile
        import threading
        
        # アカウント固有の一時ディレクトリ
        thread_id = threading.current_thread().ident
        temp_suffix = f"{account_id}_{thread_id}_{random.randint(1000, 9999)}"
        temp_dir = tempfile.mkdtemp(prefix=f"chrome_{temp_suffix}_")
        
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        # 完全分離設定
        chrome_options.add_argument(f'--user-data-dir={temp_dir}')
        chrome_options.add_argument(f'--remote-debugging-port={9000 + account_id + random.randint(0, 100)}')
        chrome_options.add_argument(f'--disable-shared-memory')
        chrome_options.add_argument(f'--disable-dev-shm-usage')
        
        # プロキシ設定
        proxy = account.get("proxy", {})
        if proxy and proxy.get("host") and proxy.get("port"):
            proxy_url = f"{proxy['host']}:{proxy['port']}"
            chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
        
        try:
            driver = uc.Chrome(options=chrome_options, version_main=139)
            driver.implicitly_wait(10)
            print(f"  [{account_id}] ✓ 分離ドライバー起動成功")
            return driver
        except Exception as e:
            print(f"  [{account_id}] ✗ ドライバー起動エラー: {str(e)[:50]}")
            # 一時ディレクトリをクリーンアップ
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            return None'''

    # メソッドをクラス内に追加
    if "def print_summary" in content:
        # print_summaryメソッドの直前に挿入
        insertion_point = content.find("    def print_summary")
        content = (
            content[:insertion_point]
            + new_isolated_method
            + "\n"
            + content[insertion_point:]
        )
        print("  ✓ 分離処理メソッドを追加しました")

    # ファイル保存
    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("\n" + "=" * 60)
    print(" 複数同時実行の実装完了")
    print("=" * 60)
    print("\n実装内容:")
    print("✓ 真の並列処理（ThreadPoolExecutor）")
    print("✓ 完全分離されたChromeプロファイル")
    print("✓ スタガード起動で競合回避")
    print("✓ アカウント別の一時ディレクトリ")
    print("✓ 独立したデバッグポート")

    print("\nテスト手順:")
    print("1. py -3.10 cli_interface.py")
    print("2. メニュー「9. 自動操作実行」")
    print("3. 同時実行数を2-3に設定してテスト")
    print("4. 成功したら5-10に段階的に増加")


if __name__ == "__main__":
    main()
