import argparse
from bioconda_utils import recipe
from os.path import join

from packagedb import PackageDBResource
from utils import get_brg_ci_homedir_path
from bioconda_recipe_gen import build


CI_HOMEDIR = get_brg_ci_homedir_path()
#CMAKE_PACKAGES_DB_PATH = CI_HOMEDIR + "/small_python_cands.yaml"
CMAKE_PACKAGES_DB_PATH = CI_HOMEDIR + "/cmake_packages.yaml" # TODO: more general name
BR_BUILD_FILTERED_PACKAGES_DB_PATH = CI_HOMEDIR + "/br_build_filtered.yaml"


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


def filter_candidates(recipes_path):
    """ From the list of candidates run 'bioconda-utils build' with the recipe
         from bioconda/recipes.
         return a list of candidates that builded succesfully
    """
    with PackageDBResource(CMAKE_PACKAGES_DB_PATH) as packageDB:
        candidates = packageDB.get_new_packages()

    if candidates == None:
        print("No new packages to filter")
        return

    with open(join(recipes_path, "../build-fail-blacklist")) as fp:
        blacklisted = set(map(lambda l:l[len('recipes/'):], filter(lambda l:l != "", [l.replace('\n','').strip() for l in fp.readlines() if not l.startswith("#")])))

    filtered_candidates = {} 
    for cand_name in candidates.keys():
        if cand_name in blacklisted:
            continue
        increment_build_number(recipes_path, cand_name)
        result = mini_sanity_check(recipes_path, cand_name)
        if result:
            filtered_candidates[cand_name] = candidates.get(cand_name)

    with PackageDBResource(BR_BUILD_FILTERED_PACKAGES_DB_PATH) as packageDB:
        packageDB.add_new_packages(filtered_candidates)


def main():
    parser = argparse.ArgumentParser(
        description="The br-build-filter module takes a path to the Bioconda-recipe recipes folder and create a list of packages from cmake_packages.yaml and writes, all the packages that could build with bioconda-utils build, into the file packages_to_be_tested.yaml" 
    )
    parser.add_argument(
        "recipes_path",
        help="The path to the bioconda-recipe/recipes directory"
    )
    args = parser.parse_args()
    filter_candidates(args.recipes_path)


if __name__ == "__main__":
    main()

