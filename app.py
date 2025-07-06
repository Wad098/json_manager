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
            print("4. Add a checkpoint")
            print("5. Exit")
            choice = input("Enter your choice (1-5): ")

            if choice == "1":
                self.update_value()
            elif choice == "2":
                self.append_object()
            elif choice == "3":
                self.remove_object()
            elif choice == "4":
                self.add_checkpoint()
            elif choice == "5":
                print("Exiting JSON Manager CLI. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def add_checkpoint(self):
        """
        Add a checkpoint by selecting a path from the JSON structure.
        """
        def collect_json_paths(data, prefix=""):
            """
            Recursively collect all JSON paths in a list.
            """
            paths = []
            if isinstance(data, dict):
                for key, value in data.items():
                    paths.extend(collect_json_paths(value, prefix + key + "/"))
            elif isinstance(data, list):
                paths.append(prefix + "[Array]")
            else:
                paths.append(prefix + "[Value]")
            return paths

        print("Current JSON structure:")
        paths = collect_json_paths(self.manager.data)
        for i, path in enumerate(paths):
            print(f"{i + 1}. {path}")

        try:
            choice = int(input("Select a path by number: ")) - 1
            if choice < 0 or choice >= len(paths):
                print("Invalid choice. Please try again.")
                return

            selected_path = paths[choice].replace(
                "[Array]", "").replace("[Value]", "").rstrip("/")
            checkpoint_name = input("Enter the checkpoint name: ")
            json_path = "$." + selected_path.replace("/", ".")
            self.manager.add_checkpoint(checkpoint_name, json_path)
            self.manager.save_checkpoints()
            print(
                f"Checkpoint '{checkpoint_name}' added for path '{json_path}'.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"Error: {e}")

    def append_object(self):
        """
        Append a JSON object to an array in the JSON data.
        """
        print("Available checkpoints pointing to lists:")
        checkpoints = [
            checkpoint_name for checkpoint_name, path in self.manager.checkpoints.items()
            if isinstance(self.manager._get_value(path), list)
        ]
        if not checkpoints:
            print("No checkpoints pointing to lists are available.")
            return

        for i, checkpoint_name in enumerate(checkpoints):
            print(f"{i + 1}. {checkpoint_name}")

        try:
            choice = int(input("Select a checkpoint by number: ")) - 1
            if choice < 0 or choice >= len(checkpoints):
                print("Invalid choice. Please try again.")
                return

            checkpoint_name = checkpoints[choice]
            new_object = json.loads(
                input("Enter the JSON object to append (e.g., {\"key\": \"value\"}): "))
            index_field = input(
                "Enter the index field (default is 'index'): ") or "index"
            position_input = input(
                "Enter the position to insert the object (leave empty for end): ")
            position = int(position_input) if position_input.strip() else None

            self.manager.insert_object_to_array_index(
                checkpoint_name, new_object, position=position, index_field=index_field)
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
        print("Available checkpoints pointing to lists:")
        checkpoints = [
            checkpoint_name for checkpoint_name, path in self.manager.checkpoints.items()
            if isinstance(self.manager._get_value(path), list)
        ]
        if not checkpoints:
            print("No checkpoints pointing to lists are available.")
            return

        for i, checkpoint_name in enumerate(checkpoints):
            print(f"{i + 1}. {checkpoint_name}")

        try:
            choice = int(input("Select a checkpoint by number: ")) - 1
            if choice < 0 or choice >= len(checkpoints):
                print("Invalid choice. Please try again.")
                return

            checkpoint_name = checkpoints[choice]
            index = int(input("Enter the index of the object to remove: "))
            index_field = input("Enter the index field (default is 'index'): ") or "index"

            removed_object = self.manager.delete_object_from_array(
                checkpoint_name, index, index_field=index_field)
            self.manager.save_to_file()
            print(f"Removed object from '{checkpoint_name}': {removed_object}.")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Initialize the application with the JSON file and checkpoint file
    app = Application("example.json", "checkpoints.json")
    app.start()
