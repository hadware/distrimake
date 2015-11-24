import logging
import re
from enum import Enum

from syntax_tree import MakeFile, MakeFileRule, Command


class ParsingError(Exception):
    def __init__(self, line_number, message):
        super().__init__(message)
        self.line_number = line_number

    def __str__(self):
        return "Parsing error at line %i : %s" % (self.line_number + 1, super().__str__())

#defining various regex used in the parsing
class Regexps:
    symbol = re.compile(r"\w+\.?\w+")
    mkfile_head = re.compile(r"\w+\.?\w+\s*:\s*[\w+\.?\w+]*")
    blank_line = re.compile(r"\s+")
    rulecommand_line = re.compile(r"\t\S+")

class AutomataState(Enum):
    OUTSIDERULE = 1
    INRULE = 2

def parse_mkfilerule_head(makefile_tree, line_no, line_string):
    """Parses a mkfile rule head, returns the new rule"""
    try:
        target, dependencies = [s.strip() for s in line_string.split(":")]
    except:
        raise ParsingError(line_no, " Invalid Makefile rule head")
        #transforming targets into symbols
    target = makefile_tree.symbol_factory(target)
    dependencies = [makefile_tree.symbol_factory(dep.strip()) for dep in dependencies.split()]

    return MakeFileRule(target, dependencies)

def parse_makefile(makefile_filepath):
    """This function does all the dirty work :
        - parses the file
        - returns a MakeFile syntax tree
    """
    logging.info("Parsing makefile %s" % makefile_filepath)

    with open(makefile_filepath, "r") as makefile:
        automata = AutomataState.OUTSIDERULE
        makefile_tree = MakeFile(makefile_filepath)
        current_rule = None

        for line_no, current_line in enumerate(makefile.readlines()):
            if automata == AutomataState.OUTSIDERULE:
                if Regexps.mkfile_head.match(current_line):
                    #parsing the rule head, and creating a new rule
                    current_rule = parse_mkfilerule_head(makefile_tree, line_no, current_line)
                    automata = AutomataState.INRULE

                elif Regexps.rulecommand_line.match(current_line):
                    raise ParsingError(line_no, "Unexpected command line")

            else: #it's in the inside rule mode
                if Regexps.rulecommand_line.match(current_line):
                    current_rule.add_command(Command(current_line.strip()))

                elif Regexps.blank_line.match(current_line):
                    #found a blank line, just saving the current rule
                    makefile_tree.add_rule(current_rule)
                    automata = AutomataState.OUTSIDERULE

                elif Regexps.mkfile_head.match(current_line):
                    #saving the current rule, and creating a new one
                    makefile_tree.add_rule(current_rule)
                    #parsing the rule head, and creating a new rule
                    current_rule = parse_mkfilerule_head(makefile_tree, line_no, current_line)

                else:
                    raise ParsingError(line_no, "Expecting an indented tab line, or a blank line")

        #in case the automata was still INRULE,"dump" the last rule to the MakeFile
        if automata == AutomataState.INRULE:
            makefile_tree.add_rule(current_rule)
    logging.info("Finished parsing the makefile")
    return makefile_tree
