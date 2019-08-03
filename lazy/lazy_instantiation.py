class Expensive:
    def beegyoshi(self):
        return "!!!"

e = Expensive()

class LazyWrapper:
    def __init__(self, clazz, *args, **kwargs):
        self.clazz = clazz
        self.args = args
        self.kwargs = kwargs
        self.instance = None

    def __getattr__(self, attr):
        if self.instance is None:
            self.instance = self.clazz(*self.args, **self.kwargs)
        return getattr(self.instance, attr)

e = LazyWrapper(Expensive)
print(e.beegyoshi())
