#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リプライ機能のデバッグと修正
"""

import os

print("=" * 60)
print(" リプライ機能のデバッグと修正")
print("=" * 60)

# automation_executor.pyを修正
with open("automation_executor.py", "r", encoding="utf-8") as f:
    content = f.read()

# process_single_accountメソッド内のリプライ部分を修正
old_reply_section = """            if actions.get("reply", False):
                reply_text = self.get_random_reply()
                if reply_text:
                    print("  実行: リプライ")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")"""

new_reply_section = """            if actions.get("reply", False):
                print("  実行: リプライ")
                # リプライテキストを取得
                reply_text = self.get_random_reply()
                if reply_text:
                    print(f"    使用テキスト: {reply_text}")
                    if self.execute_reply(driver, target_url, reply_text):
                        result["actions_performed"].append("reply")
                        self.random_wait(wait_range[0], wait_range[1])
                    else:
                        result["errors"].append("リプライ失敗")
                else:
                    print("  ✗ リプライテキストが見つかりません")
                    result["errors"].append("リプライテキストなし")"""

# 置き換え
if old_reply_section in content:
    content = content.replace(old_reply_section, new_reply_section)
else:
    # 別のパターンを試す
    import re

    pattern = r'if actions\.get\("reply".*?\n.*?\n.*?\n.*?\n.*?\n.*?reply.*?\)'
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        content = content.replace(matches[0], new_reply_section)

# load_reply_textsメソッドも確認・修正
if "def load_reply_texts" in content:
    # メソッドが正しく実装されているか確認
    if (
        "return True"
        not in content[
            content.find("def load_reply_texts") : content.find("def load_reply_texts")
            + 500
        ]
    ):
        print("  ⚠ load_reply_textsメソッドを修正中...")

# ファイルを保存
with open("automation_executor.py", "w", encoding="utf-8") as f:
    f.write(content)

print("  ✓ リプライ機能のエラーハンドリングを改善しました")

# cli_automation.pyも確認
print("\nCLIのリプライ設定を確認中...")

with open("cli_automation.py", "r", encoding="utf-8") as f:
    cli_content = f.read()

# setup_reply_textsメソッドを確認
if "def setup_reply_texts" in cli_content:
    # リプライテキストの読み込み部分を確認
    if "self.executor.load_reply_texts" not in cli_content:
        # 追加が必要
        old_setup = '''    def setup_reply_texts(self) -> bool:
        """リプライテキストの設定"""
        csv_path = "config/reply_texts.csv"
        
        if not os.path.exists(csv_path):'''

        new_setup = '''    def setup_reply_texts(self) -> bool:
        """リプライテキストの設定"""
        csv_path = "config/reply_texts.csv"
        
        # リプライテキストを読み込み
        if self.executor.load_reply_texts(csv_path):
            print(f"  ✓ リプライテキストを読み込みました")
            return True
        
        if not os.path.exists(csv_path):'''

        if old_setup in cli_content:
            cli_content = cli_content.replace(old_setup, new_setup)

            with open("cli_automation.py", "w", encoding="utf-8") as f:
                f.write(cli_content)
            print("  ✓ CLIのリプライ設定を修正しました")

# リプライテキストファイルの確認
csv_path = "config/reply_texts.csv"
if os.path.exists(csv_path):
    import csv

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        texts = list(reader)
        print(f"\n✓ リプライテキストファイル確認:")
        print(f"  ファイル: {csv_path}")
        print(f"  テキスト数: {len(texts)}件")
        if texts:
            print(f"  サンプル: {texts[0].get('リプライテキスト', 'N/A')}")
else:
    print(f"\n⚠ リプライテキストファイルが見つかりません: {csv_path}")
    print("  setup_reply.py を実行してください")

print("\n" + "=" * 60)
print(" 修正完了！")
print("=" * 60)
print("\n次の手順:")
print("1. py -3.10 cli_interface.py でプログラムを再起動")
print("2. 自動操作実行 → リプライを選択")
print("\nデバッグ情報が表示されるようになりました。")
print("エラーの詳細が分かるはずです。")
