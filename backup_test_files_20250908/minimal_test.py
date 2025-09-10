# minimal_test.py - 最小限のブラウザ起動テスト（新規作成）
import undetected_chromedriver as uc
import time

print("最小限のテスト開始")

try:
    # 最もシンプルな起動
    driver = uc.Chrome(version_main=139)
    print("✓ ブラウザ起動成功")

    driver.get("https://www.google.com")
    time.sleep(5)

    driver.quit()
    print("✓ 正常終了")

except Exception as e:
    print(f"✗ エラー: {str(e)}")
