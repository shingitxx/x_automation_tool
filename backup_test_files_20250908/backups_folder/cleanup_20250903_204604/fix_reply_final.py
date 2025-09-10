#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リプライ機能の最終修正
"""

import os

print("=" * 60)
print(" リプライ機能の最終修正")
print("=" * 60)

# cli_automation.pyを修正
with open("cli_automation.py", "r", encoding="utf-8") as f:
    content = f.read()

# run_automation メソッド内のリプライ設定部分を修正
old_section = """        # リプライテキストの確認（リプライが選択された場合）
        if actions.get("reply", False):
            if not self.setup_reply_texts():
                actions["reply"] = False"""

new_section = """        # リプライテキストの確認（リプライが選択された場合）
        if actions.get("reply", False):
            print("\\nリプライテキストを読み込み中...")
            if not self.setup_reply_texts():
                print("  ✗ リプライテキストの読み込みに失敗しました")
                actions["reply"] = False
            else:
                print("  ✓ リプライテキストを読み込みました")"""

content = content.replace(old_section, new_section)

# setup_reply_textsメソッドを修正
old_setup_method = '''    def setup_reply_texts(self) -> bool:
        """リプライテキストの設定"""
        csv_path = "config/reply_texts.csv"
        
        if not os.path.exists(csv_path):
            print(f"\\nリプライテキストファイルが見つかりません: {csv_path}")
            create_sample = input("サンプルファイルを作成しますか？ (y/n): ").strip().lower()
            if create_sample == 'y':
                create_sample_reply_csv(csv_path)
            else:
                return False
        
        # リプライテキストを読み込み
        return self.executor.load_reply_texts(csv_path)'''

new_setup_method = '''    def setup_reply_texts(self) -> bool:
        """リプライテキストの設定"""
        csv_path = "config/reply_texts.csv"
        
        if not os.path.exists(csv_path):
            print(f"\\nリプライテキストファイルが見つかりません: {csv_path}")
            create_sample = input("サンプルファイルを作成しますか？ (y/n): ").strip().lower()
            if create_sample == 'y':
                # サンプル作成関数を呼び出し
                from automation_executor import create_sample_reply_csv
                create_sample_reply_csv(csv_path)
            else:
                return False
        
        # リプライテキストを読み込み
        success = self.executor.load_reply_texts(csv_path)
        if success:
            print(f"  読み込んだテキスト数: {len(self.executor.reply_texts)}件")
        return success'''

content = content.replace(old_setup_method, new_setup_method)

with open("cli_automation.py", "w", encoding="utf-8") as f:
    f.write(content)

print("  ✓ cli_automation.py を修正しました")

# automation_executor.pyのload_reply_textsメソッドを確認
with open("automation_executor.py", "r", encoding="utf-8") as f:
    exec_content = f.read()

# load_reply_textsメソッドを修正
old_load_method = """    def load_reply_texts(self, csv_path: str = "config/reply_texts.csv") -> bool:
        if not os.path.exists(csv_path):
            return False
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.reply_texts = []
                for row in reader:
                    if 'リプライテキスト' in row:
                        self.reply_texts.append(row['リプライテキスト'])
            return True
        except:
            return False"""

new_load_method = '''    def load_reply_texts(self, csv_path: str = "config/reply_texts.csv") -> bool:
        """リプライテキストをCSVから読み込み"""
        if not os.path.exists(csv_path):
            print(f"  ✗ ファイルが見つかりません: {csv_path}")
            return False
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.reply_texts = []
                for row in reader:
                    if 'リプライテキスト' in row and row['リプライテキスト'].strip():
                        self.reply_texts.append(row['リプライテキスト'].strip())
            
            if self.reply_texts:
                print(f"  ✓ {len(self.reply_texts)}件のリプライテキストを読み込みました")
                return True
            else:
                print(f"  ✗ リプライテキストが空です")
                return False
        except Exception as e:
            print(f"  ✗ 読み込みエラー: {e}")
            return False'''

if old_load_method in exec_content:
    exec_content = exec_content.replace(old_load_method, new_load_method)
else:
    # 別のパターンを探す
    import re

    pattern = r"def load_reply_texts.*?return False"
    match = re.search(pattern, exec_content, re.DOTALL)
    if match:
        exec_content = exec_content.replace(match.group(0), new_load_method.strip())

with open("automation_executor.py", "w", encoding="utf-8") as f:
    f.write(exec_content)

print("  ✓ automation_executor.py を修正しました")

# config/reply_texts.csvの内容を確認
csv_path = "config/reply_texts.csv"
if os.path.exists(csv_path):
    import csv

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        texts = [row["リプライテキスト"] for row in reader if "リプライテキスト" in row]

    print(f"\n現在のリプライテキスト:")
    print(f"  ファイル: {csv_path}")
    print(f"  テキスト数: {len(texts)}件")
    if texts:
        for i, text in enumerate(texts[:3], 1):
            print(f"  {i}. {text}")
        if len(texts) > 3:
            print(f"  ... 他{len(texts)-3}件")

print("\n" + "=" * 60)
print(" 修正完了！")
print("=" * 60)
print("\nもう一度リプライをテストしてください:")
print("1. py -3.10 cli_interface.py")
print("2. 自動操作実行 → リプライ")
print("\n今回はリプライテキストの読み込み状況が")
print("詳しく表示されるようになりました。")
