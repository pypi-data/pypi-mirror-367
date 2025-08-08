import pytest
import os

from datetime import date
from gitevo import GitEvo
from gitevo.exceptions import BadGitRepo, BadDateUnit, BadYearRange
from tests.conftest import remove_folder_if_exists

testrepo = 'https://github.com/andrehora/testrepo'

def test_invalid_repo():

    msg = 'Invalid repository'

    with pytest.raises(BadGitRepo) as e:
        GitEvo(repo='')
    assert str(e.value) == msg

    with pytest.raises(BadGitRepo) as e:
            GitEvo(repo=None)
    assert str(e.value) == msg

    with pytest.raises(BadGitRepo) as e:
        GitEvo(repo=[])
    assert str(e.value) == msg

    with pytest.raises(BadGitRepo) as e:
        GitEvo(repo=123)
    assert str(e.value) == msg

def test_invalid_dir():

    with pytest.raises(BadGitRepo) as e:
        GitEvo(repo='invalid_dir')
    assert str(e.value) == 'invalid_dir is not a directory'

def test_empty_dir():

    empty_dir = 'empty_dir'
    remove_folder_if_exists(empty_dir)
    if not os.path.exists(empty_dir):
        os.makedirs(empty_dir)

    with pytest.raises(BadGitRepo) as e:
        GitEvo(repo=empty_dir,)
    assert 'empty_dir is not a directory with git repositories' in str(e.value)

    remove_folder_if_exists(empty_dir)

def test_invalid_repo_list():

    with pytest.raises(BadGitRepo) as e:
        GitEvo(repo=['invalid_repo'])
    assert str(e.value) == 'Invalid repository'

def test_invalid_date_unit():

    with pytest.raises(BadDateUnit) as e:
        GitEvo(repo=testrepo, date_unit=None)
    assert str(e.value) == 'date_unit must be year or month'

    with pytest.raises(BadDateUnit) as e:
        GitEvo(repo=testrepo, date_unit='')
    assert str(e.value) == 'date_unit must be year or month'

    with pytest.raises(BadDateUnit) as e:
        GitEvo(repo=testrepo, date_unit='foo')
    assert str(e.value) == 'date_unit must be year or month'

def test_invalid_year_range():

    with pytest.raises(BadYearRange) as e:
        GitEvo(repo=testrepo, from_year=2010, to_year=2000)
    assert str(e.value) == 'from_year must be equal or smaller than to_year'

def test_valid_year_range():
    
    evo = GitEvo(repo=testrepo, from_year=2020, to_year=2025)
    assert evo.from_year == 2020
    assert evo.to_year == 2025

def test_default_year_range():
    
    evo = GitEvo(repo=testrepo)
    assert evo.from_year == date.today().year - 5
    assert evo.to_year == date.today().year