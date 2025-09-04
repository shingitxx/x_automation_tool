#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リプライコードの重複箇所を特定して修正
"""

import os

print("=" * 60)
print(" リプライコードの解析と修正")
print("=" * 60)

with open("automation_executor.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# "リプライテキストが見つかりません"を含む行を探す
found_lines = []
for i, line in enumerate(lines):
    if "リプライテキストが見つかりません" in line:
        found_lines.append((i + 1, line.strip()))
        print(f"行 {i+1}: {line.strip()}")

        # 前後の行も表示
        print("  前の行:", lines[i - 1].strip() if i > 0 else "N/A")
        print("  次の行:", lines[i + 1].strip() if i < len(lines) - 1 else "N/A")
        print()

if found_lines:
    print(f"\n見つかった重複行数: {len(found_lines)}")

    # 該当行を削除
    new_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue

        if "✗ リプライテキストが見つかりません" in line:
            # この行と関連する行をスキップ
            if i > 0 and "print" in lines[i - 1]:
                new_lines.pop()  # 前の行も削除
            continue

        new_lines.append(line)

    # ファイルを保存
    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("✓ 重複コードを削除しました")
else:
    print("重複コードは見つかりませんでした")

print("\n修正完了。もう一度テストしてください。")
