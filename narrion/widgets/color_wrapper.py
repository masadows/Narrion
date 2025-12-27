import functools

COLOR_LISTENERS = list()


def color(cls):
    original_init = cls.__init__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        COLOR_LISTENERS.append(self)

    cls.__init__ = new_init
    return cls
