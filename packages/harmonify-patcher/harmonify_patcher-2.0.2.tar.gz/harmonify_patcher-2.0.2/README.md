# Harmonify

Harmonify is a Python library that allows users to change the behavior of classes at runtime, with nothing more than a few function calls.
Inspired by Harmony (the *very* popular C# library that also allows runtime behavior modification), Harmonify is flexible and uses a simple system based on monkey-patching.
Like its C# equivalent, it can be used for:
* **Debugging:** Inject logging or checks into methods without changing them permanently.
* **Testing:** Isolate parts of your code by temporarily changing how certain methods behave.
* **Extending Libraries:** Add new features or modify behavior of classes from libraries you can't edit directly.
* **Experimentation:** Play around with how code runs in a non-destructive way.

## Features

* **Prefix Patching:** Run your custom code *before* the original method executes.
* **Postfix Patching:** Run your custom code *after* the original method executes, even allowing you to modify its return value.
* **Replace Patching:** Completely swap out the original method's logic with your own.
* **Create & Delete methods:** Add or remove methods from a class or a module, without changing the other ones.
* **Easy Unpatching:** Restore methods to their original state with a simple call.
* **Function Patching:** Patch functions as easily as methods!
* **Function and Method Hooking:** Use a *very* simple API to hook into any method (that is hookable)!
* **Code Injection & Injection undo-ing:** Add you own code inside any Python function or method and revert at any time.
  * *Note:* Be careful with code injection, and *do **not** inject code coming from a source you don't trust!* If you're a library developer and want to prevent your code from being injected into, decorate your code with the `harmonify.injector.security.no_inject` decorator.

## Installation

Installing Harmonify is as easy as using `pip`:

```shell
pip install harmonify-patcher
```
After that, Harmonify will be available globally!



## Example Programs

### Function Patching
#### my_library.py
```python
def sqrt(x: float) -> float:
	return x ** (1 / 2)

def pow(x: float, n: int) -> float:
	return x ** n

def get_version():
	return "1.0"
```

#### main.py
```python
import harmonify
import my_library

def new_get_ver():
	return "Latest release"

print(my_library.get_version())   # 1.0
harmonify.patch_function(
	target_module = my_library,
	function_name = "get_version",
	replace = new_get_ver
)
print(my_library.get_version())   # Latest release
```


### Code Injection
#### api_lib.py
```python
import harmonify

def open_api1():
	print("Doing API stuff...")

@harmonify.allow_inject
def open_api2():
	print("More API stuff...")

@harmonify.no_inject
def restricted_api(uname, passwd):
	print(f"Doing restricted API access with:\n\tUsername: {uname}\n\tPassword: {passwd}")
```

#### main.py
```python
import harmonify
import api_lib

if harmonify.inject_function(
    target_module = api_lib,
    function_name = "open_api1",
    path = harmonify.TreePath(0),
    inject_type = harmonify.InjectType.AFTER_TARGET,
    code_to_inject = "print('Injected!')"
):
    print("Successfully injected open_api1()")

if harmonify.inject_function(
    target_module = api_lib,
    function_name = "open_api2",
    path = harmonify.TreePath(0),
    inject_type = harmonify.InjectType.AFTER_TARGET,
    code_to_inject = "print('Injected!')"
):
    print("Successfully injected open_api2()")

if harmonify.inject_function(
    target_module = api_lib,
    function_name = "restricted_api",
    path = harmonify.TreePath(0),
    inject_type = harmonify.InjectType.AFTER_TARGET,
    code_to_inject = "print('Stealing info!')"
):
    print("Successfully injected restricted_api()")

api_lib.open_api1()
api_lib.open_api2()
api_lib.restricted_api(uname="Super Secret Agent #42", passwd="SuperSecretPassword123")
```



# Changelog

# 2.0.2
Allow hooks to be called with parameters from the target library.
Alternate branch support for the injector will be added in the **2.1.0** update.

# 2.0.1
Fixed many bugs with the new injector, allowing it to be somewhat usable.
*Future plan (most probably in 2.0.2): add the ability to walk the alternate branches (`else` statements) for `if` and `for` constructs.*

# 2.0.0
Final fix made regarding import syntax.

## 2.0.0 (Release Candidate 2)
Fixed import syntax. It seems like Python hates me.

## 2.0.0 (Release Candidate 1)
Remade the injector module, separating it as a package and remaking the API for injecting cleaner.
Added the `TreePath` class, meant for retrieving statements based on an exact path.
These changes make the injector more robust and simpler to use.
Updated the injector example from above.

## 1.4.2
Added functions for easy use of the context managers from **1.4.1**, named `apply_patch`, `apply_inject` and `add_hook`.

## 1.4.1
Added the generic `call_hook` function, along with context managers for temporary patches/injections/hooks.
Also added the `remove_function` function, which was missing from a previous release.

## 1.4.0
Added hooks. These can be registered to a callable via the `register_function_hook` and `register_method_hook` functions.
Hooks can be called by a library function with `call_function_hook` or `call_method_hook`. Multiple hooks can be added to the same callable. <br>
*Future plan (possibly in 1.4.1): add a generic `call_hook` function, which would dispatch to `call_function_hook` or `call_method_hook`, depending on the caller.*

## 1.3.2
Fixed an internal bug where an `UnboundLocalError` would appear when creating a new patch.

## 1.3.1
Added the `PatchInfo` utility class and two new fucntions, `get_function_patches` and `get_method_patches`.
These two functions return informations about every patch that has been applied up until the call.

## 1.3.0
Slightly improved safeguards to provide an easy API. This *does* mean that the library dev needs to have Harmonify installed, which is not ideal.

## 1.2.3
Added injection safeguards. These should be applied in the target library.

## 1.2.2
Fixed a problem where the code would be injected *before* the target line.
