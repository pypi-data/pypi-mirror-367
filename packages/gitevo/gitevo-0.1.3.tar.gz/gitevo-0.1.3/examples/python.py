from gitevo import GitEvo, ParsedCommit


remote = 'https://github.com/pallets/flask'
# remote = 'https://github.com/fastapi/fastapi'
# remote = 'https://github.com/django/django'
# remote = 'https://github.com/pytest-dev/pytest'
# remote = 'https://github.com/pandas-dev/pandas'
# remote = 'https://github.com/pytorch/pytorch'
# remote = 'https://github.com/numpy/numpy'

evo = GitEvo(repo=remote, extension='.py')

@evo.metric('Lines of code (LOC)', show_version_chart=False)
def loc(commit: ParsedCommit):
    return commit.loc

@evo.metric('Python files', show_version_chart=False)
def files(commit: ParsedCommit):
    return len(commit.parsed_files)

@evo.metric('LOC / Python files', show_version_chart=False)
def loc_per_file(commit: ParsedCommit):
    parsed_files = len(commit.parsed_files)
    if parsed_files == 0: return 0
    return commit.loc / parsed_files

@evo.metric('production file', show_version_chart=False, group='Production and test files')
def production_files(commit: ParsedCommit):
    return len([file for file in commit.parsed_files if 'test' not in file.name])

@evo.metric('test file', show_version_chart=False, group='Production and test files')
def test_files(commit: ParsedCommit):
    return len([file for file in commit.parsed_files if 'test' in file.name])

@evo.metric('Data structures', categorical=True)
def data_structures(commit: ParsedCommit):
    return commit.find_node_types(['dictionary', 'list', 'set', 'tuple'])

@evo.metric('Functions and classes', categorical=True)
def definitions(commit: ParsedCommit):
    return commit.find_node_types(['class_definition', 'function_definition'])

@evo.metric('class', group='LOC of functions and classes (mean)')
def class_loc(commit: ParsedCommit):
    return commit.loc_by_type('class_definition', 'mean')

@evo.metric('function', group='LOC of functions and classes (mean)')
def function_loc(commit: ParsedCommit):
    return commit.loc_by_type('function_definition', 'mean')

@evo.metric('Functions: def vs. async def', categorical=True)
def sync_async(commit: ParsedCommit):
    function_definitions = commit.find_nodes_by_type(['function_definition'])
    return ['async def' if as_str(func.child(0).text) == 'async' else 'def' for func in function_definitions]

@evo.metric('Function parameters', categorical=True, version_chart_type='hbar', top_n=5)
def parameter_types(commit: ParsedCommit):
    function_definitions = commit.find_nodes_by_type(['function_definition'])
    func_def_parameters = [func.child_by_field_name('parameters') for func in function_definitions if func.child_by_field_name('parameters')]
    return [named_param.type for parameters in func_def_parameters for named_param in commit.named_children_for(parameters)]

@evo.metric('Function return type', categorical=True)
def return_types(commit: ParsedCommit):
    function_definitions = commit.find_nodes_by_type(['function_definition'])
    return ['yes' if func.child_by_field_name('return_type') else 'no' for func in function_definitions]

@evo.metric('Functions: return vs. yield', categorical=True)
def return_yield(commit: ParsedCommit):
    return commit.find_node_types(['return_statement', 'yield'])

@evo.metric('@dataclass', show_version_chart=False)
def definitions(commit: ParsedCommit):
    decorated_definitions = commit.find_nodes_by_type(['decorated_definition'])
    decorated_classes = [decorated_definition for decorated_definition in decorated_definitions if decorated_definition.child_by_field_name('definition').type == 'class_definition']
    dataclasses = [decorated_class for decorated_class in decorated_classes if as_str(decorated_class.child(0).text).startswith('@dataclass')]
    return len(dataclasses)

@evo.metric('Control flows', categorical=True)
def control_flow(commit: ParsedCommit):
    return commit.find_node_types(['for_statement', 'while_statement', 'if_statement', 'try_statement', 'match_statement', 'with_statement'])

@evo.metric('Conditionals', categorical=True)
def conditionals(commit: ParsedCommit):
    return commit.find_node_types(['if_statement', 'conditional_expression'])

@evo.metric('Comprehensions', categorical=True)
def comprehensions(commit: ParsedCommit):
    return commit.find_node_types(['dictionary_comprehension', 'list_comprehension', 'set_comprehension'])

@evo.metric('Loops', categorical=True)
def for_while(commit: ParsedCommit):
    return commit.find_node_types(['for_statement', 'while_statement', 'for_in_clause'])

@evo.metric('Exception statements', categorical=True)
def exceptions(commit: ParsedCommit):
    return commit.find_node_types(['try_statement', 'raise_statement'])

@evo.metric('Import statements', categorical=True)
def imports(commit: ParsedCommit):
    return commit.find_node_types(['import_statement', 'import_from_statement', 'future_import_statement'])

def as_str(text: bytes) -> str:
    return text.decode('utf-8')
    
evo.run()
