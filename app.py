from shiny import App, ui, render, reactive
import math

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Dati del Soggetto"),
        ui.input_select(
            "sesso",
            "Sesso",
            choices={"M": "Maschio", "F": "Femmina"}
        ),
        ui.input_numeric("eta", "Et‡ (anni)", value=10, min=0, max=18, step=0.1),
        ui.input_numeric("altezza", "Altezza (cm)", value=140, min=50, max=220),
        ui.input_numeric("peso", "Peso (kg)", value=35, min=10, max=150),
        ui.input_numeric("altezza_seduto", "Altezza da seduto (cm)", value=70, min=30, max=120),
        ui.input_numeric("lunghezza_gamba", "Lunghezza gamba (cm)", value=70, min=30, max=120),
        ui.input_numeric("altezza_madre", "Altezza madre (cm)", value=165, min=120, max=200),
        ui.input_numeric("altezza_padre", "Altezza padre (cm)", value=178, min=130, max=220),
        width=350
    ),
    ui.h2("Calcolatore di Maturazione e Crescita"),
    ui.navset_card_tab(
        ui.nav_panel(
            "Peak Height Velocity (PHV)",
            ui.card(
                ui.card_header("Metodo Mirwald et al. (2002)"),
                ui.output_text_verbatim("phv_mirwald")
            ),
            ui.card(
                ui.card_header("Metodo Moore et al. (2015)"),
                ui.output_text_verbatim("phv_moore")
            ),
            ui.card(
                ui.card_header("Metodo Fransen et al. (2018)"),
                ui.output_text_verbatim("phv_fransen")
            )
        ),
        ui.nav_panel(
            "Maturity Offset",
            ui.card(
                ui.card_header("Maturity Offset - Mirwald"),
                ui.output_text_verbatim("offset_mirwald")
            ),
            ui.card(
                ui.card_header("Maturity Offset - Moore"),
                ui.output_text_verbatim("offset_moore")
            ),
            ui.card(
                ui.card_header("Maturity Offset - Fransen"),
                ui.output_text_verbatim("offset_fransen")
            )
        ),
        ui.nav_panel(
            "Altezza da Adulto",
            ui.card(
                ui.card_header("Metodo Khamis-Roche"),
                ui.output_text_verbatim("altezza_khamis")
            ),
            ui.card(
                ui.card_header("Metodo della Media Genitoriale"),
                ui.output_text_verbatim("altezza_media_genitori")
            ),
            ui.card(
                ui.card_header("Metodo Bayley-Pinneau (Semplificato)"),
                ui.output_text_verbatim("altezza_bayley")
            )
        ),
        ui.nav_panel(
            "Metodi di Misurazione",
            ui.card(
                ui.markdown("""
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
                - Soggetto seduto su una panca con schiena dritta
                - Misurazione dalla sommit‡ del capo alla superficie di seduta
                - Importante per calcolare la lunghezza delle gambe
                - Box standard di 50 cm di altezza
                
                **4. Lunghezza della Gamba**
                - Calcolata come: Altezza totale - Altezza da seduto
                - Oppure misurata direttamente dal grande trocantere al suolo
                - Importante per equazioni di maturazione
                
                **5. Altezza dei Genitori**
                - Altezza dichiarata o misurata di madre e padre
                - Necessaria per metodo Khamis-Roche e media genitoriale
                - Miglior predittore se misurata professionalmente
                
                ### Note Importanti
                - Tutte le misurazioni devono essere effettuate da personale qualificato
                - Le misurazioni devono essere ripetute per garantire l'accuratezza
                - L'et‡ deve essere calcolata in anni decimali per maggiore precisione
                """)
            )
        )
    )
)

