import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class emlinefit(object):
    """
    This package will fit a gaussian to an emission line.

    Attributes:
        wavelength (array): the wavelength values
        flux (array): the flux values
        line_l (float, int): lower wavelength limit for emission line
        line_u (float, int): upper wavelength limit for emission line
        fit_type (str, optional): fit profile, 'gaussian' or 'asymmetric'


    """
    def __init__(self, wavelength, flux, line_l, line_u, fit_type='gaussian'):
        """
        __init__ method

        Args:
            wavelength (array): the wavelength values
            flux (array): the flux values
            line_l (float, int): lower wavelength limit for emission line
            line_u (float, int): upper wavelength limit for emission line
            fit_type (str, optional): fit profile, 'gaussian' or 'asymmetric'

        """
        self.wavelength=wavelength
        self.flux=flux
        self.line_l=line_l
        self.line_u=line_u
        self.fit_type=fit_type
        
    def gaussian(self, wavelength, amp, mu, sigma):
        """
        This function creates a gaussian profile

        Args:
            wavelength (array): the wavelength (x) values
            amp (float or int): the amplitude of the gaussian profile
            mu (float or int): the wavelength (x) value where the gaussian profile peaks
            sigma (float or int): the width of the gaussian profile

        Returns:
            Array of y-values for the gaussian profile
            The same length as the input wavelength array
        """

        exponential = -1 * (wavelength - mu)**2 / (2 * sigma**2)
        return amp * np.exp(exponential)

    def asym_gaussian(self, wavelength, A, a_asym, d):
        """
        This function creates an asymmetruc gaussian profile

        Args:
            wavelength (array): the wavelength (x) values
            A (float or int): amp
            a_asym (float or int): asymemtric parameter
            d (float or int): width parameter

        Returns:
            Array of y-values of the asymmetric gaussian profile
            The same length as the input wavelength array
        """

        ind = (wavelength>self.line_l) & (wavelength<self.line_u)
        ind_full = (self.wavelength>self.line_l) & (self.wavelength<self.line_u)
        delta_vel=wavelength[ind]-self.wavelength[ind_full][np.argmax(self.flux[ind_full])]
        return A * np.exp((-delta_vel**2) / (2 * (a_asym*delta_vel + d)**2))

    def cal_fwhm(self):
        """
        This function transforms the width parameter from the asymmetric gaussian profile into a FWHM

        Returns:
            Float or interger FWHM of the asymmetric gaussian profile
        """
        return 2*np.sqrt(2*np.log(2))*self.d/(1-2*np.log(2)*self.asym**2)

    def gaussfitting(self):
        """
        This function fits a gaussian profile to the input data

        Returns:
            Fitted gaussian paramters of amplitude, peak wavelength, and width
            Covariance
        """
        ind = (self.wavelength>self.line_l) & (self.wavelength<self.line_u)
        popt,pcov=curve_fit(self.gaussian, self.wavelength[ind], self.flux[ind],
                    bounds=([0,self.line_l,0],[np.max(self.flux[ind]),self.line_u,((self.line_u-self.line_l)/2)]))
        return popt,pcov
    
    def asymfitting(self):
        """
        Thus function fits an asymmetric gaussian profile to the input data

        Returns:
            Fitted asymmetric gaussian paramters of amplitude, asymmetric paramter, and width
            Covariance
        """
        ind = (self.wavelength>self.line_l) & (self.wavelength<self.line_u)
        popt,pcov=curve_fit(self.asym_gaussian, self.wavelength[ind], self.flux[ind],
                    p0=[np.max(self.flux[ind]),1,0.4])
        return popt,pcov
    
    def asym_width(self):
        """
        This function returns the FWHM of a fitted asymmetric gaussian

        Returns:
            FWHM of the fitted asymmetric gaussian
        """
        popt, _ = self.asymfitting()
        self.A, self.asym, self.d = popt
        width = self.cal_fwhm()
        return width
    
    def return_result(self):
        """
        This function calls the correct fitting routine (gaussian or asymmetric gaussian) based on the
        input fit-type

        Returns:
            Fitted gaussian parameters of amplitude, wavelength of gaussian peak, profile width, fit covariance
            Fitted asymmetric gaussian parameters of amplitude, asymmetric paramter, width, fit covariance
            ValueError if input 'fit_type' is not 'gaussian' or 'asymmetric'
        """

        if self.fit_type == 'gaussian':
            popt, pcov = self.gaussfitting()
            return popt[0], popt[1], popt[2], pcov
        elif self.fit_type == 'asymmetric':
            popt, pcov = self.asymfitting()
            self.A, self.asym, self.d = popt
            width = self.cal_fwhm()
            return self.A, self.asym, self.d, width, pcov
        else:
            raise ValueError("fit_type must be either 'gaussian' or 'asymmetric'")
        
    def plot_fit(self):
        """
        This function plots the input wavelength and flux arrays along with the fitted profile
        """

        ind = (self.wavelength>self.line_l) & (self.wavelength<self.line_u)
        plt.figure(figsize=(8,5))
        plt.plot(self.wavelength, self.flux, label='Data', color='black')
        if self.fit_type == 'gaussian':
            popt, _ = self.gaussfitting()
            plt.plot(self.wavelength, self.gaussian(self.wavelength, *popt), label='Gaussian Fit', color='red')
        elif self.fit_type == 'asymmetric':
            popt, _ = self.asymfitting()
            plt.plot(self.wavelength[ind], self.asym_gaussian(self.wavelength[ind], *popt), label='Asymmetric Gaussian Fit', color='blue')
        plt.xlabel('Wavelength')
        plt.ylabel('Flux')
        plt.title('Emission Line Fit')
        plt.legend()
        plt.show()
