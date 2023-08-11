from typing import Any, Callable, Dict, Generic, TypeVar

ArgType = TypeVar("ArgType")

class Signal(Generic[ArgType]):
    """
    A custom signal implementation for implementing the observer pattern.

    This class provides a basic mechanism for creating custom signals
    and connecting event handlers to those signals.

    Attributes:
        _handlers (list): A list to store event handlers connected to the signal.

    Methods:
        connect(handler): Connects an event handler to the signal.
        disconnect(handler): Disconnects an event handler from the signal.
        emit(*args, **kwargs): Emits the signal, calling all connected event handlers.
    """

    def __init__(self, *args: ArgType, **kwargs: Dict[str, ArgType]):
        self._handlers: list[Callable[[ArgType, Dict[str, ArgType]], Any]] = []

    def __call__(self, *args: ArgType, **kwargs: Dict[str, ArgType]):
        self.emit(*args, **kwargs)


    def connect(self, handler: Callable[[ArgType, Dict[str, ArgType]], Any]):
        """
        Connect an event handler to the signal.

        Args:
            handler (callable): The event handler function to connect.
        """
        self._handlers.append(handler)

    def disconnect(self, handler: Callable[[ArgType, Dict[str, ArgType]], Any]):
        """
        Disconnect an event handler from the signal.

        Args:
            handler (callable): The event handler function to disconnect.
        """
        self._handlers.remove(handler)

    def emit(self, *args: ArgType, **kwargs: Dict[str, ArgType]):
        """
        Emit the signal, invoking all connected event handlers.

        Args:
            *args: Variable arguments to pass to the event handlers.
            **kwargs: Keyword arguments to pass to the event handlers.
        """
        for handler in self._handlers:
            handler(*args, **kwargs)
