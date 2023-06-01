When creating a new addon, create a folder inside the addons folder

Then place the addon's files inside that folder.

Lets make the main run file match the name of the folder.

for example if making a work_timer tool:

Create "work_timer" folder, put "work_timer.py" inside of it. only that file will be run via main.py


Issues:

1. I put the test scripts inside of the tests folder. However I don't know how to run the tests within that folder.

2. SaveFile and FileSystem should be renamed to save_file and file_system for better readability?? (ChatGPT recommended this, idk if its necessary honestly, yall tell me)

3. The src folder seems too cluttered still.

4. the ui folder might need to be cleaned up a little

5. the youtube downloader doesn;t launch with main.py although it should theoretically, not sure what I did wrong there. The only way I can run it is by running "python -m addons.youtube_downloader.youtube_downloader" from the src folder

6. Tired of python cache cluttering the folders, do we need them?