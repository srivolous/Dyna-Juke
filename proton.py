import subprocess
import os as os

def get_gps_data():
    try:
        # Run the ADB command to get GPS data
        #command = ["adb", "shell", "dumpsys", "location","adb shell dumpsys location | findstr "vel=.""]
        command = 'powershell.exe adb shell dumpsys location | findstr \"vel=."'
        result = subprocess.check_output(command, universal_newlines=True)

        # Parse the output to extract useful GPS information
        # You may need to adjust this part depending on the output format
        if "last location" in result:
            #print("GPS Data:")
   
            chaco = result
            vanko = chaco.split()
            vanko = vanko[6]
            vanko = vanko[4:]
            django = float(vanko)/22;
            return django
        else:
            print("No GPS data found.")
    except subprocess.CalledProcessError as e:
        print(f"Error fetching GPS data: {e}")

if __name__ == "__main__":
    while True:
        checo = get_gps_data()

        print(checo)