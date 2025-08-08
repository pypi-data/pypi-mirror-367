from gitevo import GitEvo, ParsedCommit


evo = GitEvo(report_title='Python', report_filename='rich', 
             repo='../projects/python/rich', extension='.py', 
             date_unit='year', from_year=2020)

@evo.metric('Python files', show_version_chart=False)
def files(commit: ParsedCommit):
    return len(commit.parsed_files)

@evo.metric('LOC', show_version_chart=False)
def files(commit: ParsedCommit):
    return commit.loc

@evo.metric('dataclass total', group='dataclass vs. namedtuple (total)')
def dataclass(commit: ParsedCommit):
    return _dataclass_count(commit)

@evo.metric('namedtuple total', group='dataclass vs. namedtuple (total)')
def namedtuple(commit: ParsedCommit):
    return _namedtuple_count(commit)

@evo.metric('dataclass', group='dataclass vs. namedtuple')
def dataclass(commit: ParsedCommit):
    dataclass_count = _dataclass_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(dataclass_count, total)

@evo.metric('namedtuple', group='dataclass vs. namedtuple')
def namedtuple(commit: ParsedCommit):
    namedtuple_count = _namedtuple_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(namedtuple_count, total)

def _dataclass_count(commit: ParsedCommit):
    return _count_imports(commit, 'dataclasses', 'dataclass')

def _namedtuple_count(commit: ParsedCommit):
    collections_namedtuple_count = _count_imports(commit, 'collections', 'namedtuple')
    typing_namedtuple_count = _count_imports(commit, 'typing', 'NamedTuple')
    return collections_namedtuple_count + typing_namedtuple_count

def _count_imports(commit: ParsedCommit, module_name: str, entity_name: str):
    import_from_statements = commit.find_nodes_by_type(['import_from_statement'])
    import_modules = [each for each in import_from_statements if as_str(each.child_by_field_name('module_name').text) == module_name]
    return len([imp for imp in import_modules for name in imp.children_by_field_name('name') if as_str(name.text) == entity_name])

@evo.metric('list total', group='list vs. tuple (total)')
def data_structures(commit: ParsedCommit):
    return commit.count_nodes(['list'])

@evo.metric('tuple total', group='list vs. tuple (total)')
def data_structures(commit: ParsedCommit):
    return commit.count_nodes(['tuple'])

@evo.metric('list', group='list vs. tuple')
def data_structures(commit: ParsedCommit):
    list_count = commit.count_nodes(['list'])
    total = commit.loc / KLOC_FACTOR
    return ratio(list_count, total)

@evo.metric('tuple', group='list vs. tuple')
def data_structures(commit: ParsedCommit):
    tuple_count = commit.count_nodes(['tuple'])
    total = commit.loc / KLOC_FACTOR
    return ratio(tuple_count, total)

@evo.metric('list comprehension total', group='list comprehension vs. generator expression (total)')
def data_structures(commit: ParsedCommit):
    return commit.count_nodes(['list_comprehension'])

@evo.metric('generator expression total', group='list comprehension vs. generator expression (total)')
def data_structures(commit: ParsedCommit):
    return commit.count_nodes(['generator_expression'])

@evo.metric('list comprehension', group='list comprehension vs. generator expression')
def data_structures(commit: ParsedCommit):
    list_comp_count = commit.count_nodes(['list_comprehension'])
    total = commit.loc / KLOC_FACTOR
    return ratio(list_comp_count, total)

@evo.metric('generator expression', group='list comprehension vs. generator expression')
def data_structures(commit: ParsedCommit):
    gen_exp_count = commit.count_nodes(['generator_expression'])
    total = commit.loc / KLOC_FACTOR
    return ratio(gen_exp_count, total)

@evo.metric('__str__ total', group='__str__ vs. __repr__ (total)')
def str(commit: ParsedCommit):
    return _str_count(commit)

@evo.metric('__repr__ total', group='__str__ vs. __repr__ (total)')
def rep(commit: ParsedCommit):
    return _repr_count(commit)

@evo.metric('__str__', group='__str__ vs. __repr__')
def str(commit: ParsedCommit):
    str_count = _str_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(str_count, total)

