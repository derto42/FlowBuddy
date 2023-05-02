import PySimpleGUI as sg
import webbrowser
import keyboard
import json
import os
import subprocess
from typing import List

# Set the theme
sg.theme('DarkBlue')

# Update the style of buttons
button_style = {
    'button_color': ('white', '#007ACC'),
    'font': ('Helvetica', 10, 'bold')
}

DATA_FILE = "data.json"

# Function to open the provided URL
def open_url(url):
    webbrowser.open(url)

# Function to load data from a JSON file
# Function to load data from a JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                data = json.load(file)
                # Ensure the 'file' key is present in all tasks
                for group in data:
                    for task in group["tasks"]:
                        if "file" not in task:
                            task["file"] = ""
                return data
            except json.JSONDecodeError:
                return []
    return []



def update_overlay(window: sg.Window, groups: List[dict]):
    layout = [[sg.Text("Workflow Solution", font=("Helvetica", 14, "bold"))]]

    for group in groups:
        group_header = sg.Frame("", [
            [sg.Text(group["name"], font=("Helvetica", 12, "bold"))],
            [sg.Button(button_text="Add Task", key=f"add_task_{group['name']}"),
             sg.Button(button_text="Edit Group", key=f"edit_group_{group['name']}")]
        ])
        layout.append([group_header])

        for task in group["tasks"]:
            task_row = [
                sg.Text(task["name"]),
                sg.Button(button_text=task["button_text"], key=f"open_{task['url']}"),
                sg.Button(button_text="Edit Task", key=f"edit_task_{task['name']}_{task['url']}"),
            ]
            layout[-1].append(task_row)

    layout.append([sg.Button("Add Group"), sg.Button("Exit")])

    window.extend_layout(window, layout)

# Function to save data to a JSON file
def save_data(groups):
    with open(DATA_FILE, "w") as file:
        json.dump(groups, file, indent=4)

# Function to generate a unique name for groups and tasks
def generate_unique_name(name, existing_names):
    if not name:
        name = "Untitled"
    unique_name = name
    counter = 1
    while unique_name in existing_names:
        unique_name = f"{name} ({counter})"
        counter += 1
    return unique_name


def create_overlay(groups, window=None):
    layout = [
        [sg.Text("Workflow Solution", font=("Helvetica", 14, "bold"), pad=(10, 10))]
    ]

    for group in groups:
        group_elements = [
            [sg.Text(group["name"], font=("Helvetica", 12, "bold"))],
            [
                sg.Button(button_text="Add Task", key=f"add_task_{group['name']}", **button_style),
                sg.Button(button_text="Edit Group", key=f"edit_group_{group['name']}", **button_style)
            ]
        ]

        for task in group["tasks"]:
            task_row = [
                sg.Text(task["text"]) if task.get("text") else sg.Text(""), # Add this line to display the text value
                sg.Button(button_text=task["button_text"], 
                          key=f"open_url_{task['url']}" if task["url"] else f"open_file_{task['file']}", **button_style),
                sg.Button(button_text="Edit Task", key=f"edit_task_{task['name']}_{task['url']}_{task['file']}", **button_style)
            ]

            group_elements.append(task_row)

        group_header = sg.Frame("", group_elements, element_justification='left', pad=(20, 5))
        layout.append([group_header])

    layout.append([
        sg.Button("Add Group", **button_style),
        sg.Button("Exit", **button_style)
    ])

    if window:
        window.extend_layout(window, layout)
    else:
        return sg.Window("Workflow Overlay", layout, no_titlebar=True, keep_on_top=True, grab_anywhere=True)


# Function to handle the events

# Function to handle the events
def event_handler(window, groups):
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event.startswith("open_url_"):
            url = event.split("open_url_")[1]
            open_url(url)
        elif event.startswith("open_file_"):
            file_path = event.split("open_file_")[1]
            subprocess.Popen(file_path, shell=True)
        elif event.startswith("open_"):
            url = event.split("open_")[1]
            open_url(url)
        elif event == "Add Group":
            updated_groups = edit_group_window(None, groups)
            if updated_groups:
                groups = updated_groups
                window = create_overlay(groups, window)
        elif event.startswith("edit_group"):
            group_name = event.split("edit_group_")[1]
            updated_groups = edit_group_window(group_name, groups)
            if updated_groups:
                groups = updated_groups
                window = create_overlay(groups, window)
        elif event.startswith("add_task"):
            group_name = event.split("add_task_")[1]
            updated_groups = edit_task_window(None, None, group_name, groups)
            if updated_groups:
                groups = updated_groups
                window = create_overlay(groups, window)
        elif event.startswith("edit_task"):
            task_data = event.split("edit_task_")[1].split("_")
            task_name, task_url = task_data[0], task_data[1]
            group_name = [group["name"] for group in groups if task_name in [task["name"] for task in group["tasks"]]][0]
            updated_groups = edit_task_window(task_name, task_url, group_name, groups)
            if updated_groups:
                groups = updated_groups
                window = create_overlay(groups, window)
    return True

