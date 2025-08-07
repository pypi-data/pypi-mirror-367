import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

class LightCurveTheoretical(object):

    def __init__(self, ticksinper = 100, depth = 0, duration = 0, noise = .001, numper = 1):
        """
        Light Curve with transit details for one period, for theoretical transit details

        Args:
        ticksinper (int): number of timesteps in one period
        length (integer): number of total timesteps
        depth (0 < float < 1.0): depth of simulated transit
        duration (0 < float < 1.0): time length of simulated transit
        noise (float): normalized noise of flux
        location (0 < float < 1.0): central location of transit
        flux (array of floats): normalized flux of light curve
        numper (int): number of periods

        """
        self.ticksinper = ticksinper
        self.length = self.ticksinper * numper
        if depth == 0:
            self.depth = np.random.uniform(.01,.20)
        else:
            self.depth = np.random.normal(loc = depth, scale = .03, size = 1)
        if duration == 0:
            self.duration = np.random.randint(.02 * ticksinper, .15 * ticksinper)
        else:
            self.duration = duration * ticksinper
        self.noise = noise
        self.location = np.random.randint(0,ticksinper)
        self.flux = np.ones(self.length) + np.random.normal(loc = 0, scale = self.noise, size = self.length)
        self.per = 0
        self.numper = numper
    
    def new_transit(self):
        """
        Creates new transit with slight variation in depth, and new location 1 period from previous
        """
        self.depth = np.random.normal(loc=self.depth, scale = 0.001, size = 1)
        self.location = self.location + self.ticksinper
        
    def plot_transit(self, phase_flag = False):
        """ 
        Subtracts transit from the flux and plots the resulting lightcurve
        
        kwargs:
        phase_flag (False, Bool): Decides if graph is plotted phasefolded or not
        """
        lowerbound = int(self.location - self.duration/2)
        upperbound = int(self.location + self.duration/2)
        #print("FIRST")
        #print(lowerbound,upperbound,self.location)
        if lowerbound < 0:
            self.ub = self.length + lowerbound
            self.lb = upperbound
            self.flux[0:self.lb] -= self.depth
            self.flux[self.ub:self.length] -= self.depth
            self.overflow_flag = True
        elif upperbound > self.length:
            self.lb = int(upperbound - self.length)
            self.ub = int(lowerbound)
            self.flux[0:self.lb] -= self.depth
            self.flux[self.ub:self.length] -= self.depth
            self.overflow_flag = True
        else:
            self.ub = int(upperbound)
            self.lb = int(lowerbound) 
            self.flux[self.lb:self.ub] -= self.depth
            self.overflow_flag = False
        self.plot(phase_flag=True)

    def plot(self, phase_flag = False):
        """
        Plots the light curve including the transit, then updates the period counter"""
        if phase_flag == True:
            if self.overflow_flag == True:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1] % 1, label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1] % 1, color = "navy", zorder = 3)
                plt.plot(np.arange(self.ub-1,self.length)/self.ticksinper, self.flux[self.ub-1:self.length] % 1, color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()            
            else:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper % 1,self.flux[self.lb-1:self.ub+1], label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper % 1,self.flux[self.lb-1:self.ub+1], color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()
        else:

            if self.overflow_flag == True:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1], label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1], color = "navy", zorder = 3)                    
                plt.plot(np.arange(self.ub-1,self.length)/self.ticksinper, self.flux[self.ub-1:self.length], color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()            
            else:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper,self.flux[self.lb-1:self.ub+1], label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper,self.flux[self.lb-1:self.ub+1], color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()
        self.per += 1


class LightCurveExoplanet(object):

    def __init__(self, planet, star, ticksinper = 100, noise = .001, numper = 1):
        """
        Light Curve with transit details for one period for exoplanet and star system details

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
        numper (int): number of periods

        """
        self.ticksinper = ticksinper
        self.length = self.ticksinper * numper
        self.depth = float(((planet.radius / star.radius).to(''))**2)
        self.duration = float((star.radius/(planet.a * 2 * np.pi)).to('') * self.ticksinper)
        self.noise = noise
        self.location = np.random.randint(0,ticksinper)
        self.flux = np.ones(self.length) + np.random.normal(loc = 0, scale = self.noise, size = self.length)
        self.per = 0
        self.numper = numper
    
    def new_transit(self):
        self.depth = np.random.normal(loc=self.depth, scale = 0.001, size = 1)
        self.location = self.location + self.ticksinper
        
    def plot_transit(self, phase_flag = False):
        """ 
        Subtracts transit from the flux and plots the resulting lightcurve
        """
        lowerbound = int(self.location - self.duration/2)
        upperbound = int(self.location + self.duration/2)
        #print("FIRST")
        #print(lowerbound,upperbound,self.location)
        if lowerbound < 0:
            self.ub = self.length + lowerbound
            self.lb = upperbound
            self.flux[0:self.lb] -= self.depth
            self.flux[self.ub:self.length] -= self.depth
            self.overflow_flag = True
        elif upperbound > self.length:
            self.lb = int(upperbound - self.length)
            self.ub = int(lowerbound)
            self.flux[0:self.lb] -= self.depth
            self.flux[self.ub:self.length] -= self.depth
            self.overflow_flag = True
        else:
            self.ub = int(upperbound)
            self.lb = int(lowerbound) 
            self.flux[self.lb:self.ub] -= self.depth
            self.overflow_flag = False
        if self.lb == 0:
            self.lb = 1
        if self.ub == self.length:
            self.ub = self.ub - 1
        print(self.lb,self.ub,self.location)
        print(self.overflow_flag)
        self.plot(phase_flag)

    def plot(self, phase_flag = False):
        
        if phase_flag == True:
            if self.overflow_flag == True:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1] % 1, label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1] % 1, color = "navy", zorder = 3)
                plt.plot(np.arange(self.ub-1,self.length)/self.ticksinper, self.flux[self.ub-1:self.length] % 1, color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()            
            else:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper % 1,self.flux[self.lb-1:self.ub+1], label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper % 1, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper % 1,self.flux[self.lb-1:self.ub+1], color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()
        else:

            if self.overflow_flag == True:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1], label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per+self.lb+1, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per+self.lb+1:self.ticksinper * (1 + self.per)], color = "deepskyblue")
                    plt.plot(np.arange(0,self.lb+1)/self.ticksinper,self.flux[0:self.lb+1], color = "navy", zorder = 3)                    
                plt.plot(np.arange(self.ub-1,self.length)/self.ticksinper, self.flux[self.ub-1:self.length], color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()            
            else:
                if self.per == 0:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], label = "Lightcurve", color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper,self.flux[self.lb-1:self.ub+1], label = "Transit", color = "navy", zorder = 3)
                else:
                    plt.plot(np.arange(self.ticksinper*self.per, self.ticksinper * (1 + self.per))/self.ticksinper, self.flux[self.ticksinper*self.per:self.ticksinper * (1 + self.per)], color = "deepskyblue")
                    plt.plot(np.arange(self.lb-1,self.ub+1)/self.ticksinper,self.flux[self.lb-1:self.ub+1], color = "navy", zorder = 3)
                plt.xlabel("Period")
                plt.ylabel("Normalized Flux")
                plt.title("Generated Light Curve")
                plt.legend()
        self.per += 1
class Exoplanet(object):
    """
    Simulated exoplanet
    Args:
    rad (float): radius of exoplanet in jupiter masses
    a (float): semi-major axis of exoplanet in AU
    """
    def __init__(self, rad, a, rad_unit = "R_J", a_unit = "AU"):
        
        if rad_unit == "R_J":
            self.radius = rad * u.R_jup
        elif rad_unit == "R_earth":
            self.radius = rad * u.R_earth
        elif rad_unit == "m":
            self. radius == rad * u.m
        else: 
            raise("ValueError: rad_unit must be 'R_J', 'R_earth', or 'm'.")
        if a_unit == "AU":
            self.a = a * u.au
        elif a_unit == "m":
            self.a = a * u.m
        else:
            raise("ValueError: a_unit must be either 'AU' or 'm'.")
        #self.mass = mass * u.M_jup

class Star(object):
    """
    Simulated Star
    Args:
    rad (float): radius of star in R_sun
    """

    def __init__(self, rad):
        self.radius = rad * u.R_sun
#        self.mass = mass * u.M_sun

