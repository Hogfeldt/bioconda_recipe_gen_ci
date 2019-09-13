import fcntl
from ruamel_yaml import YAML
import hashlib


class PackageDBResource:
    def __init__(self, DB_path):
        self.DB_path = DB_path

    def __enter__(self):
        class PackageDB:
            def __init__(self, DB_path):
                self._fp = open(DB_path, "r+")
                fcntl.lockf(self._fp, fcntl.LOCK_EX)
                self.__load_packages()

            def __load_packages(self):
                yaml_dict = YAML().load(self._fp)
                self._sha = yaml_dict["sha"]
                self._packages = dict(yaml_dict["packages"])

            def __calculate_sha(self):
                string_to_hash = ""
                for name, source in self._packages.items():
                    string_to_hash += name + source
                return hashlib.md5(string_to_hash.encode()).hexdigest()

            def __append_and_update(self, new_packages):
                for name in self._packages.keys() & new_packages.keys():
                    self._packages[name] = new_packages[name]
                for name in new_packages.keys() - self._packages.keys():
                    self._packages.update({name: new_packages[name]})

            def add_new_packages(self, new_packages):
                if self._sha == self.__calculate_sha():
                    self._packages = new_packages
                else:
                    self.__append_and_update(new_packages)

            def get_new_packages(self):
                if self._sha == self.__calculate_sha():
                    return None
                else:
                    self._sha = self.__calculate_sha()
                    return self._packages

            def __write_packageDB_to_file(self):
                self._fp.seek(0)
                self._fp.truncate()
                dict_to_write = {"sha": self._sha}
                dict_to_write.update({"packages": self._packages})
                YAML().dump(dict_to_write, self._fp)

            def _release_resources(self):
                self.__write_packageDB_to_file()
                fcntl.lockf(self._fp, fcntl.LOCK_UN)
                self._fp.close()

        self.packageDB_obj = PackageDB(self.DB_path)
        return self.packageDB_obj

    def __exit__(self, exc_type, exc_value, traceback):
        self.packageDB_obj._release_resources()
