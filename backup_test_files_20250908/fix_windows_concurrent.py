#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows同時実行エラー修正スクリプト
automation_executor.pyのsetup_driver_isolatedメソッドを修正
"""

import os
import shutil


def main():
    print("=" * 60)
    print(" Windows同時実行エラー修正")
    print("=" * 60)

    if not os.path.exists("automation_executor.py"):
        print("❌ automation_executor.py が見つかりません")
        return

    # バックアップ作成
    backup_file = "automation_executor_backup.py"
    shutil.copy("automation_executor.py", backup_file)
    print(f"✓ バックアップ作成: {backup_file}")

    # ファイル読み込み
    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 修正箇所特定
    old_method = '''    def setup_driver_isolated(self, account_id: int) -> Optional[webdriver.Chrome]:
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

    new_method = '''    def setup_driver_isolated(self, account_id: int) -> Optional[webdriver.Chrome]:
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
            return None'''

    # メソッド置換
    if old_method in content:
        new_content = content.replace(old_method, new_method)

        # ファイル更新
        with open("automation_executor.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ setup_driver_isolated メソッドを修正しました")
        print()
        print("修正内容:")
        print("・UUID使用でディレクトリ名完全ユニーク化")
        print("・10回リトライで確実な一時ディレクトリ作成")
        print("・ポート範囲拡大で競合回避強化")
        print("・Windows特有設定追加")
        print("・エラーハンドリング改善")

    else:
        print("❌ 対象メソッドが見つかりませんでした")
        print("手動で修正が必要です")

    print()
    print("修正完了後、以下でテストしてください:")
    print("py -3.10 cli_interface.py")


if __name__ == "__main__":
    main()
