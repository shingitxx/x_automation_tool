#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいリプライテキストセットを作成
"""

import os
import csv

print("=" * 60)
print(" 新しいリプライテキストを作成")
print("=" * 60)

# 異なる10個のテキスト
new_reply_texts = [
    "興味深い内容ですね",
    "シェアしてくださってありがとう",
    "これは知らなかったです！",
    "めちゃくちゃ良いですね",
    "最高の投稿です",
    "この情報は助かります",
    "またひとつ学びました",
    "すごく役立つ情報です",
    "これからも投稿楽しみにしてます",
    "有益な情報をありがとう！",
]

# CSVファイルに保存
csv_path = "config/reply_texts.csv"
os.makedirs("config", exist_ok=True)

with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["リプライテキスト"])  # ヘッダー
    for text in new_reply_texts:
        writer.writerow([text])

print(f"✓ {csv_path} を更新しました")
print(f"  新しいテキスト数: {len(new_reply_texts)}件")
print("\n新しいテキスト内容:")
for i, text in enumerate(new_reply_texts, 1):
    print(f"  {i}. {text}")

print("\n" + "=" * 60)
print(" 完了！")
print("=" * 60)
print("\n新しいテキストでテストしてください:")
print("1. py -3.10 cli_interface.py")
print("2. 自動操作実行 → リプライ")
print("\n「素晴らしい投稿ですね！」などの前のテキストではなく、")
print("「興味深い内容ですね」などの新しいテキストが使われるはずです。")
