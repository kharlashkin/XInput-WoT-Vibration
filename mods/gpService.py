TIME_DELTA = 50
K_SIT_LEFT = [0.333, 0.0]
K_SIT_RIGHT = [0.333, 0.0]
K_BACK_LOW_LEFT = [0.166, 0.166]
K_BACK_LOW_RIGHT = [0.166, 0.166]
K_BACK_MID_LEFT = [0.0, 0.333]
K_BACK_MID_RIGHT = [0.0, 0.333]
LOG_CLASS_ON = True
LOG_ROUTE_ON = True
LOG_SERV_ON = True
transferCoefficientDict = {1: K_SIT_RIGHT,
 2: K_BACK_LOW_RIGHT,
 3: K_BACK_MID_RIGHT,
 9: K_SIT_LEFT,
 10: K_BACK_LOW_LEFT,
 11: K_BACK_MID_LEFT}

def _testBit(zone_group, zone):
    mask = 1 << zone
    return bool((zone_group & mask) >> zone)


import threading, time, sys
from gpXInput import gpXInputClass
from flask import Flask, request

class gpVibroEffect:
    isRunning = property(lambda self: self.__isRunning)
    stopEvent = property(lambda self: self.__stopEvent)
    fileName = property(lambda self: self.__fileName)
    effectLength = property(lambda self: self.__effectLength)

    def __init__(self):
        self.__isRunning = False
        self.__isLoaded = False
        self.__effectLength = 0
        self.__vibrationsArrayLeftMotor = []
        self.__vibrationsArrayRightMotor = []
        self.__effectGain = 1.0
        self.__stopEvent = threading.Event()
        self.__stopEvent.clear()

    def setXInputObject(self, gpXInputObject):
        self.__gpXInputObject = gpXInputObject

    def play(self, count = 1):
        startTime = time.clock()
        if LOG_CLASS_ON:
            print self.__fileName, 'is started'
        lValue = 0.0
        rValue = 0.0
        gain = self.__effectGain
        if count > sys.maxint:
            count = sys.maxint
        for c in xrange(count):
            if self.__stopEvent.isSet():
                break
            for x in range(int(self.__effectLength / TIME_DELTA)):
                if x == 0 and c == 0:
                    lDelta = self.__vibrationsArrayLeftMotor[x]
                    rDelta = self.__vibrationsArrayRightMotor[x]
                else:
                    lDelta = self.__vibrationsArrayLeftMotor[x] - self.__vibrationsArrayLeftMotor[x - 1]
                    rDelta = self.__vibrationsArrayRightMotor[x] - self.__vibrationsArrayRightMotor[x - 1]
                lValue += lDelta
                rValue += rDelta
                self.__gpXInputObject.adjust_vibration(lDelta * gain, rDelta * gain)
                if LOG_CLASS_ON:
                    print x, '%0.2f, %0.2f' % (lValue, rValue)
                if self.__stopEvent.isSet():
                    break
                time.sleep(2 * TIME_DELTA / 1000.0)

        lDelta = -lValue
        lValue += lDelta
        rDelta = -rValue
        rValue += rDelta
        self.__gpXInputObject.adjust_vibration(lDelta * gain, rDelta * gain)
        finishTime = time.clock()
        self.__isRunning = False
        if LOG_CLASS_ON:
            print x + 1, '%0.2f, %0.2f' % (lValue, rValue)
            print 'Time elapsed: %.3fs' % (finishTime - startTime)
            print self.__fileName, 'is stopped'

    def loadEffectFromFile(self, fileName):
        self.__isLoaded = False
        self.__fileName = fileName
        if LOG_CLASS_ON:
            print 'loading', self.__fileName
        from xml.etree import ElementTree as ET
        uwvTree = ET.parse(self.__fileName)
        uwvRoot = uwvTree.getroot()
        effectLength = 0
        for node in uwvRoot.getiterator():
            if 'time' in node.attrib:
                if int(node.attrib['time']) > effectLength:
                    effectLength = int(node.attrib['time'])

        self.__effectLength = effectLength
        for i in range(int(self.__effectLength / TIME_DELTA)):
            self.__vibrationsArrayLeftMotor.append(0)
            self.__vibrationsArrayRightMotor.append(0)

        for vibration in uwvRoot.getchildren():
            if 'vibration' in vibration.tag:
                timePrev = 0
                amplPrev = 0
                zones = int(vibration.attrib['zones'], 16)
                zoneLength = 0
                for vpoint in vibration.getchildren():
                    if int(vpoint.attrib['time']) > zoneLength:
                        zoneLength = int(vpoint.attrib['time'])

                self.__zonesGroupArrayLeftMotor = []
                self.__zonesGroupArrayRightMotor = []
                for i in range(int(zoneLength / TIME_DELTA) + 1):
                    self.__zonesGroupArrayLeftMotor.append(0)
                    self.__zonesGroupArrayRightMotor.append(0)

                for vpoint in vibration.getchildren():
                    timeCur = int(vpoint.attrib['time'])
                    amplCur = float(vpoint.attrib['amplitude'])
                    if timePrev == timeCur and amplPrev != amplCur:
                        x = int(timeCur / TIME_DELTA)
                        ampl = amplCur
                        for key in transferCoefficientDict.keys():
                            if _testBit(zones, key):
                                pass

                    elif timePrev != timeCur and amplPrev == amplCur:
                        for x in range(int(timePrev / TIME_DELTA), int(timeCur / TIME_DELTA)):
                            ampl = amplCur
                            for key in transferCoefficientDict.keys():
                                if _testBit(zones, key):
                                    self.__zonesGroupArrayLeftMotor[x] += ampl * transferCoefficientDict[key][0]
                                    self.__zonesGroupArrayRightMotor[x] += ampl * transferCoefficientDict[key][1]

                    elif '1' in vpoint.tag and timeCur != 0:
                        x = int(timeCur / TIME_DELTA)
                        ampl = amplCur
                        for key in transferCoefficientDict.keys():
                            if _testBit(zones, key):
                                pass

                    elif timePrev != timeCur and amplPrev != amplCur:
                        x1 = int(timePrev / TIME_DELTA)
                        x2 = int(timeCur / TIME_DELTA) - 1
                        y1 = amplPrev
                        y2 = amplCur
                        try:
                            k = (y2 - y1) / (x2 - x1)
                            b = y2 - k * x2
                        except:
                            k = 0
                            b = 0

                        for x in range(int(timePrev / TIME_DELTA), int(timeCur / TIME_DELTA)):
                            ampl = k * x + b
                            for key in transferCoefficientDict.keys():
                                if _testBit(zones, key):
                                    self.__zonesGroupArrayLeftMotor[x] += ampl * transferCoefficientDict[key][0]
                                    self.__zonesGroupArrayRightMotor[x] += ampl * transferCoefficientDict[key][1]

                    timePrev = timeCur
                    amplPrev = amplCur

                looped = vibration.attrib['looped']
                if looped == 'true':
                    y = 0
                    for x in range(int(effectLength / TIME_DELTA)):
                        self.__vibrationsArrayLeftMotor[x] += self.__zonesGroupArrayLeftMotor[y]
                        self.__vibrationsArrayRightMotor[x] += self.__zonesGroupArrayRightMotor[y]
                        y += 1
                        if y == int(zoneLength / TIME_DELTA):
                            y = 0

                else:
                    for x in range(int(zoneLength / TIME_DELTA)):
                        self.__vibrationsArrayLeftMotor[x] += self.__zonesGroupArrayLeftMotor[x]
                        self.__vibrationsArrayRightMotor[x] += self.__zonesGroupArrayRightMotor[x]

        self.__isLoaded = True

    def startEffect(self, count=1):
        if not self.__isLoaded:
            return
        if self.__isRunning:
            self.__stopEvent.set()
            while self.__isRunning:
                pass

        self.__stopEvent.clear()
        self.__thread = threading.Thread(target=self.play, args=(count,))
        self.__isRunning = True
        self.__thread.start()

    def stopEffect(self):
        self.__stopEvent.set()

    def setEffectGain(self, effectGain):
        self.__effectGain = effectGain / 100.0