def server(input, output, session):
    
    @reactive.calc
    def calcola_mirwald():
        """Calcola Maturity Offset usando il metodo Mirwald et al. (2002)"""
        try:
            altezza = input.altezza()
            peso = input.peso()
            altezza_seduto = input.altezza_seduto()
            lunghezza_gamba = input.lunghezza_gamba()
            eta = input.eta()
            sesso = input.sesso()
            
            # Interazione altezza per lunghezza gamba
            interazione = altezza * lunghezza_gamba
            
            if sesso == "M":
                # Equazione per maschi
                offset = -9.236 + (0.0002708 * interazione) - \
                        (0.001663 * eta * lunghezza_gamba) + \
                        (0.007216 * eta * altezza_seduto) + \
                        (0.02292 * peso / altezza * 100)
            else:
                # Equazione per femmine
                offset = -9.376 + (0.0001882 * interazione) + \
                        (0.0022 * eta * lunghezza_gamba) + \
                        (0.005841 * eta * altezza_seduto) - \
                        (0.002658 * eta * peso) + \
                        (0.07693 * peso / altezza * 100)
            
            phv_age = eta - offset
            
            return {
                "offset": offset,
                "phv_age": phv_age,
                "metodo": "Mirwald et al. (2002)"
            }
        except:
            return None
    
    @reactive.calc
    def calcola_moore():
        """Calcola usando il metodo Moore et al. (2015)"""
        try:
            altezza = input.altezza()
            peso = input.peso()
            altezza_seduto = input.altezza_seduto()
            eta = input.eta()
            sesso = input.sesso()
            
            if sesso == "M":
                # Equazione Moore per maschi
                offset = -7.999994 + (-0.0036124 * eta * altezza_seduto)
            else:
                # Equazione Moore per femmine  
                offset = -7.709133 + (0.0042232 * eta * altezza_seduto)
            
            phv_age = eta - offset
            
            return {
                "offset": offset,
                "phv_age": phv_age,
                "metodo": "Moore et al. (2015)"
            }
        except:
            return None
    
    @reactive.calc
    def calcola_fransen():
        """Calcola usando il metodo Fransen et al. (2018)"""
        try:
            altezza = input.altezza()
            peso = input.peso()
            eta = input.eta()
            sesso = input.sesso()
            
            if sesso == "M":
                # Equazione Fransen per maschi (semplificata)
                offset = -7.85 + (0.0192 * peso) + (0.0693 * altezza / 100)
            else:
                # Equazione Fransen per femmine (semplificata)
                offset = -7.25 + (0.0213 * peso) + (0.0647 * altezza / 100)
            
            phv_age = eta - offset
            
            return {
                "offset": offset,
                "phv_age": phv_age,
                "metodo": "Fransen et al. (2018)"
            }
        except:
            return None
    
    @reactive.calc
    def calcola_khamis_roche():
        """Calcola altezza adulta prevista con metodo Khamis-Roche"""
        try:
            altezza = input.altezza()
            peso = input.peso()
            eta = input.eta()
            altezza_madre = input.altezza_madre()
            altezza_padre = input.altezza_padre()
            sesso = input.sesso()
            
            # Media altezze genitori
            media_genitori = (altezza_madre + altezza_padre) / 2
            
            # Coefficienti approssimati Khamis-Roche (variano per et‡)
            # Questi sono valori semplificati
            if sesso == "M":
                altezza_prevista = (1.27 * altezza) + (0.37 * media_genitori) - 31.8
            else:
                altezza_prevista = (1.29 * altezza) + (0.39 * media_genitori) - 42.3
            
            return {
                "altezza_prevista": altezza_prevista,
                "metodo": "Khamis-Roche"
            }
        except:
            return None
    
    @reactive.calc
    def calcola_media_genitori():
        """Calcola altezza prevista con metodo della media genitoriale"""
        try:
            altezza_madre = input.altezza_madre()
            altezza_padre = input.altezza_padre()
            sesso = input.sesso()
            
            if sesso == "M":
                # Per maschi: (altezza padre + altezza madre + 13) / 2
                altezza_prevista = (altezza_padre + altezza_madre + 13) / 2
            else:
                # Per femmine: (altezza padre + altezza madre - 13) / 2
                altezza_prevista = (altezza_padre + altezza_madre - 13) / 2
            
            return {
                "altezza_prevista": altezza_prevista,
                "metodo": "Media Genitoriale"
            }
        except:
            return None
    
    @reactive.calc
    def calcola_bayley_pinneau():
        """Calcola altezza prevista con metodo Bayley-Pinneau semplificato"""
        try:
            altezza = input.altezza()
            eta = input.eta()
            sesso = input.sesso()
            
            # Percentuale di crescita completata (approssimata)
            # Questi valori sono semplificati e variano con l'et‡ ossea
            if sesso == "M":
                if eta < 10:
                    perc_complet
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
            else:  # Femmina
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
            
            # Calcolo altezza prevista
            altezza_prevista = altezza / perc_completata
            
            return {
                "altezza_prevista": altezza_prevista,
                "perc_completata": perc_completata * 100,
                "metodo": "Bayley-Pinneau"
            }
        except:
            return None
    
    # Output per PHV
    @output
    @render.text
    def phv_mirwald():
        risultato = calcola_mirwald()
        if risultato:
            return f"""Et‡ al PHV: {risultato['phv_age']:.2f} anni
Maturity Offset: {risultato['offset']:.2f} anni
Metodo: {risultato['metodo']}"""
        return "Dati insufficienti per il calcolo"
    
    @output
    @render.text
    def phv_moore():
        risultato = calcola_moore()
        if risultato:
            return f"""Et‡ al PHV: {risultato['phv_age']:.2f} anni
Maturity Offset: {risultato['offset']:.2f} anni
Metodo: {risultato['metodo']}"""
        return "Dati insufficienti per il calcolo"
    
    @output
    @render.text
    def phv_fransen():
        risultato = calcola_fransen()
        if risultato:
            return f"""Et‡ al PHV: {risultato['phv_age']:.2f} anni
Maturity Offset: {risultato['offset']:.2f} anni
Metodo: {risultato['metodo']}"""
        return "Dati insufficienti per il calcolo"
    
    # Output per Maturity Offset
    @output
    @render.text
    def offset_mirwald():
        risultato = calcola_mirwald()
        if risultato:
            stato = "Post-PHV" if risultato['offset'] > 0 else "Pre-PHV"
            return f"""Maturity Offset: {risultato['offset']:.2f} anni
Stato: {stato}
(Valore positivo = dopo PHV, negativo = prima PHV)"""
        return "Dati insufficienti per il calcolo"
    
    @output
    @render.text
    def offset_moore():
        risultato = calcola_moore()
        if risultato:
            stato = "Post-PHV" if risultato['offset'] > 0 else "Pre-PHV"
            return f"""Maturity Offset: {risultato['offset']:.2f} anni
Stato: {stato}
(Valore positivo = dopo PHV, negativo = prima PHV)"""
        return "Dati insufficienti per il calcolo"
    
    @output
    @render.text
    def offset_fransen():
        risultato = calcola_fransen()
        if risultato:
            stato = "Post-PHV" if risultato['offset'] > 0 else "Pre-PHV"
            return f"""Maturity Offset: {risultato['offset']:.2f} anni
Stato: {stato}
(Valore positivo = dopo PHV, negativo = prima PHV)"""
        return "Dati insufficienti per il calcolo"
    
    # Output per altezza prevista
    @output
    @render.text
    def altezza_khamis():
        risultato = calcola_khamis_roche()
        if risultato:
            return f"""Altezza prevista da adulto: {risultato['altezza_prevista']:.1f} cm
Metodo: {risultato['metodo']}
(Basato su altezza corrente e altezza genitori)"""
        return "Dati insufficienti per il calcolo"
    
    @output
    @render.text
    def altezza_media_genitori():
        risultato = calcola_media_genitori()
        if risultato:
            return f"""Altezza prevista da adulto: {risultato['altezza_prevista']:.1f} cm
Metodo: {risultato['metodo']}
(Target genetico basato solo sui genitori)"""
        return "Dati insufficienti per il calcolo"
    
    @output
    @render.text
    def altezza_bayley():
        risultato = calcola_bayley_pinneau()
        if risultato:
            return f"""Altezza prevista da adulto: {risultato['altezza_prevista']:.1f} cm
Crescita completata: {risultato['perc_completata']:.1f}%
Metodo: {risultato['metodo']}
(Semplificato - normalmente richiede et‡ ossea)"""
        return "Dati insufficienti per il calcolo"

app = App(app_ui, server)
