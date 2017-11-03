import os
import subprocess
import sys

dir_path = os.getcwd()

def run_blame(fn, ln):
    line_range = ln + "," + ln

    process = subprocess.Popen(["git", "blame", fn, "-L", line_range], stdout=subprocess.PIPE, cwd=dir_path)

    return str(process.communicate()[0])

if (len(sys.argv) < 3):
    print("Filename: ", flush=True)
    file_name = input()
    print("Starting line: ", flush=True)
    line_number = input()
else :
    file_name = sys.argv[1]
    line_number = sys.argv[2]

print(dir_path)

print(run_blame(file_name, line_number))