effectsDict = dict()
gpXInputObject = gpXInputClass()
gpXInputObject.stop_vibration()


if not LOG_SERV_ON:
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
app = Flask(__name__)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return


@app.route('/disconnect')
def disconnect():
    shutdown_server()
    for effect in effectsDict:
        effectsDict[effect].stopEffect()

    gpXInputObject.stop_vibration()
    time.sleep(2 * TIME_DELTA / 1000.0)
    return 'Server shutting down...'


@app.route('/connect')
def connect():
    if LOG_ROUTE_ON:
        print 'Connection checked - Ok.'
    return 'True'


@app.route('/loadEffectFromFile')
def loadEffectFromFile():
    effectHandle = request.args.get('effectHandle')
    fileName = request.args.get('fileName')
    import os
    fileName = os.path.dirname(__file__) + '/' + fileName
    if os.path.exists(fileName):
        effectsDict[effectHandle] = gpVibroEffect()
        effectsDict[effectHandle].setXInputObject(gpXInputObject)
        effectsDict[effectHandle].loadEffectFromFile(fileName)
    else:
        print 'loadEffectFromFile Error: file not found:', fileName
    if LOG_ROUTE_ON:
        print
        print 'loadEffectFromFile'
        print 'effectHandle =', effectHandle
        print 'fileName =', fileName
    return ''


