from collections import defaultdict


class F90NML(defaultdict):
    """
    Object that represents a fortran90 namelist file
    """
    def __init__(self):
        """Initialize an empty namelist object"""
        super().__init__(dict)
        self.comments = defaultdict(dict)
        self.filename = None
        self.source_line = defaultdict(dict)

    @classmethod
    def read(cls, file):
        """Read Fortran90 namelist from file."""
        new = cls()
        new.filename = file
        print('Reading {:}'.format(file))
        with open(file, 'r') as f:
            header = None
            for line in f.readlines():
                if line[0] == '!':
                    continue
                content = line.strip()
                if len(content) > 0 and content[0] == '!':
                    continue
                if line[0] == '&':
                    header = line.split()[0][1:]
                    comment = ''
                    if '!' in line:
                        comment = line.split('!', 1)[1].strip()
                    continue
                if '=' in line:
                    param, b = line.split('=', 1)
                    param = param.strip()
                    comment = ''
                    value = b.split()[0].strip()
                    if '!' in b:
                        c = b.split('!')
                        comment = c[1].strip()
                        value = c[0].strip()
                    new[header][param] = value
                    new.comments[header][param] = comment
                    new.source_line[header][param] = line
        return new


def flatten_dict(d):
    """
    Flatten a nested dictionary.
    """
    out = {}
    for key, item in d.items():
        if isinstance(item, dict):
            r = flatten_dict(item)
            out.update(r)
        else:
            out[key] = item
    return out


def flatten_nml(a):
    """
    Returns a flattened version of a F90NML namelist.

    I.e. all parameters are grouped under a single header 'flat'
    """
    new_a = F90NML()
    new_a.filename = a.filename
    master_header = 'flat'
    new_a.comments[master_header] = flatten_dict(a.comments)
    new_a.source_line[master_header] = flatten_dict(a.source_line)
    new_a[master_header] = flatten_dict(a)
    return new_a


def compare_nmls(a, b, flatten=False):
    """
    Print parameters in order and compare parameters and values
    """
    print('Comparing files:\n A: {:}\n B: {:}\n'.format(a.filename,
                                                        b.filename))

    if flatten:
        a = flatten_nml(a)
        b = flatten_nml(b)

    all_headers = sorted(list(set(h for h in list(a.keys()) + list(b.keys()))))

    def get_value(a, header, param, default=None):
        v = '---'
        if header not in a:
            return v
        if param not in a[header]:
            return v
        return a[header][param]

    def print_legend():
        print('{:14} {:18}: {:24} {:24} {:}'.format(
            '[Namelist]', '[Param]',
            '[Value_A]',
            '[Value_B]',
            '[Comment]')
        )

    def print_param(header, param, a, b):
        if header in a.comments and param in a.comments[header]:
            comment = a.comments[header][param]
        elif header in b.comments:
            comment = b.comments[header].get(param, '')
        else:
            comment = ''
        print('{:14} {:18}: {:24} {:24} "{:}"'.format(
            header, param,
            get_value(a, header, param),
            get_value(b, header, param),
            comment)
        )

    def comp(a, b, eq=True):
        """Compare (in)equality of float/bool/string parameters."""
        _a = a
        _b = b

        def fix_bool(a):
            if '.TRUE.' in a or '.FALSE.' in a:
                return a.lower()
            return a

        def numerify(a):
            try:
                return float(a)
            except ValueError:
                pass
            return a

        _a = numerify(fix_bool(_a))
        _b = numerify(fix_bool(_b))
        if eq:
            return _a == _b
        return _a != _b

    def is_in(a, h, p):
        return h in a and p in a[h]

    def filter_match(a, b, h, p):
        return (is_in(a, h, p) and is_in(b, h, p) and
                comp(get_value(a, h, p), get_value(b, h, p)))

    def filter_differ(a, b, h, p):
        return (is_in(a, h, p) and is_in(b, h, p) and
                comp(get_value(a, h, p), get_value(b, h, p), eq=False))

    def filter_in_a(a, b, h, p):
        return is_in(a, h, p) and not is_in(b, h, p)

    def filter_in_b(a, b, h, p):
        return not is_in(a, h, p) and is_in(b, h, p)

    def section(title, filter_func):
        print('\n{:}:\n'.format(title))
        print_legend()
        for h in all_headers:
            all_params = set(h for h in list(a[h].keys()) + list(b[h].keys()))
            all_params = sorted(list(all_params))
            for p in all_params:
                if filter_func(a, b, h, p):
                    print_param(h, p, a, b)

    section('Matching parameters', filter_match)
    section('Different parameters', filter_differ)
    section('Only defined in A', filter_in_a)
    section('Only defined in B', filter_in_b)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Compare two Fortran90 namelist files')
    parser.add_argument('file_a', help='First file to compare')
    parser.add_argument('file_b', help='Second file to compare')
    parser.add_argument('--cfg_a', help='CFG file for first namelist')
    parser.add_argument('--cfg_b', help='CFG file for second namelist')
    parser.add_argument('-F', '--flatten',
                        help='Ignore namelist headers', action='store_true')

    args = parser.parse_args()
    a = F90NML.read(args.file_a)
    b = F90NML.read(args.file_b)

    def update_cfg(nml, cfg_file):
        if cfg_file is not None:
            cfg_nml = F90NML.read(cfg_file)
            print('Add {:} to {:}'.format(cfg_nml.filename, nml.filename))
            for key in nml:
                if key in cfg_nml:
                    nml[key].update(cfg_nml[key])

    update_cfg(a, args.cfg_a)
    update_cfg(b, args.cfg_b)

    compare_nmls(a, b, flatten=args.flatten)
