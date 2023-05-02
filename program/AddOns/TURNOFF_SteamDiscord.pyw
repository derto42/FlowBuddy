import subprocess

# Use the taskkill command to force quit all Steam processes
subprocess.run(["taskkill", "/F", "/IM", "Steam.exe"])

# Use the taskkill command to force quit all Discord processes
subprocess.run(["taskkill", "/F", "/IM", "Discord.exe"])


# Exit the script
exit()
