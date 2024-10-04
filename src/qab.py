import uiautomator2 as u2
import cv2
import numpy as np
from time import sleep
import os, subprocess, signal

def find_image(image_path1, image_path2, tolerance):
  """
  This function takes two image paths and a tolerance as parameters.
  It searches for the image at `image_path2` within the image at `image_path1` and returns the center coordinates of the found rectangle.

  Args:
    image_path1: The path to the main image.
    image_path2: The path to the image to search for.
    tolerance: The color tolerance for the match.

  Returns:
    A tuple representing the center coordinates (x, y) of the found rectangle, or None if no match is found.
  """

  # Check if the images exist
  if not os.path.exists(image_path1) or not os.path.exists(image_path2):
    # If either of the images does not exist, return None
    return None, None

  # Read the images
  image1 = cv2.imread(image_path1)
  image2 = cv2.imread(image_path2)

  # Convert to grayscale
  image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
  image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

  # Apply template matching
  result = cv2.matchTemplate(image1_gray, image2_gray, cv2.TM_CCOEFF_NORMED)

  # Find the location of the best match
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

  # Check if the match is good enough
  if max_val >= tolerance:
    # Find the top-left corner of the matching region
    topLeft = max_loc

    # Find the bottom-right corner of the matching region
    bottomRight = (topLeft[0] + image2.shape[1], topLeft[1] + image2.shape[0])

    # Calculate the center coordinates based on top-left and bottom-right corners
    centerX = (topLeft[0] + bottomRight[0]) // 2
    centerY = (topLeft[1] + bottomRight[1]) // 2

    # Return the center coordinates as a tuple
    return (centerX, centerY)

  # If the match is not good enough, return None
  return None, None

def find_text(text):
    # TODO
    return

def wait_for_reference():
    return

def get_files_in_folder(folder_path):
    """
    Esta função recebe o caminho de uma pasta e retorna uma lista com todos os arquivos dentro da pasta.

    Args:
        folder_path: O caminho para a pasta.

    Returns:
        Uma lista de strings representando os nomes dos arquivos na pasta.
    """

    if not os.path.exists(folder_path):
        raise OSError(f"Caminho da pasta inválido: {folder_path}")

    files = []
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            files.append(file)

    return files

def get_device_resolution():
    """
    Retrieves the device's screen resolution.

    Returns:
        str: A string representing the device's screen resolution in the format "heightxwidth".
    """
    d = u2.connect()
    return str(f"{d.info['displayHeight']}x{d.info['displayWidth']}")

def clear_logcat_buffer():
  """Clears the Android logcat buffer using adb."""
  subprocess.run(['adb', 'logcat', '-c'])

def logcat_capture():
    print("Taking logs...")
    subprocess.run(['adb', 'logcat', '>', 'log.txt'], timeout=1)

def is_app_installed(package_name):
    # use adb shell dumpsys package to check if the package is installed
    d = u2.connect()
    try:
        app_info = d.app_info(package_name)
    except:
        print(f"Package {package_name} is not installed.")
        return False
    #if app_info is None:
    #    return False

    print(f"App {package_name} {app_info} is installed")
    return app_info

def uninstall_app(package_name: str):
    """
    Uninstalls an application with the given package name.

    Args:
        package_name (str): The name of the package to be uninstalled.

    Returns:
        None
    """
    d = u2.connect()
    d.app_stop(package_name)
    d.app_uninstall(package_name)

#uninstall_app("com.hcg.ctw.gp")

def check_onscreen_app():
    """
    Retrieves the package name of the app currently on screen.
    
    Uses the Android Debug Bridge (ADB) to execute a shell command that dumps the display information and finds the foreground app package name.
    
    Returns:
        str: The package name of the app currently on screen.
    """
    comando = 'adb shell dumpsys display | find "mForegroundAppPackageName"'
    full_stdout = subprocess.run(comando, capture_output=True, shell=True, text=True).stdout
    onscreen_package_name = full_stdout.split("=")[1].strip()
    return onscreen_package_name