@app.route('/startEffect')
def startEffect():
    handle = request.args.get('handle')
    count = int(request.args.get('count'))
    if handle in effectsDict:
        effectsDict[handle].startEffect(count)
    else:
        print 'startEffect Error: Handle', handle, 'is empty'
    if LOG_ROUTE_ON:
        print
        print 'startEffect'
        print 'handle =', handle
        print 'count =', str(count)
    return ''


@app.route('/stopEffect')
def stopEffect():
    handle = request.args.get('handle')
    if handle in effectsDict:
        effectsDict[handle].stopEffect()
    else:
        print 'stopEffect Error: Handle', handle, 'is empty'
    if LOG_ROUTE_ON:
        print
        print 'stopEffect'
        print 'handle =', handle
    return ''


@app.route('/setEffectGain')
def setEffectGain():
    vibroEffectHandle = request.args.get('vibroEffectHandle')
    effectGain = float(request.args.get('effectGain'))
    if vibroEffectHandle in effectsDict:
        effectsDict[vibroEffectHandle].setEffectGain(effectGain)
    else:
        print 'setEffectGain Error: Handle', vibroEffectHandle, 'is empty'
    if LOG_ROUTE_ON:
        print
        print 'setEffectGain'
        print 'vibroEffectHandle =', vibroEffectHandle
        print 'effectGain =', effectGain
    return ''


@app.route('/cloneEffect')
def cloneEffect():
    sourceEffectHandle = request.args.get('sourceEffectHandle')
    destEffectHandle = request.args.get('destEffectHandle')
    if sourceEffectHandle in effectsDict:
        effectsDict[destEffectHandle] = gpVibroEffect()
        effectsDict[destEffectHandle].setXInputObject(gpXInputObject)
        effectsDict[destEffectHandle].loadEffectFromFile(effectsDict[sourceEffectHandle].fileName)
    else:
        print 'cloneEffect Error: sourceHandle', sourceEffectHandle, 'is empty'
    if LOG_ROUTE_ON:
        print
        print 'cloneEffect'
        print 'sourceEffectHandle =', sourceEffectHandle
        print 'destEffectHandle =', destEffectHandle
    return ''


if __name__ == '__main__':
    app.run()