def main():
    groups = load_data()

    while True:
        if keyboard.is_pressed("`"):
            window = create_overlay(groups)
            refresh = event_handler(window, groups)
            window.close()
            if refresh:
                groups = load_data()
        elif keyboard.is_pressed("esc"):
            break


# Function to create and manage the group editing window
def edit_group_window(group_name, groups):
    title = "Edit Group" if group_name else "Add Group"

    layout = [
        [sg.Text("Group Name:", pad=(5, 5))],
        [sg.Input(default_text=group_name if group_name else "", key="group_name")],
        [
            sg.Button("Save", **button_style),
            sg.Button("Cancel", **button_style),
            sg.Button("Delete", **button_style) if group_name else sg.Text("")
        ]
    ]

    window = sg.Window(title, layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Cancel":
            break
        elif event == "Save":
            new_group_name = values["group_name"]
            new_group_name = generate_unique_name(new_group_name, [group["name"] for group in groups])
            if group_name:
                group = [group for group in groups if group["name"] == group_name][0]
                group["name"] = new_group_name
            else:
                groups.append({"name": new_group_name, "tasks": []})
            save_data(groups)
            break
        elif event == "Delete":
            groups = [group for group in groups if group["name"] != group_name]
            save_data(groups)
            break

    window.close()
    return False


def edit_task_window(task_name, task_url, group_name, groups):
    title = "Edit Task" if task_name else "Add Task"

    if task_name:
        for group in groups:
            if group["name"] == group_name:
                for task in group["tasks"]:
                    if task["name"] == task_name:
                        break
                break

    existing_names = [task["name"] for task in next((group for group in groups if group["name"] == group_name), {}).get("tasks", [])]
    new_task_name = generate_unique_name(task_name, existing_names)

    layout = [
        [sg.Text("Task Name:", pad=(5, 5))],
        [sg.Input(default_text=new_task_name if new_task_name else "", key="task_name")],
        [sg.Text("Button Text:", pad=(5, 5))],
        [sg.Input(default_text=task.get("button_text", "") if task_name else "", key="button_text")],
        [sg.Text("URL:", pad=(5, 5))],
        [sg.Input(default_text=task_url if task_url else "", key="url")],
        [sg.Text("File:", pad=(5, 5))],
        [sg.Input(default_text=task["file"] if task_name and task.get("file") else "", key="file"), sg.FileBrowse()],
        [sg.Text("Text (optional):", pad=(5, 5))],
        [sg.Input(default_text=task.get("text", "") if task_name else "", key="text")],
        [
            sg.Button("Save", **button_style),
            sg.Button("Cancel", **button_style),
            sg.Button("Delete", **button_style)
        ]
    ]

    window = sg.Window(title, layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Cancel":
            break
        elif event == "Save":
            new_task = {
                "name": values["task_name"],
                "button_text": values["button_text"],
                "url": values["url"],
                "file": values["file"],
                "text": values["text"]  # Add this line to store the text value
            }
            for group in groups:
                if group["name"] == group_name:
                    if not task_name:  # Add new task
                        group["tasks"].append(new_task)
                    else:  # Update existing task
                        for task in group["tasks"]:
                            if task["name"] == task_name:
                                task["name"] = values["task_name"]
                                task["button_text"] = values["button_text"]
                                task["url"] = values["url"]
                                task["file"] = values["file"]
                                task["text"] = values["text"]
                                break
                    break
            save_data(groups)
            break
        elif event == "Delete":
            for group in groups:
                if group["name"] == group_name:
                    group["tasks"] = [task for task in group["tasks"] if task["name"] != task_name]
                    break
            save_data(groups)
            break

    window.close()

    return False



    

# Main function
def main():
    groups = load_data()

    window = create_overlay(groups)
    refresh = event_handler(window, groups)
    window.close()
    if refresh:
        groups = load_data()



if __name__ == "__main__":
    main()
