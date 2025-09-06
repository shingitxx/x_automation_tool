import os
import json
from datetime import datetime

# プロファイルフォルダをスキャン
profiles_dir = "profiles"
profile_folders = [f for f in os.listdir(profiles_dir) if f.startswith("profile_")]

# 新しいインデックスを作成
new_index = {"profiles": {}}

for folder in profile_folders:
    # profile_xxxxx から xxxxx を抽出
    account_name = folder.replace("profile_", "").replace("_at_", "@").replace("_", ".")

    new_index["profiles"][account_name] = {
        "email": account_name,
        "profile_path": os.path.abspath(os.path.join(profiles_dir, folder)),
        "created_at": "2025-09-05T00:00:00",
        "last_used": datetime.now().isoformat(),
        "login_status": "logged_in",
        "cookies_saved": True,
    }

# バックアップを作成
if os.path.exists("data/profile_index.json"):
    os.rename("data/profile_index.json", "data/profile_index_backup.json")

# 新しいインデックスを保存
with open("data/profile_index.json", "w", encoding="utf-8") as f:
    json.dump(new_index, f, ensure_ascii=False, indent=2)

print(f"✓ {len(profile_folders)}個のプロファイルを登録しました")
