
import os
import shutil
import pytest

from git import Repo

@pytest.fixture(scope='module')
def local_repo():
    repo_folder = 'testrepo'
    remove_folder_if_exists(repo_folder)
    remove_report_if_exists()
    repo = Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path=repo_folder)
    yield repo_folder
    repo.close()
    remove_folder_if_exists(repo_folder)
    remove_report_if_exists()

@pytest.fixture
def clear_reports():
    remove_report_if_exists()
    yield
    remove_report_if_exists()

def remove_report_if_exists():
    remove_file_if_exists('report_testrepo.html')
    remove_file_if_exists('report_library.html')
    remove_file_if_exists('report_testrepo.csv')
    remove_file_if_exists('report_library.csv')

def remove_folder_if_exists(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name, onerror=onerror)

def remove_file_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)

def onerror(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise