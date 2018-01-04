from parser import Parser
from python_writer import PythonWriter

def main():
    f = open('../data/inputs/landerFuncs.oln.py')
    # f = open('../data/inputs/funcs.oln.py')
    lines = f.readlines()

    parser = Parser()
    for l in lines:
        parser.parse(l)

    parser.signal_EOF()

    writer = PythonWriter(parser.functions, 'funcs') # funcs

    ut_file = open('../data/samples/landerFuncs_tests.py', 'w')
    # ut_file = open('../data/samples/funcs_tests.py', 'w')

    tpl_file = open('../data/samples/landerFuncs.py', 'w')
    # tpl_file = open('../data/samples/funcs.py', 'w')

    writer.write_template(tpl_file)
    writer.write_unittest(ut_file)

    ut_file.close()
    tpl_file.close()

if __name__ == '__main__':
    main()