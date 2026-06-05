# main4.py
import analysis.utils
import frontend.utils

value = 33
if analysis.utils.inspect(value) == frontend.utils.inspect(value):
    print("Inspection equal!")
