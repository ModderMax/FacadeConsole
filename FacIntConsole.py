import platform
import subprocess
import sys 
import pkg_resources
import time 
import keyboard # keyboard will need to be installed [pip install keyboard]
from xml.etree.ElementTree import tostring

# Check selenium version
def check_selenium():
    try:
        selenium_version = pkg_resources.get_distribution("selenium").version
        if pkg_resources.parse_version(selenium_version) >= pkg_resources.parse_version("3.0.0"):
            print(f"Selenium is installed and up-to-date (version {selenium_version}).")
        else:
            print(f"Selenium is installed but outdated (version {selenium_version}).")
            install_selenium_prompt()
    except pkg_resources.DistributionNotFound:
        print("Selenium is not installed.")
        install_selenium_prompt()
        
# Prompt Selenium Install
def install_selenium_prompt():
    response = input("Do you want to install/update Selenium to the latest version? (yes/no): ").strip().lower()
    if response == 'yes':
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "selenium"])
        print("Selenium has been installed/updated to the latest version.")
    else:
        print("Selenium was not installed/updated.")

# Run check for selenium
check_selenium()

from selenium import webdriver # Selenium needs to be installed
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

# Run Terminal for corresponding operating system
os_type = 0

def get_os_info():
    global os_type
    system = platform.system()
    release = platform.release()
    
    if system == 'Windows':
        if release in ['10', '11']:
            os_type = 1
        elif release in ['7', '8', '8.1']:
            os_type = 3
        else:
            os_type = 0
    elif system == 'Linux':
        os_type = 2
    elif system == 'Darwin':
        os_type = 2
    else:
        os_type = 0

def open_terminal():
    global os_type
    if os_type == 1:
        # Open PowerShell in minimized mode
        subprocess.Popen(['powershell.exe', '-NoExit', '-WindowStyle', 'Minimized'])
    elif os_type == 2:
        # Open console in minimized mode (macOS/Linux)
        if platform.system() == 'Darwin':
            subprocess.Popen(['osascript', '-e', 'tell application "Terminal" to do script "" & tell application "Terminal" to set miniaturized of window 1 to true'])
        else:
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'echo -e "\e[8;40;80t"; exec bash'], shell=True)
    elif os_type == 3:
        # Open Command Prompt in minimized mode
        subprocess.Popen(['cmd.exe', '/k', 'start /min cmd'])

def send_command_to_terminal(command):
    global os_type
    if os_type == 1:
        return execute_powershell_command(command)
    elif os_type == 2:
        return execute_console_command(command)
    elif os_type == 3:
        return execute_cmd_command(command)
    else:
        return "Unsupported operating system"

def execute_powershell_command(command):
    result = subprocess.run(['powershell.exe', '-Command', command], capture_output=True, text=True)
    return result.stdout

def execute_console_command(command):
    result = subprocess.run(['bash', '-c', command], capture_output=True, text=True)
    return result.stdout

def execute_cmd_command(command):
    result = subprocess.run(['cmd.exe', '/c', command], capture_output=True, text=True)
    return result.stdout

def write_output_to_terminal(command):
    output = send_command_to_terminal(command)
    if output:
        print(output)  # Print output to standard output for debugging
        keyboard.write(output)

get_os_info()
print("FacadeInterfaceConsole version 1.0.0")

# Prompt for browser selection
def browser_select():
    browser = input('\nBrowser:\nChrome - 1\nFireFox - 2\nSafari - 3\nEdge - 4\nSelect: ')
    return browser
browser = browser_select()

# Set webdriver to selected browser
if browser == "1": 
    driver = webdriver.Chrome()
    print("\nSelected Chrome - " + str(browser))
elif browser == "2": 
    driver = webdriver.Firefox()
    print("\nSelected FireFox - " + str(browser))
elif browser == "3":
    driver = webdriver.Safari()
    print("\nSelected Safari - " + str(browser))
else: 
    print("\nBad input " + str(browser))
    browser_select()
    
driver.get("http://google.com")

# Function to allow user to select an input field
def select_input_field():
    print("Please select the input field in the browser.")
    keyboard.wait('ctrl+shift+s')
    # input("Press Enter here after selecting the input field...")  # Pause for user to select input field
    selected_element = driver.switch_to.active_element  # Get the currently active element
    return selected_element

# Global variables to control the flow
is_running = True
exit_program = False

# Select the input field
input_field = select_input_field()
open_terminal()

# Function to capture input when Enter key is pressed
def capture_input_on_enter(input_element):
    global is_running, exit_program

    last_input = ""
    while not exit_program:
        input_element.click()
        time.sleep(0.1)  # Small delay to ensure the browser processes events
        current_value = input_element.get_attribute("value")

        if last_input != current_value and current_value.endswith("\n"):
            new_input = current_value.split("\n")[-2]  # Get the newest line of input
            if is_running:
                #print(new_input)
                write_output_to_terminal(new_input)
            last_input = current_value

# Define shortcut functions
def start_capture():
    global is_running
    print("Starting input capture.")
    is_running = True

def pause_capture():
    global is_running
    print("Pausing input capture.")
    is_running = False

def exit_capture():
    global exit_program
    print("Exiting program.")
    exit_program = True
    driver.quit()

# Assign keyboard shortcuts
keyboard.add_hotkey('ctrl+shift+s', start_capture)
keyboard.add_hotkey('ctrl+shift+d', pause_capture)
keyboard.add_hotkey('ctrl+shift+e', exit_capture)

# Start capturing input on Enter key press in a separate thread
import threading
capture_thread = threading.Thread(target=capture_input_on_enter, args=(input_field,))
capture_thread.start()

# Keep the main thread alive for listeners
while not exit_program:
    time.sleep(1)

# Ensure the capture thread has finished
capture_thread.join()