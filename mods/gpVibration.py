import urllib2
import os, inspect
import datetime
import ResMgr
from helpers import VERSION_FILE_PATH
ver = ResMgr.openSection(VERSION_FILE_PATH).readString('version')
ver = ver[2:ver.index('#') - 1]
wd = 'res_mods/%s/%s' % (ver, os.path.dirname(__file__))
modPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/' + wd

class GamePadVibration:

    def __init__(self, originalVibrationObject):
        self.__originalVibrationObject = originalVibrationObject
        self.__gpServiceAddress = 'http://127.0.0.1:5000/'
        self.__gpServiceAddressTimeOut = 0.25
        self.__sysPythonPath = 'c:/python27/python.exe'
        fileNameGPService = modPath + '/GPService.pyc'
        os.spawnl(os.P_NOWAIT, self.__sysPythonPath, ' ', fileNameGPService)

    def __del__(self):
        address = self.__gpServiceAddress
        try:
            urllib2.urlopen(address + 'disconnect')
        except urllib2.URLError as e:
            print 'urllib2.URLError (disconnect):', e
        except urllib2.HTTPError as e:
            print 'urllib2.HTTPError (disconnect):', e
        except:
            print 'urllib2: Unexpected error (disconnect)'

    def reset(self):
        self.__originalVibrationObject.reset()

    def setGain(self, gain):
        self.__originalVibrationObject.setGain(gain)

    def createEffect(self):
        effectHandle = self.__originalVibrationObject.createEffect()
        return effectHandle

    def getEffectLength(self, handle):
        durationInMs = self.__originalVibrationObject.getEffectLength(handle)
        return durationInMs

    def deleteEffect(self, handle):
        self.__originalVibrationObject.deleteEffect(handle)

    def connect(self):
        address = self.__gpServiceAddress
        isServiceRunning = False
        try:
            isServiceRunning = urllib2.urlopen(address + 'connect').read()
        except urllib2.URLError as e:
            print 'urllib2.URLError (connect):', e
        except urllib2.HTTPError as e:
            print 'urllib2.HTTPError (connect):', e
        except:
            print 'urllib2: Unexpected error (connect)'

        if isServiceRunning == 'True':
            return True
        else:
            return False

    def loadEffectFromFile(self, effectHandle, fileName):
        self.__originalVibrationObject.loadEffectFromFile(effectHandle, fileName)
        address = self.__gpServiceAddress
        timeOut = self.__gpServiceAddressTimeOut
        urlSafeOpen(address, '?effectHandle=' + str(effectHandle) + '&fileName=' + str(fileName), 'loadEffectFromFile', timeOut)

    def startEffect(self, handle, effectsSettingsCount):
        address = self.__gpServiceAddress
        timeOut = self.__gpServiceAddressTimeOut
        urlSafeOpen(address, '?handle=' + str(handle) + '&count=' + str(effectsSettingsCount), 'startEffect', timeOut)

    def stopEffect(self, handle):
        address = self.__gpServiceAddress
        timeOut = self.__gpServiceAddressTimeOut
        urlSafeOpen(address, '?handle=' + str(handle), 'stopEffect', timeOut)

    def setEffectGain(self, vibroEffectHandle, effectGain):
        address = self.__gpServiceAddress
        timeOut = self.__gpServiceAddressTimeOut
        urlSafeOpen(address, '?vibroEffectHandle=' + str(vibroEffectHandle) + '&effectGain=' + str(effectGain), 'setEffectGain', timeOut)

    def cloneEffect(self, sourceEffectHandle):
        destEffectHandle = self.__originalVibrationObject.cloneEffect(sourceEffectHandle)
        address = self.__gpServiceAddress
        timeOut = self.__gpServiceAddressTimeOut
        urlSafeOpen(address, '?sourceEffectHandle=' + str(sourceEffectHandle) + '&destEffectHandle=' + str(destEffectHandle), 'cloneEffect', timeOut)
        return destEffectHandle


def urlSafeOpen(addr, req, funcName, timeOut = 0.25):
    try:
        urllib2.urlopen(addr + funcName + req, None, timeOut)
    except urllib2.URLError as e:
        print funcName, 'urllib2.URLError:', e
    except urllib2.HTTPError as e:
        print funcName, 'urllib2.HTTPError:', e
    except:
        print funcName, 'urllib2: Unexpected error'

    return


def _log_ms(msg):
    dt = datetime.datetime.now()
    print datetime.datetime.now().strftime('%H:%M:%S.') + str(dt.microsecond)[0:3] + ':', msg
