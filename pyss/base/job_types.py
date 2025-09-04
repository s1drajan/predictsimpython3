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
    ('n_repetitions', float),
    ('ngx', float),
    ('ngy', float),
    ('ngz', float),
    ('nodes', float),
    ('tasks', float),
],
    JOB_TYPE_NEKBONE: [
    # ('error',str),
    ('iel0', float),
    ('ielN', float),
    ('ifbrick', str),  # could be mapped to bool with special handling for Fortran-style '.false.'
    ('istep', float),
    ('mx', float),
    ('my', float),
    ('mz', float),
    ('nodes', float),
    ('npx', float),
    ('npy', float),
    ('npz', float),
    ('nstep', float),
    ('nx0', float),
    ('nxN', float),
    ('tasks', float),
],
    JOB_TYPE_EXAMINIMDSNAP: [
    ('comm_exchange_rate', float),
    ('comm_newton', str),
    ('dt', float),
    ('error', str),
    # ('force_cutoff', str), null in our params so it is cut out
    ('force_type', str),
    ('lattice', str),
    ('lattice_constant', float),
    ('lattice_nx', float),
    ('lattice_ny', float),
    ('lattice_nz', float),
    ('lattice_offset_x', float),
    ('lattice_offset_y', float),
    ('lattice_offset_z', float),
    ('mass', float),
    ('neighbor_skin', float),
    ('nodes', float),
    ('nsteps', float),
    ('ntypes', float),
    ('tasks', float),
    ('temperature_seed', float),
    ('temperature_target', float),
    ('thermo_rate', float),
    ('type', float),
    ('units', str),
]
}

