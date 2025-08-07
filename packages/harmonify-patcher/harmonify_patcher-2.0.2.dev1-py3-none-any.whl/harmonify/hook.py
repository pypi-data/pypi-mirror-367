import types, typing, inspect, sys


_active_function_hooks = {}
_active_method_hooks = {}


def register_function_hook(target_module: types.ModuleType, function_name: str, hook_callback: typing.Callable):
    """
    Registers a hook callback for a function in a module.

    Args:
        `target_module`: The module object where the function is defined.
        `function_name`: The name of the function to hook.
        `hook_callback`: The callback function to execute when the hook is triggered.
    """
    hook_key = (target_module, function_name)
    if hook_key not in _active_function_hooks:
        _active_function_hooks[hook_key] = []
    _active_function_hooks[hook_key].append(hook_callback)
    return True



def register_method_hook(target_class: type, method_name: str, hook_callback: typing.Callable):
    """
    Registers a hook callback for a method in a class.

    Args:
        `target_class`: The class whose method is to be hooked.
        `method_name`: The name of the method to hook.
        `hook_callback`: The callback function to execute when the hook is triggered.
    """
    hook_key = (target_class, method_name)
    if hook_key not in _active_method_hooks:
        _active_method_hooks[hook_key] = []
    _active_method_hooks[hook_key].append(hook_callback)
    return True



def remove_function_hook(target_module: types.ModuleType, function_name: str, hook_callback: typing.Callable):
    """
    Removes a hook callback for a function in a module.

    Args:
        `target_module`: The module object where the function is defined.
        `function_name`: The name of the function to unhook.
        `hook_callback`: The callback function to remove.
    """
    hook_key = (target_module, function_name)
    if hook_key in _active_function_hooks:
        _active_function_hooks[hook_key].remove(hook_callback)
        if not _active_function_hooks[hook_key]:
            del _active_function_hooks[hook_key]
    return True



def remove_method_hook(target_class: type, method_name: str, hook_callback: typing.Callable):
    """
    Removes a hook callback for a method in a class.

    Args:
        `target_class`: The class whose method is to be unhooked.
        `method_name`: The name of the method to unhook.
        `hook_callback`: The callback function to remove.
    """
    hook_key = (target_class, method_name)
    if hook_key in _active_method_hooks:
        _active_method_hooks[hook_key].remove(hook_callback)
        if not _active_method_hooks[hook_key]:
            del _active_method_hooks[hook_key]
    return True



### THESE FUNCTIONS ARE TO BE USED IN THE LIBRARY FUNCTIONS THEMSELVES ###

def call_function_hook(hook_index: int = 0):
    """
    WARNING: This function is to be used as an API in the target library.
    Calls the function hook at the specified index.

    Args:
        `hook_index`: The index of the hook to call.
    """
    # Get the calling frame (that of the function being hooked)
    frame = inspect.currentframe().f_back
    if frame is None:
        raise RuntimeError("No calling frame found.")
    
    # Get the module and function name from the frame
    module_name = frame.f_globals.get("__name__")
    function_name = frame.f_code.co_name
    target_module = sys.modules.get(module_name)
        
    if not target_module:
        raise RuntimeError(f"Module '{module_name}' not found.")
        
    hook_key = (target_module, function_name)
    # Call the registered hook with the specified index
    if hook_key in _active_function_hooks:
        hooks = _active_function_hooks[hook_key]
        if 0 <= hook_index < len(hooks):
            hooks[hook_index]()


def call_method_hook(hook_index: int = 0):
    """
    WARNING: This function is to be used as an API in the target library.
    Calls the method hook at the specified index.
    Args:
        `hook_index`: The index of the hook to call.
    """
    # Get the calling frame (that of the function being hooked)
    frame = inspect.currentframe().f_back
    if frame is None:
        raise RuntimeError("No calling frame found.")
    
    # Get the class and method name from the frame
    class_name = frame.f_locals.get("self", None).__class__
    method_name = frame.f_code.co_name
    target_module = sys.modules.get(class_name.__module__)
        
    if not target_module:
        raise RuntimeError(f"Module '{target_module}' not found.")

    hook_key = (class_name, method_name)
    # Call the registered hook with the specified index
    if hook_key in _active_method_hooks:
        hooks = _active_method_hooks[hook_key]
        if 0 <= hook_index < len(hooks):
            hooks[hook_index]()



def call_hook(hook_index: int = 0):
    """
    Calls the hook at the specified index.
    This function is a wrapper to call either a function or method hook based on the context.
    Args:
        `hook_index`: The index of the hook to call.
    """
    # Determine if we are in a function or method context
    frame = inspect.currentframe().f_back
    if frame is None:
        raise RuntimeError("No calling frame found.")
    
    if "self" in frame.f_locals:
        call_method_hook(hook_index)
    else:
        call_function_hook(hook_index)



def get_active_function_hooks() -> dict:
    """
    Returns a dictionary of currently active function hooks.
    """
    return _active_function_hooks



def get_active_method_hooks() -> dict:
    """
    Returnst a dictionary of currently active method hooks.
    """
    return _active_method_hooks
    