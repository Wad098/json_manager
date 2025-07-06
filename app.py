import json
from json_manager import JSONManager

class Application:
    def __init__(self, json_file, checkpoint_file="checkpoints.json"):
        """
        Initialize the Application with JSONManager.
        """
        self.manager = JSONManager(json_file, checkpoint_file)

    def start(self):
        """
        Start the CLI application.
        """
        print("Welcome to JSON Manager CLI!")
        while True:
            print("\nAvailable operations:")
            print("1. Update a value")
            print("2. Append an object to an array")
            print("3. Remove an object from an array")
            print("4. Exit")
            choice = input("Enter your choice (1-4): ")

            if choice == "1":
                self.update_value()
            elif choice == "2":
                self.append_object()
            elif choice == "3":
                self.remove_object()
            elif choice == "4":
                print("Exiting JSON Manager CLI. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def update_value(self):
        """
        Update a value in the JSON data.
        """
        checkpoint_name = input("Enter the checkpoint name: ")
        new_value = input("Enter the new value: ")
        try:
            old_value, updated_value = self.manager.update_value(checkpoint_name, new_value)
            self.manager.save_to_file()
            print(f"Updated '{checkpoint_name}' from '{old_value}' to '{updated_value}'.")
        except ValueError as e:
            print(f"Error: {e}")

    def append_object(self):
        """
        Append a JSON object to an array in the JSON data.
        """
        checkpoint_name = input("Enter the checkpoint name: ")
        try:
            new_object = json.loads(input("Enter the JSON object to append (e.g., {\"key\": \"value\"}): "))
            index_field = input("Enter the index field (default is 'index'): ") or None
            position = input("Enter the position to insert the object (leave empty for end): ") or None
            # self.manager.append_object_to_array(checkpoint_name, new_object)
            self.manager.insert_object_to_array_index(checkpoint_name, new_object, position=position, index_field=index_field)
            self.manager.save_to_file()
            print(f"Appended object to '{checkpoint_name}': {new_object}.")
        except ValueError as e:
            print(f"Error: {e}")
        except json.JSONDecodeError:
            print("Invalid JSON format. Please try again.")

    def remove_object(self):
        """
        Remove a JSON object from an array in the JSON data.
        """
        checkpoint_name = input("Enter the checkpoint name: ")
        index = int(input("Enter the index of the object to remove: "))
        index_field = input("Enter the index field (default is 'index'): ") or None
        try:
            removed_object = self.manager.delete_object_from_array(checkpoint_name, index, index_field=index_field)
            self.manager.save_to_file()
            print(f"Removed object from '{checkpoint_name}': {removed_object}.")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Initialize the application with the JSON file and checkpoint file
    app = Application("example.json", "checkpoints.json")
    app.start()