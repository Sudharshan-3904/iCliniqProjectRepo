import streamlit as st
from full import ICliniq

class ICliniqApp:
    def __init__(self):
        self.iclinique = ICliniq()
        self.chat_history = []

    def login(self):
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if self.iclinique.login(username, password):
                st.success("Login successful!")
            else:
                st.error("Login failed!")

    def register(self):
        st.subheader("Register")
        username = st.text_input("New Username", key="register_username")
        password = st.text_input("New Password", type="password", key="register_password")
        if st.button("Register"):
            if self.iclinique.register(username, password):
                st.success("Registration successful!")
            else:
                st.error("Registration failed!")

    def chat(self):
        st.subheader("Chat")
        user_input = st.text_input("Enter your message", key="chat_input")
        if st.button("Send"):
            response = self.iclinique.chat(user_input, "")
            self.chat_history.append({"role": "User", "content": user_input})
            self.chat_history.append({"role": "Bot", "content": response})
            st.write(f"Bot: {response}")
        if self.chat_history:
            st.subheader("Chat History")
            for msg in self.chat_history:
                st.write(f"{msg['role']}: {msg['content']}")

    def upload_file(self):
        st.subheader("Upload File")
        category = st.text_input("Enter file category", key="upload_category")
        if st.button("Upload"):
            self.iclinique.upload_file(category)
            st.success("File uploaded successfully!")

    def retrieve_file(self):
        st.subheader("Retrieve File")
        filename = st.text_input("Enter filename to retrieve", key="retrieve_filename")
        if st.button("Retrieve"):
            self.iclinique.retrieve_file(filename)
            st.success("File retrieved successfully!")

    def filter_data(self):
        st.subheader("Filter Data")
        column = st.text_input("Enter column name", key="filter_column")
        condition = st.text_input("Enter condition (e.g., > 5, == 'value')", key="filter_condition")
        if st.button("Filter"):
            result = self.iclinique.filter_file_data(column, condition)
            if result is not None:
                st.write(result)

    def sort_data(self):
        st.subheader("Sort Data")
        column = st.text_input("Enter column name", key="sort_column")
        ascending = st.checkbox("Sort ascending?", key="sort_ascending")
        if st.button("Sort"):
            result = self.iclinique.sort_file_data(column, ascending)
            if result is not None:
                st.write(result)

    def view_chat_history(self):
        st.subheader("View Chat History")
        history = self.iclinique.get_chat_history()
        for msg in history:
            st.write(f"{msg['role']}: {msg['content']}")

    def new_chat(self):
        if st.button("Start New Chat"):
            self.iclinique.start_new_chat()
            self.chat_history = []
            st.success("Started new chat session")

    def logout(self):
        if st.button("Logout"):
            self.iclinique.logout()
            st.success("Logged out successfully!")

    def run(self):
        st.title("iCliniq Streamlit App")
        menu = [
            "Login", "Register", "Chat", "Upload File", "Retrieve File",
            "Filter Data", "Sort Data", "View Chat History", "New Chat", "Logout"
        ]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            self.login()
        elif choice == "Register":
            self.register()
        elif choice == "Chat":
            self.chat()
        elif choice == "Upload File":
            self.upload_file()
        elif choice == "Retrieve File":
            self.retrieve_file()
        elif choice == "Filter Data":
            self.filter_data()
        elif choice == "Sort Data":
            self.sort_data()
        elif choice == "View Chat History":
            self.view_chat_history()
        elif choice == "New Chat":
            self.new_chat()
        elif choice == "Logout":
            self.logout()

if __name__ == "__main__":
    app = ICliniqApp()
    app.run()