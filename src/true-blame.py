import os
import re
import subprocess
import sys

dir_path = os.getcwd()


# GIT
def git_blame(file_name, line_number, head):
    line_range = str(line_number) + "," + str(line_number)

    args = ["-L", line_range, "-p", head, "--", file_name]
    return git_process("blame", args)


def git_diff(blame_hash, parent_hash):
    args = ["-M", parent_hash, blame_hash, "-U0"]
    return git_process("diff", args)


def git_rev_parse(hash):
    args = [hash + "^"]
    return git_process("rev-parse", args).replace("\n","")


def git_process(cmd, *params):
    print("git " + cmd + " " + ' '.join(str(x) for x in params[0]))

    args = ["git"] + [cmd] + params[0]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=dir_path)

    return process.communicate()[0].decode("UTF-8", "replace")


# UTIL
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

    for diff_file_name, content_lines in sorted_diffs.items():
        for content in content_lines:
            base_line_number = -1
            content_lines = content.split("\n")

            diff_line_tokens = content_lines[0].split(" ")
            for token in diff_line_tokens:
                if token[0] is "-":
                    if token.find(",") > -1:
                        base_line_number = token.split(",")[0]
                    else:
                        base_line_number = token

                    base_line_number = base_line_number.replace("-", "")
                    break

            removal_lines = -1
            for i, line in enumerate(content_lines):
                if line:
                    if line[0] is "-":
                        removal_lines += 1

                        if line.find(substring) > -1:
                            print("Traced to: " + blame_hash)
                            line_number = int(base_line_number) + removal_lines

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
            # Refactor later (regex)
            regex_string = "((previous)((.)*)(\.)([a-zA-Z]+)((\s)*)(filename))"
            other = re.compile(regex_string).split(current_blame)[1]
            parent_hash = other.split()[1]
        except:
            return blame_hash

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

    return blame_hash


def main():
    substring = None

    if (len(sys.argv) < 3):
        print("Filename: ", end="", flush=True)
        file_name = input()
        print("Line number: ", end="", flush=True)
        line_number = input()
        print("Substring (enter nothing to trace exact line): ", flush=True)
        substring = input()

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

                print(sys.argv[i + 1])
                break

    if file_name.find("\\") > -1:
        file_name = file_name.replace("\\", "/")

    head = "HEAD"

    if substring is None:
        substring = get_line(file_name, line_number).strip()
    elif substring.find("\n") > -1:
        print("ERROR: more than one line selected for blame.")
        print("Exiting True Blame.")

        sys.exit(0)

    blame_hash = recursive_blame(file_name, line_number, substring, head)
    print("==============")
    print("True Blame Commit : " + blame_hash)


main()
