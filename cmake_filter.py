import urllib.request
import os
import tempfile
import tarfile
import zipfile

from packagedb import PackageDBResource
from utils import get_brg_ci_homedir_path

CI_HOMEDIR = get_brg_ci_homedir_path()
PACKAGE_CHANGED_DB_PATH = CI_HOMEDIR + "/packages_changed.yaml"
PACKAGES_FILTERED_ON_CMAKE = CI_HOMEDIR + "/cmake_packages.yaml"

def download_and_unpack_source(src, dir_path):
    """ Download a source file and unpack it """
    try:
        # .tar.gz
        if src.lower().endswith(".tar.gz"):
            urllib.request.urlretrieve(src, "%s/source.tar.gz" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with tarfile.open("%s/source.tar.gz" % dir_path, "r:gz") as tar_ref:
                tar_ref.extractall("%s/source" % dir_path)
        # .tar.bz2
        elif src.lower().endswith(".tar.bz2"):
            urllib.request.urlretrieve(src, "%s/source.tar.bz2" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with tarfile.open("%s/source.tar.bz2" % dir_path, "r:bz2") as tar_ref:
                tar_ref.extractall("%s/source" % dir_path)
        # .tgz
        elif src.lower().endswith(".tgz"):
            urllib.request.urlretrieve(src, "%s/source.tgz" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with tarfile.open("%s/source.tgz" % dir_path, "r:gz") as tar_ref:
                tar_ref.extractall("%s/source" % dir_path)
        # .zip
        elif src.lower().endswith(".zip"):
            urllib.request.urlretrieve(src, "%s/source.zip" % dir_path)
            os.mkdir("%s/source" % dir_path)
            with zipfile.ZipFile("%s/source.zip" % dir_path, "r") as zip_ref:
                zip_ref.extractall("%s/source" % dir_path)
        else:
            print("Unknown fileformat! Cannot unpack %s" % src)
    except urllib.error.HTTPError as e:
        print('HTTP error code: ', e.code)
        print(src)
    except urllib.error.URLError as e:
        print('URL error Reason: ', e.reason)
        print(src)
    except tarfile.ReadError:
        print('Tarfile ReadError')
        print(src)
    except:
        print("Unexpected error:", sys.exc_info()[0])

def filter_out_packages_without_cmakelist():
    """ From a list of (Name, Source_urls), download and unpack source, then
        check if root of file tree contains a CMakeList.txt.
        Return list of tupple (Name, Source_urls).
        """
    packages_to_filter = dict()
    filtere_packages = dict()
    with PackageDBResource(PACKAGE_CHANGED_DB_PATH) as packageDB:
        packages_to_filter = packageDB.get_new_packages()
        if packages_to_filter is None:
            return
    print(packages_to_filter)
    for name, source in packages_to_filter.items():
        with tempfile.TemporaryDirectory() as tmpdir:
            download_and_unpack_source(source, tmpdir)
            if os.path.isdir(tmpdir+'/source'):
                _, dirs, _ = next(os.walk(tmpdir+'/source'))
                _, _, files = next(os.walk(tmpdir+'/source/' + dirs[0]))
                for file in list(map(lambda s: s.lower(), files)):
                    if "cmakelists.txt" in file:
                        filtere_packages.update({name : source})
    with PackageDBResource(PACKAGES_FILTERED_ON_CMAKE) as packageDB:
        packageDB.add_new_packages(filtere_packages)
    print(filtere_packages)


if __name__ == '__main__':
    filter_out_packages_without_cmakelist()
