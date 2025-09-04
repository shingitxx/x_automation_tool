#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSVファイル形式の修正とリプライ機能の最終調整
"""

import os
import csv

print("=" * 60)
print(" CSVファイル形式の修正")
print("=" * 60)

# 1. 正しい形式のCSVファイルを作成
csv_path = "config/reply_texts.csv"
os.makedirs("config", exist_ok=True)

# 新しいCSVデータ
reply_data = [
    "素晴らしい投稿ですね！",
    "とても参考になりました",
    "ありがとうございます",
    "勉強になります",
    "いいですね！",
    "共感します",
    "なるほど、そういう視点もありますね",
    "貴重な情報をありがとうございます",
    "フォローさせていただきました",
    "今後も楽しみにしています",
]

# CSVファイルを作成（正しい形式で）
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["リプライテキスト"])  # ヘッダー
    for text in reply_data:
        writer.writerow([text])

print(f"✓ {csv_path} を作成しました")
print(f"  テキスト数: {len(reply_data)}件")

# 2. automation_executor.pyのload_reply_textsメソッドを修正
with open("automation_executor.py", "r", encoding="utf-8") as f:
    content = f.read()

# load_reply_textsメソッドを確実に動作する版に置き換え
new_load_method = '''    def load_reply_texts(self, csv_path: str = "config/reply_texts.csv") -> bool:
        """リプライテキストをCSVから読み込み"""
        if not os.path.exists(csv_path):
            print(f"  ✗ ファイルが見つかりません: {csv_path}")
            return False
        
        try:
            self.reply_texts = []
            
            # UTF-8 BOM付きとBOMなしの両方に対応
            encodings = ['utf-8-sig', 'utf-8']
            
            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding, newline='') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            # ヘッダー名の揺れに対応
                            text = row.get('リプライテキスト') or row.get('reply_text') or ''
                            if text and text.strip():
                                self.reply_texts.append(text.strip())
                    
                    if self.reply_texts:
                        break
                except:
                    continue
            
            if self.reply_texts:
                print(f"  ✓ {len(self.reply_texts)}件のリプライテキストを読み込みました")
                return True
            else:
                print(f"  ✗ リプライテキストが空です")
                return False
                
        except Exception as e:
            print(f"  ✗ 読み込みエラー: {e}")
            return False'''

# メソッドを置き換え
import re

pattern = r"def load_reply_texts.*?return False"
match = re.search(pattern, content, re.DOTALL)
if match:
    content = re.sub(
        pattern, new_load_method.strip(), content, count=1, flags=re.DOTALL
    )
    print("✓ load_reply_textsメソッドを修正しました")

# get_random_replyメソッドも簡潔版に戻す
simple_get_random = '''    def get_random_reply(self) -> Optional[str]:
        """未使用のランダムなリプライテキストを取得"""
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
        
        return None'''

pattern2 = r"def get_random_reply.*?return None"
match2 = re.search(pattern2, content, re.DOTALL)
if match2:
    content = re.sub(
        pattern2, simple_get_random.strip(), content, count=1, flags=re.DOTALL
    )
    print("✓ get_random_replyメソッドを修正しました")

with open("automation_executor.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print(" 修正完了！")
print("=" * 60)

# 3. テスト
print("\nCSVファイルの確認:")
with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    texts = []
    for row in reader:
        if "リプライテキスト" in row:
            texts.append(row["リプライテキスト"])

print(f"読み込めたテキスト数: {len(texts)}")
if texts:
    print("サンプル:")
    for i, text in enumerate(texts[:3], 1):
        print(f"  {i}. {text}")

print("\n次の手順:")
print("1. py -3.10 cli_interface.py")
print("2. 自動操作実行 → リプライ")
print("\nCSVファイルが正しい形式に修正されました。")
print("今度こそリプライが動作するはずです。")
