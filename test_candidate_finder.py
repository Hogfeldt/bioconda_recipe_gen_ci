import argparse
import os
from bioconda_utils import recipe

# TODO: remove this or refactor to other test folder
def test_write_candidates_to_file():
     test_candicates = [("kallisto", None), ("tn93", None)]
     write_candidates_to_file(test_candicates, "../bioconda_recipe_gen/bioconda-recipes")


def write_candidates_to_file(candidates, bioconda_recipes_path):
    """ For every candidate extract name, version, source_url, test-commands and
        test files from recipe and construct a bioconda-recipe-gen command.
        Write the commands to a file.
        """
    for cand in candidates:
        recipes_path = bioconda_recipes_path + "/recipes"
        meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, cand[0])
        current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)

        cmd = "bioconda-recipe-gen %s -n %s -v %s -u %s" % (bioconda_recipes_path, current_recipe.name, current_recipe.version, current_recipe.get("source/url"))

        # add test commmands
        try:
            test_commands = " --test-commands "
            for test_cmd in current_recipe.get("test/commands"):
                test_commands += test_cmd + " "
            cmd += test_commands
        except KeyError as e:
            print(e)

        print(cmd)

def filter_candidates(candidates):
    """ From the list of candidates run 'bioconda-utils build' with the recipe
        from bioconda/recipes.
        return a list of candidates that builded succesfully
        """
    return []


def get_packages_containing_cmakelist_in_root(candidates):
    """ From a list of (Name, Source_urls), download and unpack source, then i
        check if root of file tree contains a CMakeList.txt.
        Return list of tupple (Name, Source_urls).
        """
    return []


def get_all_source_urls(recipes_path):
    """ Traverse bioconda/recipes and extract the tupple (Name, Source_Url)
        from all packages.
        """
    packages = []
    for subdir, dirs, files in os.walk(recipes_path):
        for dir in dirs:
            meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, dir)
            print(meta_yaml_path)
            if not os.path.isfile(meta_yaml_path):
                continue
            current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)
            name = current_recipe.name
            try:
                url = current_recipe.get('source/url')
            except:
                print('%s raised an Error' % name)
                continue

            packages += (name, url)
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
    for package in packages:
        print(package)
    candidates = get_packages_containing_cmakelist_in_root(packages)
    candidates = filter_candidates(candidates)
    write_candidates_to_file(candidates, "file_path")
    pass


if __name__ == "__main__":
    #main()
    test_write_candidates_to_file()
