import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

class LightCurveTheoretical(object):
    """
        Light Curve with transit details for one period, for theoretical transit details

        Args:
            ticksinper (integer): Number of timesteps in a single period
            depth (float): Depth of transit to be simulated
            duration (float): Fraction of one period for planet to be in transit
            noise (float): Noise to be added to the flux
            numper (integer): Number of periods to be simulated
            name (string): Name of the object, sent to self.plot
        

        Attributes:
            ticksinper (integer): Number of timesteps in one period
            length (integer): Number of total timesteps
            depth (float): Depth of simulated transit
            duration (float): Time length of simulated transit
            noise (float): Normalized noise to be added to flux
            location (float): Central location of transit
            fluxOG (array): Flux of the lightcurve to be stored in order to remake light curves
            per (integer): current number of period being simulated
            numper (integer): The total number of periods to be simulated
            self.slopelength (integer): Duration of which to have sloped part of transit
            self.name (string): Name of object to be passed to self.plot
            self.flux (array): Flux to be plotted on the light curve. Is reset each time plot_transit is called to preserve depth
            lb (integer): Found lower bound for transit 
            ub (integer): Found upper bound for transit
            
    """

    def __init__(self, ticksinper = 100, depth = 0, duration = 0, noise = .001, numper = 1, name = ""):
        
        #sets intiial parameters, randomizes uninputted ones

        self.ticksinper = ticksinper
        self.length = self.ticksinper * numper
        if depth == 0:
            self.depth = np.random.uniform(.01,.20)
        else:
            self.depth = depth
        if duration == 0:
            self.duration = np.random.randint(.02 * ticksinper, .15 * ticksinper)
        else:
            self.duration = duration * ticksinper
        self.noise = noise
        self.location = np.random.randint(0,ticksinper)
        self.fluxOG = np.ones(self.length) + np.random.normal(loc = 0, scale = self.noise, size = self.length) + 1
        self.per = 0
        self.numper = numper
        self.slopelength = int(self.duration/10)
        self.name = name
        
    def plot_transit(self, phase_flag = False, xlim = []):
        """ 
        Subtracts transit from the flux and plots the resulting lightcurve
        
        Args:
            phase_flag (Bool, default = False): Decides if graph plotted is phasefolded or not
            xlim (array): Limits for the x axis sent to the self.plot
        Returns:
            array: Timesteps to plot lightcurve
            array: Flux for plotted lightcurve

        """

        self.flux = self.fluxOG - 1
        self.per = 0
        while self.per < self.numper:

            #generates SHAPE of transit around period = 0.5 for each period.

            lowerbound = int(self.ticksinper/2 * (1 + 2 *self.per) - self.duration/2)
            upperbound = int(self.ticksinper/2 * (1 + 2 *self.per) + self.duration/2)

            self.ub = int(upperbound)
            self.lb = int(lowerbound) 

            self.flux[self.lb:self.ub] -= self.depth

            for i in np.arange(self.lb - self.slopelength, self.lb):
                self.flux[i] = 1 - (i - (self.lb - self.slopelength))/(self.slopelength) * (self.depth)
            for i in np.arange(self.ub, self.slopelength + self.ub):
                self.flux[i] = 1 + (i - (self.ub + self.slopelength))/(self.slopelength) * (self.depth)

            self.per += 1
            self.depth = np.random.normal(loc=self.depth, scale = 0.0001, size = 1)[0]

        #Shifts the transits to where location tells them to go

        self.flux = np.roll(self.flux,self.location)

        self.plot(phase_flag, xlim = xlim)
        self.timesteps = np.arange(self.ticksinper*self.per)/self.ticksinper

        return self.timesteps, self.flux

    def plot(self, phase_flag = False, xlim = [0,0]):
        """
        Plots the light curve including the transit, then updates the period counter

        Args:
            phase_flag (Bool, default = False): Decides if plot is phasefolded or not.
            xlim (array): Limits for the x axis sent to the self.plot


        """

        plt.figure()
        transit_idxs = np.where(self.flux<.995)[0] #Pulls indices where transit occurs after the shift

        if phase_flag == True:
            plt.scatter(np.arange(self.ticksinper*self.per)/self.ticksinper % 1, self.flux, color = 'deepskyblue', label = "Light Curve")
            plt.scatter(transit_idxs/self.ticksinper % 1, self.flux[transit_idxs], color = 'navy', label = "Transit")
            plt.xlabel("Phase")

        else:
            plt.scatter(np.arange(self.ticksinper*self.per)/self.ticksinper, self.flux, color = 'deepskyblue', label = "Light Curve")
            plt.scatter(transit_idxs/self.ticksinper, self.flux[transit_idxs], color = 'navy', label = "Transit")
            plt.xlabel("Period")

        if len(xlim) != 0: #Applies x limit
            plt.xlim(xlim[0],xlim[1])

        plt.ylabel("Normalized Flux")
        plt.title("Generated Light Curve of " + f"{self.name}")
        plt.legend()


