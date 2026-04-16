import streamlit as st
import asyncio
import os
import yaml
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, AgentGroupChat
from semantic_kernel.agents.strategies import KernelFunctionTerminationStrategy, SequentialSelectionStrategy
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.contents import ChatMessageContent, AuthorRole

# --- INITIALIZATION ---
load_dotenv(override=True)
st.set_page_config(page_title="Agent Studio", layout="wide")

# Persistent state for Kernel and Agents
if "group_chat" not in st.session_state:
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-08-01-preview"
    ))
    
    with open("config/agents.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    agents = [ChatCompletionAgent(
        service=kernel.get_service(type=AzureChatCompletion),
        name=a["name"],
        description=a["description"],
        instructions=a["instructions"]
    ) for a in config["agents"]]

    term_func = kernel.add_function(
        plugin_name="Strategy", function_name="Term",
        prompt_template_config=PromptTemplateConfig(
            template="Return 'true' if the last message contains 'TERMINATE'. History: {{$_history_}}",
            template_format="semantic-kernel",
            allow_dangerously_set_content=True
        )
    )

    st.session_state.group_chat = AgentGroupChat(
        agents=agents,
        selection_strategy=SequentialSelectionStrategy() # ,
        #termination_strategy=KernelFunctionTerminationStrategy(
         #   function=term_func, kernel=kernel, 
          #  result_parser=lambda r: "true" in str(r.value).lower(),
           # history_variable_name="_history_", maximum_iterations=10 
       # )
    )
    st.session_state.messages = []

# --- SIDEBAR & BUTTONS ---
st.sidebar.title("Example Tasks")
click_prompt = None
if st.sidebar.button("🔐 AES Encryption"):
    click_prompt = "Build a Python script for AES encryption."
if st.sidebar.button("🗄️ SQL Schema"):
    click_prompt = "Design a SQL schema for a retail store."
if st.sidebar.button("🗑️ Clear History"):
    st.session_state.messages = []
    st.rerun()

# --- MAIN UI ---
st.title("🤝 Multi-Agent Collaboration")

# 1. Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(f"**{msg['name']}**: {msg['content']}")
#1.b agents message duplicate check
def get_similarity(s1, s2):
    """Calculates word overlap between two strings (0.0 to 1.0)"""
    words1 = set(s1.lower().split())
    words2 = set(s2.lower().split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0

# 2. Logic Function (Async for AI, Sync for UI)
async def run_agent_logic(user_goal):
    # This placeholder shows progress in the sidebar
    status_placeholder = st.sidebar.status("🤖 Agents thinking...", expanded=True)
    
        # 1. Check if the USER said TERMINATE
    if "TERMINATE" in user_goal.upper():
        st.sidebar.success("Chat Ended by User.")
        st.stop() # This kills the Streamlit run for this turn
    await st.session_state.group_chat.add_chat_message(
        ChatMessageContent(role=AuthorRole.USER, content=user_goal)
    )
    
    collected_responses = []
    async for msg in st.session_state.group_chat.invoke():
        content = msg.content.strip()
          # 1. COMPARE TO PREVIOUS MESSAGE
        # We check the similarity between this agent's message and the last one added
        last_msg_content = ""
        if collected_responses:
            last_msg_content = collected_responses[-1]["content"]
        elif st.session_state.messages:
            last_msg_content = st.session_state.messages[-1]["content"]

        similarity_score = get_similarity(content, last_msg_content)

         # 2. THE "PRO" GUARD: Skip if similarity is too high (> 0.7)
        # Also skip if it's very short (often just polite filler)
        if similarity_score > 0.7 or (len(content) < 60 and similarity_score > 0.4):
            st.sidebar.write(f"🚫 Skipped duplicate from {msg.name}")
            continue

        collected_responses.append({"name": msg.name, "content": content})
        status_placeholder.write(f"Active: {msg.name}")
       
    
    status_placeholder.update(label="✅ Task Finished", state="complete", expanded=False)
    return collected_responses

# 3. Handle Inputs
user_input = st.chat_input("Enter your goal...")
active_prompt = user_input or click_prompt

if active_prompt:
    # Add User Message to UI
    st.session_state.messages.append({"role": "user", "name": "User", "content": active_prompt})
    with st.chat_message("user"):
        st.write(active_prompt)

    # RUN AGENTS
    new_responses = asyncio.run(run_agent_logic(active_prompt))
    
    # Render Agent Responses
    for r in new_responses:
        st.session_state.messages.append({"role": "assistant", "name": r["name"], "content": r["content"]})
        with st.chat_message("assistant"):
            st.write(f"**{r['name'].upper()}**: {r['content']}")
