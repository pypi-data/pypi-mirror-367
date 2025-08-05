"""
{'breif': 'MaixPy C/C++ API from MaixCDK'}
"""
from __future__ import annotations
from . import ahrs
from . import app
from . import audio
from . import camera
from . import comm
from . import display
from . import err
from . import example
from . import ext_dev
from . import fs
from . import http
from . import i18n
from . import image
from . import log
from . import network
from . import nn
from . import peripheral
from . import pipeline
from . import protocol
from . import rtmp
from . import rtsp
from . import sys
from . import tensor
from . import thread
from . import time
from . import touchscreen
from . import tracker
from . import util
from . import uvc
from . import video
__all__ = ['Vector3f', 'Vector3i16', 'Vector3i32', 'Vector3u16', 'Vector3u32', 'ahrs', 'app', 'audio', 'camera', 'comm', 'display', 'err', 'example', 'ext_dev', 'fs', 'http', 'i18n', 'image', 'log', 'network', 'nn', 'peripheral', 'pipeline', 'protocol', 'rtmp', 'rtsp', 'sys', 'tensor', 'thread', 'time', 'touchscreen', 'tracker', 'util', 'uvc', 'video']
class Vector3f:
    x: float
    y: float
    z: float
    def __init__(self, x0: float, y0: float, z0: float) -> None:
        ...
class Vector3i16:
    x: int
    y: int
    z: int
    def __init__(self, x0: int, y0: int, z0: int) -> None:
        ...
class Vector3i32:
    x: int
    y: int
    z: int
    def __init__(self, x0: int, y0: int, z0: int) -> None:
        ...
class Vector3u16:
    x: int
    y: int
    z: int
    def __init__(self, x0: int, y0: int, z0: int) -> None:
        ...
class Vector3u32:
    x: int
    y: int
    z: int
    def __init__(self, x0: int, y0: int, z0: int) -> None:
        ...
