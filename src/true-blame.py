import os
import subprocess
import sys

dir_path = os.getcwd()

def get_parent_commit(commit_hash):
        hash_string = commit_hash + "^"
        
        process = subprocess.Popen(["git", "rev-parse", hash_string], stdout=subprocess.PIPE, cwd=dir_path)

        return (process.communicate()[0]).decode("UTF-8").replace("\n","")

def run_diff(blame_hash):
        parent_hash = get_parent_commit(blame_hash)

        process = subprocess.Popen(["git", "diff", parent_hash, blame_hash, "-U0"], stdout=subprocess.PIPE, cwd=dir_path)
        gitDiff = (process.communicate()[0]).decode("UTF-8")

        return gitDiff

def run_blame(fn, ln):
    line_range = ln + "," + ln

    process = subprocess.Popen(["git", "blame", fn, "-L", line_range, "-p"], stdout=subprocess.PIPE, cwd=dir_path)
    git_blame = (process.communicate()[0]).decode("UTF-8")
    return git_blame

def get_file_diffs(git_log):
	file_diffs = { }
	split_log = git_log.split("diff --git a/")
	split_log.pop(0)

	for log in split_log:
		fileName = log.split()[0]
		fileName = fileName.split("/")[-1]

		fileDiff = log.split("@@")
		if len(fileDiff) < 2:
			print("ERROR: Invalid Diff Target")
			break
		fileDiff = "@@" + fileDiff[1] + "@@" + fileDiff[2]

		file_diffs[fileName] = fileDiff

	return file_diffs

if (len(sys.argv) < 3):
    print("Filename: ", end="", flush=True)
    file_name = input()
    print("Line number: ", end="", flush=True)
    line_number = input()
    print("Substring (enter nothing to trace exact line): ", flush=True)
    substring = input()

    # FOR TESTING
    file_name = "modules/apps/forms-and-workflow/dynamic-data-mapping/dynamic-data-mapping-type-text/src/main/java/com/liferay/dynamic/data/mapping/type/text/internal/TextDDMFormFieldTypeSettings.java"
    line_number = "98"
else:
    file_name = sys.argv[1]
    line_number = sys.argv[2]

    for i, x in enumerate(sys.argv):
        print(sys.argv[i])
            
        if x == "-s" and len(sys.argv) > (i + 1):
                substring = sys.argv[i + 1]
                break

git_blame = run_blame(file_name, line_number)
try:
	blame_hash = git_blame.split()[0]
except:
	print("ERROR: Invalid Blame Target")
	sys.exit(0)

git_diff_result = run_diff(blame_hash)
file_diffs = get_file_diffs(git_diff_result)

for fileDiff in file_diffs:
	print(fileDiff)
	print(file_diffs.get(fileDiff))
