import re
import os
from gen_test_file import *
import sys
import subprocess

"""
1 - 30 min
2 - 28 min
3 - 30 min
4 - 30 min
5 - 40 min
6 - 15 min (finished case_recog_gen_fn)
7 - 17 min
(so far 3:10)
8 - 45 min
9 - 30 min
"""

def check(condition):
    assert condition

def list_find(l, element):
    for i, a in enumerate(l):
        if a == element:
            return i
    return -1



TOKEN_REGEX = {
    "int": r'^\d+$',
    "float": r'^\d+\.\d*?$',
    "string": r'^({})$'.format("('.*'|" + '".*")'),
    "variable": r'^[A-Z]+$',
    "image_path": r'',
    "video_path": r'',
    "pdf_path": r''
}
VAR_TOKEN_TYPES = ['int', 'float', 'string', 'variable']
PATH = os.path.dirname(os.path.abspath(__file__))
CORE_COMPILER_PATH = os.path.join(PATH, "templates/compiler_core.py")

# test file tags
NEW_TAG = '########### NEW TEST CASE SET ###########'
INPUT_TAG =  '########### INPUT ###########'
OUTPUT_TAG =  '########### OUTPUT ###########'
TAGS = [NEW_TAG, INPUT_TAG, OUTPUT_TAG]
BLOCK = '\n'.join([NEW_TAG, INPUT_TAG, '', OUTPUT_TAG, '', ''])


def file_to_string(filename):
    with open(filename) as f:
        return str(f.read())

def string_to_file(text, file_name):
    target = open(file_name, 'w')
    target.write(text)
    target.close()

def get_command_output(cmd):
    try:
        import subprocess
        # Can't handle piped commands
        output = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).communicate()[0]
        return output.decode("utf-8")
    except Exception as ex:
        print('Error', ex)


def get_file_paths_recursively(directory):
    result = []
    for paths, subdirs, files in os.walk(directory):
        for file in files:
            #print(name, paths)
            pure_path = os.path.join(paths, file)
            result.append(pure_path)
    return result
    
def load_test_file(file_path):
    with open(file_path) as f:
        text = str(f.read())
    test_case_sets = text.split(NEW_TAG + '\n')

    # ignore blanks
    test_case_sets = [a for a in test_case_sets if a]

    x = []
    y = []
    for test_case_set in test_case_sets:
        test_cases_texts = test_case_set.split(INPUT_TAG + '\n')
        test_cases_texts = [a for a in test_cases_texts if a]
        test_cases_x = []
        test_cases_y = []
        for test_case_text in test_cases_texts:
            input, output = test_case_text.split(OUTPUT_TAG + '\n')
            input = input[:-1]
            output = output[:-2]
            test_cases_x.append(input)
            test_cases_y.append(output)
        x.append('\n'.join(test_cases_x))
        y.append('\n'.join(test_cases_y))
        
    return x, y

def gen_blocked_code(prefix, condition, code_block):
    header_line = '{}{}:'.format(prefix, condition)
    new_code_block = '\n'.join(['    ' + line for line in code_block.split('\n')])
    return header_line + '\n' + new_code_block

"""
def gen_if_code(condition, code_block):
    return gen_blocked_code('if ', condition, code_block)

def gen_elif_code(condition, code_block):
    return gen_blocked_code('elif ', condition, code_block)

def gen_else_code(code_block):
    return gen_blocked_code('else', '', code_block)
"""

        
def gen_if_elif_block_code(conditions, code_blocks):
    check(len(conditions) == len(code_blocks))
    if_blocks = []
    for i in range(len(conditions)):
        condition = conditions[i]
        code_block = code_blocks[i]
        if i == 0:
            prefix = 'if '
        else:
            prefix = 'elif '
        if_blocks.append(gen_blocked_code(prefix, condition, code_block))
    return '\n'.join(if_blocks)
    
    
def gen_switch_code(var_name, var_values, code_blocks):
    conditions = ['{} == {}'.format(var_name, var_value) for var_value in var_values]
    return gen_if_elif_block_code(conditions, code_blocks)
    
def gen_fn_code(fn_name, arg_str, code_block):
    return gen_blocked_code('def {}({})'.format(fn_name, arg_str), '', code_block)
    
