import asyncio
from fastmcp import Client

async def test_cloudtrail_mcp():
    """CloudTrail MCPサーバーをテスト"""
    print("🚀 CloudTrail MCP サーバーのテスト開始...")
    
    # ローカルサーバーに接続
    async with Client("http://localhost:8000/mcp") as client:
        print("✅ サーバーに接続成功!")
        
        # 利用可能なツールの一覧を取得
        print("\n📋 利用可能なツール:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # 利用可能なリソースの一覧を取得
        print("\n📋 利用可能なリソース:")
        resources = await client.list_resources()
        for resource in resources:
            print(f"  - {resource.uri}: {resource.description}")
        
        # ステータスリソースをテスト
        print("\n🔍 ステータスリソースのテスト:")
        try:
            status_result = await client.read_resource("cloudtrail://status")
            print(f"  Status: {status_result.text}")
        except Exception as e:
            print(f"  エラー: {e}")
        
        # CloudTrailツールをテスト（実際のAWS認証が必要）
        print("\n🔍 CloudTrailツールのテスト:")
        try:
            # 過去1時間のイベントを取得（テスト用）
            from datetime import datetime, timezone, timedelta
            
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=1)
            
            result = await client.call_tool("lookup_cloudtrail_events", {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "max_records": 5
            })
            
            print(f"  結果: {result.text[:200]}...")
            
        except Exception as e:
            print(f"  エラー（AWS認証が必要）: {e}")
        
        print("\n🎉 テスト完了!")

if __name__ == "__main__":
    asyncio.run(test_cloudtrail_mcp()) 