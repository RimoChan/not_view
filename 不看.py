import time
import os
import math
from pathlib import Path

import fire
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from rimo_utils import matrix
from rimo_utils import cv0
from rimo_utils import 计时

import 窗口


此处 = Path(__file__).parent

glfw.init()

window = None
图 = None

窗口大小 = None
中心 = None
当前窗口大小 = None
显示器大小 = glfw.get_video_mode(glfw.get_primary_monitor()).size
全屏 = False


def 生成opengl纹理(npdata):
    w, h, 通道数 = npdata.shape
    d = 2**int(max(math.log2(w), math.log2(h)) + 1)
    纹理 = np.zeros([d, d, 通道数], dtype=npdata.dtype)
    纹理[:w, :h] = npdata
    纹理座标 = (w / d, h / d)

    width, height = 纹理.shape[:2]
    纹理编号 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, 纹理编号)
    if 通道数 == 3:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_BGR, GL_UNSIGNED_BYTE, 纹理)
    if 通道数 == 4:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_UNSIGNED_BYTE, 纹理)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    return 纹理编号, 纹理座标


def 夹(a, x, b):
    if x < a:
        return a
    if x > b:
        return b
    return x


def 设定大小(x, y):
    width, height = glfw.get_window_size(window)
    left, top = glfw.get_window_pos(window)
    中心 = left+width/2, top+height/2

    y1, x1 = 图.shape[:2]
    if x1/y1 < x/y:
        xx = int(y/y1*x1)
        glViewport((x-xx)//2, 0, xx, y)
    else:
        yy = int(x/x1*y1)
        glViewport(0, (y-yy)//2, x, yy)

    height = min(y, 显示器大小.height)
    width = min(x, 显示器大小.width)
    if glfw.get_window_attrib(window, glfw.DECORATED):
        ymin = 38
    else:
        ymin = 0

    xmax = 显示器大小.width - width
    ymax = 显示器大小.height - height

    glfw.set_window_monitor(window, None,
                            xpos=夹(0, int(中心[0] - x/2), xmax),
                            ypos=夹(ymin, int(中心[1] - y/2), ymax),
                            width=width,
                            height=height,
                            refresh_rate=glfw.DONT_CARE
                            )


def opengl绘图循环():
    with 计时.计时('生成纹理'):
        纹理编号, 纹理座标 = 生成opengl纹理(图)

    glClearColor(0, 0, 0, 0)

    def 画图():
        glClear(GL_COLOR_BUFFER_BIT)

        glBindTexture(GL_TEXTURE_2D, 纹理编号)
        glColor4f(1, 1, 1, 1)

        a = b = -1
        c = d = 1
        q, w = 纹理座标

        [[p1, p2],
         [p4, p3]] = np.array([
             [[a, b, 0, 1, 0, 0], [a, d, 0, 1, w, 0]],
             [[c, b, 0, 1, 0, q], [c, d, 0, 1, w, q]],
         ])

        t = matrix.rotate_ax(-math.pi/2, axis=(0, 1))
        glBegin(GL_QUADS)
        for p in [p1, p2, p3, p4]:
            glTexCoord2f(*p[4:])
            glVertex4f(*(p[:4]@t))
        glEnd()
        glfw.swap_buffers(window)

    def scroll_callback(_, __, b):
        if 全屏:
            return
        global 窗口大小
        if b > 0:
            窗口大小 *= 1.15
        if b < 0:
            窗口大小 /= 1.15
        if 窗口大小[0] < 220:
            窗口大小 = np.array([220, 220/窗口大小[0]*窗口大小[1]])
    glfw.set_scroll_callback(window, scroll_callback)

    with 计时.计时('第一次画图'):
        画图()

    def key_callback(_, key, __, 方向, ___):
        window.key_callback(_, key, __, 方向, ___)
        if 方向 != 1:
            return
        # enter
        if key == 257:
            全屏切换()
    glfw.set_key_callback(window, key_callback)

    global 当前窗口大小
    当前窗口大小 = 窗口大小.copy()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        time.sleep(0.01)
        if 全屏:
            目标大小 = np.array([显示器大小.width, 显示器大小.height])
        else:
            目标大小 = 窗口大小
        if 0.9999 < 目标大小[0]/当前窗口大小[0] < 1.0001:
            continue
        当前窗口大小 = 当前窗口大小*0.6 + 目标大小*0.4
        设定大小(*当前窗口大小.astype(int))
        画图()


def 全屏切换():
    global 全屏
    全屏 = not 全屏
    if 全屏:
        glfw.set_window_attrib(window, glfw.DECORATED, False)
    else:
        glfw.set_window_attrib(window, glfw.DECORATED, True)


def fare(名字):
    global 窗口大小, window, 图

    with 计时.计时('读图'):
        图 = cv0.read(名字)
    with 计时.计时('修改通道'):
        if len(图.shape) == 2:
            图 = np.concatenate([图.reshape(*图.shape, 1)]*3, axis=2)
        x, y, _ = 图.shape

    窗口大小 = np.array([y, x], dtype=np.float64)
    if 窗口大小[0] < 220:
        窗口大小 = np.array([220, 220/窗口大小[0]*窗口大小[1]])
    t = 显示器大小.width - 100
    if 窗口大小[0] > t:
        窗口大小 = np.array([t, t/窗口大小[0]*窗口大小[1]])
    t = 显示器大小.height - 100
    if 窗口大小[1] > 显示器大小.height:
        窗口大小 = np.array([t/窗口大小[1]*窗口大小[0], t])

    标题 = f'{os.path.split(名字)[-1]} - not_view'
    window = 窗口.新建窗口(窗口大小.astype(int), 标题, 图标路径=此处/'res/rimo32.png')
    glfw.make_context_current(window)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
    设定大小(*窗口大小.astype(int))

    opengl绘图循环()


fire.Fire(fare)
