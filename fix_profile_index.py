import os
import json
from datetime import datetime

# プロファイルフォルダをスキャン
profiles_dir = "profiles"
profile_folders = [f for f in os.listdir(profiles_dir) if f.startswith("profile_")]

# 現在のインデックスを読み込み
with open("data/profile_index.json", "r", encoding="utf-8") as f:
    current_index = json.load(f)

# 修正が必要なアカウントのマッピング
folder_to_account = {
    "profile_abueno_pasabers": "abueno_pasabers",
    "profile_John_L83": "John_L83",
    "profile_fett_dominik": "fett_dominik",
    "profile_covarrubias66_": "covarrubias66_",
    "profile_carliff_": "carliff_",
    "profile_edwinm_00": "edwinm_00",
    "profile_emily_fjk": "emily_fjk",
    "profile_angel_carreon_": "angel_carreon_",
    "profile_SAFI_783": "SAFI_783",
    "profile_elodie_wan": "elodie_wan",
    "profile_Plan_s": "Plan_s",
    "profile_VX_Blood_Eagle": "VX_Blood_Eagle",
    "profile___ka__ma__": "__ka__ma__",
    "profile_crew2_jsd": "crew2_jsd",
    "profile__tom_pere": "_tom_pere",
}

# 不足しているプロファイルを追加
for folder_name, account_name in folder_to_account.items():
    if folder_name in profile_folders and account_name not in current_index["profiles"]:
        current_index["profiles"][account_name] = {
            "email": account_name,
            "profile_path": os.path.abspath(os.path.join(profiles_dir, folder_name)),
            "created_at": "2025-09-05T00:00:00",
            "last_used": datetime.now().isoformat(),
            "login_status": "logged_in",
            "cookies_saved": True,
        }
        print(f"追加: {account_name}")

# 保存
with open("data/profile_index.json", "w", encoding="utf-8") as f:
    json.dump(current_index, f, ensure_ascii=False, indent=2)

print(f"\n✓ 修正完了 - 合計 {len(current_index['profiles'])} アカウント")
