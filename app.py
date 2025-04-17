import streamlit as st
import time
from full import ICliniq
import tempfile

class StreamlitApp:
    def __init__(self, icliniq_instance):
        self.icliniq = icliniq_instance
        self.setup_page_config()
        
    def setup_page_config(self):
        st.set_page_config(
            page_title="iCliniq Assistant",
            page_icon="🏥",
            layout="wide"
        )
        
    def run(self):
        st.title("iCliniq Medical Assistant")
        
        # Sidebar for authentication
        with st.sidebar:
            self.render_auth_section()
            
        # Main content area
        if self.icliniq.current_user is not None:
            self.render_main_interface()
        else:
            st.info("Please login to continue")
            
    def render_auth_section(self):
        st.sidebar.title("Authentication")
        
        if self.icliniq.current_user is None:
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Login")

                    if submit:
                        logged_in = self.icliniq.login(username, password)
                        print(f"Username: -{username}-, Password: -{password}-, logged_in: -{logged_in}-")  # Debugging line
                        if logged_in:
                            st.success("Login successful! Redirecting...")
                            time.sleep(1.5)
                            st.session_state.is_chat_active = True
                        else:
                            st.error("Invalid credentials")
                            
            with tab2:
                with st.form("register_form"):
                    new_username = st.text_input("New Username")
                    new_password = st.text_input("New Password", type="password")
                    submit = st.form_submit_button("Register")
                    
                    if submit:
                        if self.icliniq.register(new_username, new_password):
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Registration failed")
        else:
            st.sidebar.success(f"Logged in")
            if st.sidebar.button("Logout"):
                self.icliniq.logout()
                st.rerun()
                
    def render_main_interface(self):
        # Initialize session states if not exists
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'is_chat_active' not in st.session_state:
            st.session_state.is_chat_active = False
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # File upload section
        st.subheader("Upload Medical Documents")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "csv"])
        category = st.selectbox("Document Category", ["Medical Records", "Lab Reports", "Prescriptions"])
        
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                self.icliniq.upload_file(category, tmp_file.name)
            st.success("File uploaded successfully!")

        # Chat interface
        st.markdown("---")
        st.subheader("Chat with Assistant")
        
        # Start chat button
        if not st.session_state.is_chat_active:
            if st.button("Start Chat Session"):
                st.session_state.is_chat_active = True
                st.rerun()

        # Chat interface when active
        if st.session_state.is_chat_active:
            # Display chat history from session state
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input
            if prompt := st.chat_input("Type your message here..."):
                # Add user message to state
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Get AI response
                response = self.icliniq.chat(prompt)
                
                # Add assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": response})

            # Clear chat button
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Clear Chat"):
                    st.session_state.messages = []
                    st.rerun()

        # Data display section
        if not self.icliniq.extracted_df.empty:
            st.markdown("---")  # Add visual separator
            st.subheader("Extracted Data")
            st.dataframe(self.icliniq.extracted_df)
            
            # Data filtering and sorting
            if not self.icliniq.extracted_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Filter Data")
                    filter_column = st.selectbox("Select Column to Filter", self.icliniq.extracted_df.columns)
                    filter_condition = st.text_input("Enter Filter Condition")
                    if st.button("Apply Filter"):
                        filtered_data = self.icliniq.filter_file_data(filter_column, filter_condition)
                        st.dataframe(filtered_data)
                
                with col2:
                    st.subheader("Sort Data")
                    sort_column = st.selectbox("Select Column to Sort", self.icliniq.extracted_df.columns)
                    sort_order = st.checkbox("Ascending Order", value=True)
                    if st.button("Apply Sort"):
                        sorted_data = self.icliniq.sort_file_data(sort_column, sort_order)
                        st.dataframe(sorted_data)

if __name__ == "__main__":
    icliniq_instance = ICliniq()
    # icliniq_instance.login("sujit", "sujit")  # Replace with actual login logic
    app = StreamlitApp(icliniq_instance)
    app.run()