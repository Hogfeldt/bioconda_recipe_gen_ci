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

If you don't give the optional flags, the program will save it in a folder, 
that it creates, called .bri_ci. This is used for when running all scripts 
together as a pipeline.

The output file has the same format as the input yaml file, 
but does only contain the packages that can be built with bioconda-utils.

## dependency_tester.py
This script takes two arguments:
- (Required) Path to the `bioconda-recipe/recipes` folder
- (Optional) Path to the output file from running `br_build_filter.py`

Same thing applies here for the optional flag as above.

This script runs `bioconda-recipe-gen` on all the packages in the input file.
The output is saved in a folder called `test_result` that will be created in 
the current working directory.

# Other scripts
TODO


