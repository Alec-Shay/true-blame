import os
import subprocess
import sys

dir_path = os.getcwd()

if (len(sys.argv) < 3):
    print("Filename: ", end="", flush=True)
    file_name = input()
    print("Line: ", end="", flush=True)
    line_number = input()
else :
    file_name = sys.argv[1]
    line_number = sys.argv[2]

print(dir_path)

process = subprocess.Popen(["git", "blame", file_name, "-L", line_number + "," + line_number, "-p"], stdout=subprocess.PIPE, cwd=dir_path)

print(str(process.communicate()[0]))
