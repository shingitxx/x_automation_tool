# profile_test.py - プロファイル起動テスト（新規作成）
import undetected_chromedriver as uc
import time
import os

print("プロファイルテスト開始")

# テスト1: プロファイルなしで起動
try:
    print("\n【テスト1】通常起動")
    driver = uc.Chrome(version_main=139)
    print("✓ 起動成功")
    driver.get("https://x.com")
    time.sleep(3)
    driver.quit()
except Exception as e:
    print(f"✗ エラー: {str(e)[:100]}")

time.sleep(2)

# テスト2: プロファイルありで起動
try:
    print("\n【テスト2】プロファイル付き起動")
    profile_path = os.path.abspath("profiles/profile_exdel81")
    print(f"プロファイルパス: {profile_path}")
    print(f"存在確認: {os.path.exists(profile_path)}")

    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--profile-directory=Default")

    driver = uc.Chrome(options=chrome_options, version_main=139)
    print("✓ 起動成功")
    driver.get("https://x.com/home")
    time.sleep(5)
    print(f"現在のURL: {driver.current_url}")
    driver.quit()
except Exception as e:
    print(f"✗ エラー: {str(e)[:100]}")

time.sleep(2)

# テスト3: プロファイル＋プロキシで起動
try:
    print("\n【テスト3】プロファイル＋プロキシ付き起動")
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--profile-directory=Default")

    # プロキシ追加（ホスト:ポートのみ）
    chrome_options.add_argument("--proxy-server=http://iproyalfast.hellworld.io:12321")

    driver = uc.Chrome(options=chrome_options, version_main=139)
    print("✓ 起動成功")
    driver.get("https://x.com/home")
    time.sleep(5)
    print(f"現在のURL: {driver.current_url}")
    driver.quit()
except Exception as e:
    print(f"✗ エラー: {str(e)[:100]}")
