# -*- coding: utf-8 -*-

# This example configures the receiver for a basic sweep and
# plots the sweep. The x-axis frequency is derived from the start_freq
# and bin_size values returned after configuring the device.

from sadevice.sa_api import *

import matplotlib.pyplot as plt
import seaborn as sns; sns.set() # styling
import os



def sweep():
    # Open device
    handle = sa_open_device()["handle"]

    # Configure device
    sa_config_center_span(handle, 64e6, 15e6)
    sa_config_level(handle, -30.0)
    sa_config_sweep_coupling(handle, 10e3, 10e3, 0)
    sa_config_acquisition(handle, SA_MIN_MAX, SA_LOG_SCALE)

    # Initialize
    sa_initiate(handle, SA_SWEEPING, 0)
    query = sa_query_sweep_info(handle)
    sweep_length = query["sweep_length"]
    start_freq = query["start_freq"]
    bin_size = query["bin_size"]

    # Get sweep
    sweep_max = sa_get_sweep_32f(handle)["max"]

    # Device no longer needed, close it
    sa_close_device(handle)

    # Plot
    freqs = [start_freq + i * bin_size for i in range(sweep_length)]
    plt.plot(freqs, sweep_max)
    plt.show()

if __name__ == "__main__":
    sweep()
