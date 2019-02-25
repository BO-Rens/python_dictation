"""
LED light pattern like Google Home
"""
import pickle
import apa102
import time
import threading
try:
    import queue as Queue
except ImportError:
    import Queue as Queue


class Pixels:
    PIXELS_N = 3

    def __init__(self):
        self.basis = [0] * 3 * self.PIXELS_N
        self.basis[0] = 2
        self.basis[3] = 1
        self.basis[4] = 1
        self.basis[7] = 2

        self.colors = [0] * 3 * self.PIXELS_N
        self.dev = apa102.APA102(num_led=self.PIXELS_N)

        self.next = threading.Event()
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def wakeup(self, direction=0):
        def f():
            self._wakeup(direction)

        self.next.set()
        self.queue.put(f)

    def listen(self):
        self.next.set()
        self.queue.put(self._listen)

    def think(self):
        self.next.set()
        self.queue.put(self._think)

    def speak(self):
        self.next.set()
        self.queue.put(self._speak)

    def off(self):
        self.next.set()
        self.queue.put(self._off)

    def _run(self):
        while True:
            func = self.queue.get()
            func()

    def _wakeup(self, direction=0):
        for i in range(1, 25):
            colors = [i * v for v in self.basis]
            self.write(colors)
            time.sleep(0.01)

        self.colors = colors

    def _listen(self):
        for i in range(1, 25):
            colors = [i * v for v in self.basis]
            self.write(colors)
            time.sleep(0.01)

        self.colors = colors

    def _think(self):
        colors = self.colors

        self.next.clear()
        while not self.next.is_set():
            colors = colors[3:] + colors[:3]
            self.write(colors)
            time.sleep(0.2)

        t = 0.1
        for i in range(0, 5):
            colors = colors[3:] + colors[:3]
            self.write([(v * (4 - i) / 4) for v in colors])
            time.sleep(t)
            t /= 2

        # time.sleep(0.5)

        self.colors = colors

    def _speak(self):
        colors = self.colors
        gradient = -1
        position = 24

        self.next.clear()
        while not self.next.is_set():
            position += gradient
            self.write([(v * position / 24) for v in colors])

            if position == 24 or position == 4:
                gradient = -gradient
                time.sleep(0.2)
            else:
                time.sleep(0.01)

        while position > 0:
            position -= 1
            self.write([(v * position / 24) for v in colors])
            time.sleep(0.01)

        # self._off()

    def _off(self):
        self.write([0] * 3 * self.PIXELS_N)

    def write(self, colors):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(colors[3*i]), int(colors[3*i + 1]), int(colors[3*i + 2]))

        self.dev.show()


    def _blinking1(self):
        colorsA=[0, 0, 0, 0, 0, 0, 0, 0, 0]
        colorsB=[0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.next.clear()
        while not self.next.is_set():
            
            fr = open('recfile','rb') 
            patern = pickle.load(fr)  
            fr.close()

            if patern == 1: #recording - led 1 blinking red
                colorsA[6:]=50, 0, 0
                colorsB[6:]=0, 0, 0
            elif patern ==2: #not recording - led 1 off
                colorsA[6:]=0, 0, 0
                colorsB[6:]=0, 0, 0
            elif patern ==3: # error : solid red
                colorsA[6:]=50, 0, 0
                colorsB[6:]=50, 0, 0
            else:
                colorsA[6:]=0, 0, 0
                colorsB[6:]=0, 0, 0

            fa = open('anafile','rb') 
            patern = pickle.load(fa)  
            fa.close()

            if patern == 1: #online  - led 3 solid blue 
                colorsA[:3]=0, 0, 50
                colorsB[:3]=0, 0, 50
            elif patern ==2: #analysis in progress - led 3 blinking blue
                colorsA[:3]=0, 0, 0
                colorsB[:3]=0, 0, 50
            else:
                colorsA[:3]=0, 0, 0
                colorsB[:3]=0, 0, 0

            '''
            fa = open(anafile,'r') 
            ledana = pickle.load(anafileopbj1)  
            ledonline = pickle.load(anafileobj2)
            anafileopbj.close()

            

            if ledana == 1: #analysing - led 2 blinking blue
                colorsA[3:6]=0, 0, 50
                colorsB[3:6]=0, 0, 0
            else:
                colorsA[3:6]=0, 0, 0
                colorsB[3:6]=0, 0, 0

            if ledonline == 1: #online - led 3 solid blue
                colorsA[0:3]=0, 0, 50
                colorsB[0:3]=0, 0, 50
             else:
                colorsA[0:3]=0, 0, 0
                colorsB[0:3]=0, 0, 0   
'''

            for i in range(self.PIXELS_N):
                self.dev.set_pixel(i, int(colorsA[3*i]), int(colorsA[3*i + 1]), int(colorsA[3*i + 2]))
            self.dev.show()
            time.sleep(0.3)
            for i in range(self.PIXELS_N):
                self.dev.set_pixel(i, int(colorsB[3*i]), int(colorsB[3*i + 1]), int(colorsB[3*i + 2]))
            self.dev.show()
            time.sleep(0.3)



#    def blinking(self,colorsarrA,colorsarrB):
#        self.colorsA=colorsarrA
#        self.colorsB=colorsarrB
#        self.next.set()
#        self.queue.put(self._blinking1)

    def blinking(self):
        self.next.set()
        self.queue.put(self._blinking1)

    def _blinking2(self): 
        colorsA = self.colorsA
        colorsB = self.colorsB

        self.next.clear()
        while not self.next.is_set():

            for i in range(self.PIXELS_N):
                self.dev.set_pixel(i, int(colorsA[3*i]), int(colorsA[3*i + 1]), int(colorsA[3*i + 2]))
            self.dev.show()
            time.sleep(0.3)
            for i in range(self.PIXELS_N):
                self.dev.set_pixel(i, int(colorsB[3*i]), int(colorsB[3*i + 1]), int(colorsB[3*i + 2]))
            self.dev.show()
            time.sleep(0.3)



    def blink(self, colorsA, colorsB):
        while True:
            for i in range(self.PIXELS_N):
                self.dev.set_pixel(i, int(colorsA[3*i]), int(colorsA[3*i + 1]), int(colorsA[3*i + 2]))
            self.dev.show()
            time.sleep(0.3)
            for i in range(self.PIXELS_N):
                self.dev.set_pixel(i, int(colorsB[3*i]), int(colorsB[3*i + 1]), int(colorsB[3*i + 2]))
            self.dev.show()
            time.sleep(0.3)