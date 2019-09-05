import argparse
import os
from bioconda_utils import recipe


def write_candidates_to_file(candidates, filepath):
    """ For every candidate extract name, version, source_url, test-commands and 
        test files from recipe and construct a bioconda-recipe-gen command.
        Write the commands to a file.
        """
    pass


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
    main()
