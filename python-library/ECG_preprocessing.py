#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import neurokit
from QRSDetectorOffline import QRSDetectorOffline
import wfdb
from wfdb import processing
from hrvanalysis import remove_ectopic_beats, interpolate_nan_values

"""This script provides several methods to preprocess data from ECG data frame"""

def detect_QRS_peaks_pan_tompkin_algorithm(ecg, ecg_acquisition_frequency):
    # prepare timestamps and ecg for Pan Tompkin QRS detector
    timestamps = np.arange(0, ecg_acquisition_frequency * len(ecg), ecg_acquisition_frequency)
    ecg_raw_array = np.column_stack((timestamps, ecg))
    qrsdetector = QRSDetectorOffline(ecg_raw_array, verbose=False,log_data=False, plot_data=False, show_plot=False)
    peaks_detected = qrsdetector.get_peak_indices()
    return peaks_detected

def detect_QRS_complex(ecg, ecg_acquisition_frequency) :
    # Compute QRS complex detection with 6 differents algorithms
    R_peaks = {}
    ecg_processed_hamilton = neurokit.ecg_process(ecg=np.array(ecg), sampling_rate=ecg_acquisition_frequency, hrv_features=None, segmenter='hamilton')
    R_peaks["hamilton"] = ecg_processed_hamilton['ECG']['R_Peaks']

    R_peaks["pan-tompkins"] = detect_QRS_peaks_pan_tompkin_algorithm(ecg, ecg_acquisition_frequency)

    # Compute with Gqrs
    #R_peaks["gqrs"] = processing.gqrs_detect(sig=np.array(ecg), fs=250)

    # Compute with XQRS
    R_peaks["xqrs"] = processing.xqrs_detect(sig=np.array(ecg, dtype=np.single), fs=ecg_acquisition_frequency)

    return R_peaks

def get_rr_intervals_from_R_peaks_multi(R_peaks, ecg_acquisition_frequency):
    multi_rr_intervals ={}
    multi_rr_timestamps ={}
    for key, R_peaks_single in R_peaks.items():
        multi_rr_intervals[key], multi_rr_timestamps[key]  = get_rr_intervals_from_R_peaks(R_peaks_single, ecg_acquisition_frequency)

    return multi_rr_intervals, multi_rr_timestamps

def get_rr_intervals_from_R_peaks(R_peaks, ecg_acquisition_frequency):
    rr_intervals = []
    rr_timestamps = []
    for i in range(1, len(R_peaks)):
        rr_intervals.append((R_peaks[i] - R_peaks[i-1])/ecg_acquisition_frequency)
        rr_timestamps.append(R_peaks[i-1] / ecg_acquisition_frequency)
    return rr_intervals, rr_timestamps

def clean_rr_intervals_multi(rr_intervals, rr_timestamps, removal_method = 'malik', interpolation_method = 'linear'):
    multi_rr_intervals_corrected ={}
    multi_rr_timestamps_corrected ={}

    for key, rr_intervals_single in rr_intervals.items():
        multi_rr_intervals_corrected[key], multi_rr_timestamps_corrected[key] = clean_rr_intervals(rr_intervals[key], rr_timestamps[key], removal_method = removal_method, interpolation_method = interpolation_method)
    return multi_rr_intervals_corrected, multi_rr_timestamps_corrected

def clean_rr_intervals(rr_intervals, rr_timestamps, removal_method = 'malik', interpolation_method = 'linear'):
    rr_intervals_clean = remove_ectopic_beats(rr_intervals, removal_method)
    rr_intervals_corrected = interpolate_nan_values(rr_intervals_clean, interpolation_method ,limit=2)

    rr_timestamps_corrected = []
    timestamp = rr_timestamps[0]

    for i in range(0, len(rr_intervals_corrected)):
        rr_timestamps_corrected.append(timestamp)
        timestamp += rr_intervals_corrected[i]

    return rr_intervals_corrected, rr_timestamps_corrected

def get_raw_heart_rate_multi(rr_intervals):
    multi_raw_heart_rate = {}
    for key, rr_intervals_single in rr_intervals.items():
        multi_raw_heart_rate[key] = get_raw_heart_rate(rr_intervals_single)
    return multi_raw_heart_rate

def get_raw_heart_rate(rr_intervals):
    hr = [60/rri for rri in rr_intervals]
    return hr

def get_average_heart_rate_multi(rr_intervals, average_window_size = 6):
    multi_average_heart_rate = {}
    for key, rr_intervals_single in rr_intervals.items():
        multi_average_heart_rate[key] = get_average_heart_rate(rr_intervals_single, average_window_size)
    return multi_average_heart_rate


def get_average_heart_rate(rr_intervals, average_window_size = 6):
    hr = get_raw_heart_rate(rr_intervals)
    average_hr = pd.Series(hr).rolling(window=average_window_size).mean()
    return average_hr
