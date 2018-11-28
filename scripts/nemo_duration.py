"""
Figure out NEMO simulation run speed and duration.

Parses namelist and output files to determine the statistics.
"""
import datetime
import os


def parse_iteration_count(infile='run.stat'):
    """
    Parses last line from 'run.stat' file to determine current iteration count.
    """
    with open(infile, 'r') as f:
        last_line = f.readlines()[-1]
        words = last_line.split()
        assert words[0] == 'it'
        niters = int(words[2])
    return niters


def parse_namelist(infile, key, convert_func=float):
    """
    Parses a keyword from f90 namelist
    """
    value = None
    with open(infile, 'r') as f:
        for line in f.readlines():
            words = line.split()
            if len(words) > 2 and words[0] == key:
                value = convert_func(words[2])
    assert value is not None, '{:} not found in {:}'.format(infile)
    return value


def parse_namelist_with_cfg(infile_ref, infile_cfg, key, convert_func=float):
    """
    Parses a keyword from cfg and ref namelist
    """
    try:
        value = parse_namelist(infile_cfg, key, convert_func=convert_func)
    except AssertionError:
        value = parse_namelist(infile_ref, key, convert_func=convert_func)
    return value


def parse_timestep(infile='namelist_ref', infile_cfg='namelist_cfg'):
    """
    Parses 3D time step from NEMO namelist file
    """
    return parse_namelist_with_cfg(infile, infile_cfg, 'rn_rdt', float)


def parse_total_iter_count(infile='namelist_ref', infile_cfg='namelist_cfg'):
    """
    Parses total iter count from NEMO namelist file
    """
    return parse_namelist_with_cfg(infile, infile_cfg, 'nn_itend', int)


def get_file_mod_time(file):
    """
    Return last modification time as a datetime object
    """
    mod_time = os.path.getmtime(file)
    return datetime.datetime.fromtimestamp(mod_time)


def process():
    """
    Print run speed, current state and statistics.
    """
    # get sim start time
    start_time = get_file_mod_time('layout.dat')

    # compute elapsed wallclock time
    current_time = datetime.datetime.now()
    duration = current_time - start_time
    duration_sec = duration.total_seconds()

    niters = parse_iteration_count()
    timestep = parse_timestep()
    tot_niter = parse_total_iter_count()

    # last modified time
    last_update = get_file_mod_time('run.stat')
    time_changed = round((current_time - last_update).total_seconds())

    running = time_changed < 3*60.0

    print('Run started at {:}'.format(start_time))
    print('Status: {:}'.format(
        'Running' if running else 'STOPPED'
    ))
    if not running:
        print('  last update {:} ago'.format(
            datetime.timedelta(seconds=time_changed)))

    print('Run time: {:}'.format(
        datetime.timedelta(seconds=round(duration_sec))
    ))
    print('Completed {:}/{:} iterations with dt={:} s'.format(
        niters, tot_niter, timestep
    ))

    # do the math
    simtime = round(niters*timestep)
    tot_simtime = round(tot_niter*timestep)
    iter_rate = float(niters)/duration_sec
    iters_per_day = 24*3600./timestep
    time_per_day = round(iters_per_day/iter_rate)
    tot_time = round(tot_niter/iter_rate)
    remaining_time = round((tot_niter-niters)/iter_rate)

    print('Current simulation time: {:}'.format(
        datetime.timedelta(seconds=simtime)
    ))
    print('Total simulation time: {:}'.format(
        datetime.timedelta(seconds=tot_simtime)
    ))

    print('Wallclock time for')
    print('    one day: {:}'.format(datetime.timedelta(seconds=time_per_day)))
    print(' entire run: {:}'.format(datetime.timedelta(seconds=tot_time)))
    print('Remaining wallclock time: {:}'.format(
        datetime.timedelta(seconds=remaining_time)
    ))


if __name__ == '__main__':
    process()
