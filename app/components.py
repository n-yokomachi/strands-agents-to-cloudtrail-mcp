def get_link_icons_html():
    """リンクアイコンのHTMLを返す関数"""
    return """
    <div style="display: flex; justify-content: space-around; align-items: center; margin: 16px 0;">
        <a href="https://github.com/n-yokomachi/aws-detective-agent" target="_blank" style="text-decoration: none; color: inherit;">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
        </a>
        <a href="https://x.com/_cityside" target="_blank" style="text-decoration: none; color: inherit;">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path d="M12.6.75h2.454l-5.36 6.142L16 15.25h-4.937l-3.867-5.07-4.425 5.07H.316l5.733-6.57L0 .75h5.063l3.495 4.633L12.6.75Zm-.86 13.028h1.36L4.323 2.145H2.865l8.875 11.633Z"/>
            </svg>
        </a>
        <a href="https://zenn.dev/yokomachi/articles/20250624_strands_agents_and_mcp_on_lambda" target="_blank" style="text-decoration: none; color: inherit;">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                <path d="M.264 23.771h4.984c.264 0 .498-.147.645-.352L19.614.874c.176-.293-.029-.645-.381-.645h-4.72c-.235 0-.44.117-.557.323L.03 23.361c-.088.176.029.41.234.41zM17.445 23.419l6.479-10.408c.176-.293-.029-.645-.381-.645h-4.688c-.235 0-.44.117-.557.323l-6.655 10.643c-.088.176.029.41.234.41h4.984c.264 0 .498-.147.645-.352z"/>
            </svg>
        </a>
    </div>
    """

def get_tool_list_html():
    """ツールリストのHTMLを返す関数"""
    return """
    <div style="margin: 16px 0;">
        <div style="margin-bottom: 12px; padding: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; border-left: 4px solid #FF6B6B;">
            <strong style="font-size: 14px; color: #FF6B6B;">lookup_cloudtrail_events</strong>
            <div style="font-size: 12px; color: #888; margin-top: 2px;">CloudTrailイベントを検索 (MCP)</div>
        </div>
        <div style="margin-bottom: 12px; padding: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; border-left: 4px solid #4ECDC4;">
            <strong style="font-size: 14px; color: #4ECDC4;">get_current_date</strong>
            <div style="font-size: 12px; color: #888; margin-top: 2px;">現在の日付と時刻を取得</div>
        </div>
    </div>
    """ 