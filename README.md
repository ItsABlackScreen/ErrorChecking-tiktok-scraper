# ErrorChecking-tiktok-scraper
#### A python error checking script for drawrowfly's TiktokScrape
###### Requires Python version to be above 3.5

Link to <a href= "https://github.com/drawrowfly/tiktok-scraper">tiktok-scraper</a>

The script is mainly created to work with user profiles and not the hashtag or trend pages.  
It has four functions that can be used by changing the flags to True/False:  
The names of any user profiles with errors are written to a txt file for further batch downloading:   

1. delete_files flag  
    Setting the delete_files flag to *True* removes the 'Zero' files from the history json and into a predefined folder from which they can be manually deleted. 
2. new_files flag  
   Setting this flag to *True* checks if all the entries in the json history file and the downloaded directory match and removes any json entries that are not found in the profile folder. Use this when scraping entire profiles. Don't use this if the files have been moved to a different directory or some are deleted.
3. check_recent_files  flag  
   Setting this flag to *True* just checks the newly downloaded files for errors, use this if the files have been moved. Make a copy of the history folder and enter the location in the script before downloading new files, as the script uses these previous history files for determining recent files. 
4. Remove zero files   
   This is the default behaviour of the script and removed the 'Zero' files form the json history, but doesn't move them from the folders unless the delete_files flag is set to *True*
5. self.check_size  
   Size in bytes where anything below would be considered a 'Zero' file, currently is set to 50kb which catches most errors. 
  
 Set the following paths inside the script for it to function (input the path between the quotes):  
 
 1. folder_path = Set to the base folder contaning all the dowloaded tiktok profiles. 
 2. error_check_path = Set to the copy of the history folder. 
 3. history_file_path = The full path to the 'tiktok_history.json' file.   
 4. delete_path = The path where the 'Zero' byte files would be moved to.   
 5. redownload_path = Full path to a text file where the script will write the names of profiles with error, for future batch downloading. (eg. /path/to/file/redownload.txt)  
