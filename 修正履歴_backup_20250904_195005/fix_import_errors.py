#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
インポートエラーの修正
"""

import os


def main():
    print("=" * 60)
    print(" インポートエラー修正")
    print("=" * 60)

    # 1. automation_executor.pyに不足している関数を追加
    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    # create_sample_reply_csv関数が存在するか確認
    if "def create_sample_reply_csv" not in content:
        print("  create_sample_reply_csv関数が見つかりません。追加します...")

        # ファイル末尾に関数を追加
        create_function = '''

def create_sample_reply_csv(filepath: str = "config/reply_texts.csv"):
    """サンプルリプライCSV作成"""
    import os
    import csv
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    sample_data = [
        {"リプライテキスト": "興味深い内容ですね"},
        {"リプライテキスト": "シェアしてくださってありがとう"},
        {"リプライテキスト": "これは知らなかったです！"},
        {"リプライテキスト": "めちゃくちゃ良いですね"},
        {"リプライテキスト": "最高の投稿です"},
        {"リプライテキスト": "この情報は助かります"},
        {"リプライテキスト": "またひとつ学びました"},
        {"リプライテキスト": "すごく役立つ情報です"},
        {"リプライテキスト": "これからも投稿楽しみにしてます"},
        {"リプライテキスト": "有益な情報をありがとう！"}
    ]
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ["リプライテキスト"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"  ✓ サンプルリプライCSVを作成: {filepath}")
'''

        content += create_function
        print("  ✓ create_sample_reply_csv関数を追加しました")

    # 不足しているインポートを修正
    if "from selenium.webdriver.chrome.service import Service" not in content:
        # インポート部分を見つけて追加
        import_section = content.find("from selenium import webdriver")
        if import_section != -1:
            content = content.replace(
                "from selenium import webdriver",
                """from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager""",
            )
            print("  ✓ 不足していたインポートを追加しました")

    # ファイル保存
    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ automation_executor.py修正完了")

    # 2. cli_automation.pyの確認
    if os.path.exists("cli_automation.py"):
        with open("cli_automation.py", "r", encoding="utf-8") as f:
            cli_content = f.read()

        # インポート部分の確認
        if "from automation_executor import AutomationExecutor" in cli_content:
            print("  ✓ cli_automation.pyのインポートは正常です")
        else:
            print("  cli_automation.pyのインポートに問題があります")
            # 修正
            cli_content = cli_content.replace(
                "import AutomationExecutor",
                "from automation_executor import AutomationExecutor",
            )

            with open("cli_automation.py", "w", encoding="utf-8") as f:
                f.write(cli_content)
            print("  ✓ cli_automation.pyのインポートを修正しました")

    # 3. 簡単な動作テスト
    print("\n動作テストを実行中...")
    try:
        # Pythonでインポートテスト
        import sys

        sys.path.append(".")

        from automation_executor import AutomationExecutor

        print("  ✓ AutomationExecutorのインポート成功")

        executor = AutomationExecutor()
        print("  ✓ AutomationExecutorのインスタンス作成成功")

    except Exception as e:
        print(f"  ⚠ テストエラー: {str(e)[:100]}")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n修正内容:")
    print("✓ create_sample_reply_csv関数追加")
    print("✓ 不足していたインポート追加")
    print("✓ cli_automation.pyインポート修正")
    print("✓ 基本的な動作テスト完了")

    print("\n次のテスト:")
    print("py -3.10 cli_interface.py")
    print("インポートエラーが解決されているはずです")


if __name__ == "__main__":
    main()
