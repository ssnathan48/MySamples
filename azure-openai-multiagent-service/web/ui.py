import streamlit as st
import requests

st.title("Azure Foundry Multi-Agent Team")

target = st.sidebar.selectbox("Agent Mode", ["manager", "researcher", "writer", "team"])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "user_123"

if st.sidebar.button("Clear History"):
    st.session_state.messages = []

# 1. Render history FIRST so it stays on screen
for msg in st.session_state.messages:
    role = msg.get("role", "assistant")
    with st.chat_message(role):
        if role == "user":
            st.write(msg["content"])
        else:
            agent_label = msg.get("agent", "assistant").upper()
            st.write(f"**[{agent_label}]** {msg['content']}")

# 2. Chat Input
user_query = st.chat_input("Send a message...")

if user_query:
    # Add User Message to UI
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # API Call
    endpoint = "team/colloborate" if target == "team" else f"agent/{target}"
    try:
        response = requests.post(
            f"http://localhost:8000/{endpoint}",
            params={"session_id": st.session_state.session_id, "user_input": user_query}
        )
        res = response.json()

        # Add Assistant Message to UI
        # Note: We match the backend keys: "agent" and "content"
        new_msg = {"role": "assistant", "agent": res["agent"], "content": res["reply"]}
        st.session_state.messages.append(new_msg)
        
        with st.chat_message("assistant"):
            st.write(f"**[{res['agent'].upper()}]** {res['reply']}")
            
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")