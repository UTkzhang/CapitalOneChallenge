import os
import re

# Note: The following functions are explicitly defined for diff commenting schemes, python is inherently a bit more
# difficult to check for block vs single comments because the concept of "block" comments in python doesn't really
# exist formally, so I have chosen to define a block comment as multiple lines of consecutive comments beginning with
# a "#" in the same indentation level.

# For example
# This is a block comment
     # This is no longer a block comment (though it should never happen)
pass # This is not a part of any block comment


# START OF CODE HERE
def check_python(path_to_file):
    # Taking advantage of some regex
    quote_pattern = re.compile(r"([\"'])(?:(?=(\\?))\2.)*?\1")
    space_pattern = re.compile(r"^[\s]*$")

    num_lines = 0
    num_comments = 0
    num_single_line_comments = 0
    num_comments_in_blocks = 0
    num_blocks = 0
    num_todos = 0

    block_possible = False
    block_prefix = None
    in_block = False
    last_line = ""

    with open(path_to_file) as f:
        for line in f:
            last_line = line
            num_lines += 1

            str_removed = quote_pattern.sub("", line)
            idx = str_removed.find("#")

            if idx < 0:
                block_possible = False
                block_prefix = None
                in_block = False
                continue

            num_comments += 1
            prefix = str_removed[:idx]
            suffix = str_removed[idx:]
            num_todos += int("TODO" in suffix)

            if in_block:
                if prefix == block_prefix:
                    num_comments_in_blocks += 1
                    continue
                else:
                    in_block = False
            elif block_possible:
                block_possible = False
                if prefix == block_prefix:
                    in_block = True
                    num_blocks += 1
                    num_comments_in_blocks += 2
                    num_single_line_comments -= 1
                    continue

            num_single_line_comments += 1

            if space_pattern.match(prefix):
                block_possible = True
                block_prefix = prefix

        # account for last empty line usually present in python files
        if last_line.endswith("\n"):
            num_lines += 1

    return num_lines, num_comments, num_single_line_comments, num_comments_in_blocks, num_blocks, num_todos


# Uses a very similar approach to check_python, though it is slightly less complex.
# TODO: comment characters in multi-line strings are an edge case that will require multiple steps to solve, but are
# very rarely encountered. May implement in the future if technical lead thinks its worth the cost to check.
def check_c(path_to_file):
    num_lines = 0
    num_comments = 0
    num_single_line_comments = 0
    num_comments_in_blocks = 0
    num_blocks = 0
    num_todos = 0

    in_block = False
    last_line = ""

    with open(path_to_file) as f:
        for line in f:
            last_line = line
            num_lines += 1
            num_comments += 1

            quote_pattern = re.compile(r"([\"'])(?:(?=(\\?))\2.)*?\1")
            str_removed = quote_pattern.sub("", line)

            if "//" in str_removed:
                num_single_line_comments += 1
                num_todos += int("TODO" in str_removed[str_removed.find("//"):])
            elif "/*" in str_removed:
                if "*/" in str_removed:
                    num_blocks += 1
                elif not in_block:
                    in_block = True
                num_comments_in_blocks += 1
                num_todos += int("TODO" in str_removed[str_removed.find("/*"):])
            elif "*/" in str_removed:
                if in_block:
                    in_block = False
                    num_blocks += 1
                    num_comments_in_blocks += 1
                else:
                    num_comments -= 1
            elif in_block:
                num_todos += int("TODO" in str_removed)
                num_comments_in_blocks += 1
            else:
                num_comments -= 1

        # account for last empty line (usually not in non-python files)
        if last_line.endswith("\n"):
            num_lines += 1

    return [num_lines, num_comments, num_single_line_comments, num_comments_in_blocks, num_blocks, num_todos]


# Main method checks a folder called "submitted" in the same directory as this script, for files to be processed.
if __name__ == "__main__":
    if not os.path.exists("submitted"):
        os.makedirs("submitted")

    # TODO: Need to add support for more file extensions/comment schemes
    for program_file in sorted(os.listdir("submitted")):
        if program_file.endswith(".py"):
            results = check_python(os.path.join("submitted", program_file))
        elif program_file.endswith((".h", ".c", ".cpp", ".m", ".js", ".java", ".swift")):
            results = check_c(os.path.join("submitted", program_file))
        else:
            print("Sorry, this program doesn't support the comment scheme for", program_file, "yet. \n")
            continue

        print("Statistics for file", program_file)
        print("Total # of lines:", results[0])
        print("Total # of comment lines:", results[1])
        print("Total # of single line comments:", results[2])
        print("Total # of comment lines within block comments:", results[3])
        print("Total # of block line comments:", results[4])
        print("Total # of TODO’s:", results[5], "\n")
