from pydoc import locate
from ast import literal_eval


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
        reasons = []

        # check for purpose statement presence
        is_valid &= self.purpose is not None
        if not is_valid:
            reasons.append('purpose')

        # check for argument names
        nonempty_arg_name = True
        for arg_name in self.args_names:
            nonempty_arg_name &= arg_name is not None
            is_valid &= nonempty_arg_name
        if not nonempty_arg_name:
            reasons.append('argument name(s)')

        # check for body outlines
        nonempty_body_outline = len(self.body_outlines) >= 1
        is_valid &= nonempty_body_outline
        if not nonempty_body_outline:
            reasons.append('body outline')

        return is_valid, tuple(reasons)

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

    def __init__(self, function, recognized_primitives):
        self.fxn = function
        self.args = None
        self.expt = None
        self.expl = None

        self.arity_count = 0
        self.primitives = recognized_primitives

    def add_arg(self, arg_val):
        arity = len(self.fxn.args_types)
        if self.arity_count >= arity:
            raise IndexError(
                'Attempting to add argument beyond arity {:d} for function {}'.format(arity, self.fxn.name))

        if not self.args:
            self.args = []

        arg_val = self.eval_value_str(arg_val, False)
        if arg_val == '____total__and__utter__failure':
            return False
        else:
            self.args.append(arg_val)
            self.arity_count += 1
            return True

    def add_rtrn(self, return_val):
        rtrn_val = self.eval_value_str(return_val, True)
        if rtrn_val == '____total__and__utter__failure':
            return False
        else:
            self.expt = rtrn_val
            return True

    def eval_value_str(self, val, is_rtrn_val):
        """ Timing at which this function is called when casting argument values matter! (see comment below) """
        recognized_types = self.primitives

        # The line below is the reason for the docstring ^
        # It must be called in arity order or bad things will happen ...
        type = self.fxn.return_type if is_rtrn_val else self.fxn.args_types[self.arity_count]

        try: # safety net for locate() and literal_eval()
            if val == 'None':
                return None
            elif type in recognized_types:
                cast = locate(type)

                # casting str -> bool evals according to 'Truthiness'
                if cast == bool and val == 'False':
                    val = ''

                return cast(val)
            else:
                try:
                    return literal_eval(val)
                except SyntaxError:
                    return val

        except ValueError:
            return '____total__and__utter__failure'

    def __str__(self):
        """
        Mostly for debugging.
        :return: String representation of the example.
        """
        return '{}({}) -> {}    ({})'.format(
            self.fxn.name,
            str(self.args).lstrip('[').rstrip(']'),
            str(self.expt),
            self.expl if self.expl else 'no expl'
        )
