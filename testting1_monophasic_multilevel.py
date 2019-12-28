# from packs.solvers.solvers_scipy.solver_sp import SolverSp
# from packs.running.run_simulation import RunSimulation
# # from packs.direct_solution.monophasic.monophasic1 import Monophasic
# from packs.direct_solution.biphasic.biphasic1 import Biphasic
# from packs.preprocess.preprocess1 import Preprocess1
import pdb
#
# rodar = RunSimulation(state=5)
# M = rodar.M
#
#
# prep1 = Preprocess1()
# prep1.set_saturation_regions(M)
#
# # m1 = Monophasic(M)
# m1 = Biphasic(M)
# m1.get_transmissibility_matrix_without_contours()
# m1.get_transmissibility_matrix()
# m1.get_RHS_term()
#
#
# solver = SolverSp()
# x = solver.direct_solver(m1.datas['T'], m1.datas['b'])
# m1.get_solution(x)
# m1.get_flux_faces_and_volumes()
#
# pdb.set_trace()
# M.data.update_variables_to_mesh()

#################################
##test Monophasic
# from packs.type_simulation.monophasic_tpfa import monophasicTpfa
# m1 = monophasicTpfa(M)
# m1.run()
# import pdb; pdb.set_trace()
#################################

#############################
# # test biphasic
# from packs.type_simulation.biphasic_simulation.biphasic_tpfa import biphasicTpfa
# import time
# b1 = biphasicTpfa(M, load=False)
# b1.run()
# b1.run()
# b1.update_flux_w_and_o_volumes()
# b1.update_delta_t()
# b1.update_saturation()
# b1.update_relative_permeability()
# b1.update_mobilities()
# b1.update_transmissibility()

# def r1():
#     b1.run()
#
# def r2():
#     r1()
#     b1.mesh.data.update_variables_to_mesh()
#     b1.mesh.core.print(file='test', extension='.vtk', config_input="input_cards/print_settings0.yml")
#
#
# def mostrar():
#     b1.mesh.data.update_variables_to_mesh()
#     b1.mesh.core.print(file='test', extension='.vtk', config_input="input_cards/print_settings0.yml")
#
# verif = True
# contador = 1
# while verif:
#     if contador % 2 == 0:
#         contador = 1
#         import pdb; pdb.set_trace()
#     r1()
#     contador += 1






# from packs.data_class.data_impress import Data
# from packs.data_class.elements_lv0 import ElementsLv0
# from packs.contours.wells import Wells
# from packs.convert_unit.conversion import Conversion

# import pdb; pdb.set_trace()

# def initial_mesh(load=False, convert=False):
#     from packs.load.preprocessor0 import M
#
#     elements_lv0 = ElementsLv0(M, load=load)
#     data_impress = Data(M, elements_lv0, load=load)
#     wells = Wells(M, load=load)
#     if convert:
#         conversion = Conversion(wells, data_impress)
#         conversion.convert_English_to_SI()
#
#     if not load:
#
#         wells.update_values_to_mesh()
#         wells.export_to_npz()
#         data_impress.update_variables_to_mesh()
#         data_impress.export_to_npz()
#
#     return M, elements_lv0, data_impress, wells

from packs.running.initial_mesh_properties import initial_mesh
from packs.pressure_solver.fine_scale_tpfa import FineScaleTpfaPressureSolver
from packs.directories import data_loaded
from packs.multiscale.operators.prolongation.AMS.ams_tpfa import AMSTpfa
from packs.multiscale.operators.prolongation.AMS.ams_mpfa import AMSMpfa
import scipy.sparse as sp
import numpy as np
import time

def get_gids_and_primal_id(gids, primal_ids):

    gids2 = np.unique(gids)
    primal_ids2 = []
    for i in gids2:
        primal_id = np.unique(primal_ids[gids==i])
        if len(primal_id) > 1:
            print('erro get_gids_and_primal_id')
            import pdb; pdb.set_trace()
        primal_ids2.append(primal_id[0])

    primal_ids2 = np.array(primal_ids2)

    return gids2, primal_ids2

def mostrar(i, data_impress, M, op1, rest1):
    l0 = np.concatenate(op1[:,i].toarray())
    el0 = np.concatenate(rest1[i].toarray())
    data_impress['verif_po'] = l0
    data_impress['verif_rest'] = el0
    data_impress.update_variables_to_mesh(['verif_po', 'verif_rest'])
    M.core.print(file='results/test_'+ str(n), extension='.vtk', config_input='input_cards/print_settings0.yml')

