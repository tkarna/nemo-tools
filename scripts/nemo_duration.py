"""
Figure out NEMO simulation run speed and duration.

Parses namelist and output files to determine the statistics.
"""
import datetime
import os


def parse_iteration_count_old(infile='run.stat', run_dir=None):
    """
    Parses last line from 'run.stat' file to determine current iteration count.
    """
    filename = infile if run_dir is None else os.path.join(run_dir, infile)
    with open(filename, 'r') as f:
        last_line = f.readlines()[-1]
        words = last_line.split()
        assert words[0] == 'it'
        niters = int(words[2])
    return niters


def parse_iteration_count(infile='time.step', run_dir=None):
    """
    Parses the int written in 'time.step' file.
    """
    filename = infile if run_dir is None else os.path.join(run_dir, infile)
    with open(filename, 'r') as f:
        line = f.readlines()[0]
        niters = int(line)
    return niters


def parse_namelist(infile, key, convert_func=float, run_dir=None):
    """
    Parses a keyword from f90 namelist
    """
    value = None
    filename = infile if run_dir is None else os.path.join(run_dir, infile)
    with open(filename, 'r') as f:
        for line in f.readlines():
            words = line.split()
            if len(words) > 2 and words[0] == key:
                value = convert_func(words[2])
    assert value is not None, '{:} not found in {:}'.format(filename)
    return value


def parse_namelist_with_cfg(infile_ref, infile_cfg, key, convert_func=float,
                            run_dir=None):
    """
    Parses a keyword from cfg and ref namelist
    """
    _ref = infile_ref if run_dir is None else os.path.join(run_dir, infile_ref)
    _cfg = infile_cfg if run_dir is None else os.path.join(run_dir, infile_cfg)
    try:
        value = parse_namelist(_cfg, key, convert_func=convert_func)
    except (AssertionError, IndexError):
        value = parse_namelist(_ref, key, convert_func=convert_func)
    return value


def parse_timestep(infile='namelist_ref', infile_cfg='namelist_cfg',
                   run_dir=None):
    """
    Parses 3D time step from NEMO namelist file
    """
    return parse_namelist_with_cfg(infile, infile_cfg, 'rn_rdt',
                                   convert_func=float, run_dir=run_dir)


def parse_total_iter_count(infile='namelist_ref', infile_cfg='namelist_cfg',
                           run_dir=None):
    """
    Parses total iter count from NEMO namelist file
    """
    return parse_namelist_with_cfg(infile, infile_cfg, 'nn_itend',
                                   convert_func=int, run_dir=run_dir)


def get_file_mod_time(file):
    """
    Return last modification time as a datetime object
    """
    mod_time = os.path.getmtime(file)
    return datetime.datetime.fromtimestamp(mod_time)


def process(run_directory=None):
    """
    Print run speed, current state and statistics.
    """
    if run_directory is not None:
        print('Run directory: {:}'.format(run_directory))

    # get sim start time
    start_time = get_file_mod_time(os.path.join(run_directory, 'layout.dat'))

    niters = parse_iteration_count(os.path.join(run_directory, 'time.step'))
    timestep = parse_timestep(run_dir=run_directory)
    tot_niter = parse_total_iter_count(run_dir=run_directory)

    # last modified time
    current_time = datetime.datetime.now()
    last_update = get_file_mod_time(os.path.join(run_directory, 'time.step'))
    time_changed = round((current_time - last_update).total_seconds())

    # compute elapsed wallclock time
    duration = last_update - start_time
    duration_sec = duration.total_seconds()

    running = time_changed < 3*60.0
    finished = tot_niter == niters

    status_str = 'Running' if running else 'STOPPED'
    if finished:
        status_str = 'Finished'
    print('Run started at {:}'.format(start_time))
    print('Status: {:}'.format(status_str))
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
    import argparse

    parser = argparse.ArgumentParser(
        description='Report NEMO 4.0 execution status.',
        # includes default values in help entries
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('run_directory', type=str, nargs='?', default='.',
                        help='Run directory where "time.step" etc files are '
                        'stored (default: current directory).')
    args = parser.parse_args()
    process(args.run_directory)
