#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リプライ機能の重複コード除去と修正
"""

import os


def main():
    print("=" * 60)
    print(" リプライ機能の修正")
    print("=" * 60)

    # 1. automation_executor.py の重複コード確認
    print("\n1. automation_executor.py を確認中...")

    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # "リプライテキストが見つかりません"を含む行を探す
    found_lines = []
    for i, line in enumerate(lines):
        if "リプライテキストが見つかりません" in line:
            found_lines.append((i + 1, line.strip()))
            print(f"  重複行発見 - 行{i+1}: {line.strip()}")

    if found_lines:
        print(f"  ✓ {len(found_lines)}個の重複コードを発見しました")

        # 重複行を削除
        new_lines = []
        for i, line in enumerate(lines):
            if "✗ リプライテキストが見つかりません" in line:
                print(f"  削除: 行{i+1}")
                continue
            new_lines.append(line)

        # ファイル保存
        with open("automation_executor.py", "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print("  ✓ 重複コードを削除しました")
    else:
        print("  ✓ 重複コードは見つかりませんでした")

    # 2. リプライテキストCSVファイルの確認・作成
    print("\n2. リプライテキストファイルを確認中...")

    csv_path = "config/reply_texts.csv"
    if not os.path.exists("config"):
        os.makedirs("config")
        print("  ✓ config フォルダを作成しました")

    if not os.path.exists(csv_path):
        print("  リプライテキストファイルが存在しません。作成します...")

        # サンプルリプライテキスト
        sample_texts = [
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

        import csv

        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["リプライテキスト"])
            for text in sample_texts:
                writer.writerow([text])

        print(f"  ✓ {csv_path} を作成しました（{len(sample_texts)}件のテキスト）")
    else:
        # 既存ファイルの内容確認
        import csv

        try:
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                texts = [
                    row["リプライテキスト"]
                    for row in reader
                    if "リプライテキスト" in row and row["リプライテキスト"].strip()
                ]

            print(f"  ✓ 既存ファイル確認完了（{len(texts)}件のテキスト）")
            if texts:
                print(f"  サンプル: {texts[0]}")
        except Exception as e:
            print(f"  ✗ ファイル読み込みエラー: {e}")

    # 3. 修正完了メッセージ
    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n次のステップ:")
    print("1. python cli_interface.py を実行")
    print("2. メニュー「9. 自動操作実行」を選択")
    print("3. リプライ機能をテスト")
    print("\nリプライが正常に動作するか確認してください。")


if __name__ == "__main__":
    main()
