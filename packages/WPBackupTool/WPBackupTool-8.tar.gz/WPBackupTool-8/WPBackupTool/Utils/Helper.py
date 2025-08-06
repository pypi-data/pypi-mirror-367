import ctypes
import datetime
import errno
import os
import platform
import shutil

from WPBackupTool.Utils.Logger import Logger

def get_value_from_dict_path(dict, path, default_value=None):
    value = dict
    try:
        for path_part in path:
            value = value[path_part]
        if value is not None:
            return value
    except:
        return default_value

def getFreeSpaceMb(dirname):
    """Return folder/drive free space (in megabytes)."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize / 1024 / 1024

def getDirectorySize(dirname):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dirname):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def getAvgChildDirSize(path):
    child_dirs = os.listdir(path)
    size = 0
    for dir in child_dirs:
        dir_size = getDirectorySize(os.path.join(path, dir))
        size = size + dir_size

    if len(child_dirs) == 0:
        return 0

    return size/len(child_dirs)

def deleteMoveOldestBackup(path):
    backups = os.listdir(path)
    first_backup = None
    lowest_date = None
    for backup in backups:
        parts = backup.split("_")
        time = parts[len(parts)-1]

        date = datetime.datetime.strptime(time, '%Y-%m-%d')

        if(lowest_date is None or lowest_date > date):
            lowest_date = date
            first_backup = backup

    if first_backup is not None:
        Logger.log("deleting/moving: "+first_backup)
        path_to_delete = os.path.join(path, first_backup)
        #delete or move oldest backup
        shutil.rmtree(path_to_delete, ignore_errors=True)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise