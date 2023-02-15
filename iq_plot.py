# -*- coding: utf-8 -*-

# This example configures the receiver for IQ acquisition and plots
# the spectrum of a single IQ acquisition.

from sadevice.sa_api import *

from scipy.signal import get_window
import matplotlib.pyplot as plt
import seaborn as sns; sns.set() # styling

def iq():
    # Open device
    handle = sa_open_device()["handle"]

    # Configure device
    sa_config_center_span(handle, 869.0e6, 1.0e3)
    sa_config_level(handle, -10.0)
    sa_config_IQ(handle, 1, 250.0e3);

    # Initialize
    sa_initiate(handle, SA_IQ, 0);

    # Get IQ data
    iq = sa_get_IQ_32f(handle)["iq"]

    # No longer need device, close
    sa_close_device(handle)

    # FFT and plot

    # Create window
    window = get_window("hamming", len(iq))
    # Normalize window
    window *= len(window) / sum(window)
    # Window, FFT, normalize FFT output
    iq_data_FFT = numpy.fft.fftshift(numpy.fft.fft(iq * window) / len(window))
    # Convert to dBm
    plt.plot(10 * numpy.log10(iq_data_FFT.real ** 2 + iq_data_FFT.imag ** 2))
    plt.show()

if __name__ == "__main__":
    iq()
