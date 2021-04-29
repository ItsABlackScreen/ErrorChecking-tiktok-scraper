import os
import shutil
import json
from pathlib import Path


class TikTokFiles:
    """A simple class to model various file operations on tiktok files."""

    def __init__(
        self,
        folder_path,
        error_check_path,
        delete_path,
        redownload_path,
        history_file_path,
        delete_files,
        new_files,
        check_recent_files,
    ):
        """Initializing various attributes."""

        self.start_folder = folder_path
        self.error_check_folder = error_check_path
        self.delete_path = delete_path
        self.redownload_path = redownload_path
        self.history_file_path = history_file_path
        self.delete_flag = delete_files
        self.new_file_flag = new_files
        self.check_data_flag = check_recent_files

        self.json_error_list = []
        self.redownload_file_list = []
        self.json_check_file_error_list = []

        # Enter check_size in bytes (currently 50kb)
        self.check_size = 51200

        self.tested_count = 0
        self.folder_check_count = 0

    def run_program(self):
        self._directory_walk()
        self._write_incomplete_jobs()
        self._print_results()

    def _directory_walk(self):
        """Walking the folders under start folder."""

        for folder, _, filenames in os.walk(self.start_folder):
            folder_name = Path(folder)
            self.folder_check_count += 1

            if self.new_file_flag:
                print(f"{folder_name} contains {len(filenames)} files.")
                self._load_history_files(filenames, folder_name)
            elif self.check_data_flag:
                self._load_history_files(filenames, folder_name)
            else:
                size_error_list = []

                for filename in filenames:
                    if not filename.endswith(".mp4"):
                        continue
                    file_location = folder_name / Path(filename)
                    self._check_size(
                        file_location, folder, filename, folder_name, size_error_list
                    )
                if size_error_list:
                    self._load_history_files(filenames, folder_name, size_error_list)

    def _check_size(
        self, file_location, folder, filename, folder_name, size_error_list
    ):
        """Calculate the size of the files"""
        size = os.path.getsize(file_location)
        self.tested_count += 1

        if size < self.check_size:
            print(folder + " has " + filename + " with size " + str(size) + " bytes")
            self.redownload_file_list.append(folder_name.name)

            if self.delete_flag:
                self._delete_files(file_location, filename)
            size_error_list.append(filename[:-4])

    def _delete_files(self, file_location, filename):
        """Move files that are less than the specified size to another location"""
        check_directory = os.path.isdir(self.delete_path)

        if not check_directory:
            os.mkdir(self.delete_path)

        try:
            shutil.move(file_location, self.delete_path)
            print(f"Moved {filename} to {self.delete_path}")
        except Exception as err:
            print(err)

    def _load_history_files(self, filenames, folder_name, size_error_list=None):
        """
        Load the appropriate json files associated with the usernames.
        """
        file_path = str(Path(self.history_file_path / "tiktok_history.json"))
        with open(file_path, "r") as file:
            data = json.load(file)
        try:
            json_file_temp = Path(data["user_" + folder_name.name]["file_location"])

            json_file = Path(self.history_file_path / json_file_temp.name)
            if self.check_data_flag:
                json_check_file = Path(self.error_check_folder / json_file_temp.name)
                if json_check_file.is_file():
                    self._error_check(
                        json_file, json_check_file, filenames, folder_name
                    )
                else:
                    self.json_check_file_error_list.append(folder_name.name)
                    print(
                        f"\nNo associated json check file found for {folder_name.name}\n"
                    )
            else:
                self._modify_json_files(
                    json_file, filenames, folder_name, size_error_list
                )
        except KeyError:
            self.json_error_list.append(folder_name.name)
            print(f"\nNo associated json file found for {folder_name.name}\n")

    def _modify_json_files(self, json_file, filenames, folder_name, size_error_list):
        """
        Remove the entries from json files where size is less than expected.
        """
        json_size = os.path.getsize(json_file)
        print(f"Associated json file : {json_file}")

        if json_size > 0:
            with open(json_file, "r") as file:
                data = json.load(file)

            if self.new_file_flag:
                print(f"{folder_name} json contains {len(data)} files.")
                new_set = set(data).difference([elem[:-4] for elem in filenames])
                if new_set:
                    print(f"Errors Found : {new_set}")
                    self.redownload_file_list.append(folder_name.name)
                    for filename in new_set:
                        self._write_json_file(data, json_file, filename)
                    self._dump_data(data, json_file)

                else:
                    print("No errors found\n")
            else:
                if size_error_list:
                    for filename in size_error_list:
                        self._write_json_file(data, json_file, filename)
                    self._dump_data(data, json_file)

    def _write_json_file(self, data, json_file, filename):
        """
        Remove incorrect entries from json file.
        """
        try:
            data.remove(filename)
            print(f"Removed {filename} from {json_file}")
        except ValueError:
            pass

    def _dump_data(self, data, json_file):
        """
        Dump the json file to disk.
        """
        with open(json_file, "w") as file:
            json.dump(data, file, separators=(",", ":"))
            print(f"Successfully written file : {json_file}\n")

    def _error_check(self, json_file, json_check_file, filenames, folder_name):
        """
        Check for errors in the new json file from previous copy.
        """
        json_file_size = os.path.getsize(json_file)
        json_check_file_size = os.path.getsize(json_check_file)

        if json_file_size > 0 and json_check_file_size > 0:
            with open(json_file, "r") as file:
                data = json.load(file)
            with open(json_check_file, "r") as check_file:
                check_data = json.load(check_file)

            new_downloads = set(data).difference(check_data)
            if new_downloads:
                print(f"\n{folder_name.name} has {len(new_downloads)} new downloads")
                print(new_downloads)
                error_files = new_downloads.difference(
                    [elem[:-4] for elem in filenames]
                )
                if error_files:
                    self.redownload_file_list.append(folder_name.name)
                    print("Not found the following files:")
                    print(error_files)
                    for error in error_files:
                        print(f"Removed {error} from {json_file}")
                        data.remove(error)
                    self._dump_data(data, json_file)

    def _write_incomplete_jobs(self):
        """
        Write to a text files names of users with download errors
        """
        if self.redownload_file_list:
            self.redownload_file_list = list(dict.fromkeys(self.redownload_file_list))

            with open(self.redownload_path, "w") as file:
                for link in self.redownload_file_list:
                    file.write("%s\n" % link)

    def _print_results(self):
        """
        Print the final results of the operation.
        """
        print()
        if self.json_error_list:
            print(f"Could not find the associated json for {self.json_error_list}\n")
        if self.json_check_file_error_list:
            print(
                f"Could not find the associated json in the check folder for {self.json_check_file_error_list}\n"
            )
        if self.new_file_flag or self.check_data_flag:
            print(f"Checked {self.folder_check_count} folders.")
            print(f"Found {len(self.redownload_file_list)} files with errors.\n")
            if self.redownload_file_list:
                print(
                    f"Found errors with the following users: {self.redownload_file_list}"
                )
        else:
            print(f"Found {len(self.redownload_file_list)} files with errors.\n")
            print(f"Tested {self.tested_count} files.")


if __name__ == "__main__":

    # Various paths used in the program
    folder_path = Path("")
    error_check_path = Path("")
    history_file_path = Path("")
    delete_path = Path("")
    redownload_path = Path("")

    # True/False values for various operations
    delete_files = False
    new_files = False
    check_recent_files = False

    tk = TikTokFiles(
        folder_path,
        error_check_path,
        delete_path,
        redownload_path,
        history_file_path,
        delete_files,
        new_files,
        check_recent_files,
    )
    tk.run_program()
