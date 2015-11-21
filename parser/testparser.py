# this is probably useless until I figure out how to properly use pypeg.
# For the time being, the "handmade" parser suffices.
import re
from pypeg2 import parse, Symbol, List, separated, restline, \
    endl, maybe_some, some, name, attr, blank, Enum, optional, indent, whitespace, csl, word

Symbol.regex = re.compile(r"\w+\.?\w+")

class BashCommand(str):
    grammar = blank,  restline, endl

class File(str):
    grammar = name()

class MakeFileRule(List):
    grammar = name(), blank,  ":", blank, maybe_some(Symbol),  endl, attr("command", BashCommand)

testext = """all :  file2.txt file3.txt\n
    cat file2.txt file3.txt"""

def test_re(regexp):
    for testfilename in ["file", "file1", "file1.txt", ".file", "file_2.txt"]:
        if len(regexp.findall(testfilename)) == 1:
            print("%s : OK" % testfilename)
        else:
            print("%s : ERR" % testfilename)

#test_re(Symbol.regex)
test = parse(testext, MakeFileRule)
print(test)