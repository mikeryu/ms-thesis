import sys, os.path

from parser import Parser
from python_writer import PythonWriter


def main(args):
    input_path = args[0]

    if not os.path.isfile(input_path):
        print('Invalid input path given:', input_path)
        exit(1)

    f = open(input_path)
    lines = f.readlines()

    parser = Parser()
    for l in lines:
        parser.parse(l)

    parser.signal_EOF()

    path_dir, template_name = parse_input_path(input_path)

    if len(args) > 1:
        path_dir = args[1]

    if not os.path.isdir(path_dir):
        print('Invalid output directory path given:', path_dir)
        print('Falling back to current working directory:', os.getcwd())
        path_dir = os.getcwd()

    if path_dir[-1] != '/':
        path_dir += '/'

    writer = PythonWriter(parser.functions, template_name)  # funcs

    ut_file = open(path_dir + template_name + '_tests.py', 'w')
    tpl_file = open(path_dir + template_name + '.tpl.py', 'w')

    writer.write_template(tpl_file)
    writer.write_unittest(ut_file)

    ut_file.close()
    tpl_file.close()


def parse_input_path(given_input_path):
    if '/' in given_input_path:
        slash_ndx = given_input_path.rfind('/')
        oln_ndx = given_input_path.rfind('.oln')

        path_dir = given_input_path[:slash_ndx + 1]
        template_name = given_input_path[slash_ndx + 1:oln_ndx]
    else:
        path_dir = './'
        template_name = given_input_path.replace('.py', '')

    return path_dir, template_name


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 process.py <path_to_code_outline> [path_to_generated_output]')
        print('    path_to_generated_output is optional; when omitted, same path is input is used.')
    else:
        main(sys.argv[1:])
