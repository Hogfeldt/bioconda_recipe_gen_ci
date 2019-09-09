import argparse
import os
from bioconda_utils import recipe
from copy import deepcopy
from shutil import copy2
import subprocess
from bioconda_recipe_gen import build


def write_candidates_to_file(candidates, bioconda_recipes_path):
    """ For every candidate extract name, version, source_url, test-commands and
        test files from recipe and construct a bioconda-recipe-gen command.
        Write the commands to a file.
        """
    with open("bioconda_recipe_gen_commands.txt", "w") as cmd_file:
        for cand in candidates:
            recipes_path = bioconda_recipes_path + "/recipes"
            meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, cand[0])
            current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)

            cmd = "bioconda-recipe-gen %s -n %s2 -v %s -u %s" % (
                bioconda_recipes_path,
                current_recipe.name,
                current_recipe.version,
                current_recipe.get("source/url"),
            )

            # add test commmands
            try:
                test_commands = " --test-commands "
                for test_cmd in current_recipe.get("test/commands"):
                    test_commands += '"%s" ' % test_cmd
                cmd += test_commands
            except KeyError as e:
                print(e)

            # add path to test files
            try:
                test_files = " --test-files "
                for test_file in current_recipe.get("test/files"):
                    test_files += "\"%s\" " % test_file 
                cmd += test_files
            except KeyError as e:
                print(e)

            # write to file
            cmd_file.write(cmd + "\n")


def mini_sanity_check(recipes_path, name):
    bioconda_recipe_path = "/".join(recipes_path.split("/")[:-1])
    proc = build.bioconda_utils_build(name, bioconda_recipe_path)
    if proc.returncode == 0:
        return True
    else:
        return False


def increment_build_number(recipes_path, cand_name):
    meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, cand_name)
    current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)
    build_number = current_recipe.get("build/number")
    current_recipe.set("build/number", int(build_number) + 1)
    current_recipe.save()


def filter_candidates(candidates, recipes_path):
    """ From the list of candidates run 'bioconda-utils build' with the recipe
         from bioconda/recipes.
         return a list of candidates that builded succesfully
         """
    filtered_candidates = []
    for cand in candidates:
        increment_build_number(recipes_path, cand[0])
        result = mini_sanity_check(recipes_path, cand[0])
        if result:
            filtered_candidates.append(cand)

    return filtered_candidates


def get_packages_containing_cmakelist_in_root(candidates):
    """ From a list of (Name, Source_urls), download and unpack source, then
        check if root of file tree contains a CMakeList.txt.
        Return list of tupple (Name, Source_urls).
        """
    return []


def get_all_source_urls(recipes_path):
    """ Traverse bioconda/recipes and extract the tupple (Name, Source_Url)
        from all packages.
        """
    print("Fetching packages Name and Source...")
    packages = []
    num_of_packages = 0
    num_of_skipped = 0
    for subdir, dirs, files in os.walk(recipes_path):
        for dir in dirs:
            num_of_packages += 1
            # Skip Bioconductor or R packages
            if "bioconductor" in dir or dir.startswith("r-"):
                num_of_skipped += 1
                continue
            meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, dir)
            # print(meta_yaml_path)
            try:
                if not os.path.isfile(meta_yaml_path):
                    continue
                current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)
                name = current_recipe.name
                try:
                    url = current_recipe.get("source/url")
                except:
                    print("%s raised an Error" % name)
                    continue
                packages += (name, url)
            except:
                print("%s raised an Error" % dir)
    print("%d out of %d packages where skipped" % (num_of_skipped, num_of_packages))
    return packages


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Script for finding a set of bioconda packages, which are build with CMake and where the bioconda recipe is able to build itself"
    )
    parser.add_argument("recipes_path", help="Path to bioconda-recipes/recipes folder")
    args = parser.parse_args()

    # Run workflow
    recipes_path = args.recipes_path
    packages = get_all_source_urls(recipes_path)
    candidates = get_packages_containing_cmakelist_in_root(packages)
    # candidates = filter_candidates(candidates)
    # write_candidates_to_file(candidates, "file_path")


if __name__ == "__main__":
    main()
