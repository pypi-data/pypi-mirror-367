import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.gaia import Gaia

# class one, brown dwarf object
class BrownDwarf:
    def __init__(self, name, ra, dec, distance, color=False, temp = False):
        ''' 
        Brown Dwarf object
        Attributes
        ----------
        ra          : float, degrees
        dec         : float, degrees
        distance    : float, in kpc
        name        : string, name of object
        color       : string, color intending to plot
        temp        : float (optional), in K. Will plot color based on temp
        '''
        self.name = name
        self.ra = ra * u.deg
        self.dec = dec * u.deg
        self.distance = distance * u.pc

        if color:
            self.color = color
        if temp:
            self.temp = temp
        
        self.pos=SkyCoord(ra=self.ra,dec=self.dec, distance=self.distance,  frame='icrs')


    def get_xyz(self):
        # set set the x,y z attributes of the object
        gal=self.pos.transform_to('galactic')
        self.x = gal.cartesian.x.to(u.pc).value
        self.y = gal.cartesian.y.to(u.pc).value
        self.z = gal.cartesian.z.to(u.pc).value

# class 2, plot 3d
class Plot3D:
    def __init__(self): # initlize the plot
        self.objects = [] # list of objects to keep track of on the plot
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self._setup_plot() # set up method for putting the sun, labels, and initilize viewing angle

    def _setup_plot(self):
        self.ax.set_title("3D Galactic Plot (Sun at 0,0,0)")
        self.ax.set_xlabel("X (pc)")
        self.ax.set_ylabel("Y (pc)")
        self.ax.set_zlabel("Z (pc)")
        self.ax.set_xlim(-10,10)
        self.ax.set_ylim(-10,10)
        self.ax.set_zlim(-10,10)
        self.ax.scatter(0, 0, 0, color='orange', label='Sun')
        self.ax.legend()
        self.ax.view_init(elev=0, azim=125)

    def plot_stars(self, catalog = 'Gaia'): # method for if we want to query simbad or gaia and plot stars on there
        if catalog == 'Gaia':
            query = """
                        SELECT TOP 1000 source_id, ra, dec, l, b, phot_g_mean_mag
                        FROM gaiadr3.gaia_source
                        WHERE phot_g_mean_mag < 12
                        """
            job = Gaia.launch_job_async(query)
            results = job.get_results()
            l = results['l']
            b = results['b']
            stars = SkyCoord(l=l, b=b, frame='galactic')
            self.ax.scatter(stars.cartesian.x, stars.cartesian.y, stars.cartesian.z, 
                            color = 'black', alpha = 0.005, marker = ',')
        
    def add_object(self, obj, show_label=True):
        self.objects.append(obj) 
        obj.get_xyz() # get the x,y and z of object
        self.ax.scatter(obj.x, obj.y, obj.z, color=obj.color, label=obj.name)
        if show_label:
            self.ax.text(obj.x, obj.y, obj.z, f" {obj.name}", color=obj.color)
        self.ax.legend()
        self.fig.canvas.draw()
        print(f"Added: {obj.name} at (x={obj.x:.1f}, y={obj.y:.1f}, z={obj.z:.1f}) pc")
