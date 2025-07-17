import streamlit as st
from strands import Agent, tool
from strands.models import BedrockModel
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
from datetime import datetime
import pytz
import asyncio
import os
from components import get_link_icons_html, get_tool_list_html

st.set_page_config(
    page_title="Strands Agent with MCP Server on Lambda", 
    page_icon="🪢", 
)

st.title("🪢 AWS Detective Agent")

with st.sidebar:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("### Link")
    st.markdown(get_link_icons_html(), unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### Tool List")
    st.markdown(get_tool_list_html(), unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []

MCP_URL = os.environ["MCP_URL"]

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

system_prompt = """あなたは親しみやすいAWSエキスパート兼探偵です。
CloudTrailイベントの分析や、AWSリソースの監視に関する質問にお答えします。
口調は小説の探偵のようにして、敬語は使わないでください。
例）「よかろう」「まずは今日の日時をはっきりさせよう」「それでは調査を開始しよう」「○○さんの操作履歴だが、おおよそこんなものだろう」

利用可能なツール:
- lookup_cloudtrail_events: CloudTrailイベントを検索 (MCPサーバー経由)
- get_current_date: 現在の日付と時刻を取得

ユーザーがCloudTrailやAWSの活動について質問した場合は、適切なツールを使用してください。
現在の日付や時刻が必要な場合は、get_current_dateツールを使用してください。
日時を指定する際は、ISO 8601形式（例: "2025-07-10T00:00:00Z"）を使用してください。
CloudTrailから取得した情報の日時については、UTC時間のため、+9時間して日本時間に直してください。
また、CloudTrailから取得した情報にIPアドレスが含まれる場合、絶対にそれを表示しないでください。
"""

async def stream_agent_response(agent, prompt: str, container):
    """エージェントの応答をストリーミング"""
    try:
        text_holder = container.empty()
        text_buffer = ""
        displayed_tools = set()
        
        async for event in agent.stream_async(prompt):

            if "data" in event:
                text_buffer += event['data']
                text_holder.markdown(text_buffer + "🗕")

            if "current_tool_use" in event and event["current_tool_use"].get("name"):
                tool_name = event['current_tool_use']['name']
                if(tool_name not in displayed_tools):
                    displayed_tools.add(tool_name)
                
                    if text_buffer:
                        text_holder.markdown(text_buffer)
                        text_buffer = ""
                    
                    container.info(f"🔍 *{tool_name}* ツール実行中")
                    text_holder = container.empty()
        
        if text_buffer:
            text_holder.markdown(text_buffer)
            return text_buffer
            
    except Exception as e:
        container.error(f"ストリーミングエラー: {str(e)}")
        fallback_response = agent(prompt)
        container.markdown(fallback_response)
        return fallback_response

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🕵️‍♂️調査中…"):
            mcp_client = MCPClient(lambda: streamablehttp_client(MCP_URL))
            with mcp_client:
                mcp_tools = mcp_client.list_tools_sync()
                all_tools = list(mcp_tools) + [get_current_date]
                
                agent = Agent(
                    model=bedrock_model,
                    tools=all_tools,
                    system_prompt=system_prompt
                )
                
                # エージェントの応答をストリーミング
                loop = asyncio.new_event_loop()
                response = loop.run_until_complete(stream_agent_response(agent, prompt, st.container()))
                loop.close()
                
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response}) 