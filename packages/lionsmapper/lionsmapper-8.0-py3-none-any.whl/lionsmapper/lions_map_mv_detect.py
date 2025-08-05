#python
#script lions_map_mv_detect.py
#detect moviments by file.png updated by webcam or file png updated
#import lions_map_axis

_map_rgb = [{"MAP_NAME":"NAME","RGB":"0,0,0"}]
map_src = 'file.png'

def update_map_src(file):
      map_src = file

def get_lab_map():
     return _map_rgb

def append_map_rgb(map_name,rgb):
     #Append to lab_map_rgb
     map_temp = map_rgb.copy()
     map_temp.MAP_NAME = map_name
     map_temp.rgb = rgb
     _map_rgb.append(map_temp)

def get_move(map_rgb='FULL'):
    if(map_rgb == 'FULL'):
        _c_axis = get_axis()
        _c = [_c_axis]
        for _x in _map_rgb:
             color_rgb = _x["RGB"]
             _c_x = get_move(map_src, color_rgb)
             _c.append(_c_x)
        return _c
    else:
        _c_axis = get_axis()
        _c = [_c_axis]
        for _x in map_rgb:
             if(map_rgb == _map_rgb):
                 color_rgb = _x["RGB"]
                 _c = get_move(map_src, color_rgb)
                 return _c
    return 'BLANK'