load = data_loaded['load_data']
convert = data_loaded['convert_english_to_SI']
n = data_loaded['n_test']

M, elements_lv0, data_impress, wells = initial_mesh(load=load, convert=convert)
#######################
tpfa_solver = FineScaleTpfaPressureSolver(data_impress, elements_lv0, wells)
tpfa_solver.get_transmissibility_matrix_without_boundary_conditions()
ml = M.multilevel_data
gids, primal_ids = get_gids_and_primal_id(elements_lv0['volumes'], data_impress['PRIMAL_CLASSIC_ID_1'])

ams_prolongation = AMSTpfa(ml['interns_level_1'],
                           ml['faces_level_1'],
                           ml['edges_level_1'],
                           ml['vertex_level_1'],
                           gids,
                           primal_ids,
                           load=False)

ams_prolongation.run(tpfa_solver['Tini'])
# data_impress.update_variables_to_mesh()

op1 = ams_prolongation['OP_AMS_1']
rest1 = ml['restriction_level_1']
cont = 0
# for i in range(4, op1.shape[1]):
#     mostrar(i, data_impress, M, op1, rest1)
#     import pdb; pdb.set_trace()

# import pdb; pdb.set_trace()

T_lv2 = tpfa_solver['Tini']*op1
T_lv2 = rest1*T_lv2
#################################

#######################

# from pymoab import types
# cvs = T_lv2.shape[0]
# for cv in range(cvs):
#
#     idd = sp.find(T_lv2[cv])
#     cols = idd[1]
#     idcv = cv
#
#     cv0 = M.core.mb.get_entities_by_type_and_tag(M.core.root_set, types.MBENTITYSET, np.array([ml.tags['PRIMAL_ID_1']]), np.array([idcv]))[0]
#     elements = M.core.mb.get_entities_by_handle(cv0)
#     M.core.mb.tag_set_data(ml.tags['verif_op'], elements, np.repeat(2.0, len(elements)))
#     for i in cols:
#         if i == idcv:
#             continue
#         cc = M.core.mb.get_entities_by_type_and_tag(M.core.root_set, types.MBENTITYSET, np.array([ml.tags['PRIMAL_ID_1']]), np.array([i]))[0]
#         elements = M.core.mb.get_entities_by_handle(cc)
#         M.core.mb.tag_set_data(ml.tags['verif_op'], elements, np.repeat(1.0, len(elements)))
#
#     M.core.print(file='results/test_'+ str(n), extension='.vtk', config_input='input_cards/print_settings0.yml')
#         # import pdb; pdb.set_trace()
#
#     import pdb; pdb.set_trace()
#     M.core.mb.tag_set_data(ml.tags['verif_op'], M.core.all_volumes, np.repeat(0.0, len(M.core.all_volumes)))
# M.core.print(file='results/test_'+ str(n), extension='.vtk', config_input='input_cards/print_settings0.yml')
#
# import pdb; pdb.set_trace()
#######################

gids, primal_ids = get_gids_and_primal_id(data_impress['PRIMAL_CLASSIC_ID_1'], data_impress['PRIMAL_CLASSIC_ID_2'])

ams_2 = AMSMpfa(ml['interns_level_2'],
                ml['faces_level_2'],
                ml['edges_level_2'],
                ml['vertex_level_2'],
                gids,
                primal_ids,
                load=False)

import pdb; pdb.set_trace()
ams_2.run(T_lv2)


#
# import pdb; pdb.set_trace()
data_impress.update_variables_to_mesh()
# M.pressure.update_all()
import pdb; pdb.set_trace()
# # data_impress.export_all_datas_to_npz()
M.core.print(file='results/test_'+ str(n), extension='.vtk', config_input='input_cards/print_settings0.yml')



# import pickle
#
# from tcc.load_save_initialize.load_infos import LoadInfos
# from tcc.dual_mesh.create_dual_mesh import DualMesh1
# import numpy as np
# from . import directories
# import pdb; pdb.set_trace()
#
# # file_name = os.path.join(path_flying, 'mesh_obj.txt')
# # with open(file_name, 'wb') as handle:
# #     pickle.dump(M, handle)
#
#
#
# LoadInfos(M)
# DualMesh1(M)
#
# import pdb; pdb.set_trace()
