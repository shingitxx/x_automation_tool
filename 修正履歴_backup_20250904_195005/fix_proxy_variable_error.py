#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
変数スコープエラー修正
"""

import os


def main():
    print("=" * 60)
    print(" 変数スコープエラー修正")
    print("=" * 60)

    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # エラーが起きている箇所を修正
    # proxy変数をfor文の前に定義する
    old_section = """                # プロセス分離とポート競合回避
                debug_port = 9000 + account_id + random.randint(0, 100)
                print(f"Chrome起動中... (ポート: {debug_port})")
                print(f"プロキシ設定: {proxy_url}" if proxy.get("host") else "プロキシなし")
                
                # 複数回試行でドライバー作成（オプション毎回新規作成）
                driver = None
                for attempt in range(3):"""

    new_section = """                # プロキシ情報を事前に取得
                proxy = account.get("proxy", {})
                proxy_url = f"{proxy['host']}:{proxy['port']}" if proxy.get("host") and proxy.get("port") else None
                
                # プロセス分離とポート競合回避
                debug_port = 9000 + account_id + random.randint(0, 100)
                print(f"Chrome起動中... (ポート: {debug_port})")
                print(f"プロキシ設定: {proxy_url}" if proxy_url else "プロキシなし")
                
                # 複数回試行でドライバー作成（オプション毎回新規作成）
                driver = None
                for attempt in range(3):"""

    if old_section in content:
        content = content.replace(old_section, new_section)
        print("  ✓ proxy変数のスコープエラーを修正しました")
    else:
        print("  ⚠ 対象セクションが見つかりませんでした")

    # for文内のプロキシ設定部分も修正
    old_proxy_in_loop = """                        # プロキシ設定
                        proxy = account.get("proxy", {})
                        if proxy and proxy.get("host") and proxy.get("port"):
                            proxy_url = f"{proxy['host']}:{proxy['port']}"
                            retry_options.add_argument(f'--proxy-server=http://{proxy_url}')"""

    new_proxy_in_loop = """                        # プロキシ設定（既に定義済みの変数を使用）
                        if proxy_url:
                            retry_options.add_argument(f'--proxy-server=http://{proxy_url}')"""

    if old_proxy_in_loop in content:
        content = content.replace(old_proxy_in_loop, new_proxy_in_loop)
        print("  ✓ for文内のプロキシ設定を最適化しました")

    # ファイル保存
    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ ファイル保存完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n修正内容:")
    print("✓ proxy変数を事前定義")
    print("✓ proxy_url変数を事前計算")
    print("✓ 変数スコープエラー解決")
    print("✓ 重複するプロキシ設定処理を削除")

    print("\n次のテスト:")
    print("py -3.10 cli_interface.py")
    print("メニュー「2. 初回ログイン」で再実行")


if __name__ == "__main__":
    main()
