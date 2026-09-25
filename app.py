from shiny import App, ui, render, reactive
import math


# Fonte:
# Khamis HJ, Roche AF. Pediatrics. 1994;94:504-507.
# Erratum: Pediatrics. 1995;95:457.
# ============================================================
# Mlakar et al. (2023) Adult height prediction using the growth curve comparison method. https://doi.org/10.1371/journal.pone.0281960


KR_BOYS = {
    4.0:  (-10.2567, 1.23812, -0.0087235, 0.50286),
    4.5:  (-10.7190, 1.15964, -0.0074454, 0.52887),
    5.0:  (-11.0213, 1.10674, -0.0064778, 0.53919),
    5.5:  (-11.1556, 1.07480, -0.0057760, 0.53691),
    6.0:  (-11.1138, 1.05923, -0.0052947, 0.52513),
    6.5:  (-11.0221, 1.05542, -0.0049892, 0.50692),
    7.0:  (-10.9984, 1.05877, -0.0048144, 0.48538),
    7.5:  (-11.0214, 1.06467, -0.0047256, 0.46361),
    8.0:  (-11.0696, 1.06853, -0.0046778, 0.44469),
    8.5:  (-11.1220, 1.06572, -0.0046261, 0.43171),
    9.0:  (-11.1571, 1.05166, -0.0045254, 0.42776),
    9.5:  (-11.1405, 1.02174, -0.0043311, 0.43593),
    10.0: (-11.0380, 0.97135, -0.0039981, 0.45932),
    10.5: (-10.8286, 0.89589, -0.0034814, 0.50101),
    11.0: (-10.4917, 0.81239, -0.0029050, 0.54781),
    11.5: (-10.0065, 0.74134, -0.0024167, 0.58409),
    12.0: (-9.3522,  0.68325, -0.0020076, 0.60927),
    12.5: (-8.6055,  0.63869, -0.0016681, 0.62279),
    13.0: (-7.8632,  0.60818, -0.0013895, 0.62407),
    13.5: (-7.1348,  0.59228, -0.0011624, 0.61253),
    14.0: (-6.4299,  0.59151, -0.0009776, 0.58762),
    14.5: (-5.7578,  0.60643, -0.0008261, 0.54875),
    15.0: (-5.1282,  0.63757, -0.0006988, 0.49536),
    15.5: (-4.5092,  0.68548, -0.0005863, 0.42687),
    16.0: (-3.9292,  0.75069, -0.0004795, 0.34271),
    16.5: (-3.4873,  0.83375, -0.0003695, 0.24231),
    17.0: (-3.2830,  0.93520, -0.0002470, 0.12510),
    17.5: (-3.4156,  1.05558, -0.0001027, -0.00950),
}


KR_GIRLS = {
    4.0:  (-8.13250, 1.24768, -0.019435, 0.44774),
    4.5:  (-6.47656, 1.22177, -0.018519, 0.41381),
    5.0:  (-5.13582, 1.19932, -0.017530, 0.38467),
    5.5:  (-4.13791, 1.17880, -0.016484, 0.36039),
    6.0:  (-3.51039, 1.15866, -0.015400, 0.34105),
    6.5:  (-3.14322, 1.13737, -0.014294, 0.32672),
    7.0:  (-2.87645, 1.11342, -0.013184, 0.31748),
    7.5:  (-2.66291, 1.08525, -0.012086, 0.31340),
    8.0:  (-2.45559, 1.05135, -0.011019, 0.31457),
    8.5:  (-2.20728, 1.01018, -0.009999, 0.32105),
    9.0:  (-1.87098, 0.96020, -0.009044, 0.33291),
    9.5:  (-1.06330, 0.89989, -0.008171, 0.35025),
    10.0: (0.33468, 0.82771, -0.007397, 0.37312),
    10.5: (1.97366, 0.74213, -0.006739, 0.40161),
    11.0: (3.50436, 0.67173, -0.006136, 0.42042),
    11.5: (4.57747, 0.64150, -0.005518, 0.41686),
    12.0: (4.84365, 0.64452, -0.004894, 0.39490),
    12.5: (4.27869, 0.67386, -0.004272, 0.35850),
    13.0: (3.21417, 0.72260, -0.003661, 0.31163),
    13.5: (1.83456, 0.78383, -0.003067, 0.25826),
    14.0: (0.32425, 0.85062, -0.002500, 0.20235),
    14.5: (-1.13224, 0.91605, -0.001967, 0.14787),
    15.0: (-2.35055, 0.97319, -0.001477, 0.09880),
    15.5: (-3.10326, 1.01514, -0.001037, 0.05909),
    16.0: (-3.17885, 1.03496, -0.000655, 0.03272),
    16.5: (-2.41657, 1.02573, -0.000340, 0.02364),
    17.0: (-0.65579, 0.98054, -0.000100, 0.03584),
    17.5: (2.26429, 0.89246, 0.000570, 0.07327),
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


# ============================================================
# SHINY UI
# ============================================================

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
                ui.card_header("Metodo Bayley-Pinneau (Semplificato)"),
                ui.output_text_verbatim("altezza_bayley"),
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


# ============================================================
# SERVER
# ============================================================

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

            if sesso == "M":
                offset = -7.85 + (0.0192 * peso) + (0.0693 * altezza / 100)
            else:
                offset = -7.25 + (0.0213 * peso) + (0.0647 * altezza / 100)

            phv_age = eta - offset

            return {
                "offset": offset,
                "phv_age": phv_age,
                "metodo": "Fransen et al. (2018)",
            }

        except (TypeError, ValueError):
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
    def calcola_bayley_pinneau():
        try:
            altezza = float(input.altezza())
            eta = float(input.eta())
            sesso = input.sesso()

            if sesso == "M":
                if eta < 10:
                    perc_completata = 0.70
                elif eta < 12:
                    perc_completata = 0.78
                elif eta < 14:
                    perc_completata = 0.85
                elif eta < 16:
                    perc_completata = 0.92
                else:
                    perc_completata = 0.97
            else:
                if eta < 9:
                    perc_completata = 0.75
                elif eta < 11:
                    perc_completata = 0.84
                elif eta < 13:
                    perc_completata = 0.91
                elif eta < 15:
                    perc_completata = 0.96
                else:
                    perc_completata = 0.99

            altezza_prevista = altezza / perc_completata

            return {
                "altezza_prevista": altezza_prevista,
                "perc_completata": perc_completata * 100,
                "metodo": "Bayley-Pinneau",
            }

        except (TypeError, ValueError, ZeroDivisionError):
            return None


    # --------------------------------------------------------
    # OUTPUT PHV
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # OUTPUT MATURITY OFFSET
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # OUTPUT ALTEZZA ADULTA
    # --------------------------------------------------------

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
    def altezza_bayley():
        r = calcola_bayley_pinneau()

        if r:
            return (
                f"Altezza prevista da adulto: "
                f"{r['altezza_prevista']:.1f} cm\n"
                f"Crescita completata: "
                f"{r['perc_completata']:.1f}%\n"
                f"Metodo: {r['metodo']}\n"
                f"(Versione semplificata; normalmente richiede età ossea)"
            )

        return "Dati insufficienti per il calcolo"


app = App(app_ui, server)
