import argparse
import os
import tempfile
import subprocess

from packagedb import PackageDBResource
from utils import get_brg_ci_homedir_path
from bioconda_recipe_gen.utils import copytree

CI_HOMEDIR = get_brg_ci_homedir_path()
BR_BUILD_FILTERED_PACKAGES_DB_PATH = os.path.join(CI_HOMEDIR, "br_build_filtered.yaml")


def run_test(recipes_path):

    with PackageDBResource(BR_BUILD_FILTERED_PACKAGES_DB_PATH) as packageDB:
        candidates = packageDB.get_new_packages()

    if candidates == None:
        print("No new packages to run test on")
        return

    os.mkdir("test_result")
    result_path = os.path.join(os.getcwd(), "test_result")

    with tempfile.TemporaryDirectory() as tmpdir:
        for cand_name in candidates.keys():
            recipe_path = os.path.join(recipes_path, cand_name)
            temp_recipe_path = os.path.join(tmpdir, cand_name)
            os.mkdir(temp_recipe_path)
            copytree(recipe_path, temp_recipe_path)
            recipe_path = temp_recipe_path

            meta_lines = []
            with open(os.path.join(recipe_path, "meta.yaml"), "r") as fp:
                meta_lines = fp.readlines()

            lines_to_write = []
            in_requirements_section = False
            for line in meta_lines:
                if "[osx]" in line:
                    continue
                if in_requirements_section:
                    if line[0].isspace():
                        continue
                    else:
                        in_requirements_section = False
                        lines_to_write.append(line)
                else:
                    if "requirements" in line:
                        in_requirements_section = True
                        continue
                    lines_to_write.append(line)

            with open(os.path.join(recipe_path, "meta.yaml"), "w") as fp:
                fp.writelines(lines_to_write)

            path_elements = []
            for e in recipes_path.split('/'):
                path_elements.append(e)
                if e == "bioconda-recipes":
                    break
            bioconda_recipes_path = '/'.join(path_elements)
            print(bioconda_recipes_path)

            brg_command = "yes | bioconda-recipe-gen %s from-files %s --strategy python3" % (
                bioconda_recipes_path,
                recipe_path,
            )
            process = subprocess.Popen(
                brg_command, stdout=subprocess.PIPE, shell=True, encoding="utf-8"
            )
            output, _ = process.communicate()

            os.mkdir(os.path.join(result_path, cand_name))
            copytree(recipe_path, os.path.join(result_path, cand_name))
            with open(os.path.join(result_path, cand_name, "stdout.txt"), "w") as fp:
                fp.write(output)
            with open(os.path.join(result_path, "global_result.txt"), "a+") as fp:
                if process.returncode == 0:
                    fp.write("%s: %s\n" % (cand_name, "Builds"))
                else:
                    fp.write("%s: %s\n" % (cand_name, "Do not build"))


def main():
    parser = argparse.ArgumentParser(
        description="The purpose of this test is to get a measurment on how good BRG is to find dependencies. The method will be to use the build.sh from bioconda-recipe and then give a meta.yaml where we remove the requirements"
    )
    parser.add_argument(
        "recipes_path",
        help="The path to the bioconda-recipe/recipes directory"
    )
    parser.add_argument(
        "--input",
        help="Path to the output file from running `br_build_filter.py`"
    )
    args = parser.parse_args()

    if args.input is not None:
        global BR_BUILD_FILTERED_PACKAGES_DB_PATH
        BR_BUILD_FILTERED_PACKAGES_DB_PATH = args.input

    run_test(args.recipes_path)


if __name__ == "__main__":
    main()
