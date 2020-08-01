class Noise():
    def __init__(self, msg, noise_data = []):
        self.msg = msg
        self.noise_data = noise_data
    def __eq__(self, obj):
        return type(obj) is Noise and obj.msg == self.msg
    def __str__(self):
        return self.msg
    def __nonzero__(self): #Python 2
        return False
    def __bool__(self): #Python 3
        return False
    def noise_data(self):
        return self.noise_data
