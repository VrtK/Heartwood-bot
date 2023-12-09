import os
import sys
import cv2
import glob
import time
import ctypes
import requests
import datetime
import pyautogui
import threading
import numpy as np
import tkinter as tk
import pygetwindow as gw
from datetime import datetime
from tkinter import PhotoImage

global Lilian
full_counter = 0
lifted_coal = 0

SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

W = 0x11
A = 0x1E
S = 0x1F
D = 0x20
Z = 0x2C
X = 0x2D
Q = 0x10
E = 0x12
UP = 0xC8
DOWN = 0xD0
LEFT = 0xCB
RIGHT = 0xCD
ENTER = 0x1C


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def move_left():
    print('left')
    PressKey(A)
    time.sleep(0.3)
    ReleaseKey(A)


def move_right():
    print('right')
    PressKey(D)
    time.sleep(0.3)
    ReleaseKey(D)


def move_up():
    print('up')
    PressKey(W)
    time.sleep(0.3)
    ReleaseKey(W)


def move_down():
    print('down')
    PressKey(S)
    time.sleep(0.3)
    ReleaseKey(S)


def attack():
    print('down')
    PressKey(0x39)
    time.sleep(0.3)
    ReleaseKey(0x39)


def action():
    print('action')
    PressKey(E)
    time.sleep(0.3)
    ReleaseKey(E)


def drag_and_drop(start_x, start_y, end_x, end_y):
    # Move to the starting position
    pyautogui.moveTo(start_x, start_y)
    # Press the left mouse button
    pyautogui.mouseDown()
    # Move to the ending position
    pyautogui.moveTo(end_x, end_y)
    # Release the left mouse button
    pyautogui.mouseUp()


def wait_for_window():
    while True:
        active_window = gw.getActiveWindow()
        if active_window and active_window.title == window_title:
            return True


# Define the initial character position
window_title = 'BlueStacks App Player'
mining_template = 'MISC/mining/Capture.JPG'


def move_character_towards_object(character_x, character_y, object_center_x, object_center_y, distance):
    print(f'Moving to object {object_center_x},{object_center_y}')
    distance_x = object_center_x - character_x
    distance_y = object_center_y - character_y

    if int(distance) == 161:
        move_up()

    if distance_x > 10:
        move_right()
    elif distance_x < 10:
        move_left()

    if distance_y > 10:
        move_down()
    elif distance_y < 10:
        move_up()


def calculate_distance(obj1, obj2):
    x1, y1 = obj1
    x2, y2 = obj2

    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance


