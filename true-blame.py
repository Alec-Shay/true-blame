import os
import re
import subprocess
import sys

dir_path = os.getcwd()
ignore_case = False
quiet = False
reverse = False
reverse_end_point = "HEAD"


def git_blame(file_name, line_number, head):
    line_range = str(line_number) + "," + str(line_number)

    if reverse:
        args = ["-L", line_range, "-p", "--reverse", head + ".." + reverse_end_point, "--", file_name]
    else:
        args = ["-L", line_range, "-p", head, "--", file_name]

    return run_process(True, "git", "blame", args)


def git_diff(blame_hash, parent_hash):
    args = ["-M", parent_hash, blame_hash, "-U0"]
    return run_process(True, "git", "diff", args)


def git_log(commit):
    args = ["-1", commit]
    return run_process(True, "git", "log", args)


def git_rev_parse(hash):
    args = [hash + "^"]
    return run_process(True, "git", "rev-parse", args).replace("\n", "")


def git_rev_list_with_ancestry_path(commit_hash):
    args = ["--ancestry-path", commit_hash + ".." + reverse_end_point]
    return run_process(True, "git", "rev-list", args)


def open_gitk(commit_hash):
    run_process(False, "gitk", commit_hash, [])


def run_process(output, program, cmd, *params):
    if not quiet:
        print("\t" + program + " " + cmd + " " +
              ' '.join(str(x) for x in params[0]), flush=True)

    args = [program] + [cmd] + params[0]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=dir_path)

    if output:
        return process.communicate()[0].decode("UTF-8", "replace")


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
    file_separator_regex = "(^|\n)diff --git a\/"

    split_log = re.compile(file_separator_regex).split(git_log)
    split_log.pop(0)

    split_log = [x for x in split_log if x.strip()]

    for log in split_log:
        separate_diffs_list = []
        file_name = log.split()[0]
        file_diff = log.split("\n@@")

        if len(file_diff) < 1:
            print("WARN: Invalid Diff Target: " + file_name.split("/")[-1], flush=True)
            continue

        for x in file_diff:
            separate_diffs_list.append("@@" + x)

        file_diffs[file_name] = separate_diffs_list

    return file_diffs


def get_file_renames(git_diff_result):
    renames_map = {}

    for line in git_diff_result.splitlines():
        if line.startswith("rename from "):
            rename_from = line.replace("rename from ", "")

        if line.startswith("rename to "):
            rename_to = line.replace("rename to ", "")

            renames_map[rename_from] = rename_to

    return renames_map


def get_result_info(blame, hash):
    blame_lines = blame.splitlines()
    log_info_lines = git_log(hash).splitlines()

    blame_line_info = blame_lines[0].split()

    new_info_set = "Commit: " + hash

    for line in log_info_lines:
        if line.startswith("Date:") or line.startswith("Author:"):
            new_info_set += "\n" + line

    new_info_set += "\nSummary: "

    for i in range(4, len(log_info_lines)):
        new_info_set += log_info_lines[i].strip() + "\n"

    for i in range(0, len(blame_lines)):
        if blame_lines[i].startswith("filename"):
            if reverse:
                new_info_set += "\nPreviously found in file:"
            else:
                new_info_set += "\nIntroduced in file:"

            new_info_set += blame_lines[i][blame_lines[i].find(" "):]

            break

    new_info_set += "\nOn line: " + blame_line_info[1] + "\n\n"

    new_info_set += blame_lines[-1]

    return new_info_set


def get_blame_parent(blame_hash, blame):
    if reverse:
        parent_hash = git_rev_parse(blame_hash)
    else:
        regex_string = "((\n)(previous)((.)*)(\.)([a-zA-Z]+)((\s)*)(filename))"
        other = re.compile(regex_string).split(blame)[1]
        parent_hash = other.split()[1]

    return parent_hash


def sort_file_diffs(diffs, file_name, renames):
    sorted_diffs = {}

    if reverse and file_name in renames:
        file_name = renames[file_name]

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


def parse_diffs(input_params, sorted_diffs, renames):
    return_params = {}
    blame_hash = input_params['blame_hash']
    substring = input_params['substring']

    if reverse:
        diff_char = "+"
    else:
        diff_char = "-"

    for diff_file_name, diff in sorted_diffs.items():
        for content in diff:
            base_line_number = -1
            content_lines = content.split("\n")

            diff_line_tokens = content_lines[0].split(" ")
            for token in diff_line_tokens:
                if token[0] is diff_char:
                    if token.find(",") > -1:
                        base_line_number = token.split(",")[0]
                    else:
                        base_line_number = token

                    base_line_number = base_line_number.replace(diff_char, "")
                    break

            diff_lines = -1

            for i, line in enumerate(content_lines):
                if line:
                    if line[0] is diff_char:
                        diff_lines += 1

                        if (line.find(substring) > -1) or (ignore_case and re.search(substring, line, re.IGNORECASE)):
                            if not quiet:
                                print("Traced to: " + blame_hash, flush=True)
                            line_number = int(base_line_number) + diff_lines

                            if reverse:
                                return_params['head'] = blame_hash
                            else:
                                return_params['head'] = blame_hash + "^"

                            if reverse and diff_file_name in renames:
                                return_params['file_name'] = renames[diff_file_name]
                            else:
                                return_params['file_name'] = diff_file_name

                            return_params['line_number'] = str(line_number)
                            return_params['blaming'] = True
                            return return_params

    return_params['blaming'] = False
    return return_params


