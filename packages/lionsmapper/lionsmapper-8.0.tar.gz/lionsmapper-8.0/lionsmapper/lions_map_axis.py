#python
#script lions_map_axis.py

_axis = {'x': 0, 'y': 0}
_color_rgb = '255,255,255'

def get_move_update(time, _img_src, color_rgb):
    _axis = get_move(_img_src, color_rgb)
    if(_time == -1):
        return 'false'
    #get_move_update(time, _img_src, color_rgb)

def get_axis():
    return _axis

def get_move(_img_src, color_rgb,_update=0):
    if(_update == 1):
        __axis = getSpinRoute(img_src,color_rgb)
    return _axis #{'x': 199, 'y': 7}