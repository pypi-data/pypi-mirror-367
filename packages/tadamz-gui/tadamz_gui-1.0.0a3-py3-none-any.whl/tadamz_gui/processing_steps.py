def add_basic_processing_steps(config):
    config["processing_steps"] = [
        "extract_peaks",
        "classify_peaks",
        "coeluting_peaks",
    ]

    return config


def add_abs_quant_is(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("normalize_peaks")

    config["postprocessings"] = ["postprocessing1", "quantification"]
    config["postprocessing1"] = [
        "classify_peaks",
        "coeluting_peaks",
        "normalize_peaks",
    ]
    config["quantification"] = ["quantify"]

    return config


def add_abs_quant_no_norm(config):
    config = add_basic_processing_steps(config)

    config["postprocessings"] = ["postprocessing1", "quantification"]
    config["postprocessing1"] = [
        "classify_peaks",
        "coeluting_peaks",
    ]
    config["quantification"] = ["quantify"]
    # The calibration step must use the area_chromatogram column instead of the default normalized_area_chromatogram
    config["calibrate"]["value_col"] = "area_chromatogram"

    return config


def add_rel_quant_no_norm(config):
    config = add_basic_processing_steps(config)

    config["postprocessings"] = ["postprocessing1"]
    config["postprocessing1"] = [
        "classify_peaks",
        "coeluting_peaks",
    ]

    return config


def add_rel_quant_TIC(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("tic_normalize_peaks")

    config["postprocessings"] = ["postprocessing1"]
    config["postprocessing1"] = [
        "classify_peaks",
        "coeluting_peaks",
        "tic_normalize_peaks",
    ]

    return config


def add_rel_quant_PQN(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("pq_normalize_peaks")

    config["postprocessings"] = ["postprocessing1", "pqn"]
    config["postprocessing1"] = [
        "classify_peaks",
        "coeluting_peaks",
    ]
    config["pqn"] = [
        "pq_normalize_peaks",
    ]

    return config


def add_rel_quant_IS(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("normalize_peaks")

    config["postprocessings"] = ["postprocessing1"]
    config["postprocessing1"] = [
        "classify_peaks",
        "coeluting_peaks",
        "normalize_peaks",
    ]

    return config


def add_check_qualifier_peaks(config):
    config["processing_steps"].append("check_qualifier_peaks")
    config["postprocessing1"].append("check_qualifier_peaks")

    return config
