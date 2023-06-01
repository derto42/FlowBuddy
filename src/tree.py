import os

def generate_folder_structure(path, indent=''):
    files = []
    folders = []

    # Get all files and folders in the current path
    for entry in os.scandir(path):
        if entry.is_file():
            files.append(entry.name)
        elif entry.is_dir():
            folders.append(entry.name)

    # Print files
    for file in files:
        print(indent + '├── ' + file)

    # Recursively print sub-folders
    for i, folder in enumerate(folders):
        if i == len(folders) - 1:
            print(indent + '└── ' + folder)
            generate_folder_structure(path + '/' + folder, indent + '    ')
        else:
            print(indent + '├── ' + folder)
            generate_folder_structure(path + '/' + folder, indent + '│   ')

# Output the folder structure of the current directory
current_directory = os.getcwd()
print('Folder Structure: ' + current_directory)
generate_folder_structure(current_directory)
