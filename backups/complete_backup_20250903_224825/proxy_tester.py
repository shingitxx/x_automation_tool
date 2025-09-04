import requests
import json
from typing import Dict, Optional, List
import time
from account_manager import AccountManager

class ProxyTester:
    """プロキシ接続をテストするクラス"""
    
    def __init__(self):
        self.manager = AccountManager()
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://ipinfo.io/json",
        ]
    
    def test_proxy(self, proxy_url: str, timeout: int = 10) -> Dict:
        """単一プロキシをテスト"""
        results = {
            "proxy_url": proxy_url,
            "status": "unknown",
            "ip_address": None,
            "response_time": None,
            "error": None
        }
        
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        # プロキシURLから認証情報を隠して表示
        display_url = proxy_url.split('@')[1] if '@' in proxy_url else proxy_url
        print(f"\nプロキシをテスト中: {display_url}")
        print("-" * 50)
        
        for test_url in self.test_urls:
            try:
                print(f"テストURL: {test_url}")
                start_time = time.time()
                
                # プロキシ経由でリクエスト
                response = requests.get(
                    test_url,
                    proxies=proxies,
                    timeout=timeout
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # IPアドレスを取得
                    if "ip" in data:
                        ip_address = data["ip"]
                    elif "origin" in data:
                        ip_address = data["origin"]
                    else:
                        ip_address = str(data)
                    
                    results["status"] = "success"
                    results["ip_address"] = ip_address
                    results["response_time"] = round(response_time, 2)
                    
                    print(f"✓ 成功 - IP: {ip_address} (応答時間: {results['response_time']}秒)")
                    break
                else:
                    print(f"✗ HTTPエラー: {response.status_code}")
                    
            except requests.exceptions.ProxyError as e:
                results["error"] = f"プロキシエラー: {str(e)[:50]}"
                print(f"✗ プロキシエラー")
            except requests.exceptions.ConnectionError as e:
                results["error"] = f"接続エラー: {str(e)[:50]}"
                print(f"✗ 接続エラー")
            except requests.exceptions.Timeout:
                results["error"] = "タイムアウト"
                print(f"✗ タイムアウト")
            except Exception as e:
                results["error"] = f"エラー: {str(e)[:50]}"
                print(f"✗ エラー: {str(e)[:50]}")
        
        if results["status"] != "success":
            results["status"] = "failed"
            print(f"\n✗ プロキシテスト失敗")
            if results["error"]:
                print(f"  エラー: {results['error']}")
        
        return results
    
    def test_account_proxy(self, account_id: int) -> Dict:
        """アカウントのプロキシをテスト"""
        print(f"\nアカウントID {account_id} を検索中...")
        account = self.manager.get_account_by_id(account_id)
        if not account:
            # 利用可能なアカウントIDを表示
            available_ids = [acc["id"] for acc in self.manager.accounts.get("accounts", [])]
            print(f"  ✗ ID={account_id} のアカウントが見つかりません")
            print(f"  利用可能なID: {available_ids}")
            return {"status": "error", "error": f"アカウントID {account_id} が見つかりません"}
        
        proxy_url = self.manager.get_proxy_url(account_id)
        print(f"\nアカウント: [{account_id}] {account['email']}")
        
        return self.test_proxy(proxy_url)
    
    def test_all_accounts(self) -> List[Dict]:
        """全アカウントのプロキシをテスト"""
        accounts = self.manager.get_account_list()
        results = []
        
        print("\n" + "="*60)
        print(" 全アカウントのプロキシテスト")
        print("="*60)
        
        for i, account in enumerate(accounts, 1):
            print(f"\n[{i}/{len(accounts)}] テスト中...")
            result = self.test_account_proxy(account['id'])
            result['account_id'] = account['id']
            result['email'] = account['email']
            results.append(result)
            
            if i < len(accounts):
                print("\n次のテストまで2秒待機...")
                time.sleep(2)
        
        # 結果サマリー
        print("\n" + "="*60)
        print(" テスト結果サマリー")
        print("="*60)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        print(f"成功: {success_count}/{len(results)}")
        print(f"失敗: {failed_count}/{len(results)}")
        
        if failed_count > 0:
            print("\n失敗したアカウント:")
            for result in results:
                if result['status'] != 'success':
                    print(f"  - [{result['account_id']}] {result['email']}: {result.get('error', 'Unknown error')}")
        
        return results

def test_single_proxy():
    """単一プロキシの手動テスト"""
    print("\nプロキシ情報を入力してください:")
    host = input("ホスト: ")
    port = input("ポート: ")
    username = input("ユーザー名: ")
    password = input("パスワード: ")
    
    proxy_url = f"http://{username}:{password}@{host}:{port}"
    
    tester = ProxyTester()
    result = tester.test_proxy(proxy_url)
    
    if result['status'] == 'success':
        print(f"\n✓ プロキシは正常に動作しています！")
        print(f"  接続先IP: {result['ip_address']}")
    else:
        print(f"\n✗ プロキシ接続に失敗しました")
    
    return result
