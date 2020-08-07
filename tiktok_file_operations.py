import os, shutil, json
from pathlib import Path

class TikTokFiles:
    """A simple class to model various file operations on tiktok files."""

    def __init__(self, f_folder, e_c_folder, d_folder, t_folder, h_f_path, d_files, n_files, c_n_files):
        """Initializing various attributes."""

        self.start_folder = f_folder
        self.error_check_folder = str(e_c_folder)
        self.delete_path = d_folder
        self.redownload_path = t_folder
        self.history_file_path = h_f_path

        self.json_error_list = []
        self.redownload_file_list = []
        self.json_check_file_error_list = []

        self.delete_flag = d_files
        self.new_file_flag = n_files
        self.check_data_flag = c_n_files

        # Enter check_size in bytes (currently 50kb)
        self.check_size = 51200
        
        self.size = 0
        self.tested_count = 0

    def run_program(self):
        self._directory_walk()
        self._write_incomplete_jobs()
        self._print_results()

    def _directory_walk(self):
        """Walking the folders under start folder."""

        for folder, subfolder, self.filenames in os.walk(self.start_folder):
            self.folder_name = Path(folder)
            if self.new_file_flag:
                print(f"{self.folder_name} contains {len(self.filenames)} files.")
                self._load_history_files()
            elif self.check_data_flag:
                self._load_history_files()
            else:
                self.size_error_list = []

                for filename in self.filenames:
                    file_location = str(self.folder_name / Path(filename))
                    self._check_size(file_location,folder,filename)
                if self.size_error_list:
                    self._load_history_files()
                
    def _check_size(self, file_location, folder, filename):
        """Calculate the size of the files"""
        self.size = os.path.getsize(file_location)
        self.tested_count += 1

        if self.size < self.check_size:
            print(folder + ' has ' + filename + ' with size ' + str(self.size) + ' bytes')
            self.redownload_file_list.append(self.folder_name.name)

            if self.delete_flag:
                self._delete_files(file_location, filename)
            self.size_error_list.append(filename[:-4])

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

    def _load_history_files(self):
        """
        Load the appropriate json files associated with the usernames.
        """
        with open(self.history_file_path, 'r') as file:
            data = json.load(file)
        try:
            json_file = data['user_'+self.folder_name.name]['file_location']
            if self.check_data_flag:
                json_check_file = Path(self.error_check_folder + json_file[21:])
                if json_check_file.is_file():
                    self._error_check(Path(json_file), json_check_file)
                else:
                    self.json_check_file_error_list.append(self.folder_name.name)
                    print(f"\nNo associated json check file found for {self.folder_name.name}\n")
            else:
                self._modify_json_files(json_file)
        except KeyError as err:
            self.json_error_list.append(self.folder_name.name)
            print(f'\nNo associated json file found for {self.folder_name.name}\n')

    def _modify_json_files(self, json_file):
        """
        Remove the entries from json files where size is less than expected.
        """
        target_file = Path(json_file)
        json_size = os.path.getsize(target_file)
        print(f"Associated json file : {target_file}")

        if json_size > 0:
            with open(target_file, 'r') as file:
                data = json.load(file)

            if self.new_file_flag:
                print(f"{self.folder_name} json contains {len(data)} files.")
                new_set = set(data).difference([elem[:-4] for elem in self.filenames])
                if new_set:
                    print(f"Errors Found : {new_set}")
                    self.redownload_file_list.append(self.folder_name.name)
                    for name in new_set:
                        self.new_filename = name
                        self._write_json_file(data, target_file)
                    self._dump_data(data,target_file)

                else:
                    print("No errors found\n")
            else:
                if self.size_error_list:
                    for filename in self.size_error_list:
                        self.new_filename = filename
                        self._write_json_file(data, target_file)
                    self._dump_data(data, target_file)

    def _write_json_file(self, data, target_file):
        """
        Remove incorrect entries from json file.
        """
        if self.new_filename in data:
            data.remove(self.new_filename)
            print(f"Removed {self.new_filename} from {target_file}")

    def _dump_data(self,data,target_file):
        """
        Dump the json file to disk.
        """
        with open(target_file, 'w') as file:
            json.dump(data, file, separators=(',', ':'))
            print(f"Successfully written file : {target_file}\n")

    def _error_check(self, json_file, json_check_file):
        """
        Check for errors in the new json file from previous copy.
        """
        json_file_size = os.path.getsize(json_file)
        json_check_file_size = os.path.getsize(json_check_file)

        if json_file_size > 0 and json_check_file_size > 0:
            with open(json_file, 'r') as file:
                data = json.load(file)
            with open(json_check_file, 'r') as check_file:
                check_data = json.load(check_file)

            new_downloads = set(data).difference(check_data)
            if new_downloads:
                print(f"\n{self.folder_name.name} has {len(new_downloads)} new downloads")
                print(new_downloads)
                error_files = new_downloads.difference([elem[:-4] for elem in self.filenames])
                if error_files:
                    self.redownload_file_list.append(self.folder_name.name)
                    print('Not found the following files:')
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
            order_list = list(dict.fromkeys(self.redownload_file_list))

            with open(self.redownload_path, 'w') as file:
                for link in order_list:
                    file.write("%s\n" % link)

    def _print_results(self):
        """
        Print the final results of the operation.
        """
        print()
        if self.json_error_list:
            print(f"Could not find the associated json for {self.json_error_list}\n")
        if self.json_check_file_error_list:
            print(f"Could not find the following json in the check folder {self.json_check_file_error_list}\n")
        if self.new_file_flag or self.check_data_flag:
            print(f"Found {len(self.redownload_file_list)} files with errors.\n")
        else:
            print(f"Found {len(self.redownload_file_list)} files with errors.\n")
            print(f"Tested {self.tested_count} files. ")


if __name__ == '__main__':

    # Various paths used in the program 
    folder_path = Path('')
    error_check_path = Path('')
    history_file_path = Path('')
    delete_path = str(Path(''))
    redownload_path = str(Path(''))

    #True/False values for various operations
    delete_files = False
    new_files = False
    check_recent_files = False

    tk = TikTokFiles(folder_path, error_check_path, delete_path, redownload_path, 
        history_file_path, delete_files, new_files, check_recent_files)
    tk.run_program()
    