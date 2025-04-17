import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from full import ICliniq

class ICliniqueChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("iClinique Chat System")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")
        
        self.iclinique = ICliniq()
        self.selected_files = []
        self.create_widgets()

        root.bind("<Return>", lambda event: self.send_message())
        root.bind("<Control-l>", lambda event: self.show_login())
        root.bind("<Control-n>", lambda event: self.new_chat())
        # root.bind("<Control-Shift-l>", lambda event: self.logout())
        # root.bind("<Control-r>", lambda event: self.show_register())

    def create_widgets(self):
        sidebar = tk.Frame(self.root, bg="#2c3e50", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        nav_buttons = [
            ("Login", self.show_login),
            ("Register", self.show_register),
            ("Chat", self.show_chat),
            ("Upload File", self.select_files),
            ("Retrieve File", self.retrieve_file),
            ("Filter Data", self.filter_data),
            ("Sort Data", self.sort_data),
            ("Chat History", self.view_history),
            ("New Chat", self.new_chat),
            ("Logout", self.logout)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(sidebar, text=text, command=command,
                          bg="#34495e", fg="white", font=("Arial", 10, "bold"),
                          bd=0, width=20, height=2)
            btn.pack(pady=5)
            
        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.chat_frame = tk.Frame(self.main_frame, bg="#ffffff")
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD,
                                                 width=70, height=20,
                                                 font=("Arial", 11))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.input_frame = tk.Frame(self.main_frame, bg="#ffffff")
        self.message_input = tk.Entry(self.input_frame, font=("Arial", 11),
                                    width=50)
        self.message_input.pack(side=tk.LEFT, padx=10, pady=10)
        
        upload_button = tk.Button(self.input_frame, text="Upload File",
                                  command=self.select_files,
                                  bg="#3498db", fg="white",
                                  font=("Arial", 10, "bold"))
        upload_button.pack(side=tk.LEFT, padx=5, pady=10)
        
        send_button = tk.Button(self.input_frame, text="Send",
                              command=self.send_message,
                              bg="#2ecc71", fg="white",
                              font=("Arial", 10, "bold"))
        send_button.pack(side=tk.LEFT, padx=5, pady=10)
        
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.input_frame.pack(fill=tk.X)
        
    def select_files(self):
        file_path = filedialog.askopenfilename(title="Select Files")
        print(file_path)
        if file_path:
            self.iclinique.upload_file(file_path)
            # self.iclinique.uploaded_file_path = file_path
            messagebox.showinfo("Success", f"Selected {file_path}")

    def send_message(self):
        message = self.message_input.get()
        if message:
            self.chat_area.insert(tk.END, f"You: {message}\n")
            response = self.iclinique.chat(message)
            self.chat_area.insert(tk.END, f"Bot: {response}\n")
            self.message_input.delete(0, tk.END)
            self.chat_area.see(tk.END)
            self.selected_files = []

    def show_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("300x150")
        
        tk.Label(login_window, text="Username:").pack(pady=5)
        username_entry = tk.Entry(login_window)
        username_entry.pack(pady=5)
        
        tk.Label(login_window, text="Password:").pack(pady=5)
        password_entry = tk.Entry(login_window, show="*")
        password_entry.pack(pady=5)
        
        def login():
            username = username_entry.get()
            password = password_entry.get()
            if self.iclinique.login(username, password):
                messagebox.showinfo("Success", "Login successful!")
                login_window.destroy()
            else:
                messagebox.showerror("Error", "Login failed!")
        
        tk.Button(login_window, text="Login", command=login).pack(pady=10)
    
    def show_register(self):
        pass
    
    def show_chat(self):
        self.chat_frame.tkraise()
    
    def retrieve_file(self):
        pass
    
    def filter_data(self):
        pass
    
    def sort_data(self):
        pass
    
    def view_history(self):
        history = self.iclinique.get_chat_history()
        self.chat_area.delete(1.0, tk.END)
        for msg in history:
            self.chat_area.insert(tk.END, f"{msg['role']}: {msg['content']}\n\n")

    def new_chat(self):
        self.iclinique.start_new_chat()
        self.chat_area.delete(1.0, tk.END)
        messagebox.showinfo("Success", "Started new chat session")

    def logout(self):
        self.iclinique.logout()
        messagebox.showinfo("Success", "Logged out successfully")

def main():
    root = tk.Tk()
    app = ICliniqueChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
