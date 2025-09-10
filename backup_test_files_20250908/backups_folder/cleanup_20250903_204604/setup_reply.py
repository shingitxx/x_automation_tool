#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リプライ機能のセットアップと修正
"""

import os
import csv

print("=" * 60)
print(" リプライ機能のセットアップ")
print("=" * 60)

# 1. サンプルのリプライテキストCSVを作成
print("\nリプライテキストファイルを作成中...")

reply_texts = [
    {"リプライテキスト": "素晴らしい投稿ですね！"},
    {"リプライテキスト": "とても参考になりました"},
    {"リプライテキスト": "ありがとうございます"},
    {"リプライテキスト": "勉強になります"},
    {"リプライテキスト": "いいですね！"},
    {"リプライテキスト": "共感します"},
    {"リプライテキスト": "なるほど、そういう視点もありますね"},
    {"リプライテキスト": "貴重な情報をありがとうございます"},
    {"リプライテキスト": "フォローさせていただきました"},
    {"リプライテキスト": "今後も楽しみにしています"},
]

csv_path = "config/reply_texts.csv"
os.makedirs("config", exist_ok=True)

with open(csv_path, "w", encoding="utf-8", newline="") as f:
    fieldnames = ["リプライテキスト"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(reply_texts)

print(f"  ✓ {csv_path} を作成しました")
print(f"  リプライテキスト数: {len(reply_texts)}件")

# 2. automation_executor.pyのリプライ機能を修正
print("\nリプライ機能を修正中...")

with open("automation_executor.py", "r", encoding="utf-8") as f:
    content = f.read()

# execute_replyメソッドを修正
new_execute_reply = """    def execute_reply(self, driver: webdriver.Chrome, url: str, reply_text: str) -> bool:
        try:
            driver.get(url)
            time.sleep(5)  # ページ完全読み込み待機
            
            # ページが正しく読み込まれたか確認
            if "x.com" not in driver.current_url and "twitter.com" not in driver.current_url:
                print(f"  ✗ ページ読み込みエラー: {driver.current_url}")
                return False
            
            print(f"  リプライテキスト: {reply_text}")
            
            # リプライボタンを探してクリック（リプライ入力欄を開く）
            reply_button_selectors = [
                "[data-testid='reply']",
                "div[role='button'][aria-label*='Reply']",
                "div[role='button'][aria-label*='返信']",
                "button[aria-label*='Reply']"
            ]
            
            clicked = False
            for selector in reply_button_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        button = elements[0]
                        if button.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            clicked = True
                            print("  ✓ リプライボタンをクリック")
                            break
                except:
                    continue
            
            # リプライ入力欄を探す
            reply_input_selectors = [
                "[data-testid='tweetTextarea_0']",
                "div[role='textbox']",
                "div[contenteditable='true'][role='textbox']",
                "div[aria-label*='Post text']",
                "div[aria-label*='ポストのテキスト']"
            ]
            
            input_found = False
            for selector in reply_input_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # クリックして入力欄をアクティブにする
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(1)
                            
                            # テキストを入力
                            element.send_keys(reply_text)
                            time.sleep(2)
                            
                            input_found = True
                            print("  ✓ リプライテキストを入力")
                            break
                    
                    if input_found:
                        break
                except:
                    continue
            
            if not input_found:
                print("  ✗ リプライ入力欄が見つかりません")
                return False
            
            # 送信ボタンを探してクリック
            send_button_selectors = [
                "[data-testid='tweetButtonInline']",
                "[data-testid='tweetButton']",
                "button[data-testid='tweetButton']",
                "div[role='button'][data-testid='tweetButtonInline']",
                "//span[text()='返信']/..",
                "//span[text()='Reply']/..",
                "//span[text()='Post']/.."
            ]
            
            for selector in send_button_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)
                            print("  ✓ リプライを送信")
                            return True
                except:
                    continue
            
            print("  ✗ 送信ボタンが見つかりません")
            return False
            
        except Exception as e:
            print(f"  ✗ リプライエラー: {str(e)[:100]}")
            return False"""

# メソッドを置き換え
if "def execute_reply" in content:
    start = content.find("def execute_reply")
    # 次のメソッドまたはクラスの終わりを探す
    next_def = content.find("\n    def ", start + 1)
    if next_def == -1:
        next_def = content.find("\n\nclass", start)
    if next_def == -1:
        # process_single_accountメソッドを探す
        next_def = content.find("\n    def process_single_account", start)
    if next_def == -1:
        next_def = len(content)

    content = (
        content[:start]
        + new_execute_reply.strip()
        + "\n\n    "
        + content[next_def:].lstrip()
    )

with open("automation_executor.py", "w", encoding="utf-8") as f:
    f.write(content)

print("  ✓ リプライ機能を修正しました")

print("\n" + "=" * 60)
print(" セットアップ完了！")
print("=" * 60)
print("\nリプライ機能のテスト方法:")
print("1. py -3.10 cli_interface.py でプログラムを起動")
print("2. 自動操作実行を選択")
print("3. 操作選択で「6」（リプライ）を選択")
print("\n注意:")
print("- config/reply_texts.csv からランダムにテキストが選ばれます")
print("- カスタムテキストを追加したい場合はCSVを編集してください")
