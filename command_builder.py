import os
import argparse
from bioconda_utils import recipe

from packagedb import PackageDBResource
from utils import get_brg_ci_homedir_path
from bioconda_recipe_gen import build


CI_HOMEDIR = get_brg_ci_homedir_path()
BR_BUILD_FILTERED_PACKAGES_DB_PATH = CI_HOMEDIR + "/br_build_filtered.yaml"
PACKAGE_COMMANDS_DB_PATH = CI_HOMEDIR + "/package_commands.txt"


def make_flag_with_arg_list(flag_name, list_of_args):
    flag = " --%s " % flag_name
    for arg in list_of_args: 
        flag += '"%s" ' % arg
    return flag 


def write_candidates_to_file(recipes_path):
    """ For every candidate extract name, version, source_url, test-commands and
        test files from recipe and construct a bioconda-recipe-gen command.
        Write the commands to a file.
    """

    with PackageDBResource(BR_BUILD_FILTERED_PACKAGES_DB_PATH) as packageDB:
        candidates = packageDB.get_new_packages()

    if candidates == None:
        print("No new packages to handle")
        return
    
    packages_and_commands = {}
    for cand_name in candidates.keys():
        bioconda_recipes_path = os.path.split(recipes_path)[0]
        meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, cand_name)
        current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)

        cmd = "bioconda-recipe-gen %s -n %s2 -v %s -u %s" % (
            bioconda_recipes_path,
            cand_name,
            current_recipe.version,
            current_recipe.get("source/url"),
        )
        
        # add test commmands
        try:
            cmd += make_flag_with_arg_list("test-commands", current_recipe.get("test/commands"))
        except KeyError as e:
            print(e)
        
        # add path to test files
        try:
            cmd += make_flag_with_arg_list("test-files", current_recipe.get("test/files"))
        except KeyError as e:
            print(e)

        packages_and_commands[cand_name] = cmd

    with PackageDBResource(PACKAGE_COMMANDS_DB_PATH) as packageDB:
        packageDB.add_new_packages(packages_and_commands)

def main():
    parser = argparse.ArgumentParser(
        description="The command_builder module takes a path to the Bioconda-recipe recipes folder and creates a file of commands, for each package in the file br_build_filtered.yaml"
    ) 
    parser.add_argument(
        "recipes_path",
        help="The path to the bioconda-recipe/recipes directory"
    )
    args = parser.parse_args()
    write_candidates_to_file(args.recipes_path)


if __name__ == "__main__":
    main()

