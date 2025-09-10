#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初回ログインに同時実行数選択機能を追加
"""

import os

print("=" * 60)
print(" 同時実行数選択機能追加")
print("=" * 60)

with open("cli_interface.py", "r", encoding="utf-8") as f:
    content = f.read()

# 各選択肢に同時実行数の設定を追加
new_choice_1 = """            if choice == 1:
                # 特定番号ログイン
                self.display_accounts_with_status()
                try:
                    account_id = int(input("ログインするアカウント番号: "))
                    if self.manager.get_account_by_id(account_id):
                        self.login_manager.manual_login([account_id], 1)  # 1個なので同時実行数1
                    else:
                        print("存在しないアカウントです")
                except ValueError:
                    print("数字を入力してください")"""

new_choice_2 = """            elif choice == 2:
                # 複数選択ログイン
                self.display_accounts_with_status()
                try:
                    ids_str = input("ログインするアカウント番号をカンマ区切りで入力: ")
                    account_ids = [int(x.strip()) for x in ids_str.split(",")]
                    valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
                    if valid_ids:
                        # 同時実行数を選択
                        max_concurrent = self.get_concurrent_count(len(valid_ids))
                        self.login_manager.manual_login(valid_ids, max_concurrent)
                    else:
                        print("有効なアカウントがありません")
                except ValueError:
                    print("正しい形式で入力してください")"""

new_choice_3 = """            elif choice == 3:
                # 範囲指定ログイン
                self.display_accounts_with_status()
                try:
                    start = int(input("開始番号: "))
                    end = int(input("終了番号: "))
                    account_ids = list(range(start, end + 1))
                    valid_ids = [id for id in account_ids if self.manager.get_account_by_id(id)]
                    if valid_ids:
                        # 同時実行数を選択
                        max_concurrent = self.get_concurrent_count(len(valid_ids))
                        self.login_manager.manual_login(valid_ids, max_concurrent)
                    else:
                        print("指定範囲に有効なアカウントがありません")
                except ValueError:
                    print("数字を入力してください")"""

new_choice_4 = """            elif choice == 4:
                # 未ログインのみ
                not_logged = []
                for account in self.manager.accounts.get("accounts", []):
                    cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                    if not os.path.exists(cookie_file):
                        not_logged.append(account["id"])
                        
                if not_logged:
                    print(f"未ログインアカウント: {not_logged}")
                    # 同時実行数を選択
                    max_concurrent = self.get_concurrent_count(len(not_logged))
                    self.login_manager.manual_login(not_logged, max_concurrent)
                else:
                    print("未ログインのアカウントがありません")"""

# get_concurrent_countメソッドを追加
concurrent_method = '''
    def get_concurrent_count(self, total_accounts: int) -> int:
        """同時実行数を取得"""
        max_recommended = min(10, total_accounts)  # 最大10または総アカウント数
        
        print(f"\\n対象アカウント数: {total_accounts}")
        print(f"推奨同時実行数: 1-{max_recommended}")
        
        while True:
            try:
                concurrent = int(input(f"同時に開くブラウザ数を入力 (1-{max_recommended}): "))
                if 1 <= concurrent <= max_recommended:
                    return concurrent
                else:
                    print(f"1-{max_recommended}の範囲で入力してください")
            except ValueError:
                print("数字を入力してください")

'''

# 既存の選択肢処理を置き換え
import re

# choice == 1 を置き換え
pattern1 = r'if choice == 1:.*?print\("数字を入力してください"\)'
if re.search(pattern1, content, re.DOTALL):
    content = re.sub(pattern1, new_choice_1.strip(), content, count=1, flags=re.DOTALL)
    print("✓ 選択肢1を修正しました")

# choice == 2 を置き換え
pattern2 = r'elif choice == 2:.*?print\("正しい形式で入力してください"\)'
if re.search(pattern2, content, re.DOTALL):
    content = re.sub(pattern2, new_choice_2.strip(), content, count=1, flags=re.DOTALL)
    print("✓ 選択肢2を修正しました")

# choice == 3 を置き換え
pattern3 = r'elif choice == 3:.*?print\("数字を入力してください"\)'
if re.search(pattern3, content, re.DOTALL):
    content = re.sub(pattern3, new_choice_3.strip(), content, count=1, flags=re.DOTALL)
    print("✓ 選択肢3を修正しました")

# choice == 4 を置き換え
pattern4 = r'elif choice == 4:.*?print\("未ログインのアカウントがありません"\)'
if re.search(pattern4, content, re.DOTALL):
    content = re.sub(pattern4, new_choice_4.strip(), content, count=1, flags=re.DOTALL)
    print("✓ 選択肢4を修正しました")

# get_concurrent_countメソッドを追加
if "def get_concurrent_count" not in content:
    # display_accounts_with_statusメソッドの後に追加
    insert_point = content.find("def display_accounts_with_status")
    if insert_point > 0:
        next_method = content.find("\n    def ", insert_point + 1)
        if next_method > 0:
            content = content[:next_method] + concurrent_method + content[next_method:]
            print("✓ get_concurrent_countメソッドを追加しました")

with open("cli_interface.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print(" 修正完了")
print("=" * 60)
print("\n追加された機能:")
print("- 選択肢1: 1個固定（同時実行数設定なし）")
print("- 選択肢2-4: 同時実行数を選択可能")
print("- 推奨範囲表示（最大10まで）")
print("- 入力検証機能")
print("\n使用方法:")
print("1. py -3.10 cli_interface.py")
print("2. 初回ログイン → 選択肢2-4で同時実行数を設定")
