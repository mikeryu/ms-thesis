from pydoc import locate


class Function:

    def __init__(self, name, args, return_type):
        # contract
        self.name = name
        self.args_types = args
        self.return_type = return_type

        # purpose statement and argument names inferred from it
        self.purpose = None
        self.args_names = ([None] * len(self.args_types)) if self.args_types[0].lower() != 'none' else []
        self.return_name = None

        # original lines from the outline (to be reproduced in the template as documentation for the function)
        self.design_recipe_lines = []

        # side effect (i.e. console or disk) I/Os
        self.ins = None
        self.outs = None
        self.in_outs_source = []

        # examples
        self.examples = []

        # body outlines
        self.body_outlines = []

    def validate_completion(self):
        is_valid = True
        is_valid &= self.purpose is not None

        for arg_name in self.args_names:
            is_valid &= arg_name is not None

        # is_valid &= len(self.examples) >= 1 if self.return_type else True
        is_valid &= len(self.body_outlines) >= 1

        return is_valid

    def __str__(self):
        """
        Mostly for debugging.
        :return: String representation that is a python function stub.
        """
        header = 'def {}({}):'.format(self.name, str(self.args_names).lstrip('[').rstrip(']').replace('\'', '')) + '\n'
        contract = '    """ {} -> {} """'.format(str(self.args_types).lstrip('[').rstrip(']').replace('\'', ''),
                                                 self.return_type) + '\n'

        outline = '\n'
        for ol in self.body_outlines:
            outline += '    ' + ol + '\n'

        example = '\n'
        for ex in self.examples:
            example += '    # ' + str(ex) + '\n'

        return header + contract + outline + example


class Example:

    def __init__(self, function):
        self.fxn = function
        self.args = None
        self.rtrn = None
        self.expl = None

        self.arity_count = 0

    def add_arg(self, arg_val):
        arity = len(self.fxn.args_types)
        if self.arity_count >= arity:
            raise IndexError(
                'Attempting to add argument beyond arity {:d} for function {}'.format(arity, self.fxn.name))

        if not self.args:
            self.args = []

        arg_val = self.cast_value(arg_val, False)
        if arg_val is None:
            return False
        else:
            self.args.append(arg_val)
            self.arity_count += 1
            return True

    def add_rtrn(self, return_val):
        rtrn_val = self.cast_value(return_val, True)
        if rtrn_val is None:
            return False
        else:
            self.rtrn = rtrn_val
            return True

    def cast_value(self, val, is_rtrn_val):
        recognized_types = ['int', 'float', 'complex', 'str', 'chr', 'bool']
        type = self.fxn.return_type if is_rtrn_val else self.fxn.args_types[self.arity_count]

        try:
            if type in recognized_types:
                cast = locate(type)
                return cast(val)
            else:
                return val
        except ValueError:
            return None

    def __str__(self):
        """
        Mostly for debugging.
        :return: String representation of the example.
        """
        return '{}({}) -> {}    ({})'.format(
            self.fxn.name,
            str(self.args).lstrip('[').rstrip(']'),
            str(self.rtrn),
            self.expl if self.expl else 'no expl'
        )
