import os
import pdb
from .. import directories
from ..preprocess.init_data_class import initDataClass


__all__ = []

path_ant = os.getcwd()
os.chdir(directories.path_impress)
from impress.preprocessor0 import M

initDataClass(M)
M.data.init_datas()
M.data.init_dicts()

os.chdir(path_ant)
from ..preprocess.prep0 import Preprocess0
Preprocess0(M)
