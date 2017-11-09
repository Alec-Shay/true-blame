import os
import re
import subprocess
import sys

#PATH_TO_TRUE_BLAME_PROJECT
# run_path = "C:\\Users\\liferay\\Desktop\\me\\true-blame"
run_path = os.environ['TB_PATH']

#PATH_TO_LIFERAY_REPO
# repo_path = "C:\\Users\\liferay\\Desktop\\Repos\\liferay-portal"
repo_path = os.environ['LIFERAY_PATH']

def main():
    global run_path
    run_path = run_path + "\\true-blame.py"

    expected = "23b974bc9510a06d2a359301c1d12fab4aa61cc5"
    file_path = "modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java"
    line_number = "158"
    substring = "rootPortletId"
    
    args = [file_path, line_number, "-s", substring]
    run_test(args, expected)

    expected = "f63004e3489b5eef95a67612dfbc93552d311650"

    args = [file_path, line_number, "-s", substring, "-ic"]
    run_test(args, expected)

    expected = "b2590ecfa4b8d6cbefdb65c5cc7949a23e33155b"
    file_path = "portal-kernel/src/com/liferay/portal/kernel/util/StringUtil.java"
    line_number = "209"
    substring = "sb.append(StringPool.SPACE)"

    args = [file_path, line_number, "-s", substring]
    run_test(args, expected)

    expected = "302eae90a0f13d0ab330f73b8aef8ea7a0dbcaf4"
    file_path = "modules/apps/forms-and-workflow/dynamic-data-mapping/dynamic-data-mapping-type-text/src/main/java/com/liferay/dynamic/data/mapping/type/text/internal/TextDDMFormFieldTypeSettings.java"
    line_number = "15" 
    substring = "com.liferay.dynamic.data.mapping.type.text"

    args = [file_path, line_number, "-s", substring]
    run_test(args, expected)

    expected = "6ba980b887bfd463168c6788d91032c4233f6862"
    file_name = "modules/apps/forms-and-workflow/dynamic-data-mapping/dynamic-data-mapping-type-text/src/main/java/com/liferay/dynamic/data/mapping/type/text/internal/TextDDMFormFieldTypeSettings.java"
    line_number = "125"
    substring = "\"allowEmptyOptions=true\""

    args = [file_path, line_number, "-s", substring]
    run_test(args, expected)

    expected = "2e0dcf0783ee0c2a779016838b03cc65e71ac387"
    file_name = "modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java"
    line_number = "21"
    substring = "AssetEntry"

    args = [file_path, line_number, "-s", substring]
    run_test(args, expected)

    expected = "70489a1cbbd9919120c7f10dff8d57e2b4187bb6"
    file_name = "portal-impl/src/com/liferay/portal/util/PortalImpl.java"
    line_number = "317"
    substring = "class Portal"

    args = [file_path, line_number, "-s", substring]
    run_test(args, expected)

    print()
    print("Success!!")


def run_test(args, expected):
    global run_path
    global repo_path

    process = subprocess.Popen(["py", run_path] + args, cwd=repo_path, stdout=subprocess.PIPE, shell=True)
    result = process.communicate()[0].decode("UTF-8", "replace")

    assertResult(result, expected)


def assertResult(result, expected):
    test_result = result.split("Commit: ")[1]
    test_result = test_result.splitlines()[0]

    print("Testing " + test_result + " on " + expected)
    assert (test_result == expected), "FAILURE : \n\n" + result

main()


        # to run this test, run process with different cwd
        #file_name = "src/true-blame.py"
        #line_number = "149"
        #substring = "removal_lines"
        #reverse = True
        #head = b00428aa730944f2b08109d00376b5c9422943ca
        #reverse_end_point = f5c6a52bacebf81b81dace9e6491b29a8cf693e1