from sniffer.api import * # import the really small API
import os, termstyle

# you can customize the pass/fail colors like this
pass_fg_color = termstyle.green
pass_bg_color = termstyle.bg_default
fail_fg_color = termstyle.red
fail_bg_color = termstyle.bg_default

# All lists in this variable will be under surveillance for changes.
watch_paths = ['.', 'tests/']

# this gets invoked on every file that gets changed in the directory. Return
# True to invoke any runnable functions, False otherwise.
#
# This fires runnables only if files ending with .py extension and not prefixed
# with a period.
@file_validator
def py_files(filename):
    return filename.endswith('.py') and not os.path.basename(filename).startswith('.')

# This gets invoked for verification. This is ideal for running tests of some sort.
# For anything you want to get constantly reloaded, do an import in the function.
#
# sys.argv[0] and any arguments passed via -x prefix will be sent to this function as
# it's arguments. The function should return logically True if the validation passed
# and logicially False if it fails.
#
# This example simply runs nose.
@runnable
def execute_nose(*args):
    import nose
    return nose.run(argv=list(args))
    
# Here we instruct the 'python_tests' runnable to be kicked off
# when a .py file is changed
@select_runnable('python_tests')
@file_validator
def py_files(filename):
    return filename.endswith('.py') and not os.path.basename(filename).startswith('.')

# Here we instruct the 'javascript_tests' runnable to be kicked off
# when a .js file is changed
@select_runnable('javascript_tests')
@file_validator
def js_files(filename):
    return filename.endswith('.js') and not os.path.basename(filename).startswith('.')

@runnable
def python_tests(*args):
    import nose
    return nose.run(argv=list(args))

@runnable
def javascript_tests(*args):
    command = "mocha tests/js-tests.js"
    return call(command, shell=True) == 0
