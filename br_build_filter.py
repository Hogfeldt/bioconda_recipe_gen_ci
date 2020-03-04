import argparse
import os
import signal
import subprocess

from bioconda_utils import recipe
from os.path import join

from packagedb import PackageDBResource
from utils import get_brg_ci_homedir_path
#from bioconda_recipe_gen import build


CI_HOMEDIR = get_brg_ci_homedir_path()
CMAKE_PACKAGES_DB_PATH = CI_HOMEDIR + "/cmake_packages.yaml"
BR_BUILD_FILTERED_PACKAGES_DB_PATH = CI_HOMEDIR + "/br_build_filtered.yaml"


def bioconda_utils_build(package_name, bioconda_recipe_path):
    """ Build a bioconda package with bioconda-utils and return the standard output. """
    wd = os.getcwd()
    os.chdir(bioconda_recipe_path)
    cmd = [
        "bioconda-utils",
        "build",
        "recipes/",
        "config.yml",
        "--packages",
        package_name,
    ]
    proc = subprocess.Popen(cmd, encoding="utf-8", stdout=subprocess.PIPE)
    try:
        proc.communicate(timeout=3600)
    except subprocess.TimeoutExpired:
        print("ERROR: REACHED TIMEOUT")
        proc.kill()

    os.chdir(wd)
    return proc


def mini_sanity_check(recipes_path, name):
    bioconda_recipe_path = "/".join(recipes_path.split("/")[:-1])
    proc = bioconda_utils_build(name, bioconda_recipe_path)
    if proc.returncode == 0:
        print("Package builded successfully")
        return True
    else:
        print("Package did not build")
        return False


def increment_build_number(recipes_path, cand_name):
    meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, cand_name)
    current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)
    build_number = current_recipe.get("build/number")
    current_recipe.set("build/number", int(build_number) + 1)
    current_recipe.save()


def filter_candidates(recipes_path):
    """ From the list of candidates run 'bioconda-utils build' with the recipe
         from bioconda/recipes.
         return a list of candidates that builded succesfully
    """
    with PackageDBResource(CMAKE_PACKAGES_DB_PATH) as packageDB:
        candidates = packageDB.get_new_packages()

    if candidates is None:
        print("No new packages to filter")
        return

    with open(join(recipes_path, "../build-fail-blacklist")) as fp:
        blacklisted = set(map(lambda l:l[len('recipes/'):], filter(lambda l:l != "", [l.replace('\n','').strip() for l in fp.readlines() if not l.startswith("#")])))

    with PackageDBResource(BR_BUILD_FILTERED_PACKAGES_DB_PATH) as packageDB:
        for cand_name in candidates.keys():
            if cand_name in blacklisted:
                continue
            try:
                print("Trying to build:", cand_name)
                increment_build_number(recipes_path, cand_name)
                result = mini_sanity_check(recipes_path, cand_name)
            except Exception as e:
                print("Error when running mini_sanity_check on {}. Getting the following error: {}".format(cand_name, e))
                continue
            if result:
                packageDB.write_single_package_to_file(cand_name, candidates.get(cand_name))


def main():
    parser = argparse.ArgumentParser(
        description="The br-build-filter module takes a path to the Bioconda-recipe recipes folder and create a list of packages from cmake_packages.yaml and writes, all the packages that could build with bioconda-utils build, into the file packages_to_be_tested.yaml"
    )
    parser.add_argument(
        "recipes_path",
        help="The path to the bioconda-recipe/recipes directory"
    )
    parser.add_argument(
        "--input",
        help="Path to a yaml file with packages to filter"
    )
    parser.add_argument(
        "--output",
        help="Path where the output yaml file should be placed"
    )
    args = parser.parse_args()

    if args.input is not None:
        global CMAKE_PACKAGES_DB_PATH
        CMAKE_PACKAGES_DB_PATH = args.input
    if args.output is not None:
        global BR_BUILD_FILTERED_PACKAGES_DB_PATH
        BR_BUILD_FILTERED_PACKAGES_DB_PATH = args.output

    filter_candidates(args.recipes_path)


if __name__ == "__main__":
    main()

