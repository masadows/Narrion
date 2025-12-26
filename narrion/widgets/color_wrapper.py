import functools

COLOR_LISTENERS = list()


def color(cls):
    @functools.wraps(cls)
    def register_class(*args, **kwargs):
        new_class = cls(*args, **kwargs)
        COLOR_LISTENERS.append(new_class)
        return new_class

    return register_class
