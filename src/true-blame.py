import os
import re
import subprocess
import sys

dir_path = os.getcwd()
reverse = False
reverse_end_point = "HEAD"

# GIT
def git_blame(file_name, line_number, head):
    line_range = str(line_number) + "," + str(line_number)

    if reverse:
        args = ["-L", line_range, "-p", "--reverse", head, "--", file_name]
    else:
        args = ["-L", line_range, "-p", head, "--", file_name]

    return git_process("blame", args)


def git_diff(blame_hash, parent_hash):
    args = ["-M", parent_hash, blame_hash, "-U0"]
    return git_process("diff", args)


def git_rev_parse(hash):
    args = [hash + "^"]
    return git_process("rev-parse", args).replace("\n","")


def git_rev_list_with_ancestry_path(commit_hash):
    args = ["--ancestry-path", commit_hash + ".." + reverse_end_point]
    return git_process("rev-list", args)


def git_process(cmd, *params):
    print("git " + cmd + " " + ' '.join(str(x) for x in params[0]))

    args = ["git"] + [cmd] + params[0]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=dir_path)

    return process.communicate()[0].decode("UTF-8", "replace")


# UTIL
def fix_current_blame_with_hash(blame, hash):
    blame_lines = blame.splitlines()

    new_blame = hash + blame_lines[0][blame_lines[0].find(" "):]

    for i, x in enumerate(blame_lines):
        new_blame += "\n" + x

    return new_blame

def get_line(file_name, line_number):
    file = open(dir_path + "/" + file_name)
    line = ""

    for i, counted_line in enumerate(file):
        if i == (int(line_number) - 1):
            line = counted_line
            break

    file.close()
    return line


def get_file_diffs(git_log):
    file_diffs = {}
    # Refactor later (split)
    split_log = git_log.split("diff --git a/")
    split_log.pop(0)

    for log in split_log:
        separate_diffs_list = []
        file_name = log.split()[0]
        file_diff = log.split("@@")

        if len(file_diff) < 2:
            print("WARN: Invalid Diff Target: " + file_name.split("/")[-1])
            continue

        half = int(len(file_diff) / 2)
        for i in range(half):
            j = (i*2) + 1
            separate_diffs_list.append("@@" + file_diff[j] +
                                       "@@" + file_diff[j + 1])

        file_diffs[file_name] = separate_diffs_list

    return file_diffs


def get_blame_parent(blame_hash, blame):
    if reverse:
        parent_hash = git_rev_parse(blame_hash)
    else:
        regex_string = "((previous)((.)*)(\.)([a-zA-Z]+)((\s)*)(filename))"
        other = re.compile(regex_string).split(blame)[1]
        parent_hash = other.split()[1]

    return parent_hash


def sort_file_diffs(diffs, file_name):
    sorted_diffs = {}
    sorted_diffs[file_name] = "temp"
    simplified_file_name = file_name.split("/")[-1]

    for k, v in diffs.items():
        simplified_k = k.split("/")[-1]

        if simplified_k == simplified_file_name:
            sorted_diffs[k] = v

    for k, v in diffs.items():
        if k not in sorted_diffs:
            sorted_diffs[k] = v

    if sorted_diffs[file_name] == "temp":
        del sorted_diffs[file_name]

    return sorted_diffs


# CONTROL
def parse_diffs(input_params, sorted_diffs):
    return_params = {}
    blame_hash = input_params['blame_hash']
    substring = input_params['substring']

    if reverse:
        relevant_char = "+"
    else:
        relevant_char = "-"

    for diff_file_name, content_lines in sorted_diffs.items():
        for content in content_lines:
            base_line_number = -1
            content_lines = content.split("\n")

            diff_line_tokens = content_lines[0].split(" ")
            for token in diff_line_tokens:
                if token[0] is relevant_char:
                    if token.find(",") > -1:
                        base_line_number = token.split(",")[0]
                    else:
                        base_line_number = token

                    base_line_number = base_line_number.replace(relevant_char, "")
                    break

            relevant_lines = -1

            for i, line in enumerate(content_lines):
                if line:
                    if line[0] is relevant_char:
                        relevant_lines += 1

                        if line.find(substring) > -1:
                            print("Traced to: " + blame_hash)
                            line_number = int(base_line_number) + relevant_lines

                            return_params['head'] = blame_hash + "^"
                            return_params['file_name'] = diff_file_name
                            return_params['line_number'] = str(line_number)
                            return_params['blaming'] = True
                            return return_params

    return_params['blaming'] = False
    return return_params


