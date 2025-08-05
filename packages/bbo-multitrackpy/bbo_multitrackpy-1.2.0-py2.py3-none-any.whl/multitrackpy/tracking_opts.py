def get_default_opts():
    return {
        'mtt_file': '',
        'video_dir': '',
        'mvd_file': 'None',  # '' would make flag non-optional
        'frame_idxs': None,
        'frame_maps': None,
        'linedist_thres': 0.2,
        # Max distance between two cam lines to assume that the respective detections come from the same LED (calibration units)
        'corr_thres': 0.1,
        # Max diffeerence in point distance for correlation between model and detection (calibration units)
        'led_thres': 150,  # Minimal brightness of LED after image processing (image brightness units)
        'led_maxpixels': 5000,  # Maximal number of pixels above threshold accepted. This is usually exceed by either very overexposed leds (barely) or visible light images (by oders of magnitude)
        'n_cpu': 2,
        'track_ambiguous': False,
        'debug': 0
    }


def check_globalopts(gopts):
    return (all(name in get_default_opts() for name in gopts) and
            all(name in gopts for name in get_default_opts()))