class LightCurveExoplanet(object):
    """
        Light Curve with transit details for one period, for theoretical transit details

        Args:
            ticksinper (integer): Number of timesteps in a single period
            planet (Exoplanet): Planet which to simulate transit of
            star (Star): Star which planet will transit
            noise (float): Noise to be added to the flux
            numper (integer): Number of periods to be simulated
            name (string): Name of system to be passed to self.plot
        

        Attributes:
            ticksinper (integer): Number of timesteps in one period
            length (integer): Number of total timesteps
            depth (float): Depth of simulated transit
            duration (float): Time length of simulated transit
            noise (float): Normalized noise to be added to flux
            location (float): Central location of transit
            fluxOG (array): Flux of the lightcurve to be stored in order to remake light curves
            per (integer): current number of period being simulated
            numper (integer): The total number of periods to be simulated
            self.slopelength (integer): Duration of which to have sloped part of transit
            self.name (string): Name of object to be passed to self.plot
            self.flux (array): Flux to be plotted on the light curve. Is reset each time plot_transit is called to preserve depth
            lb (integer): Found lower bound for transit 
            ub (integer): Found upper bound for transit

    """

    def __init__(self, planet, star, ticksinper = 100, noise = .001, numper = 1, name = ""):
        """
        Light Curve with transit details for one period for exoplanet and star system. Calculates transit parameters from system 
        parameters.

        Args:
        Inputs: 
        planet (Exoplanet): exoplanet to have transit plotted
        star (Star): star which exoplanet transits
        depth (0 < float < 1.0): depth of simulated transit, calculated via d = {R_p^2}/{R_s^2}
        duration (0 < float < 1.0): time length of simulated transit calculated via t/P = R_s/(2*pi*a)
        ticksinper (int): number of timesteps in one period
        length (integer): number of total timesteps
        noise (float): normalized noise of flux
        location (0 < float < 1.0): central location of transit
        flux (array of floats): normalized flux of light curve
        numper (integer): number of periods

        """

        #Calculates the initial parameters from the inputted system

        self.ticksinper = ticksinper
        self.length = self.ticksinper * numper
        self.depth = float(((planet.radius / star.radius).to(''))**2)
        self.duration = float((star.radius/(planet.a * 2 * np.pi)).to('') * self.ticksinper)
        self.noise = noise
        self.location = np.random.randint(0,ticksinper)
        self.fluxOG = np.ones(self.length) + np.random.normal(loc = 0, scale = self.noise, size = self.length)+1
        self.per = 0
        self.slopelength = int(self.duration/10)
        self.numper = numper
        self.name = name
    
    def plot_transit(self, phase_flag = False, xlim = []):
        """ 
        Subtracts transit from the flux and plots the resulting lightcurve
        
        Args:
            phase_flag (Bool, default = False): Decides if graph plotted is phasefolded or not
        Returns:
            array: Timesteps to plot lightcurve
            array: Flux for plotted lightcurve

        """

        self.per = 0
        self.flux = self.fluxOG - 1
        while self.per < self.numper:

            #generates SHAPE of transit around period = 0.5 for each period.

            lowerbound = int(self.ticksinper/2 * (1 + 2 *self.per) - self.duration/2)
            upperbound = int(self.ticksinper/2 * (1 + 2 *self.per) + self.duration/2)

            self.ub = int(upperbound)
            self.lb = int(lowerbound) 

            self.flux[self.lb:self.ub] -= self.depth

            for i in np.arange(self.lb - self.slopelength, self.lb):
                self.flux[i] = 1 - (i - (self.lb - self.slopelength))/(self.slopelength) * (self.depth)
            for i in np.arange(self.ub, self.slopelength + self.ub):
                self.flux[i] = 1 + (i - (self.ub + self.slopelength))/(self.slopelength) * (self.depth)

            self.per += 1
            self.depth = np.random.normal(loc=self.depth, scale = 0.0001, size = 1)[0]
        
        #Shifts the transits to where location tells them to go
       
        self.flux = np.roll(self.flux,self.location)

        self.plot(phase_flag, xlim = xlim)
        self.timesteps = np.arange(self.ticksinper*self.per)/self.ticksinper
        return self.timesteps, self.flux

    def plot(self, phase_flag = False, xlim = []):
        """
        Plots the light curve including the transit, then updates the period counter

        Args:
            phase_flag (Bool, default = False): Decides if plot is phasefolded or not.

        """

        plt.figure()
        transit_idxs = np.where(self.flux<.995)[0]
        if phase_flag == True:
            plt.scatter(np.arange(self.ticksinper*self.per)/self.ticksinper % 1, self.flux, color = 'deepskyblue', label = "Light Curve")
            plt.scatter(transit_idxs/self.ticksinper % 1, self.flux[transit_idxs], color = 'navy', label = "Transit")
            plt.xlabel("Phase")

        else:
            plt.scatter(np.arange(self.ticksinper*self.per)/self.ticksinper, self.flux, color = 'deepskyblue', label = "Light Curve")
            plt.scatter(transit_idxs/self.ticksinper, self.flux[transit_idxs], color = 'navy', label = "Transit")
            plt.xlabel("Period")

        if len(xlim) != 0:
            plt.xlim(xlim[0],xlim[1])
        
        plt.ylabel("Normalized Flux")
        plt.title("Generated Light Curve of " + f"{self.name}")
        plt.legend()


