#!/usr/bin/env python
import os
import shutil
import zipfile

class ZipCompression():
    def __init__(self, path):
        self.path = path

    def compress(self, delete_source=False):
        zf = zipfile.ZipFile("%s.zip" % self.path, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(self.path)
        for dirname, subdirs, files in os.walk(self.path):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
        zf.close()
        if delete_source:
            shutil.rmtree(self.path)

    def zipDirectory(self, path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))