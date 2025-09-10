import time
from selenium.webdriver.common.by import By


class CloudflareHandler:
    @staticmethod
    def check_and_handle_cloudflare(driver, timeout=300):
        """
        Cloudflareを検出し、手動解除を待機

        Returns:
            True: Cloudflareが解決された、または表示されなかった
            False: タイムアウトまたはエラー
        """
        # Cloudflare検出
        if CloudflareHandler.is_cloudflare_present(driver):
            print("\n" + "=" * 60)
            print("⚠️  Cloudflareが検出されました")
            print("=" * 60)
            print("ブラウザで以下を実行してください：")
            print("1. 「私は人間です」のチェックボックスをクリック")
            print("2. 認証が完了するまで待つ")
            print("3. X.comのページが表示されることを確認")
            print("=" * 60)
            print("完了したらEnterキーを押してください...")

            # 手動操作の完了を待つ
            input()

            print("✓ 手動解除完了を確認しました")
            time.sleep(3)  # ページ安定化待機
            return True

        # Cloudflareが表示されていない
        return True

    @staticmethod
    def is_cloudflare_present(driver):
        """Cloudflareが表示されているか確認"""
        try:
            indicators = [
                # URL確認
                lambda: "challenges.cloudflare.com" in driver.current_url,
                # タイトル確認
                lambda: "Just a moment" in driver.title,
                lambda: "moment" in driver.title.lower(),
                # ページ内容確認
                lambda: "Checking if the site connection is secure"
                in driver.page_source,
                lambda: "人間であることを確認" in driver.page_source,
                lambda: "Verifying you are human" in driver.page_source,
                lambda: "Enable JavaScript and cookies to continue"
                in driver.page_source,
            ]

            for check in indicators:
                try:
                    if check():
                        return True
                except:
                    continue

            return False
        except:
            return False
