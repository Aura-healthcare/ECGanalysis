#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scipy import interpolate
import numpy as np

RR_INTERVALS_TOLERANCE = 0.050 # in seconds
MINIMUM_INCORRECT_INTERVAL_WIDTH = 3 # in seconds
RESAMPLING_PERIOD = 0.25 # in seconds

def filter_bad_signal_quality_intervals(reference_rr_intevals, reference_timestamps, alternative_rr_intervals, alternative_timestamps, rr_interval_tolerance = RR_INTERVALS_TOLERANCE, minimum_interval_width = MINIMUM_INCORRECT_INTERVAL_WIDTH):
    bad_quality_intervals = []

    margin_safe_alt_timestamps = np.array(alternative_timestamps)
    margin_safe_alt_rr_intervals = np.array(alternative_rr_intervals)

    # add margins to include the full reference interval
    if margin_safe_alt_timestamps[0] > reference_timestamps[0]:
        margin_safe_alt_timestamps = np.insert(margin_safe_alt_timestamps, 0, reference_timestamps[0])
        margin_safe_alt_rr_intervals = np.insert(margin_safe_alt_rr_intervals, 0, 0)

    if margin_safe_alt_timestamps[-1] < reference_timestamps[-1]:
        margin_safe_alt_timestamps = np.append(margin_safe_alt_timestamps, reference_timestamps[-1])
        margin_safe_alt_rr_intervals = np.append(margin_safe_alt_rr_intervals, 0)

    #resample signals to get a regular sampling
    ref_flinear = interpolate.interp1d(reference_timestamps, reference_rr_intevals)
    alt_flinear = interpolate.interp1d(margin_safe_alt_timestamps, margin_safe_alt_rr_intervals)

    resampled_timestamps = np.arange(reference_timestamps[0], reference_timestamps[-1], RESAMPLING_PERIOD) # resample to 0.25s
    resampled_ref_rr_intervals = ref_flinear(resampled_timestamps)
    resampled_alt_rr_intervals = alt_flinear(resampled_timestamps)

    ## Detect bad intervals
    bad_interval = [0.0, 0.0]
    is_in_bad_interval = False

    for i in range(0, len(resampled_ref_rr_intervals)):
        if is_correct_value(resampled_ref_rr_intervals[i], resampled_alt_rr_intervals[i], rr_interval_tolerance):
            if is_in_bad_interval:
                bad_interval[1] = resampled_timestamps[i]
                bad_quality_intervals.append(bad_interval)
                bad_interval = [0.0, 0.0]
                is_in_bad_interval = False
        else:
            if not is_in_bad_interval:
                bad_interval[0] = resampled_timestamps[i]
                is_in_bad_interval = True

    if is_in_bad_interval:
        bad_interval[1] = resampled_timestamps[-1]
        bad_quality_intervals.append(bad_interval)

    # Clean too small bad intervals
    filtered_too_small_bad_quality_intervals = [interval for interval in bad_quality_intervals if abs(interval[1] - interval[0]) > minimum_interval_width]
    #print(filtered_too_small_bad_quality_intervals)

    # Clean too small good intervals
    filtered_too_small_good_quality_intervals = []

    if len(filtered_too_small_bad_quality_intervals) >= 2:
        current_interval_start = filtered_too_small_bad_quality_intervals[0][0]
        for i in range (0, len(filtered_too_small_bad_quality_intervals) - 1):
            if (filtered_too_small_bad_quality_intervals[i + 1][0] - filtered_too_small_bad_quality_intervals[i][1]) > minimum_interval_width:
                filtered_too_small_good_quality_intervals.append([current_interval_start, filtered_too_small_bad_quality_intervals[i][1]])
                current_interval_start = filtered_too_small_bad_quality_intervals[i + 1][0]

        filtered_too_small_good_quality_intervals.append([current_interval_start, filtered_too_small_bad_quality_intervals[-1][1]])
    else:
        filtered_too_small_good_quality_intervals = filtered_too_small_bad_quality_intervals

    return filtered_too_small_good_quality_intervals

def is_correct_value(reference_value, alternative_value, rr_interval_tolerance) -> bool:
    return abs(reference_value - alternative_value) < rr_interval_tolerance
