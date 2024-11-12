
import streamlit as st
import requests

st.sidebar.markdown("## Chat Bot")
max_length = st.sidebar.slider("max_length", 0, 8192, 512, step=1)

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot")

API_URL = "http://localhost:5000/generate"

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "有什么可以帮您的？"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = requests.post(API_URL, json={
        'messages': st.session_state.messages,
        'max_length': max_length
    }).json()

    st.session_state.messages.append({"role": "assistant", "content": response['response']})
    st.chat_message("assistant").write(response['response'])

    # # streamlit run frontend.py --server.address 192.168.xxxxxx --server.port 6006