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
        for oln, level in fxn.body_outlines:
            outline += indent + (level * indent) + oln + '\n\n'

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

            expected = self.format_return_val(ex.expt)
            assert_type = self.determine_assert_type(ex.expt)
            args = str(ex.args).strip()[1:-1]
            body = (indent * 2) + self.determine_body(assert_type, fxn.name, args, expected)

            tests += header + expl + body + '\n'

        return tests

    def determine_body(self, assert_type, fxn_name, args, expected_val):
        if assert_type in ['assertTrue', 'assertFalse']:
            return 'self.{}({}({}))\n'.format(assert_type, fxn_name, args)
        else:
            return 'self.{}({}({}), {})\n'.format(assert_type, fxn_name, args, expected_val)

    def determine_assert_type(self, return_val):
        return_type = type(return_val)
        if return_type in [float, complex]:
            return 'assertAlmostEqual'
        elif return_type == bool:
            return 'assertTrue' if return_val else 'assertFalse'
        else:
            return 'assertEqual'

    def format_return_val(self, return_val):
        """ Dealing with None is done in function.py """
        if type(return_val) == str:
            return "\"{}\"".format(return_val.replace('"', '\"'))
        else:
            return return_val