def gen_if_main_code(code_block):
    return gen_blocked_code('if ', '__name__ == "__main__"', code_block)

def tokenize(text):
    return re.split(' +', text)
     
def recognize_type(token):
    if any([re.match(TOKEN_REGEX[var_type], token) for var_type in VAR_TOKEN_TYPES]):
        return "variable"
    else:
        return "constant"
        
def multi_find(l, match_values): # not pythonic or efficient
    # assumption: any element of values is not contained in another element
    # in values
    result = []
    for i in range(len(l)):
        for val in match_values:
            if l[i:i+len(val)] == val:
                result.append(i)
                break
    return result

def re_findall(pattern, text):
    results = re.finditer(pattern, text)
    return [obj.span()[0] for obj in results]

    


def gen_features(x_set_tokens, x_set_types):
    # iterator which yields features that can be used by the x_set
    
    def length_feature_generator(token_len):
        def length_feature(tokens, types):
            return len(tokens) == token_len
        as_text = 'lambda tokens, types: len(tokens) == {}'.format(token_len)
        return length_feature, as_text
        
    def constant_match_feature_generator(ix, constant):
        def constant_match_feature(tokens, types):
            return types[ix] == 'constant' and tokens[ix] == constant
        as_text = 'lambda tokens, types: types[{}] == "constant" and tokens[{}] == {}'.format(ix, ix, constant)
        return constant_match_feature, as_text
    
    for x_example_tokens in x_set_tokens:
        # length
        yield length_feature_generator(len(x_example_tokens))
        # match a constant
        for i in range(1, len(x_example_tokens)):
            yield constant_match_feature_generator(i, constant)
    

def case_recog_gen_fn(x_set_tokens, x_set_types): 
    """
    :x_set_tokens: list of list of strings
    :x_set_types: list of list of strings
    """
    x_set_tokens, x_set_types = list(x_set_tokens), list(x_set_types)
    feature_code = []
    conditions = []

    for i in range(len(x_set_tokens)):
        ix_to_pop = -1
        for feature_fn, feature_fn_text in gen_features(x_set_tokens, x_set_types):
            feature_values = []
            for x_example_tokens, x_example_types in zip(x_set_tokens, x_set_types):
                feature_values.append(feature_fn(x_example_tokens, x_example_types))
            n_true = feature_values.count(True)
            check(n_true > 0)
            if n_true == 1: # choose this feature_fn as it uniquely distinguishes a remaining case
                ix_to_pop = list_find(feature_values, True)
                
                # ** MORE?

                
                feature_text = 'feature{} = {}'.format(ix_to_pop, feature_fn_text)
                feature_code.append(feature_text)
                conditions.append('feature{}(tokens, types)'.format(ix_to_pop))
                break
        
        check(ix_to_pop >= 0)
        
        def result_fn(code_blocks):
            other_code = gen_if_elif_block_code(conditions, code_blocks)
            return '\n'.join(feature_code) + '\n' + other_code
        
        return result_fn

