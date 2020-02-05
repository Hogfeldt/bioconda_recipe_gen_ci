# bioconda_recipe_gen_ci
CI tools for managing the repository: https://github.com/Hogfeldt/bioconda_recipe_gen

This repo contains multiple scripts that together makes up our testing pipeline.
The flow is: 
1) git_differ 
2) cmake_filter 
3) br_build_filter
4) Two different ways to run the tests
    * command_builder and then brg_buildtest (uses from-args flag)
    * depedency_tester (uses from-files flag)

If you don't need a the pipeline to run as a cron job, but just need to run it
a single time (where you know the packages you will run on) you only need br_build_filter
and depedency_tester. How this works is described in next section. 

# Main scripts and how to use them
## br_build_filter.py

This script takes one required argument and two optional arguments:
- (Required) Path to the `bioconda-recipe/recipes` folder.
- (Optional) Path to a yaml file of the following format:
```
sha: <sha for file>
packages:
    <pkg_name_1>: <url_to_download_source_code>
    <pkg_name_2>: <url_to_download_source_code>
    <pkg_name_3>: <url_to_download_source_code>
    ...
```
- (Optional) Path to where the output file should be placed

The output file has the same format as the input yaml file, 
but does only contain the packages that can be built with bioconda-utils.

## dependency_tester.py
This script takes two arguments:
- (Required) Path to the `bioconda-recipe/recipes` folder
- (Optional) Path to the output file from running `br_build_filter.py`

This script runs `bioconda-recipe-gen` on all the packages in the input file.
The output is saved in a folder called `test_result` that will be created in 
the current working directory.

## General info about the two scrips
If you don't give the optional flags, the program will load/save in a folder, 
that it creates, called .bri_ci. This is used for when running all scripts 
together as a pipeline.

Since the 'full' pipeline was designed to only work if the previous step has
changed, you will need to manually make sure that the SHA in each file gets changed
(just remove it) if you want to run on the same input twice. Otherwise, the script will
just output that it found no changes to process.

# Other scripts
The other scripts doesn't allow for the optional flags. They assume they are being
run after each other (in the order described earlier).
Here is a short description of the scrips:
- git_differ: is used to see if there are any new packages on bioconda-recipes that
needs to be built
- cmake_filter: takes the output from git_differ as input and returns a list 
of packages that make use of cmake. (Note: we don't have a python_filter yet, but
that would be a good PR)
- command_builder: first part in the alternative to dependency_tester. Creates a list
of commands that can be used as input to brg_buildtest
- brg_buildtest: does the same as dependecy_parser, but takes another input

