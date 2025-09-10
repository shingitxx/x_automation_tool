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
            print("3. X.comのページが表示されるまで待つ")
            print("=" * 60)
            print(f"最大{timeout}秒待機します...")

            # 手動解除を待機
            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(2)

                # Cloudflareが解決されたか確認
                if not CloudflareHandler.is_cloudflare_present(driver):
                    # X.comのページに到達したか確認
                    if (
                        "x.com" in driver.current_url
                        or "twitter.com" in driver.current_url
                    ):
                        print("✓ Cloudflare解除を確認しました")
                        time.sleep(3)  # ページ読み込み待機
                        return True

                # 残り時間を表示（30秒ごと）
                elapsed = int(time.time() - start_time)
                if elapsed % 30 == 0 and elapsed > 0:
                    remaining = timeout - elapsed
                    print(f"  待機中... (残り{remaining}秒)")

            print("✗ タイムアウト: Cloudflareが解除されませんでした")
            return False

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
