import streamlit as st
import requests
import json

# Function to get a chat response from the OpenRouter API
def get_chat_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"  # API endpoint

    headers = {
        "Authorization": "Bearer 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",  # API key
        "HTTP-Referer": "https://www.sitename.com",  # Your site reference
        "X-Title": "SiteName",  # Your application title
        "Content-Type": "application/json"  # Content type
    }

    # Prepare the request payload
    data = {
        "model": "deepseek/deepseek-r1:free",  # Model selection
        "messages": [{"role": "user", "content": user_input}]  # User message
    }
    
    # Make a POST request to the API
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # Process the API response
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response received.")
    else:
        return f"Error: {response.status_code} - {response.text}"

# Function to create the chatbot UI using Streamlit
def chatbot_ui():
    st.title("🤖 AI Chatbot")  # Page title

    # Input field for the user's message
    user_input = st.text_input("Enter your message:")

    # Button to send the message
    if st.button("Send"):
        if user_input:  # Ensure the user has entered a message
            with st.spinner("Fetching response..."):  # Show a loading spinner
                response = get_chat_response(user_input)  # Get chatbot response
            st.markdown(response)  # Display the response
        else:
            st.warning("Please enter a message.")  # Show a warning if input is empty

# Run the chatbot UI function
chatbot_ui()
