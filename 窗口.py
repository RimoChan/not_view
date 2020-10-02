import glfw

from utils import cv0


glfw.init()

def 图标(path):
    图标 = cv0.read(str(path))
    图标 = cv0.cvtColor(图标, cv0.COLOR_BGRA2RGBA)
    x, y = 图标.shape[:2]
    return [y, x, 图标]


def 新建窗口(尺寸, 标题, 图标路径=None):
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.FLOATING, True)
    window = glfw.create_window(*尺寸, 标题, None, None)
    
    if 图标:
        glfw.set_window_icon(window, 1, 图标(图标路径))

    def key_callback(window, key, _, 方向, __):
        if 方向 != 1:
            return
        d = {
            'D': glfw.DECORATED,
            'F': glfw.FLOATING,
        }
        if chr(key) in d:
            flag = d[chr(key)]
            t = glfw.get_window_attrib(window, flag)
            glfw.set_window_attrib(window, flag, not t)
    glfw.set_key_callback(window, key_callback)

    return window
