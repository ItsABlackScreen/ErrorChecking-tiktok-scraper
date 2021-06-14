# ErrorChecking-tiktok-scraper
#### A python error checking script for drawrowfly's TiktokScrape
###### Requires Python version to be above 3.5

Link to <a href= "https://github.com/drawrowfly/tiktok-scraper">tiktok-scraper</a>

The script is mainly created to work with user profiles and not the hashtag or trend pages.  

The names of any user profiles with errors are written to a txt file for further batch downloading:   

The script requires command line arguments, which can be supplied on the command line itself, or through a file prefixed with the '+' character, eg: +file_args.txt.  
The default behaviour of the script is to check and remove 'empty' downloaded files.   

The Options are:  
<pre>
positional arguments:
  filepath              Path to the directory in which downloaded files exist.
  historypath           Path to directory containing history files.
  redownloadfile        Path to txt file for writing users to.

optional arguments:
  -h, --help            show this help message and exit
  --historybackup HISTORYBACKUP
                        Path to directory with history backups
  --deletepath DELETEPATH
                        Directory to move empty files to.
  -d, --delete          Argument to delete empty files.
  --updatebackup        Update the backup history files with the current history files.
  -nf, --newfiles       Argument to check new or entire profile.
  -cr, --checkrecent    Argument to check only recent files.
 </pre>


1. --delete  
    This removes the 'Zero' files from the history json and into a predefined folder from which they can be manually deleted. 
2. --newfiles   
   Checks if all the entries in the json history file and the downloaded directory match and removes any json entries that are not found in the profile folder. Use this when scraping entire profiles. Don't use this if the files have been moved to a different directory or some are deleted.
3. --checkrecent   
   Checks the newly downloaded files for errors, use this if the files have been moved. Make a copy of the history folder and enter the location in the script before downloading new files, as the script uses these previous history files for determining recent files. 
4. --updatebackup  
    Updated the history backup with any modified and corrected json files, when using --newfiles or --checkrecent.

>> self.check_size (script variable)    
   Size in bytes where anything below would be considered a 'Zero' file, currently is set to 50kb which catches most errors. 
