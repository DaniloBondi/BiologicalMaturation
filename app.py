from shiny import App, ui, render, reactive
import math


KR_BOYS = {
    4.0:  (-10.2567, 1.23812, -0.087235, 0.50286),
    4.5:  (-10.7190, 1.15964, -0.074454, 0.52887),
    5.0:  (-11.0213, 1.10674, -0.064778, 0.53919),
    5.5:  (-11.1556, 1.07480, -0.057760, 0.53691),
    6.0:  (-11.1138, 1.05923, -0.052947, 0.52513),
    6.5:  (-11.0221, 1.05542, -0.049892, 0.50692),
    7.0:  (-10.9984, 1.05877, -0.048144, 0.48538),
    7.5:  (-11.0214, 1.06467, -0.047256, 0.46361),
    8.0:  (-11.0696, 1.06853, -0.046778, 0.44469),
    8.5:  (-11.1220, 1.06572, -0.046261, 0.43171),
    9.0:  (-11.1571, 1.05166, -0.045254, 0.42776),
    9.5:  (-11.1405, 1.02174, -0.043311, 0.43593),
    10.0: (-11.0380, 0.97135, -0.039981, 0.45932),
    10.5: (-10.8286, 0.89589, -0.034814, 0.50101),
    11.0: (-10.4917, 0.81239, -0.029050, 0.54781),
    11.5: (-10.0065, 0.74134, -0.024167, 0.58409),
    12.0: (-9.3522,  0.68325, -0.020076, 0.60927),
    12.5: (-8.6055,  0.63869, -0.016681, 0.62279),
    13.0: (-7.8632,  0.60818, -0.013895, 0.62407),
    13.5: (-7.1348,  0.59228, -0.011624, 0.61253),
    14.0: (-6.4299,  0.59151, -0.009776, 0.58762),
    14.5: (-5.7578,  0.60643, -0.008261, 0.54875),
    15.0: (-5.1282,  0.63757, -0.006988, 0.49536),
    15.5: (-4.5092,  0.68548, -0.005863, 0.42687),
    16.0: (-3.9292,  0.75069, -0.004795, 0.34271),
    16.5: (-3.4873,  0.83375, -0.003695, 0.24231),
    17.0: (-3.2830,  0.93520, -0.002470, 0.12510),
    17.5: (-3.4156,  1.05558, -0.001027, -0.00950),
}


KR_GIRLS = {
    4.0:  (-8.13250, 1.24768, -0.19435, 0.44774),
    4.5:  (-6.47656, 1.22177, -0.18519, 0.41381),
    5.0:  (-5.13582, 1.19932, -0.17530, 0.38467),
    5.5:  (-4.13791, 1.17880, -0.16484, 0.36039),
    6.0:  (-3.51039, 1.15866, -0.15400, 0.34105),
    6.5:  (-3.14322, 1.13737, -0.14294, 0.32672),
    7.0:  (-2.87645, 1.11342, -0.13184, 0.31748),
    7.5:  (-2.66291, 1.08525, -0.12086, 0.31340),
    8.0:  (-2.45559, 1.05135, -0.11019, 0.31457),
    8.5:  (-2.20728, 1.01018, -0.09999, 0.32105),
    9.0:  (-1.87098, 0.96020, -0.09044, 0.33291),
    9.5:  (-1.06330, 0.89989, -0.08171, 0.35025),
    10.0: (0.33468, 0.82771, -0.07397, 0.37312),
    10.5: (1.97366, 0.74213, -0.06739, 0.40161),
    11.0: (3.50436, 0.67173, -0.06136, 0.42042),
    11.5: (4.57747, 0.64150, -0.05518, 0.41686),
    12.0: (4.84365, 0.64452, -0.04894, 0.39490),
    12.5: (4.27869, 0.67386, -0.04272, 0.35850),
    13.0: (3.21417, 0.72260, -0.03661, 0.31163),
    13.5: (1.83456, 0.78383, -0.03067, 0.25826),
    14.0: (0.32425, 0.85062, -0.02500, 0.20235),
    14.5: (-1.13224, 0.91605, -0.01967, 0.14787),
    15.0: (-2.35055, 0.97319, -0.01477, 0.09880),
    15.5: (-3.10326, 1.01514, -0.01037, 0.05909),
    16.0: (-3.17885, 1.03496, -0.00655, 0.03272),
    16.5: (-2.41657, 1.02573, -0.00340, 0.02364),
    17.0: (-0.65579, 0.98054, -0.00100, 0.03584),
    17.5: (2.26429, 0.89246, 0.000570, 0.07327),
}


