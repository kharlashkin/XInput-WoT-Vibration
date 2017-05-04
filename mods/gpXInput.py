import ctypes

class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [('wLeftMotorSpeed', ctypes.c_ushort), ('wRightMotorSpeed', ctypes.c_ushort)]


class gpXInputClass:

    def __init__(self):
        xInputDLLFileName = 'Xinput1_4'
        xinput = ctypes.WinDLL(xInputDLLFileName)
        self.__XInputSetState = xinput.XInputSetState
        self.__XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
        self.__XInputSetState.restype = ctypes.c_uint
        self.__l = 0
        self.__r = 0

    def adjust_vibration(self, left_motor_delta, right_motor_delta, set=False, controller=0):
        if set:
            self.__l = left_motor
            self.__r = right_motor
        else:
            self.__l += left_motor_delta
            self.__r += right_motor_delta
        tempL = self.__l
        tempR = self.__r
        if self.__l > 255:
            tempL = 255
        elif self.__l < 0:
            tempL = 0
        if self.__r > 255:
            tempR = 255
        elif self.__r < 0:
            tempR = 0
        vibration = XINPUT_VIBRATION(int(tempL * 65535 / 255), int(tempR * 65535 / 255))
        self.__XInputSetState(controller, ctypes.byref(vibration))

    def stop_vibration(self, controller=0):
        vibration = XINPUT_VIBRATION(0, 0)
        self.__XInputSetState(controller, ctypes.byref(vibration))


gpXInputObject = gpXInputClass()
