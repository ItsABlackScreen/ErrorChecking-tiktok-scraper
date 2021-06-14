import os
import shutil
import json
import argparse
from pathlib import Path


class TikTokFiles:
    """A simple class to model various file operations on tiktok files."""

    def __init__(self, args):
        """Initializing various attributes."""

        self.start_folder = Path(args.filepath)
        self.redownload_path = Path(args.redownloadfile)
        self.history_file_path = Path(args.historypath)
        self.error_check_folder = (
            Path(args.historybackup) if args.historybackup else args.historybackup
        )
        self.delete_path = Path(args.deletepath) if args.deletepath else args.deletepath
        self.update_backup = args.updatebackup

        self.delete_flag = args.delete
        self.new_file_flag = args.newfiles
        self.check_data_flag = args.checkrecent

        self.json_error_list = []
        self.redownload_file_list = []
        self.json_check_file_error_list = []
        self.update_backup_list = []

        # Enter check_size in bytes (currently 50kb)
        self.check_size = 51200

        self.tested_count = 0
        self.folder_check_count = 0

    def run_program(self):
        self._directory_walk()
        self._write_incomplete_jobs()
        self._print_results()
        if self.update_backup:
            self._update_backup()

    def _directory_walk(self):
        """Walking the folders under start folder."""

        for folder in [x.path for x in os.scandir(self.start_folder) if x.is_dir()]:
            folder_name = Path(folder)
            filenames = [x.name for x in os.scandir(folder_name) if x.is_file()]
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
                        file_location,
                        filename,
                        folder_name,
                        size_error_list,
                    )
                if size_error_list:
                    self._load_history_files(filenames, folder_name, size_error_list)

    def _check_size(self, file_location, filename, folder_name, size_error_list):
        """Calculate the size of the files"""
        size = os.path.getsize(file_location)
        self.tested_count += 1

        if size < self.check_size:
            print(f"{folder_name.name} has {filename} with size {size} bytes")
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
                self.update_backup_list.append(json_file)
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
                self.update_backup_list.append(json_file)
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

    def _update_backup(self):
        """
        Updates the backup history dir, with primary history dir
        """
        l_backup = len(self.update_backup_list)
        if self.update_backup_list:
            print(f"\nUpdating backup with {l_backup} modified json files.")
            for file in self.update_backup_list:
                try:
                    shutil.copy2(file, self.error_check_folder)
                except Exception as err:
                    print(f"Error occured : {err}")
        else:
            print(f"\nNo files changed, nothing to update.")

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
            print(f"Tested {self.tested_count} files.")
            print(f"Found {len(self.redownload_file_list)} files with errors.\n")


if __name__ == "__main__":

    my_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="+",
        description="Error check titok-scraper for missing and empty files.",
    )
    mutual_exc = my_parser.add_mutually_exclusive_group()

    my_parser.add_argument(
        "filepath",
        help="Path to the directory in which downloaded files exist.",
    )
    my_parser.add_argument(
        "historypath",
        help="Path to directory containing history files.",
    )
    my_parser.add_argument(
        "redownloadfile",
        help="Path to txt file for writing users to.",
    )

    my_parser.add_argument(
        "--historybackup", help="Path to directory with history backups"
    )
    my_parser.add_argument("--deletepath", help="Directory to move empty files to.")
    my_parser.add_argument(
        "-d", "--delete", action="store_true", help="Argument to delete empty files."
    )
    my_parser.add_argument(
        "--updatebackup",
        action="store_true",
        help="Update the backup history files with the current history files.",
    )

    mutual_exc.add_argument(
        "-nf",
        "--newfiles",
        action="store_true",
        help="Argument to check new or entire profile.",
    )
    mutual_exc.add_argument(
        "-cr",
        "--checkrecent",
        action="store_true",
        help="Argument to check only recent files.",
    )

    args = my_parser.parse_args()

    if args.checkrecent and not args.historybackup:
        my_parser.error("--checkrecent requires --historybackup")
    elif args.delete and not args.deletepath:
        my_parser.error("--delete requires --deletepath")
    elif args.updatebackup and not args.historybackup:
        my_parser.error("--updatebackup requires --historybackup")

    tk = TikTokFiles(args)
    tk.run_program()
