from gitevo import GitEvo, ParsedCommit

remote = 'https://github.com/mockito/mockito'
# remote = 'https://github.com/apache/dubbo'
# remote = 'https://github.com/google/guava'
# remote = 'https://github.com/spring-projects/spring-boot'

evo = GitEvo(repo=remote, extension='.java')

@evo.metric('Lines of code (LOC)', show_version_chart=False)
def files(commit: ParsedCommit):
    return commit.loc

@evo.metric('Java files', show_version_chart=False)
def files(commit: ParsedCommit):
    return len(commit.parsed_files)

@evo.metric('LOC / Java files', show_version_chart=False)
def files(commit: ParsedCommit):
    parsed_files = len(commit.parsed_files)
    if parsed_files == 0: return 0
    return commit.loc / parsed_files

@evo.metric('production file', show_version_chart=False, group='Production and test files')
def production_files(commit: ParsedCommit):
    return len([file for file in commit.parsed_files if 'test' not in file.name])

@evo.metric('test file', show_version_chart=False, group='Production and test files')
def test_files(commit: ParsedCommit):
    return len([file for file in commit.parsed_files if 'test' in file.name])

@evo.metric('Classes, interfaces, and records', categorical=True)
def type_definitions(commit: ParsedCommit):
    return commit.find_node_types(['class_declaration', 'interface_declaration', 'record_declaration'])

@evo.metric('Methods', show_version_chart=False)
def type_definitions(commit: ParsedCommit):
    return commit.count_nodes(['method_declaration'])

@evo.metric('Median method LOC', show_version_chart=False)
def functions(commit: ParsedCommit):
    return commit.loc_by_type('method_declaration', 'median')

@evo.metric('Conditionals', categorical=True)
def conditionals(commit: ParsedCommit):
    return commit.find_node_types(['if_statement', 'switch_expression', 'ternary_expression'])

@evo.metric('Switches', categorical=True, show_version_chart=False)
def conditionals(commit: ParsedCommit):
    return commit.find_node_types(['switch_block_statement_group', 'switch_rule'])

@evo.metric('Loops', categorical=True)
def loops(commit: ParsedCommit):
    return commit.find_node_types(['for_statement', 'while_statement', 'enhanced_for_statement', 'do_statement'])

@evo.metric('Exception statements', categorical=True)
def expections(commit: ParsedCommit):
    return commit.find_node_types(['try_statement', 'throw_statement'])

@evo.metric('Comments', categorical=True)
def comments(commit: ParsedCommit):
    return commit.find_node_types(['block_comment', 'line_comment'])

def as_str(text: bytes) -> str:
    return text.decode('utf-8')

evo.run()