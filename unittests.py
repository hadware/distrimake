import unittest
from parser import parse_makefile
from syntax_tree.ast import Symbol

class ParserTests(unittest.TestCase):

    def setUp(self):
        self.mkfiletree = parse_makefile("examples/very_simple_makefile")

    def test_parser_simple_symbols(self):
        symbols = {Symbol(name) for name in ["all", "file1.txt", "file2.txt"]}
        self.assertEqual( self.mkfiletree.symbols, symbols)

    def test_parser_simple_command(self):
        self.assertEqual( self.mkfiletree.ruletable[Symbol("file2.txt")].commands[0].content, 'touch file2.txt')

    def test_parser_simple_rulecount(self):
        self.assertEqual(len( self.mkfiletree.ruletable), 3)

class SchedulerTests(unittest.TestCase):

    def setUp(self):
        self.mkfiletree = parse_makefile("examples/premier/Makefile")
        self.scheduler = self.mkfiletree.build_deps("list.txt")
        self.jobs = []

    def test_deps_depth(self):
        self.assertEqual(self.scheduler.pending_jobs_tbl.__len__(), 2)

    def test_deps_number(self):
        self.assertEqual(self.scheduler.total_pending_jobs, 21)

    def test_jobs_taking(self):
        for i in range(5):
            self.jobs.append(self.scheduler.get_job())
        self.assertEqual(self.scheduler.running_jobs.__len__(), 5)