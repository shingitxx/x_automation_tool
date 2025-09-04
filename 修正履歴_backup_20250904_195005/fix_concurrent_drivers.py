#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同時実行時のドライバー競合修正
"""

import os
import random


def main():
    print("=" * 60)
    print(" 同時実行ドライバー競合修正")
    print("=" * 60)

    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    # setup_driver_with_proxyメソッドを修正
    if "def setup_driver_with_proxy" not in content:
        print("  ✗ setup_driver_with_proxyメソッドが見つかりません")
        return

    # 新しいsetup_driver_with_proxyメソッド（競合回避機能付き）
    new_setup_method = '''    def setup_driver_with_proxy(self, account_id: int) -> Optional[webdriver.Chrome]:
        """プロキシ設定付きドライバー（競合回避版）"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        # アカウント固有の設定で競合回避
        user_data_dir = f"chrome_profiles/account_{account_id}"
        debug_port = 9222 + account_id  # アカウントIDベースでポート分離
        
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-default-apps')
        
        # 競合回避のための固有設定
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        chrome_options.add_argument(f'--remote-debugging-port={debug_port}')
        chrome_options.add_argument(f'--profile-directory=Profile_{account_id}')
        
        # 一時ディレクトリの競合回避
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix=f'chrome_account_{account_id}_')
        chrome_options.add_argument(f'--temp-profile={temp_dir}')
        
        # プロキシ設定
        proxy = account.get("proxy", {})
        if proxy and proxy.get("host") and proxy.get("port"):
            proxy_url = f"{proxy['host']}:{proxy['port']}"
            chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
            print(f"  プロキシ設定: {proxy_url}")
        
        try:
            # ドライバー作成時の競合回避
            os.makedirs(user_data_dir, exist_ok=True)
            
            # 複数回試行で安定性向上
            for attempt in range(3):
                try:
                    # バージョン指定なしで最新を使用
                    driver = uc.Chrome(options=chrome_options, driver_executable_path=None)
                    driver.implicitly_wait(10)
                    print(f"  ✓ ドライバー起動成功（アカウント: {account['email']}）")
                    return driver
                except Exception as e:
                    if attempt < 2:  # 最後の試行でなければリトライ
                        print(f"  リトライ {attempt + 1}/3: {str(e)[:50]}")
                        import time
                        time.sleep(random.uniform(1, 3))  # ランダム待機で競合回避
                        continue
                    else:
                        raise e
            
        except Exception as e:
            error_msg = str(e)
            if "既に存在するファイル" in error_msg or "WinError 183" in error_msg:
                print(f"  ✗ ファイル競合エラー（アカウント{account_id}）")
                # 古いプロファイルディレクトリを削除してリトライ
                import shutil
                try:
                    if os.path.exists(user_data_dir):
                        shutil.rmtree(user_data_dir)
                        print(f"  古いプロファイル削除: {user_data_dir}")
                    
                    # 再試行
                    driver = uc.Chrome(options=chrome_options, driver_executable_path=None)
                    driver.implicitly_wait(10)
                    print(f"  ✓ リトライ成功（アカウント: {account['email']}）")
                    return driver
                except Exception as retry_e:
                    print(f"  ✗ リトライも失敗: {str(retry_e)[:50]}")
            else:
                print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            return None'''

    # 既存メソッドを置換
    import re

    pattern = r"def setup_driver_with_proxy\(self, account_id.*?(?=\n    def|\nclass|\nif __name__|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        content = content.replace(match.group(0), new_setup_method.strip())
        print("  ✓ setup_driver_with_proxyメソッドを修正しました")

        # ファイル保存
        with open("automation_executor.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("  ✓ ファイル保存完了")
    else:
        print("  ✗ メソッドが見つからず、修正できませんでした")
        return

    # chrome_profilesディレクトリ作成
    os.makedirs("chrome_profiles", exist_ok=True)
    print("  ✓ chrome_profilesディレクトリを作成しました")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n改善点:")
    print("✓ アカウント固有のユーザーデータディレクトリ")
    print("✓ 固有のデバッグポート（9222 + アカウントID）")
    print("✓ 一時ディレクトリの競合回避")
    print("✓ ファイル競合時の自動リトライ機能")
    print("✓ 古いプロファイル自動削除")
    print("\n次のテスト:")
    print("同時実行数2で再度テストしてください")
    print("py -3.10 cli_interface.py")


if __name__ == "__main__":
    main()
