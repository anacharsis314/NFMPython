# -*- coding: utf-8 -*-

# This example tests the throughput of the IQ acquisition mode
# of the receiver. Adjust the DECIMATION parameter to decimate
# the IQ data stream. DECIMATION must be a power of two.
# You should see samples rates of 486 kS/sec / DECIMATION

from sadevice.sa_api import *
import datetime

NUM_CAPTURES = 1000
DECIMATION = 1

def stream_iq():
    # Open device
    handle = sa_open_device()["handle"]

    # Configure device
    sa_config_center_span(handle, 97.1e3, 1.0e3)
    sa_config_level(handle, -10.0)
    sa_config_IQ(handle, DECIMATION, 250.0e3);

    # Initialize
    sa_initiate(handle, SA_IQ, 0);
    return_len = sa_query_stream_info(handle)["return_len"]

    # Stream IQ
    print ("Streaming...")
    sample_count = 0
    start_time = datetime.datetime.now()
    for i in range(NUM_CAPTURES):
        iq = sa_get_IQ_32f(handle)["iq"]
        sample_count += return_len

    # Print stats
    time_diff = (datetime.datetime.now() - start_time).total_seconds()
    print (f"\nCaptured {sample_count} samples @ {sample_count / time_diff / 1e3} kilasamples/sec")

    # Close device
    sa_close_device(handle)


if __name__ == "__main__":
    stream_iq()
