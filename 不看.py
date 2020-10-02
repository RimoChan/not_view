import time
import os
import math
from pathlib import Path

import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import fire

from utils import matrix
from utils import cv0

import 窗口


此处 = Path(__file__).parent

glfw.init()

窗口大小 = None
中心 = None
当前窗口大小 = None
显示器大小 = glfw.get_video_mode(glfw.get_primary_monitor()).size


def 生成opengl纹理(npdata):
    w, h = npdata.shape[:2]
    d = 2**int(max(math.log2(w), math.log2(h)) + 1)
    纹理 = np.zeros([d, d, 4], dtype=npdata.dtype)
    纹理[:, :, :3] = 1
    纹理[:w, :h] = npdata
    纹理座标 = (w / d, h / d)

    width, height = 纹理.shape[:2]
    纹理编号 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, 纹理编号)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_FLOAT, 纹理)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glGenerateMipmap(GL_TEXTURE_2D)

    return 纹理编号, 纹理座标


def 设定大小(window, x, y):
    width, height = glfw.get_window_size(window)
    left, top = glfw.get_window_pos(window)
    中心 = left+width/2, top+height/2
    glViewport(0, 0, x, y)
    glfw.set_window_monitor(window, None,
                            xpos=max(0, int(中心[0] - x/2)),
                            ypos=max(38, int(中心[1] - y/2)),
                            width=x,
                            height=min(y, 显示器大小.height),
                            refresh_rate=glfw.DONT_CARE
                            )


def opengl绘图循环(window, 图):
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
        global 窗口大小
        if b > 0:
            窗口大小 *= 1.15
        if b < 0:
            窗口大小 /= 1.15
        if 窗口大小[0] < 220:
            窗口大小 = np.array([220, 220/窗口大小[0]*窗口大小[1]])
    glfw.set_scroll_callback(window, scroll_callback)

    global 当前窗口大小
    当前窗口大小 = 窗口大小.copy()
    画图()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        time.sleep(0.01)
        if 0.9999 < 窗口大小[0]/当前窗口大小[0] < 1.0001:
            continue
        当前窗口大小 = 当前窗口大小*0.6 + 窗口大小*0.4
        设定大小(window, *当前窗口大小.astype(int))
        画图()


def fare(名字):
    global 窗口大小
    图 = cv0.read(名字).astype(np.float32)/255
    if len(图.shape) == 2:
        图 = np.concatenate([图.reshape(*图.shape, 1)]*3, axis=2)
    x, y, 通道数 = 图.shape
    if 通道数 == 3:
        图 = np.concatenate([图, np.ones(shape=[x, y, 1])], axis=2)

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
    设定大小(window, *窗口大小.astype(int))

    opengl绘图循环(window, 图)


fire.Fire(fare)
