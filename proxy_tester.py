import os
import time
import requests
from typing import Dict
from account_manager import AccountManager

class ProxyTester:
    """プロキシテスト"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://ipinfo.io/json"
        ]
    
    def test_account_proxy(self, account_id: int) -> Dict:
        """アカウントのプロキシテスト"""
        account = self.manager.get_account_by_id(account_id)
        if not account:
            return {"status": "error", "error": "アカウントが見つかりません"}
        
        proxy_url = self.manager.get_proxy_url(account_id)
        if not proxy_url:
            return {"status": "error", "error": "プロキシ情報が見つかりません"}
        
        print(f"\nアカウント: [{account_id}] {account['email']}")
        print(f"プロキシをテスト中: {account['proxy']['host']}:{account['proxy']['port']}")
        print("-" * 50)
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        results = {"successes": 0, "failures": 0, "responses": []}
        
        for test_url in self.test_urls:
            print(f"テストURL: {test_url}")
            try:
                start_time = time.time()
                response = requests.get(test_url, proxies=proxies, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = round(end_time - start_time, 2)
                    
                    if "ip" in response.text.lower():
                        try:
                            data = response.json()
                            ip = data.get('ip', data.get('origin', 'N/A'))
                            print(f"✓ 成功 - IP: {ip} (応答時間: {response_time}秒)")
                        except:
                            print(f"✓ 成功 (応答時間: {response_time}秒)")
                    else:
                        print(f"✓ 成功 (応答時間: {response_time}秒)")
                    
                    results["successes"] += 1
                    results["responses"].append({
                        "url": test_url,
                        "status": "success",
                        "response_time": response_time
                    })
                else:
                    print(f"✗ HTTPエラー: {response.status_code}")
                    results["failures"] += 1
                    
            except requests.exceptions.Timeout:
                print("✗ タイムアウト")
                results["failures"] += 1
            except requests.exceptions.ConnectionError:
                print("✗ 接続エラー")
                results["failures"] += 1
            except Exception as e:
                print(f"✗ エラー: {str(e)}")
                results["failures"] += 1
            
            print("次のテストまで2秒待機...")
            time.sleep(2)
        
        if results["successes"] > 0:
            results["status"] = "success"
        else:
            results["status"] = "failure"
        
        return results
    
    def test_all_proxies(self) -> Dict:
        """全プロキシテスト"""
        accounts = self.manager.accounts.get("accounts", [])
        if not accounts:
            return {"error": "アカウントが登録されていません"}
        
        print(f"\n{len(accounts)}個のアカウントのプロキシをテストします\n")
        
        all_results = []
        
        for account in accounts:
            result = self.test_account_proxy(account["id"])
            result["account_id"] = account["id"]
            result["email"] = account["email"]
            all_results.append(result)
        
        # サマリー表示
        success_count = sum(1 for r in all_results if r.get("status") == "success")
        print(f"\n{'='*50}")
        print(f"テスト結果サマリー")
        print(f"{'='*50}")
        print(f"総アカウント数: {len(all_results)}")
        print(f"成功: {success_count}")
        print(f"失敗: {len(all_results) - success_count}")
        
        return {"results": all_results}
