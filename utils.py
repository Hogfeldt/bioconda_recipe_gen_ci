from os.path import expanduser, isdir
from os import mkdir

def get_brg_ci_homedir_path():
    HOMEDIR = expanduser('~')
    CI_HOMEDIR = HOMEDIR + '/.brg_ci'
    if isdir(CI_HOMEDIR):
        return CI_HOMEDIR
    else:
        mkdir(CI_HOMEDIR)
        return CI_HOMEDIR
