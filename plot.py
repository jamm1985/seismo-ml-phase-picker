import os
import sys
import logging
import random

from obspy.core import read
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
import getopt

import utils.picks_slicing as picks
import utils.seisan_reader as seisan
import utils.converter as converter
import config.vars as config

# Main function body
if __name__ == "__main__":
    """
    Plots traces from provided list
    """
    # Root path to picks
    basepath = '/home/chernykh/201608/ARGI201493IM00/'

    # Picks and actions
    end_path = [('ARGI201493SHEIM00.NOISE.SHE.N', '111'),
                ('ARGI201493SHNIM00.NOISE.SHN.N', '111'),
                ('ARGI201493SHZIM00.NOISE.SHZ.N', '111')]
    # actions: Detrend, Filter, Normalize

    # Where to save plot
    patho = '/home/chernykh/dev/seismo-ml-phase-picker/'

    for x in end_path:
        path = basepath + x[0]

        st = read(path)
        out_path = patho + x[0] + '.png'

        if x[1][0] == '1':
            st.detrend(type='linear')

        if x[1][1] == '1':
            st.filter("highpass", freq=config.highpass_filter_df)

        if x[1][2] == '1':
            st.normalize(global_max=config.global_max_normalizing)

        plot = st.plot(outfile=out_path)