# Mills & Nelson (2016) Multiplier method coefficients
MILLS_NELSON_BOYS = {
    0.00: 3.535, 0.08: 3.435, 0.17: 3.335, 0.25: 3.236, 0.33: 3.136, 0.42: 3.036,
    0.50: 2.936, 0.58: 2.836, 0.67: 2.736, 0.75: 2.637, 0.83: 2.537, 0.92: 2.437,
    1.00: 2.337, 1.08: 2.313, 1.17: 2.288, 1.25: 2.264, 1.33: 2.240, 1.42: 2.215,
    1.50: 2.191, 1.58: 2.167, 1.67: 2.142, 1.75: 2.118, 1.83: 2.094, 1.92: 2.069,
    2.00: 2.045, 2.08: 2.030, 2.17: 2.014, 2.25: 1.999, 2.33: 1.983, 2.42: 1.968,
    2.50: 1.952, 2.58: 1.937, 2.67: 1.921, 2.75: 1.906, 2.83: 1.890, 2.92: 1.875,
    3.00: 1.859, 3.08: 1.848, 3.17: 1.838, 3.25: 1.827, 3.33: 1.816, 3.42: 1.806,
    3.50: 1.795, 3.58: 1.784, 3.67: 1.774, 3.75: 1.763, 3.83: 1.752, 3.92: 1.742,
    4.00: 1.731, 4.08: 1.722, 4.17: 1.714, 4.25: 1.705, 4.33: 1.696, 4.42: 1.688,
    4.50: 1.679, 4.58: 1.670, 4.67: 1.662, 4.75: 1.653, 4.83: 1.644, 4.92: 1.636,
    5.00: 1.627, 5.08: 1.619, 5.17: 1.612, 5.25: 1.604, 5.33: 1.596, 5.42: 1.589,
    5.50: 1.581, 5.58: 1.573, 5.67: 1.566, 5.75: 1.558, 5.83: 1.550, 5.92: 1.543,
    6.00: 1.535, 6.08: 1.528, 6.17: 1.522, 6.25: 1.515, 6.33: 1.508, 6.42: 1.502,
    6.50: 1.495, 6.58: 1.488, 6.67: 1.482, 6.75: 1.475, 6.83: 1.468, 6.92: 1.462,
    7.00: 1.455, 7.08: 1.449, 7.17: 1.443, 7.25: 1.437, 7.33: 1.431, 7.42: 1.425,
    7.50: 1.419, 7.58: 1.413, 7.67: 1.407, 7.75: 1.401, 7.83: 1.395, 7.92: 1.389,
    8.00: 1.383, 8.08: 1.378, 8.17: 1.373, 8.25: 1.368, 8.33: 1.363, 8.42: 1.358,
    8.50: 1.353, 8.58: 1.347, 8.67: 1.342, 8.75: 1.337, 8.83: 1.332, 8.92: 1.327,
    9.00: 1.322, 9.08: 1.318, 9.17: 1.315, 9.25: 1.311, 9.33: 1.307, 9.42: 1.304,
    9.50: 1.300, 9.58: 1.296, 9.67: 1.293, 9.75: 1.289, 9.83: 1.285, 9.92: 1.282,
    10.00: 1.278, 10.08: 1.274, 10.17: 1.271, 10.25: 1.267, 10.33: 1.264, 10.42: 1.260,
    10.50: 1.257, 10.58: 1.253, 10.67: 1.249, 10.75: 1.246, 10.83: 1.242, 10.92: 1.239,
    11.00: 1.235, 11.08: 1.231, 11.17: 1.227, 11.25: 1.223, 11.33: 1.219, 11.42: 1.215,
    11.50: 1.211, 11.58: 1.206, 11.67: 1.202, 11.75: 1.198, 11.83: 1.194, 11.92: 1.190,
    12.00: 1.186, 12.08: 1.182, 12.17: 1.178, 12.25: 1.173, 12.33: 1.169, 12.42: 1.165,
    12.50: 1.161, 12.58: 1.156, 12.67: 1.152, 12.75: 1.148, 12.83: 1.144, 12.92: 1.139,
    13.00: 1.135, 13.08: 1.131, 13.17: 1.126, 13.25: 1.122, 13.33: 1.117, 13.42: 1.113,
    13.50: 1.108, 13.58: 1.104, 13.67: 1.099, 13.75: 1.095, 13.83: 1.090, 13.92: 1.086,
    14.00: 1.081, 14.08: 1.078, 14.17: 1.075, 14.25: 1.072, 14.33: 1.069, 14.42: 1.066,
    14.50: 1.063, 14.58: 1.059, 14.67: 1.056, 14.75: 1.053, 14.83: 1.050, 14.92: 1.047,
    15.00: 1.044, 15.08: 1.042, 15.17: 1.040, 15.25: 1.038, 15.33: 1.036, 15.42: 1.034,
    15.50: 1.033, 15.58: 1.031, 15.67: 1.029, 15.75: 1.027, 15.83: 1.025, 15.92: 1.023,
    16.00: 1.021, 16.08: 1.020, 16.17: 1.019, 16.25: 1.018, 16.33: 1.017, 16.42: 1.016,
    16.50: 1.016, 16.58: 1.015, 16.67: 1.014, 16.75: 1.013, 16.83: 1.012, 16.92: 1.011,
    17.00: 1.010, 17.08: 1.010, 17.17: 1.009, 17.25: 1.009, 17.33: 1.008, 17.42: 1.008,
    17.50: 1.008, 17.58: 1.007, 17.67: 1.007, 17.75: 1.006, 17.83: 1.006, 17.92: 1.005,
    18.00: 1.005,
}

