import matplotlib.pyplot as plt
import numpy
import netCDF4


def gen_nemo_grid(jpk, ppkth, ppacr, ppdzmin, pphmax):
    """
    Compute Nemo vertical grid from ppkth, ppacr, ppdzmin, pphmax parameters
    """
    d = numpy.tanh((1-ppkth)/ppacr) - ppacr/(jpk-1) * (
            numpy.log(numpy.cosh((jpk - ppkth)/ppacr)) -
            numpy.log(numpy.cosh((1 - ppkth) / ppacr))
        )
    za1 = (ppdzmin - pphmax / (jpk-1)) / d
    za0 = ppdzmin - za1 * numpy.tanh((1-ppkth) / ppacr)
    zsur = -za0 - za1 * ppacr * numpy.log(numpy.cosh((1-ppkth)/ppacr))
    z, z_mid = gen_nemo_grid_z(n, zsur, za0, za1, ppkth, ppacr)
    return z, z_mid


def gen_nemo_grid_z(n, zsur, za0, za1, zkth, zacr):
    """
    Compute Nemo vertical grid from z parameters

    :returns z, zmin: numpy arrays of the z grid and cell mid points.
    """
    z = numpy.zeros((n, ))
    for k in range(n):
        # gdepw_1d(jk) = ( zsur + za0 * zw +
        #                  za1 * zacr * LOG ( COSH( (zw-zkth) / zacr ) )  )
        z[k] = zsur + za0*(k+1) + \
            za1 * zacr * numpy.log(numpy.cosh(((k+1) - zkth)/zacr))
    z_mid = 0.5*(z[1:] + z[:-1])
    return z, z_mid


class VerticalGrid:
    """A vertical grid object."""
    def __init__(self, z_coords, name=None):
        self.z = z_coords
        self.npoints = len(self.z)
        self.h = numpy.diff(self.z)
        self.z_midpoint = 0.5*(self.z[1:] + self.z[:-1])
        self.index = numpy.arange(self.npoints)
        if name is None:
            name = 'vgrid-{}'.format(self.npoints)
        self.name = name
        h_rat = self.h[1:]/self.h[:-1]
        print(f'Vertical grid {self.name}: {self.npoints} levels')
        print('  Resolution: {self.h.min():.3f} .. {self.h.max():.3f}')
        print('  Max h scaling ratio: {h_rat.max():.4f}')

    def print_summary(self):
        """Print grid levels"""
        print(self.name)
        print(f'levels: {self.h}')
        print('index  z_top   z_bot   z_mid      dz')
        for i, (mid, dz) in enumerate(zip(self.z_midpoint, self.h)):
            top = self.z[i]
            bot = self.z[i+1]
            print(f'{i:3d}: {top:7.3f} {bot:7.3f} {mid:7.3f} {dz:7.3f}')


def load_grid(ncfile, name=None):
    """
    Loads vertical grid from Nemo domain_cfg file
    """
    with netCDF4.Dataset(ncfile) as d:
        z = d['nav_lev'][:]
    vgrid = VerticalGrid(z, name=name)
    return vgrid


def plot_index(vgrid_list):
    """
    Plot the depth of z levels (y) versus level index (x)
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for v in vgrid_list:
        ax.plot(v.index, v.z, '+', label=v.name)
    ax.axes.invert_yaxis()
    ax.grid(True)
    ax.set_ylabel('Depth (m)')
    ax.set_xlabel('Level index')
    ax.legend()
    plt.show()


def plot_resolution(vgrid_list, ax=None, log=False, xlim=None, zlim=None):
    """
    Plot vertical grid resolution (x) as a function of depth (y)
    """
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    plot_func = ax.loglog if log else ax.plot
    for v in vgrid_list:
        plot_func(v.h, v.z_midpoint, '.-', label=v.name)
    if xlim is not None:
        ax.set_xlim(xlim)
    if zlim is not None:
        ax.set_ylim(zlim)
    ax.axes.invert_yaxis()
    ax.grid(True)
    ax.grid(True, which='minor', linestyle='dashed', linewidth=0.5)
    ax.set_ylabel('Depth (m)')
    ax.set_xlabel('Vertical resolution (m)')
    ax.legend()


# list of vertical grids to plot
v_list = []

# load from domain_cfg file
# v = load_grid('domain_cfg.nc', name='vgrid-75')
# v_list.append(v)

# generate one from NEMO namelist parameters
n = 75
kth = 55.0
cr = 12.0
dzmin = 1.0
hmax = 700.0
z, z_mid = gen_nemo_grid(n, kth, cr, dzmin, hmax)
v = VerticalGrid(z, name='vg-{}-{}-{}'.format(n, kth, cr))
v_list.append(v)

# another one
kth = 54.0
cr = 12.0
z, z_mid = gen_nemo_grid(n, kth, cr, dzmin, hmax)
v = VerticalGrid(z, name='vg-{}-{}-{}'.format(n, kth, cr))
v_list.append(v)


for v in v_list:
    v.print_summary()

# make a comparison plot
fig = plt.figure(figsize=(20, 5))
ax = fig.add_subplot(131)
plot_resolution(v_list, ax=ax)
ax = fig.add_subplot(132)
plot_resolution(v_list, ax=ax, log=True)
ax = fig.add_subplot(133)
plot_resolution(v_list, ax=ax, zlim=[0, 100], xlim=[0, 15])
plt.savefig('vertical_grid.png', dpi=100, bbox_inches='tight')
plt.show()
