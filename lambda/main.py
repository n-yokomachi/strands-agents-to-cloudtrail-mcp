import json
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastmcp import FastMCP
import os

# FastMCP サーバーの初期化
mcp = FastMCP(
    name="CloudTrail MCP Server",
    dependencies=["boto3", "fastmcp"]
)

# CloudTrail クライアントの初期化
def get_cloudtrail_client():
    """CloudTrailクライアントを作成"""
    region = os.environ.get('AWS_REGION', 'ap-northeast-1')
    return boto3.client('cloudtrail', region_name=region)

@mcp.tool
def lookup_cloudtrail_events(
    start_time: str,
    end_time: str,
    username: Optional[str] = None,
    max_records: int = 50
) -> Dict[str, Any]:
    """
    CloudTrail APIのlookup_eventsを実行してイベント履歴を取得
    
    Note: CloudTrail APIの制限により、LookupAttributesには1つの属性のみ指定可能です。
    
    Args:
        start_time: 開始時間（ISO 8601形式: YYYY-MM-DDTHH:MM:SSZ）
        end_time: 終了時間（ISO 8601形式: YYYY-MM-DDTHH:MM:SSZ）
        username: 特定のユーザー名でフィルタリング（オプション）
        max_records: 取得する最大レコード数（デフォルト50）
    
    Returns:
        CloudTrailイベントのJSON辞書
    """
    try:
        client = get_cloudtrail_client()
        
        # 時間文字列をdatetimeオブジェクトに変換
        start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # lookup_eventsのパラメータを構築
        lookup_params = {
            'StartTime': start_datetime,
            'EndTime': end_datetime,
            'MaxResults': max_records
        }
        
        # ユーザー名が指定されている場合はLookupAttributesに追加（1つのみ）
        if username:
            lookup_params['LookupAttributes'] = [
                {
                    'AttributeKey': 'Username',
                    'AttributeValue': username
                }
            ]
        
        # CloudTrail API呼び出し
        response = client.lookup_events(**lookup_params)
        
        # レスポンスを整形
        events = []
        for event in response.get('Events', []):
            event_dict = {
                'EventTime': event.get('EventTime').isoformat() if event.get('EventTime') else None,
                'EventName': event.get('EventName'),
                'EventSource': event.get('EventSource'),
                'Username': event.get('Username'),
                'UserIdentity': event.get('UserIdentity', {}),
                'SourceIPAddress': event.get('SourceIPAddress'),
                'Resources': event.get('Resources', []),
                'CloudTrailEvent': json.loads(event.get('CloudTrailEvent', '{}'))
            }
            events.append(event_dict)
        
        return {
            'success': True,
            'events_count': len(events),
            'events': events,
            'next_token': response.get('NextToken'),
            'query_params': {
                'start_time': start_time,
                'end_time': end_time,
                'username': username,
                'max_records': max_records
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'query_params': {
                'start_time': start_time,
                'end_time': end_time,
                'username': username,
                'max_records': max_records
            }
        }

@mcp.tool
def get_cloudtrail_event_names(
    start_time: str,
    end_time: str,
    username: Optional[str] = None
) -> Dict[str, Any]:
    """
    指定期間内のCloudTrailイベント名の一覧を取得
    
    Args:
        start_time: 開始時間（ISO 8601形式: YYYY-MM-DDTHH:MM:SSZ）
        end_time: 終了時間（ISO 8601形式: YYYY-MM-DDTHH:MM:SSZ）
        username: 特定のユーザー名でフィルタリング（オプション）
    
    Returns:
        イベント名と発生回数の辞書
    """
    try:
        # 全イベントを取得
        events_response = lookup_cloudtrail_events(
            start_time=start_time,
            end_time=end_time,
            username=username,
            max_records=200
        )
        
        if not events_response['success']:
            return events_response
        
        # イベント名を集計
        event_names = {}
        for event in events_response['events']:
            event_name = event.get('EventName', 'Unknown')
            event_names[event_name] = event_names.get(event_name, 0) + 1
        
        return {
            'success': True,
            'event_names': event_names,
            'total_events': len(events_response['events']),
            'query_params': {
                'start_time': start_time,
                'end_time': end_time,
                'username': username
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

@mcp.resource("cloudtrail://status")
def get_cloudtrail_status() -> str:
    """
    CloudTrail MCP サーバーの状態を取得
    
    Returns:
        サーバーの状態情報
    """
    try:
        client = get_cloudtrail_client()
        # 簡単な接続テスト
        client.describe_trails()
        return json.dumps({
            'status': 'healthy',
            'region': os.environ.get('AWS_REGION', 'ap-northeast-1'),
            'server_name': 'CloudTrail MCP Server'
        })
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        })

# Lambda Web Adapter対応
if __name__ == "__main__":
    # Lambda Web Adapter使用時
    port = int(os.environ.get('PORT', 8000))
    mcp.run(transport="http", port=port, host="0.0.0.0") 