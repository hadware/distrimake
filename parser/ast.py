
class MakeFileRule:
    """Stores the data for a makefile rule"""

    def __init__(self, target, dependencies):
        self.target = target
        self.dependencies = dependencies
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

class Command:
    """Stores a command"""

    def __init__(self, content):
        self.content = content


class Target:
    """Stores a MKfile symbol, in other words, a target or a dependency"""

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)

class MakeFile:
    """Stores the whole tree of the makefile, with a hashmap to solve dependencies"""

    def __init__(self):
        self.targets = set()
        self.ruletable = {} # keys : symbols, values : rules

    def add_rule(self, rule):
        self.ruletable[rule.target] = rule

    def target_factory(self, new_target_name):
        """Returns unique targets to act as a symbol table"""
        new_target = Target(new_target_name)
        if new_target in self.targets:
            for target in self.targets: #this whole block is done to keep uniqueness
                if target == new_target:
                    return target
        else:
            self.targets.add(new_target)
            return new_target

