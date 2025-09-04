# relogin_profile.py として保存
from login_manager_v2 import LoginManagerV2

login_manager = LoginManagerV2()

# アカウント1と2を再ログイン（プロファイルに保存）
account_ids = [1, 2]

print("プロファイルへの再ログインを実行します")
print("=" * 50)

results = login_manager.manual_login(account_ids, max_concurrent=1)
