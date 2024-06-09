#!/bin/bash

# Path to your virtual environment
venv_path="/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/venv"

# Array to hold the PIDs of the background jobs
pids=()

# Function to stop all background jobs and close all Terminal tabs
function stop_all {
    echo "Stopping all scripts..."
    for pid in "${pids[@]}"; do
        kill $pid 2>/dev/null
    done
    osascript -e 'tell application "Terminal" to close (every window whose name contains ".py")' &>/dev/null
    exit
}

# Start a separate thread that waits for a key press, and then calls stop_all
function wait_for_keypress {
    read -p "Press any key to stop all scripts... " -n1 -s
    stop_all
}

# Start the thread
# wait_for_keypress &

# List of your scripts
scripts=("/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/server/Server_Frame_reader.py" "/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/server/cache_server.py" "/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Library/vehicle_counter.py" "/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Library/ambulance_detection.py"  "/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Library/display.py" "/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/Library/logic.py")

# Loop over your scripts
for script in "${scripts[@]}"; do
   # Open a new terminal window, activate the virtual environment, and run the script
   osascript -e "tell application \"Terminal\" to do script \"source $venv_path/bin/activate && python3 $script\"" &
   
   # Store the PID of the background job
   pids+=($!)
   
   # Delay before starting the next one
   if [ "$script" == "/Users/MAC/Final_Year_Project/colab/Final_Project_with_display/server/Server_Frame_reader.py" ];then
    sleep 10
    else
    sleep 5
   fi
done
wait_for_keypress

# Wait for all background jobs to finish
wait