def create_live_duplicate(window_title):
    global Lilian
    global lifted_coal
    # Find the game window by its title and activate it
    target_window = gw.getWindowsWithTitle(window_title)

    if len(target_window) == 0:
        print(f"Window with title '{window_title}' not found.")
        return

    target_window = target_window[0]

    character_x = target_window.width // 2
    character_y = target_window.height // 2

    while not target_window.isActive:
        time.sleep(1)

    while True:
        if not Lilian:
            break

        while not target_window.isActive:
            time.sleep(1)
        # Capture a screenshot of the active window
        screenshot = pyautogui.screenshot(
            region=(target_window.left, target_window.top, target_window.width, target_window.height))

        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # Load the template image
        mining_template_read = cv2.imread(mining_template)
        obj_mining = cv2.matchTemplate(screenshot, mining_template_read, cv2.TM_CCOEFF_NORMED)
        mining_min_val, mining_max_val, mining_min_loc, mining_max_loc = cv2.minMaxLoc(obj_mining)
        if mining_max_val > 0.85:
            print(f'Found mining action')
            action()
            lifted_coal += 1
            label_lifted_coal.config(text=f'Found Coal\n{lifted_coal}')
            time.sleep(5)

        folder_path = 'MISC/mining/ore'  # Update with the path to your folder
        image_paths = glob.glob(os.path.join(folder_path, '*.jpg')) + glob.glob(os.path.join(folder_path, '*.png'))

        for image_path in image_paths:
            template = cv2.imread(image_path)
            obj_result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            # Get the coordinates of the matched region
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(obj_result)
            if max_val > 0.7:
                print(f'Found Ore {round(max_val, 4)} {os.path.basename(image_path)}')
                # Get the width and height of the template
                template_width, template_height = template.shape[1], template.shape[0]

                # Draw a rectangle around the detected object
                top_left = max_loc
                bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
                cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)

                # Calculate the center of the detected object
                ore_object_centroid = (top_left[0] + template.shape[1] // 2, top_left[1] + template.shape[0] // 2)
                object_center_x = top_left[0] + (template_width // 2)
                object_center_y = top_left[1] + (template_height // 2)

                # Check if object is in range
                main_template = cv2.imread('MISC/mining/main.JPG')
                result = cv2.matchTemplate(screenshot, main_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = max_loc
                main_object_centroid = (top_left[0] + template.shape[1] // 2, top_left[1] + template.shape[0] // 2)

                if max_val > 0.7:
                    distance = calculate_distance(main_object_centroid, ore_object_centroid)
                    if distance > 450:
                        print(f'Too far! Distance:{round(distance, 4)}')
                        continue
                    else:
                        # Move the character towards the object
                        move_character_towards_object(character_x, character_y, object_center_x, object_center_y, distance)
                else:
                    print('Cannot find main obj, lets search it')
                    move_down()

                break
        check_for_misc()
        display_image(screenshot)


def display_image(screenshot):
    height, width, _ = screenshot.shape
    aspect_ratio = width / height
    new_width = min(300, width)
    new_height = min(200, int(new_width / aspect_ratio))
    resized_image = cv2.resize(screenshot, (new_width, new_height))

    # Convert NumPy array to Tkinter PhotoImage
    screenshot_tk = PhotoImage(data=cv2.imencode('.ppm', resized_image)[1].tobytes())

    # Update the output_widget with the new image
    image_label.config(image=screenshot_tk)
    image_label.image = screenshot_tk


def check_for_misc():
    folder_path = 'MISC/game/lost_connection'
    image_paths = glob.glob(os.path.join(folder_path, '*.jpg'))
    for image_path in image_paths:
        _, _, val = find_object_in_game(window_title, image_path)
        if val > 0.5:
            print('connection lost')
            telegram('connection lost')
            stop_function()

    _, _, val = find_object_in_game(window_title, 'MISC/game/died.JPG')
    if val > 0.5:
        print('Died :(')
        telegram('Died :(')
        stop_function()

    _, _, val = find_object_in_game(window_title, 'MISC/mining/storage/coal_onground.JPG')
    if val > 0.5:
        print('Found Coal on ground')
        global full_counter
        global lifted_coal
        full_counter += 1
        action()  # Trying to collect the coal
        if full_counter == 6:
            print('Full Bag! Yay!')
            telegram(f'Full Bag!, Lifted coal: {lifted_coal}')
            full_counter = 0
            lifted_coal = 0
            global Lilian
            Lilian = False
            print(f'Bot is active? {Lilian}')
            town_function(bank=True)
            back_to_spot_function()
            Lilian = True
            print(f'Bot is active? {Lilian}')


def start_function():
    global Lilian
    print("Starting Bot")
    Lilian = True
    print(f'Bot is active? {Lilian}')
    threading.Thread(target=create_live_duplicate, args=(window_title,)).start()
    start_button["state"] = "disabled"
    stop_button["state"] = "normal"


def stop_function():
    global Lilian
    print("Stopping Bot")
    Lilian = False
    print(f'Bot is active? {Lilian}')
    start_button["state"] = "normal"
    stop_button["state"] = "disabled"


def find_object_in_game(window_title, obj_path):
    target_window = gw.getWindowsWithTitle(window_title)[0]
    screenshot = pyautogui.screenshot(
        region=(target_window.left, target_window.top, target_window.width, target_window.height))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    results = cv2.matchTemplate(screenshot, cv2.imread(obj_path), cv2.TM_CCOEFF_NORMED)
    result_min_val, result_max_val, result_min_loc, result_max_loc = cv2.minMaxLoc(results)
    x, y = result_max_loc
    x += target_window.left
    y += target_window.top
    return x, y, result_max_val


def store_function():
    wait_for_window()
    print('Start store coal')

    # First create on empty slot
    x, y, coal_val = find_object_in_game(window_title, 'MISC/mining/storage/coal.JPG')
    if coal_val > 0.6:
        x_empty, y_empty, _ = find_object_in_game(window_title, 'MISC/mining/storage/empty.JPG')
        drag_and_drop(x + 25, y + 25, x_empty + 25, y_empty + 25)

        x_coal = 1030
        counter = 0
        for itemx in range(6):
            print(f'Store item #{itemx}')
            x_coal += 70
            y_coal = 230
            for itemy in range(6):
                y_coal += 70
                drag_and_drop(x_coal, y_coal, x_empty + 25, y_empty + 55)
                time.sleep(0.2)
                counter += 1
                if counter == 20:
                    x, y, _ = find_object_in_game(window_title, 'MISC/mining/storage/coal.JPG')
                    x_empty, y_empty, _ = find_object_in_game(window_title, 'MISC/mining/storage/empty.JPG')
                    drag_and_drop(x, y, x_empty + 25, y_empty + 25)
                    time.sleep(0.2)


def pull_function():
    wait_for_window()
    print('Pulling Items')
    x_coal = 1030
    for itemx in range(6):
        print(f'Pull item #{itemx}')
        x_coal += 70
        y_coal = 230
        for itemy in range(6):
            x, y, _ = find_object_in_game(window_title, 'MISC/mining/storage/coal_in_bank.JPG')
            y_coal += 70
            drag_and_drop(x + 25, y + 25, x_coal, y_coal)
            time.sleep(0.2)


def trade_function():
    wait_for_window()
    print('Trading Coal')
    x_empty, y_empty, val_trade = find_object_in_game(window_title, 'MISC/mining/storage/trade_title.JPG')
    for item in range(6):
        x, y, coal_max_val = find_object_in_game(window_title, 'MISC/mining/storage/coal.JPG')
        if coal_max_val > 0.9:
            y_empty += 70
            drag_and_drop(x + 25, y + 25, x_empty, y_empty)
            time.sleep(0.2)


def shout_function():
    wait_for_window()
    shout_text = '############ Sell Coal 4g, PM ME ### Sell Coal 4g, PM ME ### Sell Coal 4g, PM ME ### Sell Coal 4g, PM ME ##############'
    val_msg = 0
    while val_msg < 0.5:
        time.sleep(3)
        move_up()
        print('Shouting!')
        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.write(shout_text)
        time.sleep(0.5)
        pyautogui.press('enter')
        move_down()
        _, _, val_msg = find_object_in_game(window_title, 'MISC/game/new_message.JPG')
        if val_msg > 0.8:
            print('Stop Shouting')
            telegram('Found Buyer!')
            break


def town_function(bank=True):
    wait_for_window()
    x, y, val_town = find_object_in_game(window_title, 'MISC/game/town.JPG')
    if val_town > 0.8:
        print('Going to town')
        pyautogui.click(x, y)
    time.sleep(3)
    for _ in range(2):
        move_up()
        move_right()
    for _ in range(11):
        move_right()
    for _ in range(10):
        move_up()
    if bank:
        action()
        time.sleep(2.5)
        store_function()
        time.sleep(1)
        pyautogui.press('esc')
        time.sleep(1)


def back_to_spot_function():
    print('Going back to spot')
    for _ in range(13):
        move_down()
    for _ in range(23):
        move_left()
    for _ in range(20):
        move_down()


class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        lines = string.split('\n')

        for line in lines:
            if line:
                self.text_widget.insert(tk.END, timestamp + line + '\n')
        self.text_widget.see(tk.END)  # Autoscroll to the bottom


def telegram(string):
    # Some telegram settings
    chat_id = 1012000000000701
    id_and_token = 'bot1742531231:AAG2xjsDJ9heaNWM96wMEB433bVwLHVVHAU'
    requests.get(f"https://api.telegram.org/{id_and_token}/sendMessage?chat_id={chat_id}&text={string}")


if __name__ == "__main__":
    Lilian = False
    root = tk.Tk()
    root.title("Bukra Fil mish-mish")
    root.geometry("305x555+0+0")
    root.attributes("-topmost", True)
    root.wm_attributes('-toolwindow', 1)

    # Create a Text widget to display the console output
    console_output = tk.Text(root, wrap=tk.WORD, height=14, width=35)
    console_output.grid(row=1, column=0, columnspan=2, padx=10, pady=10)  # span both columns
    sys.stdout = RedirectText(console_output)

    start_button = tk.Button(root, text="Start", command=start_function, fg="green")
    start_button.grid(row=0, column=0, padx=10, pady=10)

    stop_button = tk.Button(root, text="Stop", command=stop_function, fg="red")
    stop_button.grid(row=0, column=1, padx=10, pady=10)

    store_button = tk.Button(root, text="Store Coal", command=store_function, padx=1, pady=1)
    store_button.grid(row=3, column=0)

    pull_button = tk.Button(root, text="Pull Coal", command=pull_function, padx=1, pady=1)
    pull_button.grid(row=3, column=1)

    trade_button = tk.Button(root, text="Trade Coal", command=trade_function, padx=1, pady=1)
    trade_button.grid(row=3, column=0, columnspan=3)

    shout_button = tk.Button(root, text="Shout", command=shout_function, padx=1, pady=1)
    shout_button.grid(row=4, column=0, columnspan=3)

    town_button = tk.Button(root, text="Town", command=town_function, padx=1, pady=1)
    town_button.grid(row=4, column=1)

    spot_button = tk.Button(root, text="Back To Spot", command=back_to_spot_function, padx=1, pady=1)
    spot_button.grid(row=4, column=0)

    image_label = tk.Label(root)
    image_label.grid(row=2, column=0, columnspan=3, padx=0, pady=10)

    label_lifted_coal = tk.Label(root, text="", fg="blue")
    label_lifted_coal.grid(row=0, column=0, columnspan=3, padx=0, pady=10)

    print('Welcome!')
    print('Version 1.1')
    stop_button["state"] = "disabled"

    root.mainloop()
