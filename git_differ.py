from git import Repo
from os.path import isfile

from .utils import get_brg_ci_homedir_path

CI_HOMEDIR = get_brg_ci_homedir_path()
COMMIT_FILE = CI_HOMEDIR + 'latest_commit.data'

def get_latest_commit():
    with open(COMMIT_FILE, 'r') as fp:
        sha = fp.readline()
        if sha.endswith('/n'):
            sha = sha[:-len('/n')]
        return sha

def get_all_source_urls(recipes_path):
    """ Traverse bioconda/recipes and extract the tupple (Name, Source_Url)
        from all packages.
        """
    print("Fetching packages Name and Source...")
    packages = []
    num_of_packages = 0
    num_of_skipped = 0
    if isfile(COMMIT_FILE):
        latest_commit = get_latest_commit()
        head_commit = git.Repo(recipes_path+'/..').head.commit
        diff = hcommit.diff(latest_commit)
        dirs = [ item.a_path.split('/')[1] for item in diff] 
    else:
    _, dirs, _ = next(os.walk(recipes_path))
    for dir in dirs:
        num_of_packages += 1
        # Skip Bioconductor or R packages
        if "bioconductor" in dir or dir.startswith("r-"):
            num_of_skipped += 1
            continue
        meta_yaml_path = "%s/%s/meta.yaml" % (recipes_path, dir)
        try:
            if not os.path.isfile(meta_yaml_path):
                continue
            current_recipe = recipe.Recipe.from_file(recipes_path, meta_yaml_path)
            name = current_recipe.name
            try:
                url = current_recipe.get("source/url")
                if(type(url) is not str):
                    url=url[0]
            except:
                print("%s raised an Error" % name)
                continue
            packages.append(Package(name, url))
        except:
            print("%s raised an Error" % dir)
    print("%d out of %d packages where skipped" % (num_of_skipped, num_of_packages))
    return packages
