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

def get_file_diffs(git_log):
	file_diffs = { }
	split_log = git_log.split("diff --git a/")
	split_log.pop(0)

	for log in split_log:
		fileName = log.split()[0]
		fileName = fileName.split("/")[-1]

		fileDiff = log.split("@@")
		fileDiff = "@@" + fileDiff[1] + "@@" + fileDiff[2]

		file_diffs[fileName] = fileDiff

	return file_diffs

if (len(sys.argv) < 3):
    print("Filename: ", end="", flush=True)
    file_name = input()
    file_name = "modules/apps/forms-and-workflow/dynamic-data-mapping/dynamic-data-mapping-type-text/src/main/java/com/liferay/dynamic/data/mapping/type/text/internal/TextDDMFormFieldTypeSettings.java"
    print("Starting line: ", end="", flush=True)
    line_number = input()
    line_number = "98"
else :
    file_name = sys.argv[1]
    line_number = sys.argv[2]

git_blame = run_blame(file_name, line_number)
blame_hash = git_blame.split()[0]

git_log = run_log(blame_hash)
file_diffs = get_file_diffs(git_log)

for fileDiff in file_diffs:
	print(fileDiff)
	print(file_diffs.get(fileDiff))