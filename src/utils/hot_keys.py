from typing import Callable
from pynput import keyboard


class HotKeys:
    _shortcuts_and_callbacks: dict[str, list[Callable, ...]] = {}
    _listener = None

    @staticmethod
    def add_global_shortcut(shortcut: str, callback: Callable) -> None:
        """
        Adds a global shortcut with the specified `shortcut` key combination and `callback` function.

        This method adds a global shortcut that can be triggered by pressing the specified `shortcut` key combination
        from anywhere with or without the application. When the shortcut is triggered, the associated `callback` function will be called.

        Args:
            shortcut (str): The key combination for the global shortcut, specified in a string format. The format should
                follow the keyboard library's syntax for defining keyboard shortcuts.
            callback (Callable): The function to be called when the global shortcut is triggered. The function should
                be callable and take no arguments.
                
        Example:
            HotKeys.add_global_shortcut('<ctrl>+<shift>+a', my_callback_function)

        Note:
            - The `shortcut` argument should be unique for each global shortcut. If a duplicate `shortcut` is added, the
            existing shortcut will be overwritten.
            - The `callback` function will be called synchronously when the global shortcut is triggered. It should
            execute quickly and avoid any long-running or blocking operations to prevent freezing the application.
        """
        
        if not isinstance(callback, Callable):
            raise TypeError("Callback must be a callable object.")
        
        if shortcut not in HotKeys._shortcuts_and_callbacks.keys():
            HotKeys._shortcuts_and_callbacks[shortcut] = []
        HotKeys._shortcuts_and_callbacks[shortcut].append(callback)
        
        if HotKeys._listener is not None and HotKeys._listener.is_alive():
            HotKeys._listener.stop()
            
        hot_keys = {_shortcut: lambda _shortcut=_shortcut: HotKeys._call_callbacks(_shortcut) for _shortcut in HotKeys._shortcuts_and_callbacks.keys()}
        HotKeys._listener = keyboard.GlobalHotKeys(hot_keys)
        HotKeys._listener.setName("HotKeys Listener")
        HotKeys._listener.start()
        HotKeys._listener.wait()
    
    
    @staticmethod
    def _call_callbacks(shortcut: str) -> None:
        """
        Calls all the callback functions associated with the specified `shortcut`.

        This method retrieves the list of callback functions associated with the given `shortcut` and calls each
        function sequentially. The functions should be previously added using the `add_global_shortcut` method.

        Args:
            shortcut (str): The key combination of the global shortcut for which the callback functions need to be called.
        """
        [func() for func in HotKeys._shortcuts_and_callbacks[shortcut]]



# for test
if __name__ == "__main__":
    HotKeys.add_global_shortcut("<ctrl>+k", lambda: print("key 1"))
    HotKeys.add_global_shortcut("<ctrl>+k", lambda: print("key 2"))
    HotKeys.add_global_shortcut("<ctrl>+k", lambda: print("key 3"))
    HotKeys.add_global_shortcut("<ctrl>+l", lambda: print("key 4"))
    
    input()
    