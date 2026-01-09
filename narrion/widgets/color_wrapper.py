"""Theme Observer Registration Mechanism.

This module provides a decorator-based system to automatically register UI components
that need to react to theme color changes (specifically icon recoloring).

Instead of manually registering every widget with the main window, classes
decorated with `@color` automatically add their instances to the global
`COLOR_LISTENERS` registry upon initialization. This allows the theme manager
to broadcast color updates to all active widgets efficiently.
"""

import functools

COLOR_LISTENERS = list()
"""Global registry of active widget instances.

This list contains references to all instantiated objects whose classes
were decorated with `@color`. The main application window iterates over
this list to call `changeFontColor` on each object when the theme changes.
"""


def color(cls):
    """Class decorator for automatic theme subscription.

    Wraps the `__init__` method of the target class. When a new instance
    of the decorated class is created, it is automatically appended to the
    `COLOR_LISTENERS` global list.

    This implements a passive registration pattern, ensuring that any widget
    that needs dynamic icon recoloring is tracked without requiring
    registration code in the widget's constructor.

    Args:
        cls (type): The class to be decorated (usually a QWidget subclass).

    Returns:
        type: The decorated class with the modified `__init__` method.

    Example:
        ```python
        @color
        class MyWidget(QWidget):
            def __init__(self):
                super().__init__()
                # ... setup UI ...

            def changeFontColor(self, new_color):
                # Update icons here
                pass
        ```
    """
    original_init = cls.__init__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        COLOR_LISTENERS.append(self)

    cls.__init__ = new_init
    return cls
