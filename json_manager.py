import json
import os
from jsonpath_ng.ext import parse  # Import jsonpath-ng for path parsing


class JSONManager:
    def __init__(self, default_file_path, checkpoint_file="checkpoints.json"):
        """
        Initialize the JSONManager with a default JSON file and a checkpoint mapping.
        """
        # self.default_file_path = default_file_path
        # self.data = self._load_json(default_file_path)
        # self.checkpoints = {}  # Dictionary to map checkpoints to JSON paths
        self.default_file_path = default_file_path
        self.checkpoint_file = checkpoint_file
        self.data = self._load_json(default_file_path)
        self.checkpoints = self._load_checkpoints()
        # self.checkpoints = {}

    def _load_json(self, file_path):
        """
        Load JSON data from a file.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return {}

    def _load_checkpoints(self):
        """
        Load checkpoints from a JSON file.
        """
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as file:
                return json.load(file)
        return {}

    def save_checkpoints(self):
        """
        Save checkpoints to a JSON file.
        """
        with open(self.checkpoint_file, 'w') as file:
            json.dump(self.checkpoints, file, indent=4)

    def add_checkpoint(self, checkpoint_name, json_path):
        """
        Add a checkpoint mapping to a JSON path.
        """
        self.checkpoints[checkpoint_name] = json_path

    def _resolve_checkpoint(self, checkpoint_name):
        """
        Resolve a checkpoint name to its corresponding JSON path.
        """
        if checkpoint_name in self.checkpoints:
            return self.checkpoints[checkpoint_name]
        raise ValueError(f"Checkpoint '{checkpoint_name}' does not exist.")

    def _get_value(self, path):
        """
        Get a value from the JSON data using jsonpath-ng.
        """
        jsonpath_expr = parse(path)
        matches = jsonpath_expr.find(self.data)
        if matches:
            return matches[0].value
        raise ValueError(f"Path '{path}' does not exist in the JSON data.")

    def _set_value(self, path, new_value):
        """
        Set a value in the JSON data using jsonpath-ng.
        """
        jsonpath_expr = parse(path)
        matches = jsonpath_expr.find(self.data)
        if matches:
            match = matches[0]
            parent = match.context.value
            key = match.path.fields[0] if match.path.fields else match.path.index
            parent[key] = new_value
        else:
            raise ValueError(f"Path '{path}' does not exist in the JSON data.")

    def update_value(self, checkpoint_name, new_value):
        """
        Update a value in the JSON data using a checkpoint name.
        """
        path = self._resolve_checkpoint(checkpoint_name)
        old_value = self._get_value(path)

        # Attempt to convert new_value to the same type as old_value
        try:
            if isinstance(old_value, (int, float)):
                new_value = type(old_value)(new_value)  # Convert to int/float if old_value is numeric
            elif isinstance(old_value, str):
                new_value = str(new_value)  # Convert to string if old_value is a string
            else:
                raise ValueError(
                    f"Unsupported type: Cannot update '{checkpoint_name}' with type {type(old_value).__name__}."
                )
        except ValueError:
            raise ValueError(
                f"Type mismatch: Cannot update '{checkpoint_name}' from {type(old_value).__name__} to {type(new_value).__name__}."
            )

        self._set_value(path, new_value)
        return old_value, new_value

    def append_to_list(self, checkpoint_name, value):
        """
        Append a value to a list in the JSON data using a checkpoint name.
        """
        path = self._resolve_checkpoint(checkpoint_name)
        target_list = self._get_value(path)
        if isinstance(target_list, list):
            target_list.append(value)
        else:
            raise ValueError(
                f"Checkpoint '{checkpoint_name}' does not point to a list.")

    def delete_from_list(self, checkpoint_name, index):
        """
        Delete an item from a list in the JSON data using a checkpoint name.
        """
        path = self._resolve_checkpoint(checkpoint_name)
        target_list = self._get_value(path)
        if isinstance(target_list, list) and 0 <= index < len(target_list):
            removed_value = target_list.pop(index)
            return removed_value
        else:
            raise ValueError(
                f"Invalid index or checkpoint '{checkpoint_name}' does not point to a list.")

    def append_object_to_array(self, checkpoint_name, new_object):
        """
        Append a JSON object to an array in the JSON data using a checkpoint name.
        """
        path = self._resolve_checkpoint(checkpoint_name)
        target_array = self._get_value(path)
        if isinstance(target_array, list):
            target_array.append(new_object)
        else:
            raise ValueError(
                f"Checkpoint '{checkpoint_name}' does not point to an array.")

    def insert_object_to_array_index(self, checkpoint_name, new_object, position=None, index_field="index"):
        print(f"+++++++++++++++++++++++Inserting object at position {position} with index field '{index_field}'")
        """
        Insert a JSON object into an array at a specified position in the JSON data using a checkpoint name.
        Re-plan the indices of all objects in the array based on the specified index field.
        """
        path = self._resolve_checkpoint(checkpoint_name)
        target_array = self._get_value(path)
        if isinstance(target_array, list):
            if position is None or position >= len(target_array):
                # Append to the end if no position is specified or position is out of bounds
                target_array.append(new_object)
            else:
                # Insert at the specified position
                target_array.insert(position, new_object)

            # Re-plan indices for all objects in the array
            for i, obj in enumerate(target_array):
                if isinstance(obj, dict):
                    obj[index_field] = i
        else:
            raise ValueError(
                f"Checkpoint '{checkpoint_name}' does not point to an array.")

    def delete_object_from_array(self, checkpoint_name, index, index_field=None):
        """
        Delete a JSON object from an array in the JSON data using a checkpoint name.
        Re-plan the indices of other objects in the array if an index field is specified.
        """
        path = self._resolve_checkpoint(checkpoint_name)
        target_array = self._get_value(path)
        if isinstance(target_array, list) and 0 <= index < len(target_array):
            removed_object = target_array.pop(index)
            if index_field:
                # Re-plan indices for remaining objects
                for i, obj in enumerate(target_array):
                    if isinstance(obj, dict) and index_field in obj:
                        obj[index_field] = i
            return removed_object
        else:
            raise ValueError(
                f"Invalid index or checkpoint '{checkpoint_name}' does not point to an array.")

    def save_to_file(self, file_path=None):
        """
        Save the current JSON data to a file.
        """
        file_path = file_path or self.default_file_path
        with open(file_path, 'w') as file:
            json.dump(self.data, file, indent=4)


if __name__ == "__main__":
    # Example usage
    manager = JSONManager("example.json")

    # Adding checkpoints
    # manager.add_checkpoint("user_profile_name", "$.user.profile.name")
    # manager.add_checkpoint("user_profile_age", "$.user.profile.age")
    # manager.add_checkpoint("user_hobbies", "$.user.hobbies")
    # manager.add_checkpoint("user_education", "$.user.education")
    # manager.add_checkpoint("settings_theme", "$.settings.theme")
    # manager.add_checkpoint("settings_notifications_email",
    #                        "$.settings.notifications.email")

    # Update a value
    old_value, new_value = manager.update_value(
        "user_profile_name", "John Doe")
    print(f"Updated 'user_profile_name' from '{old_value}' to '{new_value}'")

    # Append to a list
    manager.append_to_list("user_hobbies", "Reading")

    # Delete from a list
    removed_value = manager.delete_from_list("user_hobbies", 0)
    print(f"Removed value from 'user_hobbies': {removed_value}")

    # new_object = {
    # "index": 2,
    # "degree": "PhD",
    # "field": "Artificial Intelligence",
    # "year": 2022
    # }
    # manager.append_object_to_array("user_education", new_object)
    # print(f"Appended object to 'user_education': {new_object}")

    new_object_position = {"degree": "XXXXXX","field": "Mathematics","year": 201}
    for i in range(3):
        manager.insert_object_to_array_index(
            "user_education", new_object_position, position=1, index_field="index")
        print(
            f"Inserted object into 'user_education' at position 1: {new_object_position}")

    # try to remove an object from the 'education' array
    removed_object = manager.delete_object_from_array(
        "user_education", 0, index_field="index")

    manager.save_checkpoints()

    # Delete an object from the 'education' array and re-plan indices
    # removed_object = manager.delete_object_from_array("user_education", 0, index_field="index")
    # print(f"Removed object from 'user_education': {removed_object}")

    # Save changes to file
    manager.save_to_file()
