from writer import Writer


class PythonWriter(Writer):

    def __init__(self, functions, template_name):
        super().__init__(functions)
        self.language = "Python 3"
        self.main = template_name

    def write_template(self, file):
        try:
            file.write(self.get_template_header())

            for fxn in self.fxns:
                fxn_template = self.get_template_function(fxn)
                file.writelines(fxn_template)

        except IOError:
            return False

        return True

    def write_unittest(self, file):
        try:
            file.write(self.get_unittest_header())
            file.write(self.get_unittest_class_wrapper())

            for fxn in self.fxns:
                tests = self.get_unittests(fxn)
                file.writelines(tests)

            file.write(self.get_unittest_footer())

        except IOError:
            return False

        return True

    def get_template_header(self):
        return '"""\nProject _\n\nName: Boaty MacBoatface\nInstructor: Mike Ryu\nSection: __\n"""\n\n' \
               'from math import sqrt\n\n'

    def get_template_function(self, fxn):
        indent = '    '

        header = 'def {}({}):\n'.format(fxn.name, str(fxn.args_names).lstrip('[').rstrip(']').replace('\'', ''))

        design_recipe = indent + '"""\n'
        for drl in fxn.design_recipe_lines:
            design_recipe += indent + drl
        design_recipe += indent + '"""\n'

        body = indent + 'pass    # delete "pass" once you have real code for this function!\n'

        outline = '\n'
        for oln in fxn.body_outlines:
            outline += indent + oln + '\n\n'

        return header + design_recipe + body + outline + '\n'

    def get_unittest_header(self):
        return 'import unittest\nfrom {} import *\n\n'.format(self.main)

    def get_unittest_footer(selfs):
        return '\nif __name__ == \'__main__\':\n    unittest.main()\n'

    def get_unittest_class_wrapper(self):
        return '\nclass TestCases(unittest.TestCase):\n'

    def get_unittests(self, fxn):
        indent = '    '
        tests = '\n' if fxn.examples else ''

        for count, ex in enumerate(fxn.examples):
            header = indent + 'def test_{}_{:d}(self):\n'.format(fxn.name, count + 1)
            expl = (indent * 2) + ex.expl + '\n' if ex.expl else ''

            assert_type = 'assertAlmostEqual' if type(ex.rtrn) in [float, complex] else 'assertEqual'

            return_val = "\"{}\"".format(ex.rtrn.replace('"', '\"')) if type(ex.rtrn) == str else ex.rtrn
            return_val = None if return_val == "\"None\"" else return_val  # TODO do better than this

            args = str(ex.args).strip().lstrip('[').rstrip(']')

            body = (indent * 2) + 'self.{}({}({}), {})\n'.format(assert_type, fxn.name, args, return_val)

            tests += header + expl + body + '\n'

        return tests
