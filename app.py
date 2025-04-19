import streamlit as st
import os
from full import ICliniq

st.set_page_config(
    page_title="iCliniq Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'icliniq' not in st.session_state:
    st.session_state.icliniq = ICliniq()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.markdown("""
    <style>
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e6f3ff;
    }
    .assistant-message {
        background-color: #f0f0f0;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🏥 iCliniq")
    
    if not st.session_state.logged_in:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Login"):
                if st.session_state.icliniq.login(username, password):
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        with col2:
            if st.button("Register"):
                if st.session_state.icliniq.register(username, password):
                    st.success("Registration successful!")
                else:
                    st.error("Username already exists")
    
    else:
        st.success("Logged in")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.icliniq.logout()
            st.session_state.messages = []
            st.rerun()
        
        st.subheader("Upload Medical Reports")
        uploaded_file = st.file_uploader("Choose a file", type=['png', 'jpg', 'jpeg', 'pdf', 'csv'])
        if uploaded_file:
            file_path = os.path.join("temp", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.icliniq.upload_file("medical_report", file_path)
            st.success("File uploaded and processed successfully!")

st.title("Medical Assistant Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.logged_in:
    if prompt := st.chat_input("What can I help you with?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.icliniq.chat(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Please login to start chatting")

if st.session_state.logged_in and st.session_state.messages:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.icliniq.start_new_chat()
        st.rerun()
