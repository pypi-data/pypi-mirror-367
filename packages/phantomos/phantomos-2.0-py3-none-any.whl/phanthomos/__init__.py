#python
#dataglove_driver.py
import tkinter as tk
import keyboard
import pyautogui
import cv2
import os
from tkinter import Tk, Label
from PIL import Image, ImageTk
from lionsmapper import lions_map_axis as lmx
from lionsmapper import lions_mapper_webcam_capture as lwc
from lionsmapper import lions_map_mv_detect as lmd
import phatom_data_glover_config

_screen_width = 0
_screen_height = 0
_map_keyboard_axis = {"x":0,"y":0,"_key":"HELLO WORLD"}
_keyboard_axis = [_map_keyboard_axis]
_vc = ''
_video_path = 'blank.mp4'
_output_dir = 'blank_fr'
_frame_c = 0
_fl_o = 'blank'

def mv_cap_lst():
	_fl = get_file_saved()
	_fl_o = f"\\temp\\temp_{_fl}\\"
	_vc = cv2.VideoCapture(_fl)
	while _vc.isOpened():
		ret, frame = _vc.read()
		if not ret:
			break
		frame_filename = os.path.join(_fl_o, f'frame_{frame_count:04d}.jpg')
		cv2.imwrite(frame_filename, frame)
		_frame_c += 1
		_vc.release()
	return _fl_o

def get_frame_jpg(_fr_x):
	_vc = cv2.VideoCapture(_fr_x)
	_fl_o = f"\\temp\\temp_{_fl}\\"
	while _vc.isOpened():
		ret, frame = _vc.read()
		if not ret:
			break
		_fr_saved = os.path.join(_fl_o, f'frame_{frame_count:04d}.jpg')
		cv2.imwrite(_fr_saved, frame)
		_frame_c += 1
		_vc.release()
		return _fr_saved
	return 'BLANK'

def mv_cap_axis(_color_rgb):
	frame = lwc.get_frame()
	_fl = get_file_saved()
	_fl_jpg = get_frame_jpg(_fl)
	_frame = f"{_fl_jpg}_map_rgb"
	lmd.update_map_src(_fl_jpg)
	lmd.append_map_rgb(_frame, _color_rgb)
	lmd.get_move(_frame)
	_c = lmd.get_axis()
	return _c

def set_ecran(ecran_src=0):
	root = tk.Tk()
	_screen_width = root.winfo_screenwidth()
	_screen_height = root.winfo_screenheight()
	root.destroy()

def set_keyboard(_axis):
	map_key = find_map_keyboard(_axis)
	keyboard.press(_map_key)

def set_keyboard_return(_axis):
	keyboard.release(_map_key)

def find_map_keyboard(_x,_y,_value):
	_c = _map_keyboard_axis.copy()
	_c = {"x":_x,"y":_y,"_key":_value}
	_keyboard_axis.append(_c)

def set_mouse(_axis):
	pyautogui.moveTo(_axis["x"], _axis["y"], duration=1)

def open_virtual_keyboard():
	window = Tk()
	window.title("PHANTOM_OS_V2L-XKEYBOARD")
	image = Image.open("keyboard.png")
	photo = ImageTk.PhotoImage(image)
	label = Label(window, image=photo)
	label.pack()
	window.mainloop()

def open_virtual_mouse(RGB_DATAGLOVE_LEFT,RGB_DATAGLOVE_RIGHT,RGB_LEFT_CLICK, RGB_RIGHT_CLICK,RGB_SCROOL_DOWN,RGB_SCROOL_UP,RGB_CURSOR):
	if(_c == RGB_DATAGLOVE_LEFT):
		pyautogui.click() #collect RGB DICT GLOVE MAP
	if(_c == RGB_DATAGLOVE_RIGHT):
		pyautogui.hotkey('shift', 'F10')  #collect RGB DICT GLOVE MAP
	if(_c == RGB_LEFT_CLICK):
		pyautogui.click()  #collect RGB DICT GLOVE MAP
	if(_c == RGB_RIGHT_CLICK):
		pyautogui.hotkey('shift', 'F10')  #collect RGB DICT GLOVE MAP
	if(_c == RGB_SCROOLDOWN):
		pyautogui.hotkey('space bar')  #collect RGB DICT GLOVE MAP
	if(_c == RGB_SCROOL_UP):
		pyautogui.hotkey('shift', 'space bar')  #collect RGB DICT GLOVE MAP
	if(_c == RGB_CURSOR):
		pyautogui.moveTo(_axis["x"], _axis["y"], duration=1)  #collect RGB DICT GLOVE MAP

def start_dataglove():
	lwc.start_webcam(video_source=0, max_frame_rate=12)