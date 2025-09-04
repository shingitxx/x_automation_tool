#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動作していた状態に復旧
cleanup_files.py作成時点の状態に戻す
"""

import os

def main():
    print("="*60)
    print(" 動作していた状態に復旧")
    print("="*60)
    
    # バックアップファイルの確認
    backup_files = [
        "automation_executor_backup.py",
        "automation_executor_original.py", 
        "automation_executor_chrome_backup.py",
        "automation_executor_temp_profile_backup.py"
    ]
    
    available_backups = []
    for backup in backup_files:
        if os.path.exists(backup):
            available_backups.append(backup)
            print(f"✓ バックアップ発見: {backup}")
    
    if not available_backups:
        print("❌ 利用可能なバックアップが見つかりません")
        return
    
    # 最も適切なバックアップを選択（最初に作成されたもの）
    if "automation_executor_backup.py" in available_backups:
        restore_from = "automation_executor_backup.py"
    elif "automation_executor_original.py" in available_backups:
        restore_from = "automation_executor_original.py"
    else:
        restore_from = available_backups[0]
    
    print(f"\n復旧元: {restore_from}")
    
    # automation_executor.pyを復旧
    try:
        import shutil
        shutil.copy(restore_from, "automation_executor.py")
        print(f"✅ automation_executor.py を {restore_from} から復旧完了")
        
        # 復旧後のファイル確認
        with open("automation_executor.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n復旧ファイル確認:")
        print(f"  ファイルサイズ: {len(content)} 文字")
        print(f"  行数: {len(content.split('\n'))} 行")
        
        # 重要なクラス・メソッドの存在確認
        important_items = [
            "class AutomationExecutor",
            "def setup_driver_with_proxy",
            "def setup_driver_isolated", 
            "def process_single_account",
            "def execute_parallel",
            "undetected_chromedriver"
        ]
        
        found_items = []
        for item in important_items:
            if item in content:
                found_items.append(item)
                print(f"  ✓ {item}")
            else:
                print(f"  - {item}")
        
        if len(found_items) >= 4:
            print(f"\n✅ 復旧成功 - 主要機能が確認できました")
            print(f"テスト実行: py -3.10 cli_interface.py")
        else:
            print(f"\n⚠ 復旧したファイルに不足があります")
            print(f"見つかった項目: {len(found_items)}/{len(important_items)}")
        
    except Exception as e:
        print(f"❌ 復旧失敗: {e}")

if __name__ == "__main__":
    main()