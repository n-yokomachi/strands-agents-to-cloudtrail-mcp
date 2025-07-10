import streamlit as st
from strands import Agent, tool
from strands.models import BedrockModel
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
from datetime import datetime
import pytz
import asyncio

st.set_page_config(
    page_title="Strands Agent with MCP Server on Lambda", 
    page_icon="🪢", 
)

st.title("🕵️‍♂️ AWS Detective Agent")
st.markdown("*https://github.com/n-yokomachi/strands-agents_and_mcp-on-lambda*")

if 'messages' not in st.session_state:
    st.session_state.messages = []

MCP_URL = "https://xuej2izzm6asams4zbvjchuptm0psutq.lambda-url.ap-northeast-1.on.aws/mcp"

@tool
def get_current_date(timezone: str = "Asia/Tokyo", format: str = "%Y-%m-%d %H:%M:%S"):
    tz = pytz.timezone(timezone)
    current_time = datetime.now(tz)
    return current_time.strftime(format)

bedrock_model = BedrockModel(
    model_id='apac.anthropic.claude-3-5-sonnet-20241022-v2:0',
    region_name='ap-northeast-1',
    temperature=0.7,
    max_tokens=4000
)

system_prompt = """あなたは親しみやすいAWSエキスパートです。
CloudTrailイベントの分析や、AWSリソースの監視に関する質問にお答えします。

私はClaude 3.5 Sonnet v2を使用しています。
複雑な問題について詳しく分析が必要な場合は、詳しく考えることができます。

利用可能なツール:
- lookup_cloudtrail_events: CloudTrailイベントを検索 (MCPサーバー経由)
- get_current_date: 現在の日付と時刻を取得

ユーザーがCloudTrailやAWSの活動について質問した場合は、適切なツールを使用してください。
現在の日付や時刻が必要な場合は、get_current_dateツールを使用してください。
日時を指定する際は、ISO 8601形式（例: "2025-07-10T00:00:00Z"）を使用してください。"""

async def stream_agent_response(agent, prompt: str, container):
    """エージェントの応答をストリーミング表示"""
    try:
        text_holder = container.empty()
        buffer = ""
        shown_tools = set()
        
        async for chunk in agent.stream_async(prompt):
            # ツール実行を検出して表示
            tool_id, tool_name = extract_tool_from_chunk(chunk)
            if tool_id and tool_name and tool_id not in shown_tools:
                shown_tools.add(tool_id)
                if buffer:
                    text_holder.markdown(buffer)
                    buffer = ""
                container.info(f"🛠️ *{tool_name}* ツール実行中")
                text_holder = container.empty()
            
            # テキストを抽出
            text = extract_text_from_chunk(chunk)
            
            if text:
                buffer += text
                text_holder.markdown(buffer + "🗕")
        
        # 最終表示
        if buffer:
            text_holder.markdown(buffer)
            return buffer
            
    except Exception as e:
        container.error(f"ストリーミングエラー: {str(e)}")
        # エラー時は通常実行にフォールバック
        response = agent(prompt)
        container.markdown(response)
        return response

def extract_tool_from_chunk(chunk):
    """チャンクからツール情報を抽出"""
    event = chunk.get('event', {})
    if 'contentBlockStart' in event:
        tool_use = event['contentBlockStart'].get('start', {}).get('toolUse', {})
        return tool_use.get('toolUseId'), tool_use.get('name')
    return None, None

def extract_text_from_chunk(chunk):
    """チャンクからテキストを抽出"""
    if text := chunk.get('data'):
        return text
    elif delta := chunk.get('delta', {}).get('text'):
        return delta
    return ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔考え中…"):
            mcp_client = MCPClient(lambda: streamablehttp_client(MCP_URL))
            with mcp_client:
                mcp_tools = mcp_client.list_tools_sync()
                all_tools = list(mcp_tools) + [get_current_date]
                
                agent = Agent(
                    model=bedrock_model,
                    tools=all_tools,
                    system_prompt=system_prompt
                )
                
                # 非同期実行でストリーミング
                loop = asyncio.new_event_loop()
                response = loop.run_until_complete(stream_agent_response(agent, prompt, st.container()))
                loop.close()
                
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})

with st.sidebar:
    st.header("Tool List")
    st.markdown("""
    - lookup_cloudtrail_events: CloudTrailイベントを検索 (MCP)
    - get_current_date: 現在の日付と時刻を取得
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun() 