@evo.metric('__repr__', group='__str__ vs. __repr__')
def repr(commit: ParsedCommit):
    repr_count = _repr_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(repr_count, total)

def _str_count(commit: ParsedCommit):
    return len([name for name in _method_names(commit) if name == '__str__'])

def _repr_count(commit: ParsedCommit):
    return len([name for name in _method_names(commit) if name == '__repr__'])

def _method_names(commit: ParsedCommit):
    class_definitions = commit.find_nodes_by_type(['class_definition'])
    return [as_str(each.child_by_field_name('name').text) for cd in class_definitions 
            for each in cd.child_by_field_name('body').children if each.type == 'function_definition']

@evo.metric('__getattr__ total', group='__getattr__ vs. __getattribute__ (total)')
def imports(commit: ParsedCommit):
    return _getattr_count(commit)

@evo.metric('__getattribute__ total', group='__getattr__ vs. __getattribute__ (total)')
def imports(commit: ParsedCommit):
    return _getattr_count(commit)

@evo.metric('__getattr__', group='__getattr__ vs. __getattribute__')
def imports(commit: ParsedCommit):
    getattr_count = _getattr_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(getattr_count, total)

@evo.metric('__getattribute__', group='__getattr__ vs. __getattribute__')
def imports(commit: ParsedCommit):
    getattribute_count = _getattribute_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(getattribute_count, total)

def _getattr_count(commit: ParsedCommit):
    return len([name for name in _method_names(commit) if name == '__getattr__'])

def _getattribute_count(commit: ParsedCommit):
    return len([name for name in _method_names(commit) if name == '__getattribute__'])
    
@evo.metric('@classmethod total', group='@classmethod vs. @staticmethod (total)')
def definitions(commit: ParsedCommit):
    return _classmethod_count(commit)

@evo.metric('@staticmethod total', group='@classmethod vs. @staticmethod (total)')
def definitions(commit: ParsedCommit):
    return _staticmethod_count(commit)

@evo.metric('@classmethod', group='@classmethod vs. @staticmethod')
def definitions(commit: ParsedCommit):
    classmethod_count = _classmethod_count(commit)
    staticmethod_count = _staticmethod_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(classmethod_count, total)

@evo.metric('@staticmethod', group='@classmethod vs. @staticmethod')
def definitions(commit: ParsedCommit):
    classmethod_count = _classmethod_count(commit)
    staticmethod_count = _staticmethod_count(commit)
    total = commit.loc / KLOC_FACTOR
    return ratio(staticmethod_count, total)

def _classmethod_count(commit: ParsedCommit):
    return len([df for df in _decorated_functions(commit) if as_str(df.child(0).text).startswith('@classmethod')])

def _staticmethod_count(commit: ParsedCommit):
    return len([df for df in _decorated_functions(commit) if as_str(df.child(0).text).startswith('@staticmethod')])

def _decorated_functions(commit: ParsedCommit):
    decorated_definitions = commit.find_nodes_by_type(['decorated_definition'])
    return [dd for dd in decorated_definitions if dd.child_by_field_name('definition').type == 'function_definition']

@evo.metric('import total', group='import vs. import from (total)')
def data_structures(commit: ParsedCommit):
    return commit.count_nodes(['import_statement'])

@evo.metric('import from total', group='import vs. import from (total)')
def data_structures(commit: ParsedCommit):
    return commit.count_nodes(['import_from_statement'])

@evo.metric('import', group='import vs. import from')
def imports(commit: ParsedCommit):
    import_count = commit.count_nodes(['import_statement'])
    total = commit.loc / KLOC_FACTOR
    return ratio(import_count, total)

@evo.metric('import from', group='import vs. import from')
def imports(commit: ParsedCommit):
    import_from_count = commit.count_nodes(['import_from_statement'])
    total = commit.loc / KLOC_FACTOR
    return ratio(import_from_count, total)

KLOC_FACTOR = 1000

def as_str(text: bytes) -> str:
    return text.decode('utf-8')

def ratio(a: int, b: int) -> int:
    if b == 0:
        return 0
    return round(a/b, 3)

evo.run()