import os
import subprocess
import sys

dir_path = os.getcwd()

def run_log(blame_hash):
	process = subprocess.Popen(["git","log", blame_hash, "-1", "-p", "--full-diff"], stdout=subprocess.PIPE)
	git_log = (process.communicate()[0]).decode("UTF-8")

	return git_log

def run_blame(fn, ln):
    line_range = ln + "," + ln

    process = subprocess.Popen(["git", "blame", fn, "-L", line_range, "-p"], stdout=subprocess.PIPE, cwd=dir_path)
    git_blame = (process.communicate()[0]).decode("UTF-8")
    return git_blame

if (len(sys.argv) < 3):
    print("Filename: ", end="", flush=True)
    file_name = input()
    print("Starting line: ", end="", flush=True)
    line_number = input()
    print("Substring (enter nothing to trace exact line): ", flush=True)
    substring = input()
else:
    file_name = sys.argv[1]
    line_number = sys.argv[2]

    for i, x in enumerate(sys.argv):
        print(sys.argv[i])
            
        if x == "-s" and len(sys.argv) > (i + 1):
                substring = sys.argv[i + 1]
                break

git_blame = run_blame(file_name, line_number)
blame_hash = git_blame.split()[0]

git_log = run_log(blame_hash)
print(git_log)