#print(check_onscreen_app())

def click_in_image(image_path, connection: u2.connect = None):
    """
    Simulates a click on a given image within the current screen.

    Args:
        image_path (str): The path to the image to be clicked.
        connection (u2.connect, optional): The connection object. Defaults to None.

    Returns:
        int: 1 if the click was successful, -1 if the image was not found.
    """
    if connection is None:
        #print("Connecting...")
        d = u2.connect()

    d.screenshot("./.tmp/actual_screenshot.png")
    if not d:
        raise ValueError("Invalid connection object")

    screenshot_path = "./.tmp/actual_screenshot.png"
    if not os.path.exists(screenshot_path):
        raise FileNotFoundError("Screenshot file not found")

    x, y = find_image(screenshot_path, image_path, 0.85)
    if x is None or y is None:
        print(f"Asset {image_path} not found in the screenshot.")
        return -1
    else:
        print(f"Asset {image_path} found in the screenshot.")
        d.click(x, y)
        print(f"Click x={x} y={y}")
        return 1
    
#click_in_image('./mlbb_icon.png')
#find_image("./tmp/actual_screenshot.png", "./mlbb_icon.png", 0.8)

def write_text(text_to_write: str, end_enter: bool = True, connection: u2.connect = None):
    """
    Writes the given text to the current device screen and optionally presses the enter key.

    Args:
        text_to_write (str): The text to be written to the device screen.
        end_enter (bool, optional): Whether to press the enter key after writing the text. Defaults to True.
        connection (u2.connect, optional): The connection object to use. If None, a new connection will be established. Defaults to None.

    Returns:
        None
    """
    if connection is None:
        d = u2.connect()
    d.send_keys(text_to_write)
    if end_enter:
        sleep(1)
        d.press('enter')

def start_app(package_name):
    """
    Starts the application with the given package name.
    Args:
        package_name (str): The name of the package to be started.
    Returns:
        tuple: A tuple containing the u2 connection object and the package name.
    """
    d = u2.connect()

    d.app_stop('com.github.uiautomator')
    print(f"Starting {package_name}...")
    d.app_stop(package_name)
    d.app_start(package_name)
    return d, package_name

def start_recording() -> int:
    """
    Starts recording the screen of the device connected to the computer using adb screenrecorder.

    Args:
        output_file_path (str): The path where the recorded screen will be saved.

    Returns:
        int: The process ID of the running ADB command.
    """
    # TODO: create a tmp folder: sdcard/qab_tmp
    
    command = f"adb shell screenrecord sdcard/qab_tmp/recording.mp4"
    process = subprocess.Popen(command, shell=True)
    print(f"Recording started with PID: {process.pid}")
    return process.pid

def stop_recording(adb_recording_pid: str):
    """
    Stops the recording process with the given ADB recording PID.

    Args:
        adb_recording_pid (int): The PID of the ADB recording process.

    Returns:
        None
    """
    os.kill(adb_recording_pid, signal.SIGILL)
    print("Recording stopped")
    return


'''recording_PID = start_recording()
print(f'recording PID: {recording_PID}')
sleep(5)
start_app('com.android.vending')
sleep(10)
stop_recording(recording_PID)'''

def app_flow(test_name: str):
    """
    Test the app flow of the given package name.

    Args:
        package_name (str): The name of the package to be tested.

    Returns:
        None
    """
    package_name = check_onscreen_app()
    
    not_found_counter = 0
    clicked_asset_buffer = []
    test_assets_path = f"./app_flows/{package_name}/assets"#/{test_name}"
    not_found_counter = 0
    while not_found_counter < 5:
        test_assets_list = sorted(get_files_in_folder(test_assets_path), key=lambda x: int(x.split("_")[0]))
        print(f"test_assets_list: {test_assets_list}")
        for asset in list(set(test_assets_list) - set(clicked_asset_buffer)):
            result = click_in_image(test_assets_path + "/" + asset)
            if result == 1:
                clicked_asset_buffer.insert(0, asset)
                clicked_asset_buffer = clicked_asset_buffer[:3]
                print(f"clicked_asset_buffer: {clicked_asset_buffer}")
                not_found_counter = 0
                break
        not_found_counter += 1
        print(f"not_found_counter: {not_found_counter}")
        sleep(1)
    return

