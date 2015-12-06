from parser import parse_makefile

if __name__ == "__main__":
    mkfile_tree = parse_makefile("examples/premier/Makefile")
    parse_makefile("ex")
    print("ok")