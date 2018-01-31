#!/usr/bin/env python3

import sys, time, datetime, traceback, os.path

from parser import Parser
from python_writer import PythonWriter
from logpath import _logpath

_tpl_suffix = '.py'
_ut_suffix = '_tests.py'

_logdata = {}

def main(args):
    input_path = args[0]

    if not os.path.isfile(input_path):
        print('Invalid input path given:', input_path, file=sys.stderr)
        exit(1)
    elif input_path[-len('.oln.py'):] != '.oln.py':
        print('Name of code outline file must end with ".oln.py"', file=sys.stderr)
        exit(1)

    f = open(input_path)
    lines = f.readlines()

    parser = Parser()
    for l in lines:
        parser.parse(l)

    parser.signal_EOF()

    path_dir, template_name = parse_input_path(input_path)

    if len(args) > 1 and args[1] != '--debug':
        path_dir = args[1]

    if not os.path.isdir(path_dir):
        print('Invalid output directory path given:', path_dir, file=sys.stderr)
        print('Falling back to current working directory:', os.getcwd(), file=sys.stderr)
        path_dir = os.getcwd()

    if path_dir[-1] != '/':
        path_dir += '/'

    _logdata['input_path'] = input_path
    _logdata['output_path_dir'] = path_dir

    writer = PythonWriter(parser.functions, template_name)

    tpl_file_path = path_dir + template_name + _tpl_suffix
    ut_file_path = path_dir + template_name + _ut_suffix

    check_dup_and_write(tpl_file_path, writer)
    check_dup_and_write(ut_file_path, writer)


def check_dup_and_write(file_path, writer):
    # stupid, but stderr and stdout mixed ain't gonna fly with 101 student
    time.sleep(0.1)
    is_test_file = file_path[-len(_ut_suffix):] == _ut_suffix

    if get_duplicate_overwrite_permission(file_path):
        file_to_write = open(file_path, 'w')
        is_success = True

        if is_test_file:
            is_success = writer.write_unittest(file_to_write)
        else:
            is_success = writer.write_template(file_to_write)

        if not is_success:
            print('DRCOP failed to write: \'{}\'' +
                  '\nPlease check directory permissions.'.format(file_path),
                  file=sys.stderr)

        file_to_write.close()
        print('{} file \'{}\' has been generated.'.format('Unittest' if is_test_file else 'Template', file_path))
    else:
        print('Skipped generating a {} file.'.format('unittest' if is_test_file else 'template'))


def get_duplicate_overwrite_permission(path_to_file):
    if os.path.isfile(path_to_file):
        sys.stderr.flush()
        response = input(
            '\nFile \'{}\' already exists.\n'.format(path_to_file) +
            '\n    Overwriting it may result in PERMANENT LOSS of data!' +
            '\n    Is it really okay for DRCOP to overwrite it? [Y/n] ')
        print()
        return response.lower() == 'y'
    else:
        return True


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


def wrap_top_level_exception(e):
    ts = time.time()
    ts_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    error_hash = abs(hash(e))
    log_file_name = 'ERROR-{}.log'.format(error_hash)
    log_file_path = _logpath + log_file_name

    print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', end='\n\n')
    print('    A critical error has occurred and DRCOP had to call it quits :(', end='\n\n')
    print('        Your instructor is very sorry that you had to experience this.')
    print('        Please show your instructor this error code: {}.'.format(error_hash), end='\n\n')
    print('    This might have been caused by some invalid syntax in your .oln.py file.')
    print('    Please review your code outline and try again.', end='\n\n')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', end='\n\n')

    with open(log_file_path, 'w') as f:
        f.write('Exception occurred at {} (local timestamp)\n\n'.format(ts_str))
        f.write('Log data:\n    {}\n\n'.format(str(_logdata)))
        f.write(str(e) + '\n\n')
        f.write(traceback.format_exc())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: DRCOP <path_to_code_outline> [path_to_generated_output]', end='\n\n')
        print('    path_to_generated_output is optional; when omitted, path_to_code_outline is used.')
        print('    If you\'re unsure about the usage of this tool, please contact your instructor.', end='\n\n')
    else:
        try:
            main(sys.argv[1:])
        except Exception as e:
            if '--debug' in sys.argv[2:]:
                raise e
            else:
                wrap_top_level_exception(e)
                exit(-1)