class Exoplanet(object):

    """
    Simulated exoplanet
    Args:
        rad (float): radius of exoplanet in jupiter masses
        a (float): semi-major axis of exoplanet in AU
        rad_unit (string, default = R_J): unit of inputted radius
        a_unit (string, default = AU): unit of inputted semi-major axis

    Attributes:
        radius (float): Planetary radius in units rad_unit
        a (float): semi-major axis in units a_unit
    
    """

    def __init__(self, rad, a, rad_unit = "R_J", a_unit = "AU"):
        
        if rad_unit == "R_J":
            self.radius = rad * u.R_jup
        elif rad_unit == "R_earth":
            self.radius = rad * u.R_earth
        elif rad_unit == "m":
            self. radius == rad * u.m
        else: 
            raise Exception("ValueError: rad_unit must be 'R_J', 'R_earth', or 'm'.")
        if a_unit == "AU":
            self.a = a * u.au
        elif a_unit == "m":
            self.a = a * u.m
        else:
            raise Exception("ValueError: a_unit must be either 'AU' or 'm'.")
        #self.mass = mass * u.M_jup

class Star(object):
    """
    Simulated Star
    
    Args:
        rad (float): radius of star in R_sun

    Attributes:
        radius (float): radius of star in solar radii.
    """

    def __init__(self, rad):
        self.radius = rad * u.R_sun