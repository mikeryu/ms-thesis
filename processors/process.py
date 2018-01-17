import sys, os.path

from parser import Parser
from python_writer import PythonWriter


def main(args):
    input_path = args[0]

    if not os.path.isfile(input_path):
        print('Invalid input path given:', input_path, file=sys.stderr)
        exit(1)
    elif input_path[-len('.oln.py'):] != '.oln.py':
        print('Name of code outline file must end with ".oln.py"', file=sys.stderr)

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
        print('Invalid output directory path given:', path_dir, file=sys.stderr)
        print('Falling back to current working directory:', os.getcwd(), file=sys.stderr)
        path_dir = os.getcwd()

    if path_dir[-1] != '/':
        path_dir += '/'

    writer = PythonWriter(parser.functions, template_name)

    tpl_file_path = path_dir + template_name + '.tpl.py'
    ut_file_path = path_dir + template_name + '_tests.py'

    tpl_file = open(tpl_file_path, 'w')
    ut_file = open(ut_file_path, 'w')

    if not writer.write_template(tpl_file):
        print('Failed to write template file:', tpl_file_path, '\nCheck directory permissions.', file=sys.stderr)

    if not writer.write_unittest(ut_file):
        print('Failed to write unit test file:', ut_file_path, '\nCheck directory permissions.', file=sys.stderr)

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
        template_name = given_input_path.replace('.oln.py', '')

    return path_dir, template_name


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 process.py <path_to_code_outline> [path_to_generated_output]', end='\n\n')
        print('    path_to_generated_output is optional; when omitted, same path is input is used.')
        print('    If you\'re unsure about the usage of this tool, please contact your instructor.')
    else:
        main(sys.argv[1:])
