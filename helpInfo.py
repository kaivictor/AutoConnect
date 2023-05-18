class useError(Exception):
    def __init__(self, value):
        self.value = 'not support'

    def __str__(self):
        return repr(self.value)


class tError(Exception):
    def __init__(self, value):
        self.value = 'not support'

    def __str__(self):
        return repr(self.value)


class MissParameter(Exception):
    def __init__(self, value='Parameter Mission'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class StateError(Exception):
    def __init__(self, value='Expected Unexpected'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Report():
    def __init__(self, isTrue, msg):
        self.isTrue = isTrue
        self.msg = msg
        self.value = msg