MILLS_NELSON_GIRLS = {
    0.00: 3.290, 0.08: 3.201, 0.17: 3.111, 0.25: 3.022, 0.33: 2.932, 0.42: 2.843,
    0.50: 2.753, 0.58: 1.965, 0.67: 2.574, 0.75: 2.485, 0.83: 2.395, 0.92: 2.306,
    1.00: 2.216, 1.08: 2.190, 1.17: 2.166, 1.25: 2.141, 1.33: 2.116, 1.42: 2.091,
    1.50: 2.067, 1.58: 2.042, 1.67: 2.017, 1.75: 1.992, 1.83: 1.967, 1.92: 1.942,
    2.00: 1.917, 2.08: 1.902, 2.17: 1.887, 2.25: 1.987, 2.33: 1.856, 2.42: 1.841,
    2.50: 1.826, 2.58: 1.811, 2.67: 1.796, 2.75: 1.781, 2.83: 1.765, 2.92: 1.750,
    3.00: 1.735, 3.08: 1.726, 3.17: 1.716, 3.25: 1.707, 3.33: 1.697, 3.42: 1.688,
    3.50: 1.679, 3.58: 1.669, 3.67: 1.660, 3.75: 1.650, 3.83: 1.641, 3.92: 1.631,
    4.00: 1.622, 4.08: 1.613, 4.17: 1.604, 4.25: 1.595, 4.33: 1.586, 4.42: 1.577,
    4.50: 1.568, 4.58: 1.559, 4.67: 1.550, 4.75: 1.541, 4.83: 1.532, 4.92: 1.523,
    5.00: 1.514, 5.08: 1.506, 5.17: 1.499, 5.25: 1.491, 5.33: 1.483, 5.42: 1.475,
    5.50: 1.468, 5.58: 1.460, 5.67: 1.452, 5.75: 1.444, 5.83: 1.437, 5.92: 1.429,
    6.00: 1.421, 6.08: 1.414, 6.17: 1.408, 6.25: 1.401, 6.33: 1.394, 6.42: 1.388,
    6.50: 1.381, 6.58: 1.374, 6.67: 1.368, 6.75: 1.361, 6.83: 1.354, 6.92: 1.348,
    7.00: 1.341, 7.08: 1.336, 7.17: 1.331, 7.25: 1.326, 7.33: 1.320, 7.42: 1.315,
    7.50: 1.310, 7.58: 1.305, 7.67: 1.300, 7.75: 1.295, 7.83: 1.289, 7.92: 1.284,
    8.00: 1.279, 8.08: 1.275, 8.17: 1.271, 8.25: 1.267, 8.33: 1.262, 8.42: 1.258,
    8.50: 1.254, 8.58: 1.250, 8.67: 1.246, 8.75: 1.242, 8.83: 1.237, 8.92: 1.233,
    9.00: 1.229, 9.08: 1.225, 9.17: 1.221, 9.25: 1.218, 9.33: 1.214, 9.42: 1.210,
    9.50: 1.206, 9.58: 1.202, 9.67: 1.198, 9.75: 1.195, 9.83: 1.191, 9.92: 1.187,
    10.00: 1.183, 10.08: 1.179, 10.17: 1.175, 10.25: 1.171, 10.33: 1.167, 10.42: 1.163,
    10.50: 1.159, 10.58: 1.155, 10.67: 1.151, 10.75: 1.147, 10.83: 1.143, 10.92: 1.139,
    11.00: 1.135, 11.08: 1.131, 11.17: 1.126, 11.25: 1.122, 11.33: 1.117, 11.42: 1.113,
    11.50: 1.109, 11.58: 1.104, 11.67: 1.100, 11.75: 1.095, 11.83: 1.091, 11.92: 1.086,
    12.00: 1.082, 12.08: 1.079, 12.17: 1.075, 12.25: 1.072, 12.33: 1.068, 12.42: 1.065,
    12.50: 1.061, 12.58: 1.058, 12.67: 1.054, 12.75: 1.051, 12.83: 1.047, 12.92: 1.044,
    13.00: 1.040, 13.08: 1.038, 13.17: 1.037, 13.25: 1.035, 13.33: 1.033, 13.42: 1.031,
    13.50: 1.030, 13.58: 1.028, 13.67: 1.026, 13.75: 1.024, 13.83: 1.023, 13.92: 1.021,
    14.00: 1.019, 14.08: 1.018, 14.17: 1.017, 14.25: 1.016, 14.33: 1.015, 14.42: 1.014,
    14.50: 1.014, 14.58: 1.013, 14.67: 1.012, 14.75: 1.011, 14.83: 1.010, 14.92: 1.009,
    15.00: 1.008, 15.08: 1.008, 15.17: 1.007, 15.25: 1.007, 15.33: 1.007, 15.42: 1.006,
    15.50: 1.006, 15.58: 1.006, 15.67: 1.005, 15.75: 1.005, 15.83: 1.005, 15.92: 1.004,
    16.00: 1.004, 16.08: 1.004, 16.17: 1.004, 16.25: 1.004, 16.33: 1.003, 16.42: 1.003,
    16.50: 1.003, 16.58: 1.003, 16.67: 1.003, 16.75: 1.003, 16.83: 1.002, 16.92: 1.002,
    17.00: 1.002, 17.08: 1.000, 17.17: 1.000, 17.25: 1.000, 17.33: 1.000, 17.42: 1.000,
    17.50: 1.000, 17.58: 1.000, 17.67: 1.000, 17.75: 1.000, 17.83: 1.000, 17.92: 1.000,
    18.00: 1.000,
}


