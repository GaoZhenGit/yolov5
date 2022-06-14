import time
import subprocess as sp
from threading import Thread


class Rtmp:
    def __init__(self, rtmp_url, fps, width, height):
        sizeStr = str(width) + 'x' + str(height)
        fps = 10
        hz = int(1000.0 / fps)
        print ('------------------size:'+ sizeStr + ' fps:' + str(fps) + ' hz:' + str(hz) + '------------------')
        command = ['ffmpeg',
                '-hwaccel','cuvid',
                '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', "{}x{}".format(width, height),
                '-r', str(fps),
                '-i', '-',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'veryfast',
                '-b:v', '1.5M',
                '-maxrate', '2M',
                '-bufsize','3000k',
                # '-vf', 'drawtext="drawtext=fontsize=160:text=\'%\{localtime\:%T\}\'"',
                '-f', 'flv',
                rtmp_url]
        self.pipe = sp.Popen(command, stdin=sp.PIPE) #,shell=False
        pass

    def push(self, frame):
        self.pipe.stdin.write(frame.tostring())
    
    def release(self):
        pass