def recursive_blame(file_name, line_number, substring, head):
    blaming = True

    while blaming:
        print("==============")
        print("Checking : " + head)
        current_blame = git_blame(file_name, line_number, head)

        try:
            blame_hash = current_blame.split()[0]

            if reverse:
                parent_hash = blame_hash

                ancestry = git_rev_list_with_ancestry_path(blame_hash).splitlines()

                try:
                    blame_hash = ancestry[-1]
                except:
                    return current_blame
            else:
                try:
                    parent_hash = get_blame_parent(blame_hash, current_blame)
                except:
                    return current_blame
        except:
            print("ERROR: Invalid commit for git blame.")
            sys.exit(0)

        git_diff_result = git_diff(blame_hash, parent_hash)
        file_diffs_map = get_file_diffs(git_diff_result)

        sorted_diffs = sort_file_diffs(file_diffs_map, file_name)

        input_params = {'blame_hash': blame_hash,
                        'substring': substring}
        output_params = parse_diffs(input_params, sorted_diffs)

        blaming = output_params['blaming']
        if blaming:
            head = output_params['head']
            file_name = output_params['file_name']
            line_number = output_params['line_number']
        # for k, v in output_params:
        #     locals()['k'] = v

    if reverse:
        current_blame = fix_current_blame_with_hash(current_blame, blame_hash)

    return current_blame


def main():
    global reverse
    global reverse_end_point

    head = "HEAD"
    substring = None

    help = False

    for x in enumerate(sys.argv):
    	if x == "--help":
    		help = True
    		break

    if help:
        print("Basic syntax: tb path/to/file/filename.extension line_number <arguments>\n\n")

        print("Arguments:\n")
        print("\t-s <string>: specify a specific substring of the desired line to search on")
        print("\t\tnot using -s will use the whole line by default (without leading/trailing whitespace)\n")
        print("\t-r <start-commit> <end-commit>: search in reverse")
        print("\t\tstart-commit and  end-commit are assumed HEAD by default")
        sys.exit(0)
    elif (len(sys.argv) < 3):
        print("Filename: ", end="", flush=True)
        file_name = input()
        print("Line Number: ", end="", flush=True)
        line_number = input()
        print("Substring (default: exact line): ", flush=True)
        substring = input()

        print("Reverse? (Y/N) ", end="", flush=True)
        reverse_string = input()
        reverse = reverse_string[0] is "Y" or reverse_string[0] is "y"

        if reverse:
            print("Starting Hash (default: HEAD): ", end="", flush=True)
            head = input()

            if head is None:
                head = "HEAD"

            print("Ending Hash (default: HEAD): ", end="", flush=True)
            reverse_end_point = input()

            if reverse_end_point is None:
                reverse_end_point = "HEAD"

        # FOR TESTING
        #file_name = "modules/apps/forms-and-workflow/dynamic-data-mapping/dynamic-data-mapping-type-text/src/main/java/com/liferay/dynamic/data/mapping/type/text/internal/TextDDMFormFieldTypeSettings.java"
        #line_number = "125"
        #substring = "\"allowEmptyOptions=true\""

        # file_name = "portal-kernel/src/com/liferay/portal/kernel/util/StringUtil.java"
        # line_number = "209"
        # substring = "sb.append(StringPool.SPACE)"
        # EXPECT : b2590ecfa4b8d6cbefdb65c5cc7949a23e33155b

        file_name = "modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java"
        line_number = "157"
        substring = "rootPortletId"
        # EXPECT : 23b974bc9510a06d2a359301c1d12fab4aa61cc5

        #file_name = "modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java"
        #line_number = "21"
        #substring = "AssetEntry"

        #file_name = "portal-impl/src/com/liferay/portal/util/PortalImpl.java"
        #line_number = "317"
        #substring = "class Portal"
    else:
        file_name = sys.argv[1]
        line_number = sys.argv[2]

        for i, x in enumerate(sys.argv):
            print(sys.argv[i])

            if x == "-s" and len(sys.argv) > (i + 1):
                substring = sys.argv[i + 1]

            if x == "-r":
                reverse = True
    
                if len(sys.argv) > (i + 1) and sys.argv[i + 1][0] is not "-":
                    head = sys.argv[i + 1]

                if len(sys.argv) > (i + 2) and sys.argv[i + 2][0] is not "-":
                    reverse_end_point = sys.argv[i + 2]

    try:
        file_name = file_name.strip()
        line_number = line_number.strip()

        if file_name.find("\\") > -1:
            file_name = file_name.replace("\\", "/")

        if not re.compile('^[^\s\"\'\.]+(\.)[a-z]{1,6}$').match(file_name):
            print("INFO: " + file_name)

        if not re.compile(r'^[0-9]+$').match(line_number):
            raise Exception()
    except:
        print("Filename: " + file_name)
        print("Line Number: " + line_number)

        print("ERROR: INVALID PARAMETERS")
        print("Exiting.")

        sys.exit(0)

    if substring is None:
        substring = get_line(file_name, line_number).strip()
    elif substring.find("\n") > -1:
        print("ERROR: Mulitple blame lines selected.")
        print("Exiting.")

        sys.exit(0)

    blame = recursive_blame(file_name, line_number, substring, head)
    print("==============")
    print("True Blame : \n" + blame)

main()
