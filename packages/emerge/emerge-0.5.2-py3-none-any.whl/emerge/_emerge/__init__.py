# """A Python based FEM solver.
# Copyright (C) 2025  name of Robert Fennis

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see
# <https://www.gnu.org/licenses/>.

# """
# import os

# os.environ["OMP_NUM_THREADS"] = "1"
# os.environ["MKL_NUM_THREADS"] = "1"
# os.environ["OPENBLAS_NUM_THREADS"] = "1"

# from loguru import logger
# from .logsettings import logger_format
# import sys

# logger.remove()
# logger.add(sys.stderr, format=logger_format)

# logger.debug('Importing modules')
# from _emerge.simmodel import Simulation3D
# from _emerge.material import Material, FR4, AIR, VACUUM, COPPER
# import bc
# from _emerge.solver import superlu_info, SolverBicgstab, SolverGMRES, SolveRoutine, ReverseCuthillMckee, Sorter, SolverPardiso, SolverUMFPACK
# from _emerge.cs import CoordinateSystem, Plane, Axis, XAX, YAX, ZAX, XYPLANE, XZPLANE, YZPLANE, YXPLANE, ZXPLANE, ZYPLANE
# from _emerge.coord import Line
# import geo
# from _emerge.selection import Selection, FaceSelection, DomainSelection, EdgeSelection
# from _emerge.mth.common_functions import norm
# logger.debug('Importing complete!')