def _interpolate_coefficients(age, table):
    """Linear interpolation between the published half-year rows."""
    ages = sorted(table)

    if age < ages[0] or age > ages[-1]:
        return None

    if age in table:
        return table[age]

    lower = max(a for a in ages if a < age)
    upper = min(a for a in ages if a > age)

    fraction = (age - lower) / (upper - lower)

    return tuple(
        table[lower][i] +
        fraction * (table[upper][i] - table[lower][i])
        for i in range(4)
    )


def _interpolate_multiplier(age, table):
    """Linear interpolation for Mills & Nelson multiplier coefficients."""
    ages = sorted(table)

    if age < ages[0] or age > ages[-1]:
        return None

    if age in table:
        return table[age]

    lower = max(a for a in ages if a < age)
    upper = min(a for a in ages if a > age)

    fraction = (age - lower) / (upper - lower)

    return table[lower] + fraction * (table[upper] - table[lower])


def predict_khamis_roche(
    height_cm,
    weight_kg,
    age_years,
    mother_height_cm,
    father_height_cm,
    sex,
):
    """
    Khamis-Roche prediction.

    Input:
        height_cm              current standing height
        weight_kg              current body mass
        age_years              chronological age
        mother_height_cm       mother's adult height
        father_height_cm       father's adult height
        sex                    "M" or "F"

    Output:
        dict or None if age is outside the model range.
    """

    values = [
        height_cm,
        weight_kg,
        age_years,
        mother_height_cm,
        father_height_cm,
    ]

    if any(v is None for v in values):
        return None

    try:
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)
        age_years = float(age_years)
        mother_height_cm = float(mother_height_cm)
        father_height_cm = float(father_height_cm)
    except (TypeError, ValueError):
        return None

    if any(v <= 0 for v in values):
        return None

    sex = str(sex).upper()

    if sex not in ("M", "F"):
        return None

    table = KR_BOYS if sex == "M" else KR_GIRLS
    coefficients = _interpolate_coefficients(age_years, table)

    if coefficients is None:
        return {
            "valid": False,
            "reason": (
                "Il metodo Khamis-Roche è applicabile "
                "nell'intervallo 4.0–17.5 anni."
            ),
        }

    b0, b_height, b_weight, b_midparent = coefficients

    # Conversione metriche -> imperiali richiesta dalle tabelle originali.
    height_in = height_cm / 2.54
    weight_lb = weight_kg * 2.20462262185

    mother_in = mother_height_cm / 2.54
    father_in = father_height_cm / 2.54

    midparent_in = (mother_in + father_in) / 2

    # Equazione Khamis-Roche.
    predicted_in = (
        b0
        + b_height * height_in
        + b_weight * weight_lb
        + b_midparent * midparent_in
    )

    predicted_cm = predicted_in * 2.54

    percent_adult = (height_cm / predicted_cm) * 100

    return {
        "valid": True,
        "predicted_cm": predicted_cm,
        "predicted_in": predicted_in,
        "percent_adult": percent_adult,
        "midparent_cm": midparent_in * 2.54,
        "coefficients": coefficients,
        "age": age_years,
        "sex": sex,
    }