class CompilerCodeGenerator:
    def __init__(self, path='compilers/default_compiler_path.py'):
        self.code = None
        self.path = path
    
    def fit(self, x, y):
        """
        :x: list of strings (example inputs)
        :y: list of strings (corresponding outputs)
        """
        imports = ['import re']
        global_variables = ['# global variables']
        cmds = []
        cmd_blocks = []
        code_suffix = file_to_string(CORE_COMPILER_PATH)
    
        for x_set, y_set in zip(x, y):  # each test case
            # tokenize and annotate input
            x_set_tokens = [tokenize(test_case) for test_case in x_set.split('\n')]
            x_set_types = [[recognize_type(token) for token in test_case] for test_case in x_set_tokens]

            # make sure the x has a consistent command
            cmd = x_set_tokens[0][0]
            for x_example in x_set_tokens:
                check(x_example[0] == cmd)
            cmds.append(cmd)

            # format y set

            if len(x_set_tokens) == 1:
                y_set = [y_set]
            else:
                y_set = y_set.split('\n')

            case_blocks = []
            for x_example_tokens, y_example in zip(x_set_tokens, y_set):
                # get list of variables
                var_names = []
                var_indices = []
                for test_case, test_case_types in zip(x_set_tokens, x_set_types):
                    for i, (token, type) in enumerate(zip(test_case, test_case_types)):
                        if type == "variable":
                            var_names.append(token)
                            var_indices.append(i)
                var_indices_dict = dict([(var_name, var_index) for var_name, var_index in zip(var_names, var_indices)])
                
                # solving the input-output mapping problem
                # find variables in output
                var_output_matches = []
                for i in range(len(var_names)):
                    match_indices = re_findall(var_names[i], y_example)
                    for ix in match_indices:
                        var_output_matches.append((ix, var_indices[i]))
                var_output_matches = list(sorted(var_output_matches))
                var_ordered_wrt_output = [a[1] for a in var_output_matches]
                # we now have the list of variable indices of the input token array
                # in the order that they occur in the output
                
                # build code
                comment = '# example: ' + ' '.join(x_example_tokens)
                var_code = []
                output_code = ['output = (']
                for var_name, var_ix in zip(var_names, var_indices):
                    var_code.append('var{} = tokens[{}]'.format(var_ix, var_ix))
                
                all_var_pattern = r'({})'.format('|'.join(var_names))
                output_split_by_var = re.split(all_var_pattern, y_example)

                # get rid of delimiter caused by using () syntax
                output_split_by_var = [a for i, a in enumerate(output_split_by_var) if i % 2 == 0]

                for i, output_chunk in enumerate(output_split_by_var):
                    output_code.append('"{}"'.format(output_chunk.replace('\n', '\\n')))
                    if i < len(output_split_by_var) - 1:  # add variable use
                        output_code.append(' + var{} +\n'.format(var_ordered_wrt_output[i]) + ' ' * 10)
                output_code.append(')')
                
                case_block = comment + '\n' + '\n'.join(var_code) + '\n' + '\n'.join(output_code)
                case_blocks.append(case_block)

            gen_case_block_fn = case_recog_gen_fn(x_set_tokens, x_set_types)
            cmd_block = gen_case_block_fn(case_blocks)
            
            cmd_blocks.append(cmd_block)

        cmd_strings = ['"{}"'.format(c) for c in cmds]
        translate_fn_contents = ('output = ""\ntokens = re.split(" +", input.strip())\ntypes = None\ncmd = tokens[0]\n' +
                                 gen_switch_code('cmd', cmd_strings, cmd_blocks) + '\nreturn output')
        translate_fn_code = gen_fn_code('translate', 'input', translate_fn_contents)
        
        code = imports + global_variables + [translate_fn_code, code_suffix]
        self.code = '\n'.join(code)

        self.save()

    def save(self):
        string_to_file(self.code, self.path)
    
    def transform(self, input):
        check(self.code is not None)
        string_to_file(input, 'temp')

        #cat_process = subprocess.Popen(['cat', 'temp'], stdout=subprocess.PIPE)
        #python_process = subprocess.Popen(['python', '"{}"'.format(self.path)], stdin=cat_process.stdout,
        #                                  stdout=subprocess.PIPE)
        #cat_process.stdout.close()  # Allow ps_process to receive a SIGPIPE if grep_process exits.
        #result = python_process.communicate()[0]

        result = get_command_output('python "{}" temp'.format(self.path))

        return result


def main():
    #test_folder_path = sys.argv[1]
    #test_file_paths = get_file_paths_recursively(test_folder_path)
    test_file_path = sys.argv[1]
    compiler_path = sys.argv[2]

    gen = CompilerCodeGenerator(compiler_path)

    #for test_file_path in test_file_paths:
    x, y = load_test_file(test_file_path)
    gen.fit(x, y)

    print('done creating the compiler')
    print('now testing inputs with expected outputs')

    n_success = 0
    for test_x, test_y in zip(x, y):
        output = gen.transform(test_x)
        if test_y.strip() == output.strip():
            n_success += 1
        else:
            print('Failed Equality Between Prediction\n{}\nAND Expected Ouput\n{}'.format(output, test_y))
    print(n_success, 'of', len(x), 'were successful')
    
    #print(gen_code.split('\n'))
    
    
if __name__ == "__main__":
    main()