def test_flow(test_name, excluded_assets: list = []):
    not_found_counter = 0
    clicked_asset_buffer = []
    test_assets_path = f"./testing_flows/{test_name}"
    not_found_counter = 0
    while not_found_counter < 5:
        test_assets_list = sorted(get_files_in_folder(test_assets_path), key=lambda x: int(x.split("_")[0]))
        print(f"test_assets_list: {test_assets_list}")
        for asset in list(set(test_assets_list) - set(clicked_asset_buffer) - set(excluded_assets)):
            result = click_in_image(test_assets_path + "/" + asset)
            #print(f"Result: {result}")
            if result == 1:
                clicked_asset_buffer.insert(0, asset)
                clicked_asset_buffer = clicked_asset_buffer[:3]
                print(f"clicked_asset_buffer: {clicked_asset_buffer}")
                not_found_counter = 0
                break
        not_found_counter += 1
        print(f"not_found_counter: {not_found_counter}")
        sleep(1)
    return


'''def app_crawler(test_list: list, test_functions_list: list = None, *args, **kwargs):
    package_name = input(f"Package name to be tested: ")#script_path.split("/")[-2]

    tests_dict = {i+1: valor for i, valor in enumerate(test_list)}
    print(tests_dict)
    print("==============================")
    for test_number, test_name in tests_dict.items():
        print(f"{test_number}. {test_name}")
    print("==============================")

    base_assets_path = f"./tests/{test_name}"
    assets_path = "./MyTests/" + package_name + "/assets"
    tmp_screenshot_path = "./MyTests/" + package_name + "/.tmp/actual_screenshot.png"

    test_number = input(f"Test to be done: ")
    test_name = tests_dict[int(test_number)]

    d = start_app(package_name)

    print("Sleeping for 15sec for loading...")
    sleep(15)

    #asset = '/Users/joaofaria/Desktop/Tools/apk_tester/MyTests/com.matchington.mansion/assets/red_x.png'
    print("here")

    clear_logcat_buffer() # Clear the logcat buffer

    while 1:
        is_base_asset = None
        x, y= None, None
        ingame_assets_list = sorted(get_files_in_folder(assets_path))
        base_assets_list = sorted(get_files_in_folder(base_assets_path))
        # print(base_assets_list)
        # print(ingame_assets_list)
        actual_screenshot = d.screenshot(tmp_screenshot_path)
        for base_asset in base_assets_list:
            x, y = find_image(tmp_screenshot_path, base_assets_path + "/" + base_asset, 0.8)
            if x != None and y != None:
                print(f"Asset {base_asset} found in the screenshot.")
                d.click(x, y)
                print("tap x=%s y=%s" % (x, y))
                is_base_asset = True
            else:
                print(f"Asset {base_asset} not found in the screenshot.")
        if is_base_asset != True:
            for asset in ingame_assets_list:
                x, y = find_image(tmp_screenshot_path, assets_path + "/" + asset, 0.8)
                if x != None and y != None:
                    print(f"Asset {asset} found in the screenshot.")
                    d.click(x, y)
                    print("tap x=%s y=%s" % (x, y))
                    is_base_asset = False
                else:
                    print(f"Asset {asset} not found in the screenshot.")
        if is_base_asset is None:
            if test_functions_list is None:
                for test_function in test_functions_list:
                    result = test_function(*args, **kwargs)
        #logcat_capture()
        #sleep(3)
    return'''