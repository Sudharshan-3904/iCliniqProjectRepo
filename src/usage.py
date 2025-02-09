from full import IClinique
import sys

def display_menu():
    print("\n=== iClinique CLI ===")
    print("1. Login")
    print("2. Register")
    print("3. Chat")
    print("4. Upload File") 
    print("5. Retrieve File")
    print("6. Filter Data")
    print("7. Sort Data")
    print("8. View Chat History")
    print("9. New Chat")
    print("10. Logout")
    print("0. Exit")

def main():
    iclinique = IClinique()
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (0-10): ")

        if choice == "0":
            sys.exit(0)
            
        elif choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            if iclinique.login(username, password):
                print("Login successful!")
            else:
                print("Login failed!")
                
        elif choice == "2":
            username = input("New username: ")
            password = input("New password: ")
            if iclinique.register(username, password):
                print("Registration successful!")
            else:
                print("Registration failed!")
                
        elif choice == "3":
            user_input = input("Enter your message: ")
            response = iclinique.chat(user_input)
            print(f"Bot: {response}")
            
        elif choice == "4":
            category = input("Enter file category: ")
            iclinique.upload_file(category)
            
        elif choice == "5":
            filename = input("Enter filename to retrieve: ")
            iclinique.retrieve_file(filename)
            
        elif choice == "6":
            column = input("Enter column name: ")
            condition = input("Enter condition (e.g. > 5, == 'value'): ")
            result = iclinique.filter_file_data(column, condition)
            if result is not None:
                print(result)
            
        elif choice == "7":
            column = input("Enter column name: ")
            ascending = input("Sort ascending? (y/n): ").lower() == 'y'
            result = iclinique.sort_file_data(column, ascending)
            if result is not None:
                print(result)
            
        elif choice == "8":
            history = iclinique.get_chat_history()
            for msg in history:
                print(f"{msg['role']}: {msg['content']}")
            
        elif choice == "9":
            iclinique.start_new_chat()
            print("Started new chat session")
            
        elif choice == "10":
            iclinique.logout()
            print("Logged out successfully")

if __name__ == "__main__":
    main()
