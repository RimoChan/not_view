import glfw
from rimo_utils import cv0


glfw.init()


def 图标(path):
    图标 = cv0.read(str(path))
    图标 = cv0.cvtColor(图标, cv0.COLOR_BGRA2RGBA)
    x, y = 图标.shape[:2]
    return [y, x, 图标]


def 新建窗口(尺寸, 标题, 图标路径=None, 内置按键回调=True):
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.FLOATING, True)
    window = glfw.create_window(*尺寸, 标题, None, None)

    if 图标路径:
        glfw.set_window_icon(window, 1, 图标(图标路径))

    if 内置按键回调:
        def key_callback(_, key, __, 方向, ___):
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
            # esc
            if key == 256:
                glfw.set_window_should_close(window, True)
        window.key_callback = key_callback
        glfw.set_key_callback(window, key_callback)

    return window
