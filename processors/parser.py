import re, sys
from pydoc import locate
from function import *


class State:
    """
    Represents a state of the parser
    """

    class Primary:
        INIT = 0b000
        BLOCK = 0b001
        DESIGN_RECIPE = 0b010
        BODY_OUTLINE = 0b100
        STR = {INIT: 'INIT', BLOCK: 'BLOCK',
               DESIGN_RECIPE: 'DESIGN_RECIPE',
               BODY_OUTLINE: 'BODY_OUTLINE'}

    class Sub:
        NONE = 0b0000
        CONTRACT = 0b0001
        PURPOSE = 0b0010
        IN_OUTS = 0b0100
        EXAMPLE = 0b1000
        STR = {NONE: 'NONE', CONTRACT: 'CONTRACT',
               PURPOSE: 'PURPOSE', IN_OUTS: 'IN_OUTS', EXAMPLE: 'EXAMPLE'}

    def __init__(self):
        self.primary = State.Primary.INIT
        self.sub = State.Sub.NONE

    def __str__(self):
        return State.Primary.STR[self.primary] + ('.' + State.Sub.STR[self.sub])

    def is_in(self, primary, sub=None):
        return (primary == self.primary) and ((sub == self.sub) if sub else True)


class Parser:
    """
    Parser is a state machine that switches from a state to state while parsing.
    State is reevaluated as new lines are given to be processed.

    Parser will iteratively built Function objects with each call made to it.
    At the EOF of the code outline, the client may expect to get a list of Function objects
    in the attribute 'functions.' Function objects then can be used for code template generation.
    """

    ###################################################################################################################
    # Constructors and Public Functions

    def __init__(self, indentation_size, recognized_primitives):
        """
        Mostly class member declarations and initializations.
        """

        # indentation size to use when parsing the body outline
        self.indent_size = indentation_size

        # used in casting primitives from str to corresponding types
        self.recognized_primitives = recognized_primitives

        # line being processed
        self.line_num = 0
        self.line = None
        self.prev_line = None

        # state of the parser
        self.prev_state = None
        self.state = State()

        # mostly for debugging
        self.state_history = ''

        # functions built so far
        self.curr_fx = None
        self.functions = []

    def parse(self, line):
        """
        Determine the state of the parser and call the appropriate method to actually parse the line.
        Designed to be called by a client, one call per line of code outline.
        """
        self.prev_line = self.line
        self.line = line
        self.line_num += 1

        self.re_eval_state(line)

        # PRINT STATEMENTS FOR DEBUGGING
        # print('At line {:4d} : ['.format(self.line_num), line.replace('\n', ''), ']')
        # print('Parser state :', str(self.prev_state), '->', str(self.state), end='\n\n')
        # print(self.state_history)

        if self.state.is_in(State.Primary.DESIGN_RECIPE, State.Sub.CONTRACT):
            self.parse_contract(line)
            self.curr_fx.design_recipe_lines.append(line)
        elif self.state.is_in(State.Primary.DESIGN_RECIPE, State.Sub.PURPOSE):
            self.parse_purpose(line)
            self.curr_fx.design_recipe_lines.append(line.replace('`', ''))
        elif self.state.is_in(State.Primary.DESIGN_RECIPE, State.Sub.IN_OUTS):
            self.parse_in_outs(line)
            self.curr_fx.design_recipe_lines.append(line)
        elif self.state.is_in(State.Primary.DESIGN_RECIPE, State.Sub.EXAMPLE):
            self.parse_example(line)
            self.curr_fx.design_recipe_lines.append(line)
        elif self.state.is_in(State.Primary.BODY_OUTLINE):
            self.parse_body_outline(line)

    def signal_EOF(self):
        """
        To be called by the client at the end of the code outline to signal the end and finalize the current function.
        """
        self.validate_current_function_completion()
        self.functions.append(self.curr_fx)

    ###################################################################################################################
    # State Evaluation Functions

    def re_eval_state(self, line):
        """
        Reevaluates the state of this parser based on the line being parsed.
        :param line: line to look into for determining the state (as given by the client of Parser)
        """
        line = line.strip()
        # current primary state is INIT
        if self.state.is_in(State.Primary.INIT):
            if line[:3] == '"""':
                self.update_state(State.Primary.BLOCK, State.Sub.NONE)
            elif line[:1] == '#':
                self.update_state(State.Primary.BODY_OUTLINE, State.Sub.NONE)
            else:
                self.maintain_state()
        # current primary state is BLOCK
        elif self.state.is_in(State.Primary.BLOCK):
            if line[:3] == '"""':
                self.update_state(State.Primary.INIT, State.Sub.NONE)
            else:
                if not self.check_and_update_design_recipe_sub_states(line):
                    self.maintain_state()
        # current primary state is DESIGN_RECIPE
        elif self.state.is_in(State.Primary.DESIGN_RECIPE):
            if line[:3] == '"""':
                self.update_state(State.Primary.BLOCK, State.Sub.NONE)
                self.re_eval_state(line)
            else:
                if not self.check_and_update_design_recipe_sub_states(line):
                    self.update_state(State.Primary.DESIGN_RECIPE, State.Sub.NONE)
        # current primary state is BODY_OUTLINE
        elif self.state.is_in(State.Primary.BODY_OUTLINE):
            if line[:3] == '"""':
                self.update_state(State.Primary.INIT, State.Sub.NONE)
                self.re_eval_state(line)
            elif line[:1] == '#':
                self.update_state(State.Primary.BODY_OUTLINE)
            else:
                self.maintain_state()
        else:
            self.maintain_state()

    def maintain_state(self):
        """
        Updates the state with the exact same state as the current state.
        """
        self.update_state(self.state.primary, self.state.sub)

    def check_and_update_design_recipe_sub_states(self, line):
        """
        Determine which portion of the design recipe is currently being parsed.
        :param line: line to look into for determining the state (as given by the client of Parser)
        :return: True if sub state update occurred, otherwise False.
        """
        primary = State.Primary.DESIGN_RECIPE
        return self.check_line_header_and_update_sub_state('CONTRACT', line, primary, State.Sub.CONTRACT) or \
               self.check_line_header_and_update_sub_state('PURPOSE', line, primary, State.Sub.PURPOSE) or \
               self.check_line_header_and_update_sub_state('IN/OUTS', line, primary, State.Sub.IN_OUTS) or \
               self.check_line_header_and_update_sub_state('EXAMPLE', line, primary, State.Sub.EXAMPLE)

    def check_line_header_and_update_sub_state(self, line_header_str, line, primary_state, sub_state):
        """
        Check the header of the given line and update the sub state of the parser if applicable.
        :param line_header_str: design recipe header string: 'CONTRACT', 'PURPOSE', 'IN/OUTS', or 'EXAMPLE'.
        :param line: line to look into for determining the state (as given by the client of Parser).
        :param primary_state: Primary state of the parser (to be maintained), should be State.Primary.DESIGN_RECIPE
        :param sub_state: One of the sub states matching the line_header_str
        :return: True if sub state update occurred, otherwise False.
        """
        if line[:len(line_header_str)].upper() == line_header_str and self.state.sub <= sub_state:
            self.update_state(primary_state, sub_state)
            return True
        elif line_header_str == 'EXAMPLE' and ('->' in line):
            self.update_state(primary_state, sub_state)
            return True
        else:
            return False

    def update_state(self, primary, sub=None):
        """
        Updates the parser's state as given by the parameters.
        :param primary: primary state to update the parser to; must be given for every call.
        :param sub: sub state to update, default None, which signals maintaining of the sub state.
        """
        self.update_prev_state()
        self.state.primary = primary
        if sub is not None:
            self.state.sub = sub

        # PRINT STATEMENTS FOR DEBUGGING
        # self.state_history += ('    ' + str(self.state) + ' for [ ' + self.line.replace('\n', ' ]\n'))

    def update_prev_state(self):
        """
        "Archive" the current state as the prev_state when the update occurs.
        """
        if not self.prev_state:
            self.prev_state = State()

        self.prev_state.primary = self.state.primary
        self.prev_state.sub = self.state.sub

    ###################################################################################################################
    # Parser Functions

    def parse_contract(self, line):
        """
        Parse the contract line of the design recipe to extract the function signature.
        :param line: CONTRACT line in the design recipe.
        """
        line = self.get_design_recipe_line_content_only(line)
        line_tokens = line.replace(':', '').split()

        if line_tokens[-2] != '->':
            loc = -1 * (len(line_tokens[-1]) + len(line_tokens[-2])) + len('CONTRACT | ') + len(line)
            self.print_parse_error(self.line, loc,
                                   'CONTRACT must have an arrow (->) and a single return type.', True)
        else:
            func_name = line_tokens[0]
            return_type = line_tokens[-1]
            arg_types = line_tokens[1:-2]

            if self.curr_fx:
                self.validate_current_function_completion()
                self.functions.append(self.curr_fx)

            self.curr_fx = Function(func_name, arg_types, return_type)

    def parse_purpose(self, line):
        """
        Parse the purpose line of the design recipe to extract function argument names.
        :param line: PURPOSE line in the design recipe.
        """
        self.curr_fx.purpose = self.get_design_recipe_line_content_only(line)

        # any string of characters between ticks (`) are considered variable names.
        # alphanumeric chars, single quote or apostrophe ('), dash (-), underscore (_), and whitespaces are permitted.
        # examples: `Skater's Weight` --> Skaters_Weight
        #           `1st velocity of some_object 2` --> _1st_velocity_of_some_object_2
        names = re.findall(r"`[\w\s\-'_]+`", self.curr_fx.purpose)
        var_names = [self.convert_variable_name(n.strip('`')) for n in names]

        num_names = len(var_names)
        num_spots = len(self.curr_fx.args_names)

        ndx = 0

        # variable names are assigned to function args in the order they are presented.
        while ndx < num_names and ndx < num_spots:
            self.curr_fx.args_names[ndx] = var_names[ndx]
            ndx += 1

        # return value of the function can also be given a name.
        if ndx < num_names:
            self.curr_fx.return_name = var_names[ndx]

        # function args that were not designated any variable name will be given a generic name
        # based on their declared type (as given in the CONTRACT), i.e. float_val_1
        if ndx < num_spots:
            counter = 1
            while counter <= num_spots:
                self.curr_fx.args_names[ndx] = self.curr_fx.args_types[ndx] + '_val_' + str(counter)
                counter += 1

    def parse_in_outs(self, line):
        """
        Parse the in/outs (side effects) line of the design recipe to extract what kind of side effects are expected.
        :param line: IN/OUTS line in the design recipe.
        """
        line = self.get_design_recipe_line_content_only(line)
        ndx = 0

        try:
            ndx = line.index('/')
        except ValueError:
            self.print_parse_error(line, line.index(' ') if ' ' in line else 0,
                                   'Slash (/) token is expected in IN/OUTS.')

        comment_ndx = line.index('#') if '#' in line else len(line)

        # look into the comment on side effects to see if file or console I/O is expected.
        # just simple keyword detection ... instruct students to use these keywords.
        if '#' in line:
            comment = line[comment_ndx:].lower()
            if 'console' in comment or 'command' in comment or 'terminal' in comment:
                self.curr_fx.in_outs_source.append('console')
            if 'file' in comment or 'drive' in comment or 'disk' in comment or 'filesystem' in comment:
                self.curr_fx.in_outs_source.append('file')

        inz = line[:ndx].lower().strip()
        if inz in self.recognized_primitives:
            self.curr_fx.ins = locate(inz)
        elif inz != 'none':
            self.print_parse_error(line, len(inz) // 2, 'Unrecognized input type ' + '\'' + inz + '\'.')

        outz = line[ndx + 1:comment_ndx].lower().strip()
        if outz in self.recognized_primitives:
            self.curr_fx.outs = locate(outz)
        elif outz != 'none':
            self.print_parse_error(line, ndx + (len(outz) // 2), 'Unrecognized output type ' + '\'' + outz + '\'.')

    def parse_example(self, line):
        """
        Parse the example line of the design recipe to extract unit test information.
        :param line: EXAMPLE line in the design recipe.
        :return:
        """
        if not self.curr_fx:
            self.print_parse_error(self.line, 0,
                                   'Invalid syntax has caused function object to not populate (check your outline).',
                                   True)

        line = self.get_design_recipe_line_content_only(line)

        # 'n/a' signals no applicable (trivially unit-testable) examples could be given.
        if line.lower() != 'n/a':
            explanation = None

            # comment at the end of the line serves as the explanation for the example
            if '#' in line:
                comment_ndx = line.index('#')
                explanation = line[comment_ndx:]
                line = line[:comment_ndx].strip()

            line_tokens = line.split()
            if '->' not in line_tokens:
                self.print_parse_error(line, len(line), 'Arrow (->) is expected in EXAMPLE.')
            else:
                arrow_ndx = line.index('->')
                args_portion = line[:arrow_ndx].strip()
                return_portion = line[arrow_ndx:].replace('->', '').strip()

                example = Example(self.curr_fx, self.recognized_primitives)
                example.expl = explanation

                return_portions = self.separate_example_portions(return_portion, is_return_portion=True)
                self.add_rtrn_to_example(example, return_portion, return_portions)

                arg_portions = self.separate_example_portions(args_portion)

                offset = len('EXAMPLES | ')
                for ndx, arg_val in enumerate(arg_portions):
                    if arg_val:
                        offset += len(arg_val)
                        try:
                            self.add_arg_to_example(arg_val, example, ndx, offset)
                        except IndexError:
                            self.print_parse_error(self.line, offset,
                                                   'Too many argument values - ignoring \'{}\'.'.format(arg_val))
                    else:
                        self.print_parse_error(self.line, offset,
                                               'Expected {:d} value(s), but only got {:d} value(s).'
                                               .format(len(self.curr_fx.args_types), ndx))

                self.curr_fx.examples.append(example)

    def add_arg_to_example(self, arg_val, example, ndx, offset):
        result = example.add_arg(arg_val)
        if not result:
            cast_type = self.curr_fx.args_types[ndx]
            self.print_parse_error(self.line, offset,
                                   'Casting \'{}\' to {}type \'{}\' failed; defaulting to None.'
                                   .format(arg_val,
                                           'unsupported ' if cast_type not in self.recognized_primitives else '',
                                           cast_type))
            example.add_arg('None')

    def add_rtrn_to_example(self, example, return_portion, return_portions):
        result = example.add_rtrn(return_portions[0])
        if not result:
            cast_type = self.curr_fx.return_type
            self.print_parse_error(self.line, len(self.line) - len(return_portion[0]) - 1,
                                   'Casting \'{}\' to {}type \'{}\' failed; defaulting to None.'
                                   .format(return_portions[0],
                                           'unsupported ' if cast_type not in self.recognized_primitives else '',
                                           cast_type))
            example.add_rtrn('None')

    def parse_body_outline(self, line):
        """
        Add the body outline (any comment lines outside of the design recipe) to a list tied to the function.
        :param line: line to parse.
        """
        if not self.curr_fx:
            self.print_function_object_unpopulated_error(self.line)

        line_stripped = line.strip()
        if line_stripped and line_stripped[0] == '#':
            level = self.determine_body_outline_level(line)
            self.curr_fx.body_outlines.append((line_stripped, level))

    ###################################################################################################################
    # Helper Functions

    def determine_body_outline_level(self, line):
        hash_index = line.index('#')
        return round(hash_index / self.indent_size)

    def separate_example_portions(self, portion, is_return_portion=False):
        if not self.curr_fx:
            self.print_function_object_unpopulated_error(self.line)

        portion = portion.strip().replace(',', ' ')
        args_strs = [None] if is_return_portion else [None] * len(self.curr_fx.args_types)

        token_match_close_open = {']': '[', ')': '(', '}': '{'}
        token_match_open_close = {'[': ']', '(': ')', '{': '}'}

        ndx = 0
        prev = ' '
        part_str = ''
        token_stack = []
        in_string = False

        loc = 0  # declared early to avoid UnboundLocalError when dealing with unclosed brackets
        for loc, char in enumerate(portion, start=len('EXAMPLES | ')):
            if char == '"' and not token_stack:
                # manually detect literal string start and end
                if in_string:
                    in_string = False
                elif not prev or prev == ' ':
                    in_string = True

                if part_str:
                    self.add_arg_str(args_strs, ndx, part_str, loc + len('EXAMPLES | '))
                    part_str = ''
                    ndx += 1
            elif in_string and char != '"':
                # when in string, add everything but the double quote
                part_str += char
            elif not in_string:
                # start of a next token
                if char == ' ' and prev != ' ':
                    # first encounter of space since the last non-space encounter
                    if token_stack:
                        # stack has something (inside of a structure)
                        part_str += ','
                    elif prev != '"':
                        # assume it's the end of the structure unless prev == '"'
                        # stack is empty (not inside of a structure)
                        self.add_arg_str(args_strs, ndx, part_str, loc + len('EXAMPLES | '))
                        part_str = ''
                        ndx += 1

                # manual bracket matching using the stack
                elif char in ['[', '(', '{']:
                    part_str += char
                    token_stack.append(char)
                elif char in [']', ')', '}']:
                    expected_other_end = token_match_close_open[char]
                    try:
                        actual_other_end = token_stack.pop()
                        if actual_other_end != expected_other_end:
                            self.print_parse_error(self.line, loc,
                                                   'Unmatched brackets; was expecting \'{}\' but found \'{}\'.'
                                                   .format(expected_other_end, actual_other_end))
                        part_str += char
                    except IndexError:
                        self.print_parse_error(self.line, loc,
                                               'Unmatched brackets; \'{}\' is not matched with any open \'{}\'.'
                                               .format(char, expected_other_end))
                elif char != ' ':
                    part_str += char

            prev = char

        if in_string:
            part_str += '"'
            self.print_parse_error(self.line, loc,
                                   'Unclosed quote \'"\' found; DRCOP is placing \'"\' at the end.')

        while token_stack:
            unclosed = token_stack.pop()
            part_str += token_match_open_close[unclosed]
            self.print_parse_error(self.line, loc,
                                   'Unclosed bracket \'{}\' found; DRCOP is placing \'{}\' at the end.'
                                   .format(unclosed, token_match_open_close[unclosed]))

        if ndx < len(args_strs):
            args_strs[ndx] = part_str

        return args_strs

    def add_arg_str(self, args_strs, ndx, part_str, loc=0):
        try:
            args_strs[ndx] = part_str
        except IndexError:
            self.print_parse_error(self.line, loc,
                                   'Unexpected value (possibly due to unmatched brackets) - ignoring \'{}\'.'
                                   .format(part_str))

    def validate_current_function_completion(self):
        if not self.curr_fx:
            self.print_parse_error(self.line, 0,
                                   'Invalid syntax caused function object to not populate correctly (check your outline).',
                                   True)
        else:
            is_complete, reasons = self.curr_fx.validate_completion()
            if not is_complete:
                msg = 'Function \'{}\' is incomplete'.format(self.curr_fx.name) + \
                      ' (missing {})'.format(', '.join(reasons)) if reasons else ''
                self.print_parse_error(self.prev_line, 0, msg, line_number_offset=-1)

        # PRINT STATEMENT FOR DEBUGGING
        # else:
        #     print(str(self.curr_fx))

    def get_design_recipe_line_content_only(self, line):
        line = line.strip()
        ndx = 0

        try:
            ndx = line.index('|')
        except ValueError:
            self.print_parse_error(line, line.index(' ') if ' ' in line else 0,
                                   'Pipe (|) token is expected at the design recipe header.')

        return line[ndx + 1:].strip()

    def convert_variable_name(self, natural_name):
        var_name = ''
        if not (natural_name[0] == '_' or natural_name[0].isalpha()):
            var_name += '_'

        var_name += re.sub(r'[^\w\d_]', '_', natural_name.replace('\'', ''))
        return var_name

    def print_function_object_unpopulated_error(self, line, loc=0):
        self.print_parse_error(line, loc,
                               'Invalid syntax caused function object to not populate (check your outline).', True)

    def print_parse_error(self, line, loc, msg, is_critical=False, line_number_offset=0):
        try:
            prefix = 'PARSE ERROR'
            critical = 'CRITICAL'
            ignorable = 'Ignorable'

            severity = critical if is_critical else ignorable

            content = line.replace('\n', '')
            spaces = (' ' * loc)
            location = ('\u2500' * loc)

            # shorten the line output if it's getting too long
            column_length_limit = 80  # TODO: Uhh ... refactor later
            if len(content) > column_length_limit:
                condense_to = len(content) - column_length_limit
                content = '... ' + content[condense_to:]
                location = '\u2500\u2500\u2500\u2500' + location[condense_to:]
                spaces += '    '

            header_start = '\u250C\u2500 {} {} at line {:d}:\n\u2502\n'.format(
                severity, prefix, self.line_num if self.line_num else 0 + line_number_offset
            )

            message = '\u2502  {}\n\u2502\n'.format(msg)
            content = '\u2502    {}\n'.format(content)

            arrow = '\u2502    {}\u25B2\n'.format(spaces)
            location = '\u2514\u2500\u2500\u2500\u2500{}{}\n'.format(location, '\u2518')

            print('\n' + header_start + message + content + arrow + location, file=sys.stderr)

            sys.stderr.flush()
        except:
            self.print_parse_error(
                line if line else '(unable to reproduce the line being processed)', loc if loc else 1,
                'An unexpected error has occurred while attempting to report a PARSE ERROR.', is_critical=True
            )

        if is_critical:
            exit(1)
