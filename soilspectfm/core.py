"""Scikit-learn compatible transforms for spectroscopic data preprocessing."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['SNV', 'MSC', 'TakeDerivative', 'WaveletDenoise', 'SavGolSmooth', 'ToAbsorbance', 'Resample']

# %% ../nbs/00_core.ipynb 3
from fastcore.all import *
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from scipy.signal import savgol_filter
from scipy.interpolate import CubicSpline
from typing import Callable
import pywt

# %% ../nbs/00_core.ipynb 7
class SNV(BaseEstimator, TransformerMixin):
    """
    Standard Normal Variate transformation with flexible centering and scaling.
    
    Common centering functions:
    
        - np.mean: Standard choice, sensitive to outliers
        - np.median: Robust to outliers, slower computation
        - np.min: Ensures positive values, sensitive to noise
        - lambda x, **kw: 0: No centering, preserves absolute values
    
    Common scaling functions:
    
        - np.std: Standard choice, assumes normal distribution
        - lambda x, **kw: np.sqrt(np.mean(x**2, **kw)): RMS, good for baseline variations
        - scipy.stats.iqr: Robust to outliers, ignores extreme peaks
        - lambda x, **kw: np.max(x, **kw) - np.min(x, **kw): Preserves relative peaks
        - lambda x, **kw: np.median(np.abs(x - np.median(x, **kw)), **kw): Most robust, slower
    """
    def __init__(self, 
                 center_func: Callable=np.mean, # Function to center the data
                 scale_func: Callable=np.std, # Function to scale the data
                 eps: float=1e-10 # Small value to avoid division by zero
                 ):
        store_attr()
    def fit(self, X, y=None): return self
    def transform(self, 
                  X: np.ndarray # Spectral data to be transformed
                  ) -> np.ndarray: # Transformed spectra
        center = self.center_func(X, axis=1, keepdims=True)
        scale = self.scale_func(X - center, axis=1, keepdims=True) + self.eps
        return (X - center) / scale

# %% ../nbs/00_core.ipynb 10
class MSC(BaseEstimator, TransformerMixin):
    "Multiplicative Scatter Correction with fastai-style implementation"
    def __init__(self, 
                 reference_method: Union[str, np.ndarray] = 'mean', # Method to compute reference spectrum ('mean'/'median') or custom reference spectrum
                 n_jobs: Optional[int] = None # Number of parallel jobs to run. None means using all processors
                 ):
        store_attr()
        self.reference_ = None
        
    def _compute_reference(self, x: np.ndarray):
        "Compute reference spectrum from array using specified method"
        if isinstance(self.reference_method, str):
            assert self.reference_method in ['mean', 'median'], "reference_method must be 'mean' or 'median'"
            return np.mean(x, axis=0) if self.reference_method == 'mean' else np.median(x, axis=0)
        return np.array(self.reference_method)
    
    def fit(self, X: np.ndarray, y=None):
        "Compute the reference spectrum"
        self.reference_ = self._compute_reference(X)
        return self
    
    def _transform_single(self, 
                          x: np.ndarray # Spectral data to be transformed
                          ) -> np.ndarray: # Transformed spectra
        "Transform a single spectrum"
        coef = np.polyfit(self.reference_, x, deg=1)
        return (x - coef[1]) / coef[0]
    
    def transform(self, 
                  X: np.ndarray # Spectral data to be transformed
                  ) -> np.ndarray: # Transformed spectra
        "Apply MSC to the spectra"
        if self.reference_ is None: raise ValueError("MSC not fitted. Call 'fit' first.")
        return np.array(parallel(self._transform_single, X, n_workers=self.n_jobs))

# %% ../nbs/00_core.ipynb 16
class TakeDerivative(BaseEstimator, TransformerMixin):
    "Creates scikit-learn derivation + savitsky-golay smoothing custom transformer"
    def __init__(self, 
                 window_length=11, # Window length for the savgol filter
                 polyorder=1, # Polynomial order for the savgol filter
                 deriv=1 # Derivation degree
                 ):
        self.window_length = window_length
        self.polyorder = polyorder
        self.deriv = deriv

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return savgol_filter(X, self.window_length, self.polyorder, self.deriv)

# %% ../nbs/00_core.ipynb 21
class WaveletDenoise(BaseEstimator, TransformerMixin):
    "Wavelet denoising transformer compatible with scikit-learn."    
    def __init__(self, 
                 wavelet:str='db6', # Wavelet to use for decomposition
                 level:Optional[int]=None, # Decomposition level. If None, maximum level is used
                 threshold_mode:str='soft' # Thresholding mode  ('soft'/'hard')
                 ):
        store_attr()
        
    def _denoise_single(self, spectrum):
        "Denoise a single spectrum"
        # If level is None, calculate maximum possible level
        if self.level is None:
            self.level_ = pywt.dwt_max_level(len(spectrum), 
                                             pywt.Wavelet(self.wavelet).dec_len)
        else:
            self.level_ = self.level
            
        coeffs = pywt.wavedec(spectrum, self.wavelet, level=self.level_)
        
        # Calculate threshold using MAD estimator
        detail_coeffs = np.concatenate([c for c in coeffs[1:]])
        sigma = np.median(np.abs(detail_coeffs)) / 0.6745
        threshold = sigma * np.sqrt(2 * np.log(len(spectrum)))
        
        # Apply threshold to detail coefficients
        new_coeffs = list(coeffs)
        for i in range(1, len(coeffs)):
            new_coeffs[i] = pywt.threshold(coeffs[i], 
                                         threshold * (1/2**((self.level_-i)/2)),
                                         mode=self.threshold_mode)

        denoised = pywt.waverec(new_coeffs, self.wavelet)
        return denoised[:len(spectrum)]
    
    def fit(self, X, y=None):
        "Fit the transformer (no-op)"
        return self
    
    def transform(self, X):
        "Apply wavelet denoising to spectra."
        X = np.asarray(X)
        X_denoised = np.zeros_like(X)
        for i in range(X.shape[0]): X_denoised[i] = self._denoise_single(X[i])
        return X_denoised

# %% ../nbs/00_core.ipynb 23
class SavGolSmooth(BaseEstimator, TransformerMixin):
    "Savitzky-Golay smoothing transformer compatible with scikit-learn."
    def __init__(self, 
                 window_length:int=15, # Window length for the savgol filter
                 polyorder:int=3, # Polynomial order for the savgol filter
                 deriv:int=0 # Derivation degree
                 ):
        store_attr()
        
    def _validate_params(self):
        "Validate parameters."
        if self.window_length % 2 == 0:
            raise ValueError("window_length must be odd")
        if self.window_length <= self.polyorder:
            raise ValueError("window_length must be greater than polyorder")
        if self.deriv > self.polyorder:
            raise ValueError("deriv must be <= polyorder")
            
    def fit(self, 
            X:np.ndarray,# Spectral data to be smoothed.
            y:Optional[np.ndarray]=None # Ignored
            ):
        "Validate parameters and fit the transformer."
        self._validate_params()
        return self
    
    def transform(self, 
                  X: np.ndarray # Spectral data to be smoothed.
                  ) -> np.ndarray: # Smoothed spectra
        "Apply Savitzky-Golay filter to spectra."
        X = np.asarray(X)
        X_smoothed = np.zeros_like(X)
        
        for i in range(X.shape[0]):
            X_smoothed[i] = savgol_filter(X[i], 
                                        window_length=self.window_length,
                                        polyorder=self.polyorder,
                                        deriv=self.deriv)
        
        return X_smoothed

# %% ../nbs/00_core.ipynb 26
class ToAbsorbance(BaseEstimator, TransformerMixin):
    "Creates scikit-learn transformer to transform reflectance to absorbance"
    def __init__(self, 
                 eps: float=1e-5 # Small value to avoid log(0)
                 ): self.eps = eps
    def fit(self, X, y=None): return self
    def transform(self, X, y=None): return -np.log10(np.clip(X, self.eps, 1))

# %% ../nbs/00_core.ipynb 27
class Resample(BaseEstimator, TransformerMixin):
    "Resampling transformer compatible with scikit-learn."
    def __init__(self, 
                 target_x: np.ndarray, # Target x-axis points (wavenumbers or wavelengths) for resampling
                 interpolation_kind: str='cubic' # Type of spline interpolation to use
                 ):
        store_attr()
        
    def fit(self, 
            X: np.ndarray, # Spectral data to be resampled
            x: np.ndarray=None, # Original x-axis points (wavenumbers or wavelengths)
            y: np.ndarray=None # Original y-axis points
            ):
        "Fit the transformer"
        if x is None: raise ValueError("Original x-axis (wavenumbers or wavelengths) must be provided")
        self.original_x_ = np.asarray(x)
        return self
    
    def transform(self, 
                  X: np.ndarray # Spectral data to be resampled
                  ):
        "Resample spectra to new x-axis points."
        X = np.asarray(X)
        X_transformed = np.zeros((X.shape[0], len(self.target_x)))
        
        for i in range(X.shape[0]):
            cs = CubicSpline(self.original_x_, X[i])
            X_transformed[i] = cs(self.target_x)
        
        return X_transformed
