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

    def __init__(self, indentation_size):
        """
        Mostly class member declarations and initializations.
        """

        # indentation size to use when parsing the body outline
        self.indent_size = indentation_size

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
            loc = -1 * (len(line_tokens[-1]) + len(line_tokens[-2]))
            self.print_parse_error(line, loc, 'Arrow (->) is expected in CONTRACT')
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
                                   'Slash (/) token is expected in IN/OUTS')

        comment_ndx = line.index('#') if '#' in line else len(line)

        # look into the comment on side effects to see if file or console I/O is expected.
        # just simple keyword detection ... instruct students to use these keywords.
        if '#' in line:
            comment = line[comment_ndx:].lower()
            if 'console' in comment or 'command' in comment or 'terminal' in comment:
                self.curr_fx.in_outs_source.append('console')
            if 'file' in comment or 'drive' in comment or 'disk' in comment or 'filesystem' in comment:
                self.curr_fx.in_outs_source.append('file')

        # currently only supporting Python primitives and 'None' for side effect types
        recognized_types = ['int', 'float', 'complex', 'str', 'chr', 'bool']

        inz = line[:ndx].lower().strip()
        if inz in recognized_types:
            self.curr_fx.ins = locate(inz)
        elif inz != 'none':
            self.print_parse_error(line, len(inz) // 2, 'Unrecognized input type ' + '\'' + inz + '\'')

        outz = line[ndx + 1:comment_ndx].lower().strip()
        if outz in recognized_types:
            self.curr_fx.outs = locate(outz)
        elif outz != 'none':
            self.print_parse_error(line, ndx + (len(outz) // 2), 'Unrecognized output type ' + '\'' + outz + '\'')

    def parse_example(self, line):
        """
        Parse the example line of the design recipe to extract unit test information.
        :param line: EXAMPLE line in the design recipe.
        :return:
        """
        if not self.curr_fx:
            self.print_parse_error(self.line, 0,
                                   'Invalid syntax has caused function object to not populate', True)

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
                self.print_parse_error(line, len(line), 'Arrow (->) is expected in EXAMPLE')
            else:
                arrow_ndx = line.index('->')
                args_portion = line[:arrow_ndx].strip()
                return_portion = line[arrow_ndx:].replace('->', '').strip().strip('"').strip("'")

                example = Example(self.curr_fx)
                example.add_rtrn(return_portion)
                example.expl = explanation

                offset = 0
                for arg_val in args_portion.split():
                    offset += len(arg_val) + 1

                    try:
                        result = example.add_arg(arg_val)
                        if not result:
                            self.print_parse_error(line, offset,
                                                   'Argument value \'{}\' was not accepted.'.format(arg_val))
                    except IndexError:
                        self.print_parse_error(line, offset, 'Too many argument values - ignoring ' + str(arg_val))

                self.curr_fx.examples.append(example)

    def parse_body_outline(self, line):
        """
        Add the body outline (any comment lines outside of the design recipe) to a list tied to the function.
        :param line: line to parse.
        """
        if not self.curr_fx:
            self.print_parse_error(self.line, 0,
                                   'Invalid syntax has caused function object to not populate\n' +
                                   '            |     You might be trying to convert a non-functions file with DRCOP.\n' +
                                   '            |     DRCOP does not yet support conversion of a non-funtion file.',
                                   True)

        line_stripped = line.strip()
        if line_stripped and line_stripped[0] == '#':
            level = self.determine_body_outline_level(line)
            self.curr_fx.body_outlines.append((line_stripped, level))

    ###################################################################################################################
    # Helper Functions

    def determine_body_outline_level(self, line):
        hash_index = line.index('#')
        return round(hash_index / self.indent_size)

    def validate_current_function_completion(self):
        if not self.curr_fx:
            self.print_parse_error(self.line, 0,
                                   'Invalid syntax caused function object to not populate correctly.', True)
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

    def print_parse_error(self, line, loc, msg, is_critical=False, line_number_offset=0):
        prefix = 'PARSE ERROR'
        critical = 'CRITICAL :('
        ignorable = '(ignorable)'

        message = prefix + ' | At line ' + str(self.line_num + line_number_offset) + ' -- ' + msg + '\n'
        content = (critical if is_critical else ignorable) + ' | ' + line.replace('\n', '') + '\n'
        location = (' ' * len(prefix) + ' | ') + (' ' * loc) + '^\n'

        print('\n' + message + content + location, file=sys.stderr)
        sys.stderr.flush()

        if is_critical:
            exit(1)
