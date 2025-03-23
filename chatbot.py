import streamlit as st
import requests
import json

def get_chat_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "HTTP-Referer": "https://www.sitename.com",
        "X-Title": "SiteName",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": user_input}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response received.")
    else:
        return f"Error: {response.status_code} - {response.text}"

def chatbot_ui():
    st.title("🤖 AI Chatbot")
    user_input = st.text_input("Enter your message:")
    if st.button("Send"):
        if user_input:
            with st.spinner("Fetching response..."):
                response = get_chat_response(user_input)
            st.markdown(response)
        else:
            st.warning("Please enter a message.")