def predict_mills_nelson_multiplier(height_cm, age_years, sex):
    """
    Mills & Nelson (2016) Multiplier method for adult height prediction.

    Input:
        height_cm              current standing height
        age_years              chronological age
        sex                    "M" or "F"

    Output:
        dict or None if age is outside the model range.
    """

    if height_cm is None or age_years is None:
        return None

    try:
        height_cm = float(height_cm)
        age_years = float(age_years)
    except (TypeError, ValueError):
        return None

    if height_cm <= 0 or age_years < 0:
        return None

    sex = str(sex).upper()

    if sex not in ("M", "F"):
        return None

    table = MILLS_NELSON_BOYS if sex == "M" else MILLS_NELSON_GIRLS
    multiplier = _interpolate_multiplier(age_years, table)

    if multiplier is None:
        return {
            "valid": False,
            "reason": (
                "Il metodo dei moltiplicatori è applicabile "
                "nell'intervallo 0.0–18.0 anni."
            ),
        }

    predicted_cm = height_cm * multiplier

    return {
        "valid": True,
        "predicted_cm": predicted_cm,
        "multiplier": multiplier,
        "age": age_years,
        "sex": sex,
    }


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Dati del soggetto"),

        ui.input_select(
            "sesso",
            "Sesso",
            choices={
                "M": "Maschio",
                "F": "Femmina",
            },
        ),

        ui.input_numeric(
            "eta",
            "Età (anni)",
            value=10,
            min=0,
            max=18,
            step=0.1,
        ),

        ui.input_numeric(
            "altezza",
            "Altezza (cm)",
            value=140,
            min=50,
            max=220,
            step=0.1,
        ),

        ui.input_numeric(
            "peso",
            "Peso (kg)",
            value=35,
            min=10,
            max=150,
            step=0.1,
        ),

        ui.input_numeric(
            "altezza_seduto",
            "Altezza da seduto (cm)",
            value=70,
            min=30,
            max=120,
            step=0.1,
        ),

        ui.input_numeric(
            "lunghezza_gamba",
            "Lunghezza gamba (cm)",
            value=70,
            min=30,
            max=120,
            step=0.1,
        ),

        ui.input_numeric(
            "altezza_madre",
            "Altezza madre (cm)",
            value=165,
            min=120,
            max=200,
            step=0.1,
        ),

        ui.input_numeric(
            "altezza_padre",
            "Altezza padre (cm)",
            value=178,
            min=130,
            max=220,
            step=0.1,
        ),

        width=350,
    ),

    ui.h2("Calcolatore di Maturazione e Crescita"),

    ui.navset_card_tab(
        ui.nav_panel(
            "Peak Height Velocity (PHV)",

            ui.card(
                ui.card_header("Metodo Mirwald et al. (2002)"),
                ui.output_text_verbatim("phv_mirwald"),
            ),

            ui.card(
                ui.card_header("Metodo Moore et al. (2015)"),
                ui.output_text_verbatim("phv_moore"),
            ),

            ui.card(
                ui.card_header("Metodo Fransen et al. (2018)"),
                ui.output_text_verbatim("phv_fransen"),
            ),
        ),

        ui.nav_panel(
            "Maturity Offset",

            ui.card(
                ui.card_header("Maturity Offset - Mirwald"),
                ui.output_text_verbatim("offset_mirwald"),
            ),

            ui.card(
                ui.card_header("Maturity Offset - Moore"),
                ui.output_text_verbatim("offset_moore"),
            ),

            ui.card(
                ui.card_header("Maturity Offset - Fransen"),
                ui.output_text_verbatim("offset_fransen"),
            ),
        ),

        ui.nav_panel(
            "Altezza da Adulto",

            ui.card(
                ui.card_header("Metodo Khamis-Roche"),
                ui.output_text_verbatim("altezza_khamis"),
            ),

            ui.card(
                ui.card_header("Metodo della Media Genitoriale"),
                ui.output_text_verbatim("altezza_media_genitori"),
            ),

            ui.card(
                ui.card_header("Multiplier Method"),
                ui.output_text_verbatim("altezza_mills_nelson"),
            ),
        ),

        ui.nav_panel(
            "Metodi di Misurazione",

            ui.card(
                ui.markdown(
                    """
                    ### Metodi di Misurazione Richiesti

                    **1. Altezza (Statura)**
                    - Misurazione in posizione eretta con stadiometro
                    - Soggetto scalzo, talloni uniti, schiena dritta
                    - Testa in posizione di Francoforte
                    - Precisione: ±0.1 cm

                    **2. Peso Corporeo**
                    - Bilancia calibrata
                    - Soggetto in abbigliamento leggero
                    - Misurazione al mattino preferibilmente
                    - Precisione: ±0.1 kg

                    **3. Altezza da Seduto**
                    - Soggetto seduto con schiena dritta
                    - Misurazione dalla sommità del capo alla superficie di seduta

                    **4. Lunghezza della Gamba**
                    - Altezza totale - altezza da seduto
                    - Oppure misurata direttamente

                    **5. Altezza dei Genitori**
                    - Altezza dichiarata o misurata di madre e padre
                    - Necessaria per Khamis-Roche

                    ### Note
                    - Tutte le misurazioni devono essere effettuate correttamente.
                    - L'età deve essere espressa in anni decimali.
                    - Khamis-Roche è applicabile da 4.0 a 17.5 anni.
                    """
                )
            ),
        ),
    ),
)


