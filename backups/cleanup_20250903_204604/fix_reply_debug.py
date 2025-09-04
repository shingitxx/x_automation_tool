#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リプライ実行部分の詳細デバッグ
"""

import os

print("=" * 60)
print(" リプライ実行の詳細デバッグ版作成")
print("=" * 60)

with open("automation_executor.py", "r", encoding="utf-8") as f:
    content = f.read()

# process_single_accountメソッドのリプライ部分を詳細デバッグ版に修正
old_reply_part = """            if actions.get("reply", False):
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

new_reply_part = """            if actions.get("reply", False):
                print("  実行: リプライ")
                try:
                    # リプライテキストを取得
                    print(f"    利用可能なテキスト数: {len(self.reply_texts)}")
                    reply_text = self.get_random_reply()
                    
                    if reply_text:
                        print(f"    使用テキスト: {reply_text}")
                        if self.execute_reply(driver, target_url, reply_text):
                            result["actions_performed"].append("reply")
                            self.random_wait(wait_range[0], wait_range[1])
                            print("    ✓ リプライ成功")
                        else:
                            result["errors"].append("リプライ失敗")
                            print("    ✗ リプライ失敗")
                    else:
                        print("    ✗ リプライテキストが取得できません")
                        print(f"    reply_texts内容: {self.reply_texts[:3] if self.reply_texts else '空'}")
                        result["errors"].append("リプライテキストなし")
                except Exception as e:
                    print(f"    ✗ リプライ実行エラー: {str(e)}")
                    result["errors"].append(f"リプライエラー: {str(e)[:50]}")"""

# 置き換え
if 'if actions.get("reply"' in content:
    import re

    # リプライ部分を探して置き換え
    pattern = (
        r'if actions\.get\("reply", False\):.*?result\["errors"\]\.append\([^)]+\)'
    )
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)

    if matches:
        # 最も長いマッチを使用（完全な部分を確実に置き換えるため）
        longest_match = max(matches, key=len)
        content = content.replace(longest_match, new_reply_part.strip())
        print("  ✓ リプライ実行部分を修正しました")

# get_random_replyメソッドも詳細化
old_get_random = """    def get_random_reply(self) -> Optional[str]:
        available_texts = [t for t in self.reply_texts if t not in self.used_replies]
        if not available_texts:
            self.used_replies.clear()
            available_texts = self.reply_texts
        if available_texts:
            selected = random.choice(available_texts)
            self.used_replies.add(selected)
            return selected
        return None"""

new_get_random = '''    def get_random_reply(self) -> Optional[str]:
        """未使用のランダムなリプライテキストを取得"""
        print(f"    get_random_reply開始: 総テキスト数={len(self.reply_texts)}")
        
        if not self.reply_texts:
            print("    ✗ reply_textsが空です")
            return None
            
        available_texts = [t for t in self.reply_texts if t not in self.used_replies]
        print(f"    未使用テキスト数: {len(available_texts)}")
        
        if not available_texts:
            print("    全て使用済み → リセット")
            self.used_replies.clear()
            available_texts = self.reply_texts
        
        if available_texts:
            selected = random.choice(available_texts)
            self.used_replies.add(selected)
            print(f"    選択: {selected[:30]}...")
            return selected
        
        print("    ✗ テキスト選択失敗")
        return None'''

if "def get_random_reply" in content:
    start = content.find("def get_random_reply")
    end = content.find("\n    def ", start + 1)
    if end == -1:
        end = content.find("\n\n    def ", start + 1)
    if end > 0:
        content = content[:start] + new_get_random.strip() + "\n\n    " + content[end:]

with open("automation_executor.py", "w", encoding="utf-8") as f:
    f.write(content)

print("  ✓ automation_executor.py をデバッグ版に更新しました")

print("\n" + "=" * 60)
print(" 完了！")
print("=" * 60)
print("\nもう一度テストしてください:")
print("1. py -3.10 cli_interface.py")
print("2. 自動操作実行 → リプライ")
print("\n今回は詳細なデバッグ情報が表示されます:")
print("- リプライテキストの読み込み状況")
print("- テキスト選択の過程")
print("- エラーの詳細")
