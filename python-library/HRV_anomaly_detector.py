import statistics

BASELINE_SEIZURE_OFFSET = -15 * 60 # in seconds - start 15 min before seizure seizure_event
BASELINE_WIDTH = 5 * 60 # in seconds - 5 minutes baseline

INTERVAL_STATUS_INVALID = (0, "INTERVAL_INVALID")
INTERVAL_STATUS_NORMAL = (1, "INTERVAL NORMAL")
INTERVAL_STATUS_LOW_TACHYCARDIA = (2, "INTERVAL LOW TACHYCARDIA")
INTERVAL_STATUS_HIGH_TACHYCARDIA = (3, "INTERVAL HIGH TACHYCARDIA")
INTERVAL_STATUS_LOW_BRADYCARDIA = (4, "INTERVAL LOW BRADYCARDIA")
INTERVAL_STATUS_HIGH_BRADYCARDIA = (5, "INTERVAL HIGH BRADYCARDIA")

LOW_TACHYCARDIA_THRESHOLD = 10 # in bpm
HIGH_TACHYCARDIA_THRESHOLD = 20 # in bpm
LOW_BRADYCARDIA_THRESHOLD = 10 # in bpm
HIGH_BRADYCARDIA_THRESHOLD = 20 # in bpm

def get_baseline_range(seizure_event, baseline_seizure_offset = BASELINE_SEIZURE_OFFSET, baseline_width = BASELINE_WIDTH):
    baseline_start = seizure_event + baseline_seizure_offset
    baseline_end = baseline_start + baseline_width

    # return baseline range if exists, if baseline is out of the existing interval return null
    if baseline_start >= 0:
        return [baseline_start, baseline_end]
    else:
        return None

def compute_baseline(rr_intervals, rr_timestamps, baseline_range):
    rr_baseline = []
    for i in range(0, len(rr_timestamps)):
        if rr_timestamps[i] > baseline_range[0] and rr_timestamps[i] < baseline_range[1]:
            rr_baseline.append(rr_intervals[i])

    rr_baseline_mean = statistics.mean(rr_baseline)
    return rr_baseline_mean

def is_in_invalid_interval(bad_intervals, timestamp):
    for i in range(0, len(bad_intervals)):
        if timestamp > bad_intervals[i][0] and timestamp < bad_intervals[i][1]:
            return True
    return False

def is_cardiac_anomaly(baseline, rr_interval):
    hr_baseline = 60.0 / baseline
    hr = 60.0 / rr_interval
    if hr > (hr_baseline + HIGH_TACHYCARDIA_THRESHOLD):
        return INTERVAL_STATUS_HIGH_TACHYCARDIA
    elif hr > (hr_baseline + LOW_TACHYCARDIA_THRESHOLD):
        return INTERVAL_STATUS_LOW_TACHYCARDIA
    elif hr < (hr_baseline - HIGH_BRADYCARDIA_THRESHOLD):
        return INTERVAL_STATUS_HIGH_BRADYCARDIA
    elif hr < (hr_baseline - LOW_BRADYCARDIA_THRESHOLD):
        return INTERVAL_STATUS_LOW_BRADYCARDIA
    else:
        return INTERVAL_STATUS_NORMAL



def get_status(bad_intervals, baseline, rr_interval, timestamp):
    if is_in_invalid_interval(bad_intervals, timestamp):
        return INTERVAL_STATUS_INVALID

    return is_cardiac_anomaly(baseline, rr_interval)


def detect_anomalies(rr_intervals, rr_timestamps, bad_intervals, baseline, analysis_interval):

    previous_status = INTERVAL_STATUS_NORMAL
    interval_start_timestamp = rr_timestamps[0]
    anomalies_intervals = {
        INTERVAL_STATUS_INVALID[1]:[],
        INTERVAL_STATUS_NORMAL[1]:[],
        INTERVAL_STATUS_LOW_TACHYCARDIA[1]:[],
        INTERVAL_STATUS_HIGH_TACHYCARDIA[1]:[],
        INTERVAL_STATUS_LOW_BRADYCARDIA[1]:[],
        INTERVAL_STATUS_HIGH_BRADYCARDIA[1]:[]
    }

    # Detect anomaly intervals
    for i in range(1, len(rr_timestamps)):
        status = get_status(bad_intervals, baseline, rr_intervals[i], rr_timestamps[i])
        # Close interval
        if status != previous_status:
            anomalies_intervals[previous_status[1]].append( [interval_start_timestamp, rr_timestamps[i]] )
            interval_start_timestamp = rr_timestamps[i]
            previous_status = status

    anomalies_intervals[status[1]].append( [interval_start_timestamp, rr_timestamps[-1]] )

    # Manually add first and last invalid interval
    if rr_timestamps[0] > analysis_interval[0]:
        anomalies_intervals[INTERVAL_STATUS_INVALID[1]].append([analysis_interval[0], rr_timestamps[0]])

    if rr_timestamps[-1] < analysis_interval[1]:
        anomalies_intervals[INTERVAL_STATUS_INVALID[1]].append([rr_timestamps[-1], analysis_interval[1]])

    return anomalies_intervals

def convert_anomaly_interval_to_bar_coordinates(anomalies_intervals):
        bar_coordinates = {
            "intervals":{
                INTERVAL_STATUS_INVALID[1]:[],
                INTERVAL_STATUS_NORMAL[1]:[],
                INTERVAL_STATUS_LOW_TACHYCARDIA[1]:[],
                INTERVAL_STATUS_HIGH_TACHYCARDIA[1]:[],
                INTERVAL_STATUS_LOW_BRADYCARDIA[1]:[],
                INTERVAL_STATUS_HIGH_BRADYCARDIA[1]:[]
            },
            "colors":{
                INTERVAL_STATUS_INVALID[1]:"grey",
                INTERVAL_STATUS_NORMAL[1]: "white",
                INTERVAL_STATUS_LOW_TACHYCARDIA[1]:"yellow",
                INTERVAL_STATUS_HIGH_TACHYCARDIA[1]:"red",
                INTERVAL_STATUS_LOW_BRADYCARDIA[1]:"lightblue",
                INTERVAL_STATUS_HIGH_BRADYCARDIA[1]:"darkblue"
            }
        }

        for key, value in anomalies_intervals.items():
            for interval in anomalies_intervals[key]:
                bar_coordinates["intervals"][key].append( (interval[0], interval[1] - interval[0]) )

        return bar_coordinates
