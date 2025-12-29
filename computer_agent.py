import os
import sys
import asyncio
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-2.0-flash-exp"
MAX_STEPS = 5

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY environment variable not set.")
    print("Please set it with: export GEMINI_API_KEY='your-api-key'")
    sys.exit(1)

# --- GEMINI SETUP ---
client = genai.Client(api_key=GEMINI_API_KEY)

async def run_agent(query: str):
    print(f"🚀 Starting agent for query: '{query}'")
    
    # Connection parameters for our MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["computer_mcp_server.py"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Initialize session
            await session.initialize()
            
            # 2. List tools to tell Gemini what we can do
            tools_response = await session.list_tools()
            available_tools = tools_response.tools
            
            # Convert MCP tools to Gemini tool definitions
            gemini_tools = []
            for tool in available_tools:
                gemini_tools.append({
                    "function_declarations": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    ]
                })

            # 3. Agent Loop
            history = [
                {
                    "role": "user",
                    "parts": [{"text": f"Task: {query}\n\nPlease use the provided tools to complete this task. Always start by launching the appropriate app."}]
                }
            ]
            
            step = 0
            while step < MAX_STEPS:
                step += 1
                print(f"\n--- 🧠 Step {step}/{MAX_STEPS} ---")
                
                # Call Gemini
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=history,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        temperature=0.0
                    )
                )
                
                # Check for tool calls
                tool_calls = []
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        tool_calls.append(part.function_call)
                
                if not tool_calls:
                    print("🏁 Agent finished or gave final answer:")
                    print(response.text)
                    break
                
                # Execute tool calls
                history.append(response.candidates[0].content)
                
                tool_results_parts = []
                for call in tool_calls:
                    print(f"🛠️ Calling tool: {call.name}({call.args})")
                    
                    try:
                        result = await session.call_tool(call.name, arguments=dict(call.args))
                        result_str = str(result.content[0].text) if result.content else "Success"
                        print(f"📊 Result: {result_str[:200]}...")
                        
                        tool_results_parts.append(
                            types.Part.from_function_response(
                                name=call.name,
                                response={"result": result_str}
                            )
                        )
                    except Exception as e:
                        print(f"❌ Tool error: {e}")
                        tool_results_parts.append(
                            types.Part.from_function_response(
                                name=call.name,
                                response={"error": str(e)}
                            )
                        )
                
                history.append(types.Content(role="function", parts=tool_results_parts))

async def test_mcp_connection():
    """Test connection to the MCP server without calling Gemini"""
    print("🔍 Testing MCP server connection...")
    server_params = StdioServerParameters(
        command="python",
        args=["computer_mcp_server.py"],
        env=os.environ.copy()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                print(f"✅ Connected! Available tools: {[t.name for t in tools_response.tools]}")
                return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python computer_agent.py \"Your task here\"")
        print("       python computer_agent.py --test-mcp")
        sys.exit(1)
    
    if sys.argv[1] == "--test-mcp":
        asyncio.run(test_mcp_connection())
    else:
        query = sys.argv[1]
        asyncio.run(run_agent(query))
