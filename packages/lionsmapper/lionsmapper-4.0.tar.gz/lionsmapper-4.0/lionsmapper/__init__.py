import sys
import cv2
import numpy as np
import ast
import matplotlib.pyplot as plt
from skimage import io, color
from skimage.measure import regionprops, label

def _get_color_kmeans(_img_src,color_rgb):
  _c_rgb = color_rgb.split(',')
  _r = np.dtypes.Float64DType[_c_rgb[0]]
  _g = np.dtypes.Float64DType[_c_rgb[1]]
  _b = np.dtypes.Float64DType[_c_rgb[2]]
  _rgb = [_r,_g,_b,]
  image = cv2.imread(str(img))
  hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
  lower_rgb = np.array(_rgb)
  upper_rgb = np.array(color_rgb)
  rgb_mask = cv2.inRange(hsv_image, lower_rgb, upper_rgb)
  rgb_detected = cv2.bitwise_and(image, image, mask=rgb_mask)
  return rgb_detected

def _get_spin_route(_img_src,_color_rgb):
	_img_src_fl = io.imread(_img_src)
	_c_arr = _color_rgb.split(',')
	_c_r = int(_c_arr[0])
	_c_g = int(_c_arr[1])
	_c_b = int(_c_arr[2])
	_c_rgb = [_c_r,_c_g,_c_b]
	_rgb_np = np.array(_c_rgb)
	_axis = {"x":0,"y":0}
	for _r_l in range(_img_src_fl.shape[0]):
		for _r_c in range(_img_src_fl.shape[1]):
			_px_rgb = _img_src_fl[_r_l, _r_c]
			if np.array_equal(_px_rgb, _rgb_np):
				_axis = {"x":0,"y":0}
				_axis["x"] = _r_c
				_axis["y"] = _r_l
				_reg_dt(f"{_img_src}_file_name.txt", str(_axis))
	_c = 'true'
	return _c

def get_map_reader(img_src,_ln):
	_f = _reg_rt(f"{_img_src}_file_name.txt")
	_c = _f[_ln]
	return _c

def _get_axis_line(_line):
	_c_xy = get_map_reader(_img_src,0)
	_c = ast.literal_eval(_c_xy)
	return _c

def _reg_dt(_file_name, _data):
	with open(_file_name, "a") as _f:
		_f.write(f"{_data};")

def _reg_rt(_file_name):
	with open(_file_name, "r") as _f:
		return _f.read().split(';')

def _configure_start(_image='BLANK.png',_rgb_map='255,255,255'):
	_img_src = _f_image
	_color_rgb = _map

_sx = -1
if len(sys.argv) > 1:
	_img_src = sys.argv[1]
	_sx += 1
if len(sys.argv) > 2:
	_color_rgb = sys.argv[2]
	_sx += 1
if(_sx == 1):
	_get_spin_route(_img_src,_color_rgb)
	_map_axis_xy_ln = _get_axis_line(0)