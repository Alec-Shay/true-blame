import os
import re
import subprocess
import sys

#PATH_TO_TRUE_BLAME
run_path = "C:\\Users\\liferay\\Desktop\\me\\true-blame\\true-blame.py"

#PATH_TO_LIFERAY_REPO
repo_path = "C:\\Users\\liferay\\Desktop\\Repos\\liferay-portal"

def main():
    
    expected = "23b974bc9510a06d2a359301c1d12fab4aa61cc5"
    file_path = "modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java"
    line_number = "157"
    substring = "rootPortletId"
    
    args = [file_path, line_number, "-s", substring]
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

    print()
    print("Success!!")


def run_test(args, expected):
    process = subprocess.Popen(["py", run_path] + args, cwd=repo_path, stdout=subprocess.PIPE, shell=True)
    result = process.communicate()[0].decode("UTF-8", "replace")

    assertResult(result, expected)


def assertResult(result, expected):
    test_result = result.split("Commit: ")[1]
    test_result = test_result.splitlines()[0]

    print("Testing " + test_result + " on " + expected)
    assert (test_result == expected), "FAILURE : \n\n" + result

main()

        #file_name = "modules/apps/forms-and-workflow/dynamic-data-mapping/dynamic-data-mapping-type-text/src/main/java/com/liferay/dynamic/data/mapping/type/text/internal/TextDDMFormFieldTypeSettings.java"
        #line_number = "125"
        #substring = "\"allowEmptyOptions=true\""

        #file_name = "modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java"
        #line_number = "21"
        #substring = "AssetEntry"

        #file_name = "portal-impl/src/com/liferay/portal/util/PortalImpl.java"
        #line_number = "317"
        #substring = "class Portal"

        # to run this test, run process with different cwd
        #file_name = "src/true-blame.py"
        #line_number = "149"
        #substring = "removal_lines"
        #reverse = True
        #head = b00428aa730944f2b08109d00376b5c9422943ca
        #reverse_end_point = f5c6a52bacebf81b81dace9e6491b29a8cf693e1