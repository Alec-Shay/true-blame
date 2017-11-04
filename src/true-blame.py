import os
import subprocess
import sys

dir_path = os.getcwd()

def get_line(file_name, line_number):
        line = ""
        file = open(dir_path + "/" + file_name)
        
        for i, counted_line in enumerate(file):
                if i == (int(line_number) - 1):
                        line = counted_line
                        break
        file.close()
        return line

def get_parent_commit(commit_hash):
        hash_string = commit_hash + "^"
        
        process = subprocess.Popen(["git", "rev-parse", hash_string], stdout=subprocess.PIPE, cwd=dir_path)

        return (process.communicate()[0]).decode("UTF-8").replace("\n","")

def run_diff(blame_hash):
        parent_hash = get_parent_commit(blame_hash)

        print("RUN_DIFF: " + "git diff " + parent_hash + " " + blame_hash + " -U0")
        process = subprocess.Popen(["git", "diff", parent_hash, blame_hash, "-U0"], stdout=subprocess.PIPE, cwd=dir_path)
        gitDiff = (process.communicate()[0]).decode("UTF-8")

        return gitDiff

def run_blame(fn, ln, head):
	line_range = str(ln) + "," + str(ln)

	print("git blame " + fn + " " + "-L" + " " + line_range + " " + head + "-p")

	process = subprocess.Popen(["git", "blame", fn, "-L", line_range, head, "-p"], stdout=subprocess.PIPE, cwd=dir_path)
	git_blame = (process.communicate()[0]).decode("UTF-8")
	return git_blame

def get_file_diffs(git_log):
	file_diffs = { }
	split_log = git_log.split("diff --git a/")
	split_log.pop(0)

	for log in split_log:
		separate_diffs_list = [ ]
		fileName = log.split()[0]
		fileName = fileName.split("/")[-1]
		
		# print(fileName)
		
		fileDiff = log.split("@@")

		if len(fileDiff) < 2:
			print("ERROR: Invalid Diff Target")
			break

		for i in range(int(len(fileDiff) / 2)):
			separate_diffs_list.append("@@" + fileDiff[i + 1] + "@@" + fileDiff[i + 2])

		file_diffs[fileName] = separate_diffs_list

	return file_diffs

def recursive_blame(file_name, line_number, substring, head):
	blaming = True

	while blaming:
		git_blame = run_blame(file_name, line_number, head)
		try:
			blame_hash = git_blame.split()[0]
		except:
			print("ERROR: Invalid Blame Target")
			sys.exit(0)

		git_diff_result = run_diff(blame_hash)
		file_diffs_map = get_file_diffs(git_diff_result)

		#print("git_diff_result: " + git_diff_result)

		if "/" in file_name:
			file_name2 = file_name.split("/")[-1]

		content_list = file_diffs_map.get(file_name2)

		# for c in content_list:
		# 	print(c)

		for content in content_list:
			content_lines = content.split("\n")

			diff_line_tokens = content_lines[0].split(" ")

			base_line_number = -1

			for token in diff_line_tokens:
				if token[0] is "-":
					if token.find(",") > -1:
						base_line_number = token.split(",")[0]
					else:
						base_line_number = token

					base_line_number = base_line_number.replace("-", "")

					break

			blaming = False

			for i, line in enumerate(content_lines):
				if line:
					if line[0] is "-":
						if line.find(substring) > -1:
							line_number = str(int(base_line_number) + i + 1)

							head = blame_hash

							# print("content: " + content)
							# print("base_line_number: " + str(base_line_number))
							# print("line number: " + line_number)
							# print("head: " + head)
							blaming = True
							break

			if blaming:
				break

	return blame_hash

def main():
	if (len(sys.argv) < 3):
	    print("Filename: ", end="", flush=True)
	    file_name = input()
	    print("Line number: ", end="", flush=True)
	    line_number = input()
	    print("Substring (enter nothing to trace exact line): ", flush=True)
	    substring = input()

	    # FOR TESTING
	    #file_name = "modules/apps/forms-and-workflow/dynamic-data-mapping/dynamic-data-mapping-type-text/src/main/java/com/liferay/dynamic/data/mapping/type/text/internal/TextDDMFormFieldTypeSettings.java"
	    #line_number = "98"
	    #substring = "\"allowEmptyOptions=true\""

	    #file_name = "portal-kernel/src/com/liferay/portal/kernel/util/StringUtil.java"
	    #line_number = "209"
	    #substring = "sb.append(StringPool.SPACE)"

	    file_name = "modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java"
	    line_number = "157"
	    substring = "rootPortletId"
	else:
	    file_name = sys.argv[1]
	    line_number = sys.argv[2]

	    for i, x in enumerate(sys.argv):
	        print(sys.argv[i])
	            
	        if x == "-s" and len(sys.argv) > (i + 1):
	                substring = sys.argv[i + 1]
	                break
	head = "HEAD"
	#print(get_line(file_name, line_number))

	blame_hash = recursive_blame(file_name, line_number, substring, head)
	print(blame_hash)

main()