JOB_TYPE_DEFAULT = 0
JOB_TYPE_SWFFT = 1
JOB_TYPE_NEKBONE = 2
JOB_TYPE_EXAMINIMDSNAP = 3

JOB_TYPE_RANGE = range(JOB_TYPE_EXAMINIMDSNAP+1) # max number of jobs

JOB_TYPE_TO_STR = {
    JOB_TYPE_DEFAULT: "Default",
    JOB_TYPE_SWFFT: "SWFFT",
    JOB_TYPE_NEKBONE: "Nekbone",
    JOB_TYPE_EXAMINIMDSNAP: "ExaMiniMDSnap"
}

params_map = {
    JOB_TYPE_DEFAULT: [],
    JOB_TYPE_SWFFT: [
    #NOTE: error is typically null but since its at the start the extra space to seperate DEFAULT from PARAMS
    # merges together leading to us having to null it out (same logic behind nekbone)
    # ('error',str),
    ('n_repetitions', int),
    ('ngx', int),
    ('ngy', int),
    ('ngz', int),
    ('nodes', int),
    ('tasks', int),
],
    JOB_TYPE_NEKBONE: [
    # ('error',str),
    ('iel0', int),
    ('ielN', int),
    ('ifbrick', str),  # could be mapped to bool with special handling for Fortran-style '.false.'
    ('istep', int),
    ('mx', int),
    ('my', int),
    ('mz', int),
    ('nodes', int),
    ('npx', int),
    ('npy', int),
    ('npz', int),
    ('nstep', int),
    ('nx0', int),
    ('nxN', int),
    ('tasks', int),
],
    JOB_TYPE_EXAMINIMDSNAP: [
    ('comm_exchange_rate', int),
    ('comm_newton', str),
    ('dt', float),
    ('error', str),
    # ('force_cutoff', str), null in our params so it is cut out
    ('force_type', str),
    ('lattice', str),
    ('lattice_constant', float),
    ('lattice_nx', int),
    ('lattice_ny', int),
    ('lattice_nz', int),
    ('lattice_offset_x', float),
    ('lattice_offset_y', float),
    ('lattice_offset_z', float),
    ('mass', float),
    ('neighbor_skin', float),
    ('nodes', int),
    ('nsteps', int),
    ('ntypes', int),
    ('tasks', int),
    ('temperature_seed', int),
    ('temperature_target', float),
    ('thermo_rate', int),
    ('type', int),
    ('units', str),
]
}

