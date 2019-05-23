#!/bin/bash

###############################################
# Cron wrapper for testing Bioconda-recipe-gen
###############################################

##### Constants

REPO=https://github.com/Hogfeldt/bioconda_recipe_gen.git
NAME=$(basename "$REPO" .git)
CONDA_DEPS="bioconda-utils docker-py"

# TODO:
# pull latest repository
git clone $REPO
cd "$NAME"
# setup environment
conda create --yes -n "$NAME" python=3.6 
conda config --add channels conda-forge
conda config --add channels bioconda
conda update --yes conda

source activate "$NAME"
conda install --yes "$CONDA_DEPS"

source deactivate
conda remove --yes -n "$NAME" --all                                       
# install software
# extract all cases from test script 
# run all cases and save the result of each case. 
# send mail with result
