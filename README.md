# nemo-tools

Tools for Nemo ocean model

## Installation

```bash
pip install -e <path-to-this-repository>
```

## Examples

## `nemo-progress`

Print Nemo simulation speed and duration on command line:

```bash
nemo-progress
```

Outputs:

```
Run directory: .
Run started at 2019-12-05 18:17:04
Status: Running
Run time: 0:01:01
Completed 25/29760 iterations with dt=90.0 s
Current simulation time: 0:37:30
Total simulation time: 31 days, 0:00:00
Wallclock time for
    one day: 0:39:02
 entire run: 20:10:14
Remaining wallclock time: 20:09:13
```

To inspect a run in another directory:

```bash
nemo-progress <path-to-run-dir>
```

## `compare-namelist`

Compares two fortran90 namelists:

```bash
compare-namelist run_a/namelist_ref run_b/namelist_ref
```

To include Nemo cfg name lists as well

```bash
compare-namelist namelist_ref --cfg_a=namelist_cfg run_b/namelist_ref --cfg_b=run_b/namelist_cfg
```
