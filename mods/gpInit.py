from gpVibration import GamePadVibration
from Vibroeffects.VibroManager import VibroManager

class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        if handler in self.__handlers:
            self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler


def RegisterEvent(cls, method, handler, prepend = False):
    evt = '__event_%i_%s' % (1 if prepend else 0, method)
    if hasattr(cls, evt):
        e = getattr(cls, evt)
    else:
        newm = '__orig_%i_%s' % (1 if prepend else 0, method)
        setattr(cls, evt, EventHook())
        setattr(cls, newm, getattr(cls, method))
        e = getattr(cls, evt)
        m = getattr(cls, newm)
        setattr(cls, method, lambda *a, **k: __event_handler(prepend, e, m, *a, **k))
    e += handler


def __event_handler(prepend, e, m, *a, **k):
    try:
        if prepend:
            e.fire(*a, **k)
            r = m(*a, **k)
        else:
            r = m(*a, **k)
            e.fire(*a, **k)
        return r
    except:
        logtrace(__file__)


def OverrideMethod(cls, method, handler):
    orig = getattr(cls, method)
    newm = lambda *a, **k: handler(orig, *a, **k)
    if type(orig) is not property:
        setattr(cls, method, newm)
    else:
        setattr(cls, method, property(newm))


def OverrideStaticMethod(cls, method, handler):
    orig = getattr(cls, method)
    newm = staticmethod(lambda *a, **k: handler(orig, *a, **k))
    if type(orig) is not property:
        setattr(cls, method, newm)
    else:
        setattr(cls, method, property(newm))


def myVibroManager__init__(self):
    self._VibroManager__vibrationObject = GamePadVibration(self._VibroManager__vibrationObject)


RegisterEvent(VibroManager, '__init__', myVibroManager__init__)