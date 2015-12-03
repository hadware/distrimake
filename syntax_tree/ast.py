from syntax_tree.scheduler import Scheduler


class MakeError(Exception):
    pass


class MakeFileRule:
    """Stores the data for a makefile rule"""

    def __init__(self, target, dependencies):
        self.target = target
        self.dependencies = dependencies
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def __str__(self):
        return "%s : %s \n %s" % (self.target.name,
                                  " ".join([str(dep) for dep in self.dependencies]),
                                  "\n".join([str(command) for command in self.commands]))

    def print_header(self):
        """Outputs only the header of the rule"""
        return "%s <- %s" % (self.target.name, " ".join([str(dep) for dep in self.dependencies]))

class Command:
    """Stores a command"""

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return self.content


class Symbol:
    """Stores a MKfile symbol, in other words, a target or a dependency"""

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

class MakeFile:
    """Stores the whole tree of the makefile, with a hashmap to solve dependencies"""

    def __init__(self, makefile_folder):
        self.symbols = set()
        self.ruletable = {} # keys : symbols, values : rules
        self.scheduler = None
        self.makefile_folder = makefile_folder

    def add_rule(self, rule):
        self.ruletable[rule.target] = rule

    def symbol_factory(self, new_target_name):
        """Returns unique targets to act as a symbol table"""
        new_target = Symbol(new_target_name)
        if new_target in self.symbols:
            for target in self.symbols: #this whole block is done to keep uniqueness
                if target == new_target:
                    return target
        else:
            self.symbols.add(new_target)
            return new_target

    def build_deps(self, target_name):
        """This is called *after* parsing. Instanciates a scheduler,
        passes it its ruletable, and checks if the specified rulename actually exists"""
        target_symbol = Symbol(target_name)
        if target_symbol in self.ruletable:
            self.scheduler = Scheduler(self.ruletable, target_symbol, self.makefile_folder)
            return self.scheduler
        else:
            raise MakeError("Can't find target rule")