def recursive_blame(file_name, line_number, substring, head):
    blaming = True

    while blaming:
        if not quiet:
            print("==============", flush=True)
            print("Checking: " + head.replace("^", ""), flush=True)
        current_blame = git_blame(file_name, line_number, head)

        try:
            blame_hash = current_blame.split()[0]

            if reverse:
                parent_hash = blame_hash
                ancestry = git_rev_list_with_ancestry_path(blame_hash).splitlines()

                try:
                    blame_hash = ancestry[-1]
                except:
                    return {blame_hash: get_result_info(current_blame, blame_hash)}
            else:
                try:
                    parent_hash = get_blame_parent(blame_hash, current_blame)
                except:
                    return {blame_hash: get_result_info(current_blame, blame_hash)}
        except:
            print("ERROR: Invalid Blame Commit.")
            sys.exit(0)

        git_diff_result = git_diff(blame_hash, parent_hash)
        file_diffs_map = get_file_diffs(git_diff_result)

        renames_map = get_file_renames(git_diff_result)

        sorted_diffs = sort_file_diffs(file_diffs_map, file_name, renames_map)

        input_params = {'blame_hash': blame_hash,
                        'substring': substring}
        output_params = parse_diffs(input_params, sorted_diffs, renames_map)

        blaming = output_params['blaming']
        if blaming:
            head = output_params['head']
            file_name = output_params['file_name']
            line_number = output_params['line_number']

    return {blame_hash: get_result_info(current_blame, blame_hash)}


def main():
    global ignore_case
    global quiet
    global reverse
    global reverse_end_point

    head = "HEAD"
    gitk = False
    substring = None
    
    if (len(sys.argv) < 2):
        print("Filename: ", end="", flush=True)
        file_name = input()

        print("Line Number: ", end="", flush=True)
        line_number = input()

        print("String: ", flush=True)
        substring = input()
    elif (len(sys.argv) < 3):
        print("Usage: ")
        print("\ttb path/to/file/filename.extension line_number <arguments>")

        sys.exit(0)
    elif "-help" in sys.argv or "--help" in sys.argv:
        print("Usage: ")
        print("\ttb path/to/file/filename.extension line_number <arguments>")

        print("\n\nArguments:")
        print("\n\t-s <string>: specify a specific substring to search on")
        print("\t\t<string> entire line without leading or trailing whitespace by default")

        print("\n\t-r <start-commit> <end-commit>: search in reverse")
        print("\t\t<start-commit> HEAD by default")
        print("\t\t<end-commit> HEAD by default")

        print("\n\t-ic: ignore case when searching")
        print("\t\tFalse by default")

        print("\n\t-q: only print the result")
        print("\t\tFalse by default")

        print("\n\t-gitk: open gitk on result hash")
        print("\t\tFalse by default")

        sys.exit(0)
    else:
        file_name = sys.argv[1]
        line_number = sys.argv[2]

        for i, x in enumerate(sys.argv):
            if x == "-s" and len(sys.argv) > (i + 1):
                substring = sys.argv[i + 1]

            if x == "-r" or x == "-reverse":
                reverse = True

                if len(sys.argv) > (i + 1) and sys.argv[i + 1][0] is not "-":
                    head = sys.argv[i + 1]

                if len(sys.argv) > (i + 2) and sys.argv[i + 2][0] is not "-":
                    reverse_end_point = sys.argv[i + 2]

            if x == "-ic" or x == "-ignore-case":
                ignore_case = True

            if x == "-q" or x == "-quiet":
                quiet = True

            if x == "-gitk":
                gitk = True

    try:
        file_name = file_name.strip()
        line_number = line_number.strip()

        if file_name.find("\\") > -1:
            file_name = file_name.replace("\\", "/")

        if not re.compile("^[^\s\"\'\.]+(\.)[a-z]{1,6}$").match(file_name):
            print("INFO: " + file_name, flush=True)

        if not re.compile("^[0-9]+$").match(line_number):
            raise Exception()
    except:
        print("Filename: " + file_name)
        print("Line Number: " + line_number + "\n")
        print("ERROR: Invalid Parameters.")

        sys.exit(0)

    if substring is None:
        substring = get_line(file_name, line_number).strip()
    elif substring.find("\n") > -1:
        print("ERROR: Multiple Lines Selected.")

        sys.exit(0)

    blame = recursive_blame(file_name, line_number, substring, head)
    blame_hash = list(blame.keys())[0]

    print("==============")
    print("True Blame: \n\n" + blame[blame_hash])

    if reverse:
        quiet = True
        reverse_end_point_hash = git_log(reverse_end_point).split()[1]

        if reverse_end_point_hash == blame_hash:
            print("\nThis commit is the last in the specified range. \
                The line may not have been removed!")

    if gitk:
        open_gitk(blame_hash)

main()
