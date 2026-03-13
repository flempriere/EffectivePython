"""
Item 3: Never Expect Python to Detect Errors at Compile Time

Demonstrates some common errors that arise in python. Comment out
each error in turn to see what happens - pay attention to where
the error occurs (at load time or run time).
Then try installing some linters and see which errors are caught

Based on original code developed by Brett Slatkin

Copyright 2014-2024 Brett Slatkin, Pearson Education Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# error 1: missing syntax
# should fail at compile time
# should be caught by a linter
if True
    print("hello")

# error 2: invalid literal
# should fail at compile time
# should be caught by a linter
x = 1.3j5
print(x)

# error 3: unbound variable
# should fail at run time
# should be caught by a linter
def bad_reference():
    print(local_var)
    local_var = 123

# error 4: potentially unbound variable
# should fail at run time on the second function call
# This isn't caught by my linter

def sometimes_ok(x):
    if x:
        another_local_var = 123
    print(another_local_var)


sometimes_ok(True)  # should run
sometimes_ok(False)  # should error

# error 5: bad math
# should fail at run time
# not caught by my linter

def bad_math():
    return 1 / 0

bad_math()
