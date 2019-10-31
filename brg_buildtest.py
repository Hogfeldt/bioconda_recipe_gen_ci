import subprocess
from datetime import datetime
from ruamel_yaml import YAML
from os.path import isfile, isdir
from os import mkdir
from shutil import copy2, rmtree

from utils import get_brg_ci_homedir_path
from packagedb import PackageDBResource

CI_HOMEDIR = get_brg_ci_homedir_path()
PACKAGE_COMMANDS_DB_PATH = CI_HOMEDIR + "/package_commands.txt"
GLOBAL_BUILD_RESULTS_PATH = CI_HOMEDIR + "/global_build_results.yaml"
BATCH_OUTPUTS_FOLDER = CI_HOMEDIR + "/batch_outputs"


def write_to_global_results(build_status_dict):
    if isfile(GLOBAL_BUILD_RESULTS_PATH):
        fp = open(GLOBAL_BUILD_RESULTS_PATH, "r+")
        yaml_dict = YAML().load(fp)
    else:
        fp = open(GLOBAL_BUILD_RESULTS_PATH, "w")
        yaml_dict = dict()

    for pkg_name, info_dict in build_status_dict.items():
        pkg_dict = yaml_dict.setdefault(pkg_name, {})
        buildtest_number = len(pkg_dict) + 1
        pkg_dict[buildtest_number] = info_dict

    fp.seek(0)
    YAML().dump(yaml_dict, fp)
    fp.truncate()
    fp.close()


def write_pkg_to_batch_outputs(pkg_name, date_str, output):
    if not isdir(BATCH_OUTPUTS_FOLDER):
        mkdir(BATCH_OUTPUTS_FOLDER)
    batch_folder = "%s/%s" % (BATCH_OUTPUTS_FOLDER, date_str)
    if not isdir(batch_folder):
        mkdir(batch_folder)
    pkg_path = "%s/%s" % (batch_folder, pkg_name)
    mkdir(pkg_path)

    recipe_path = "%s/meta.yaml" % pkg_name
    build_path = "%s/build.sh" % pkg_name
    output_path = "%s/stdout.txt" % pkg_path
    copy2(recipe_path, pkg_path)
    copy2(build_path, pkg_path)
    with open(output_path, "w") as out_file:
        out_file.write(output.decode("utf-8"))


def run_buildtest():
    with PackageDBResource(PACKAGE_COMMANDS_DB_PATH) as packageDB:
        candidates = packageDB.get_new_packages()

    if candidates is None:
        print("No new packages to build")
        return
    
    did_build_counter = 0
    current_datetime = datetime.now()
    date_str = "%s.%s.%s" % (current_datetime.day, current_datetime.month, current_datetime.year)
    build_status_dict = dict()
    for cand_name, cand_cmd in candidates.items():
        process = subprocess.Popen(cand_cmd, stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()

        if process.returncode == 0:
            did_build = True
            did_build_counter += 1
        else:
            did_build = False

        # TODO: add BRG og BR commit til global file
        build_status_dict[cand_name] = {"date": date_str, "builds": did_build}

        cand_name = cand_name + "2"
        write_pkg_to_batch_outputs(cand_name, date_str, output)
        rmtree(cand_name)

    write_to_global_results(build_status_dict)
    print("Could build %s/%s" % (did_build_counter, len(candidates)))

if __name__ == "__main__":
    run_buildtest()
