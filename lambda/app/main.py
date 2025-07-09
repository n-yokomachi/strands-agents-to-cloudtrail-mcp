#!/usr/bin/env python3
"""
CloudTrail MCP Server - Lambda Web Adapter Layer対応版
"""
import json
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastmcp import FastMCP
import os

# FastMCP サーバーの初期化（stateless HTTP対応）
mcp = FastMCP(stateless_http=True, json_response=True)

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
        start_time: 検索開始時刻 (ISO 8601形式, 例: "2024-01-01T00:00:00Z")
        end_time: 検索終了時刻 (ISO 8601形式, 例: "2024-01-01T23:59:59Z")
        username: フィルターするユーザー名 (オプション)
        max_records: 取得する最大レコード数 (1-50, デフォルト: 50)
    
    Returns:
        Dict[str, Any]: CloudTrail イベントのリスト
    """
    try:
        cloudtrail = get_cloudtrail_client()
        
        # パラメータの準備
        lookup_params = {
            'StartTime': datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            'EndTime': datetime.fromisoformat(end_time.replace('Z', '+00:00')),
            'MaxItems': min(max_records, 50)  # APIの制限により最大50
        }
        
        # ユーザー名フィルターの追加（指定された場合のみ）
        if username:
            lookup_params['LookupAttributes'] = [
                {
                    'AttributeKey': 'Username',
                    'AttributeValue': username
                }
            ]
        
        # CloudTrail APIの実行
        response = cloudtrail.lookup_events(**lookup_params)
        
        return {
            'status': 'success',
            'events': response.get('Events', []),
            'next_token': response.get('NextToken'),
            'total_events': len(response.get('Events', []))
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error_message': str(e),
            'error_type': type(e).__name__
        }



# FastAPIアプリケーションを取得
app = mcp.http_app() 