def server(input, output, session):

    @reactive.calc
    def calcola_mirwald():
        try:
            altezza = float(input.altezza())
            peso = float(input.peso())
            altezza_seduto = float(input.altezza_seduto())
            lunghezza_gamba = float(input.lunghezza_gamba())
            eta = float(input.eta())
            sesso = input.sesso()

            interazione = altezza * lunghezza_gamba

            if sesso == "M":
                offset = (
                    -9.236
                    + (0.0002708 * interazione)
                    - (0.001663 * eta * lunghezza_gamba)
                    + (0.007216 * eta * altezza_seduto)
                    + (0.02292 * peso / altezza * 100)
                )
            else:
                offset = (
                    -9.376
                    + (0.0001882 * interazione)
                    + (0.0022 * eta * lunghezza_gamba)
                    + (0.005841 * eta * altezza_seduto)
                    - (0.002658 * eta * peso)
                    + (0.07693 * peso / altezza * 100)
                )

            phv_age = eta - offset

            return {
                "offset": offset,
                "phv_age": phv_age,
                "metodo": "Mirwald et al. (2002)",
            }

        except (TypeError, ValueError, ZeroDivisionError):
            return None


    @reactive.calc
    def calcola_moore():
        try:
            altezza = float(input.altezza())
            altezza_seduto = float(input.altezza_seduto())
            eta = float(input.eta())
            sesso = input.sesso()

            if sesso == "M":
                offset = -8.128741 - 0.2683693 + (0.0070346 * eta * altezza_seduto)
            else:
                offset = -7.709133 + (0.0042232 * eta * altezza)

            phv_age = eta - offset

            return {
                "offset": offset,
                "phv_age": phv_age,
                "metodo": "Moore et al. (2015)",
            }

        except (TypeError, ValueError):
            return None


    @reactive.calc
    def calcola_fransen():
        try:
            altezza = float(input.altezza())       
            peso = float(input.peso())            
            eta = float(input.eta())             
            sesso = input.sesso()                
            lunghezza_gamba = float(input.lunghezza_gamba())

            if sesso == "M":
                # Calcolo del Maturity Ratio (Fransen et al., 2018)
                maturity_ratio = (
                    6.986547255416 
                    + (0.115802846632 * eta) 
                    + (0.001450825199 * (eta ** 2)) 
                    + (0.004518400406 * peso) 
                    - (0.000034086447 * (peso ** 2)) 
                    - (0.151951447289 * altezza) 
                    + (0.000932836659 * (altezza ** 2)) 
                    - (0.000001656585 * (altezza ** 3)) 
                    + (0.032198263733 * lunghezza_gamba) 
                    - (0.000269025264 * (lunghezza_gamba ** 2)) 
                    - (0.000760897942 * (altezza * eta))
                )
            else:
                raise ValueError("L'algoritmo di Fransen (2018) è validato solo per i maschi.")

            phv_age = eta / maturity_ratio
        
            # 2. Calcola il Maturity Offset (Età attuale - Età al PHV)
            # Risultato negativo = pre-PHV; Positivo = post-PHV
            offset = eta - phv_age

            return {
                "maturity_ratio": round(maturity_ratio, 4),
                "offset": round(offset, 4),
                "phv_age": round(phv_age, 4),
                "metodo": "Fransen et al. (2018)"
            }

        except (TypeError, ValueError, AttributeError) as e:
            print(f"Errore nel calcolo: {e}")
            return None
    

    @reactive.calc
    def calcola_khamis_roche():
        return predict_khamis_roche(
            height_cm=input.altezza(),
            weight_kg=input.peso(),
            age_years=input.eta(),
            mother_height_cm=input.altezza_madre(),
            father_height_cm=input.altezza_padre(),
            sex=input.sesso(),
        )


    @reactive.calc
    def calcola_media_genitori():
        try:
            madre = float(input.altezza_madre())
            padre = float(input.altezza_padre())
            sesso = input.sesso()

            if sesso == "M":
                altezza_prevista = (padre + madre + 13) / 2
            else:
                altezza_prevista = (padre + madre - 13) / 2

            return {
                "altezza_prevista": altezza_prevista,
                "metodo": "Media Genitoriale",
            }

        except (TypeError, ValueError):
            return None


    @reactive.calc
    def calcola_mills_nelson():
        return predict_mills_nelson_multiplier(
            height_cm=input.altezza(),
            age_years=input.eta(),
            sex=input.sesso(),
        )


    @output
    @render.text
    def phv_mirwald():
        r = calcola_mirwald()

        if r:
            return (
                f"Età al PHV: {r['phv_age']:.2f} anni\n"
                f"Maturity Offset: {r['offset']:.2f} anni\n"
                f"Metodo: {r['metodo']}"
            )

        return "Dati insufficienti per il calcolo"


    @output
    @render.text
    def phv_moore():
        r = calcola_moore()

        if r:
            return (
                f"Età al PHV: {r['phv_age']:.2f} anni\n"
                f"Maturity Offset: {r['offset']:.2f} anni\n"
                f"Metodo: {r['metodo']}"
            )

        return "Dati insufficienti per il calcolo"


    @output
    @render.text
    def phv_fransen():
        r = calcola_fransen()

        if r:
            return (
                f"Età al PHV: {r['phv_age']:.2f} anni\n"
                f"Maturity Offset: {r['offset']:.2f} anni\n"
                f"Metodo: {r['metodo']}"
            )

        return "Dati insufficienti per il calcolo"


    @output
    @render.text
    def offset_mirwald():
        r = calcola_mirwald()

        if r:
            stato = "Post-PHV" if r["offset"] > 0 else "Pre-PHV"

            return (
                f"Maturity Offset: {r['offset']:.2f} anni\n"
                f"Stato: {stato}\n"
                f"(Valore positivo = dopo PHV, negativo = prima PHV)"
            )

        return "Dati insufficienti per il calcolo"


    @output
    @render.text
    def offset_moore():
        r = calcola_moore()

        if r:
            stato = "Post-PHV" if r["offset"] > 0 else "Pre-PHV"

            return (
                f"Maturity Offset: {r['offset']:.2f} anni\n"
                f"Stato: {stato}\n"
                f"(Valore positivo = dopo PHV, negativo = prima PHV)"
            )

        return "Dati insufficienti per il calcolo"


    @output
    @render.text
    def offset_fransen():
        r = calcola_fransen()

        if r:
            stato = "Post-PHV" if r["offset"] > 0 else "Pre-PHV"

            return (
                f"Maturity Offset: {r['offset']:.2f} anni\n"
                f"Stato: {stato}\n"
                f"(Valore positivo = dopo PHV, negativo = prima PHV)"
            )

        return "Dati insufficienti per il calcolo"


    @output
    @render.text
    def altezza_khamis():
        r = calcola_khamis_roche()

        if not r:
            return "Dati insufficienti per il calcolo"

        if not r.get("valid", False):
            return r["reason"]

        return (
            f"Altezza adulta prevista: {r['predicted_cm']:.1f} cm\n"
            f"Stima in pollici: {r['predicted_in']:.1f} in\n"
            f"Altezza attuale: {input.altezza():.1f} cm\n"
            f"Percentuale dell'altezza adulta stimata: "
            f"{r['percent_adult']:.1f}%\n"
            f"Media altezze genitori: {r['midparent_cm']:.1f} cm\n"
            f"Metodo: Khamis-Roche (1994; erratum 1995)\n"
            f"Nota: i coefficienti sono specifici per sesso ed età."
        )


    @output
    @render.text
    def altezza_media_genitori():
        r = calcola_media_genitori()

        if r:
            return (
                f"Altezza prevista da adulto: "
                f"{r['altezza_prevista']:.1f} cm\n"
                f"Metodo: {r['metodo']}\n"
                f"(Target genetico basato sui genitori)"
            )

        return "Dati insufficienti per il calcolo"


    @output
    @render.text
    def altezza_mills_nelson():
        r = calcola_mills_nelson()

        if not r:
            return "Dati insufficienti per il calcolo"

        if not r.get("valid", False):
            return r["reason"]

        return (
            f"Altezza prevista da adulto: {r['predicted_cm']:.1f} cm\n"
            f"Moltiplicatore (M): {r['multiplier']:.4f}\n"
            f"Altezza attuale: {input.altezza():.1f} cm\n"
            f"Metodo: Moltiplicatore di Bailey et al. (2000) "
            f"secondo versione aggiornata da Mills & Nelson (2016)\n"
            f"Formula: Altezza prevista = Altezza attuale × M"
        )


app = App(app_ui, server)
