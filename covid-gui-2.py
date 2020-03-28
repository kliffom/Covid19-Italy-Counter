# ---------------------------------
# -- Librerie
# ---------------------------------

import tkinter as tk
import csv
import pandas as pd
pd.options.mode.chained_assignment = None
import time
import threading
import os

# ---------------------------------
# -- Costanti
# ---------------------------------

REGIONE_URL_CSV =  'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv'
PROVINCE_URL_CSV = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv'
NAZIONE_URL_CSV = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv'
NAZIONE_FILE = "./csv/lastData.csv"
REGIONE_FILE = "./csv/lastDataReg.csv"
BASILICATA_FILE = "./csv/lastDataBas.csv"
currentView = 0


# ---------------------------------
# -- Funzioni
# ---------------------------------

def downloadData():
    global data_nazione
    data_nazione = pd.read_csv(NAZIONE_URL_CSV)
    #Nome colonne: [data, stato, ricoverati_con_sintomi, terapia_intensiva, totale_ospedalizzati, isolamento_domiciliare, totale_attualmente_positivi, nuovi_attualmente_positivi, dimessi_guariti, deceduti, totale_casi, tamponi]
    global data_regione
    data_regione = pd.read_csv(REGIONE_URL_CSV)
    #Nome colonne: [data, stato, codice_regione, denominazione_regione, lat, long, ricoverati_con_sintomi, terapia_intensiva, totale_ospedalizzati, isolamento_domiciliare, totale_attualmente_positivi, nuovi_attualmente_positivi, dimessi_guariti, deceduti, totale_casi, tamponi]
    global data_province
    data_province = pd.read_csv(PROVINCE_URL_CSV)
    #Nome colonne: [data, stato, codice_regione, denominazione_regione, codice_provincia, denominazione_provincia, sigla_provincia, lat, long, totale_casi]

    # Prendo il numero di righe di ogni csv, per il numero di colonne usare shape[1]
    global nazione_int
    nazione_int = data_nazione.shape[0]
    global regione_int
    regione_int = data_regione.shape[0]
    global province_int
    province_int = data_province.shape[0]
    # print("nazione: %d. regione: %d. province: %d." % (nazione_int, regione_int, province_int))

def updateData(currentData):
    #dichiaro variabili da prendere globalmente
    global text_regione
    global text_data
    global text_tot_positivi
    global text_new_positivi
    global text_guariti
    global text_deceduti
    global text_tamponi
    global lastRegione
    global oldDataItDF
    global oldDataBasDF

    print("[INFO][updateData] View corrente: " + str(currentData))
    if(currentData == 0): #Caso Italia
        print("[INFO][updateData] Carico i dati Italia")

        Nattuali = data_nazione.loc[0]["totale_attualmente_positivi"]
        Nguariti = data_nazione.loc[0]["dimessi_guariti"]
        Ndeceduti = data_nazione.loc[0]["deceduti"]
        Ntamponi = data_nazione.loc[0]["tamponi"]
        nuovidati = [Nattuali, Nguariti, Ndeceduti, Ntamponi]

        for i in range(oldDataItDF.shape[1]):
            if(oldDataItDF.loc[1][i] != nuovidati[i]):
                print("[INFO][updateData - csv updating] Nuovi dati, sostituisco")
                oldDataItDF.loc[0][i] = oldDataItDF.loc[1][i]
                oldDataItDF.loc[1][i] = nuovidati[i]

        print("[INFO][updateData] overwrite file csv Italia")
        oldDataItDF.to_csv(NAZIONE_FILE, index = False, header=True) #salvo i nuovi dati

        text_data = str(data_nazione.loc[0]["data"])
        text_tot_positivi = str(data_nazione.loc[0]["totale_attualmente_positivi"])
        text_new_positivi = str(data_nazione.loc[0]["nuovi_attualmente_positivi"])
        text_guariti = "%s (%s)" % (str(data_nazione.loc[0]["dimessi_guariti"]),
            (str(oldDataItDF.loc[1]['guariti'] - oldDataItDF.loc[0]['guariti'])
            if (oldDataItDF.loc[1]['guariti'] - oldDataItDF.loc[0]['guariti'])<0
            else "+" + str(oldDataItDF.loc[1]['guariti'] - oldDataItDF.loc[0]['guariti'])))
        text_deceduti = "%s (%s)" % (str(data_nazione.loc[0]['deceduti']),
            (str(oldDataItDF.loc[1]['deceduti'] - oldDataItDF.loc[0]['deceduti'])
            if (oldDataItDF.loc[1]['deceduti'] - oldDataItDF.loc[0]['deceduti'])<0
            else "+" + str(oldDataItDF.loc[1]['deceduti'] - oldDataItDF.loc[0]['deceduti'])))
        text_tamponi = "%s (%s)" % (str(data_nazione.loc[0]['tamponi']),
            (str(oldDataItDF.loc[1]['tamponi'] - oldDataItDF.loc[0]['tamponi'])
            if (oldDataItDF.loc[1]['tamponi'] - oldDataItDF.loc[0]['tamponi'])<0
            else "+" + str(oldDataItDF.loc[1]['tamponi'] - oldDataItDF.loc[0]['tamponi'])))


    elif(currentData == 1): #Caso regioni
        print("[INFO][updateData] Carico i dati regione")

        """
        Creare lista con i nuovi dati
        Inserire i dati nel csv delle regioni
        Salvare il NAZIONE_file
        Aggiornare i text per contenere i nuovi dati
        """

        text_regione = str(data_regione.loc[lastRegione]["denominazione_regione"])
        text_data = str(data_regione.loc[lastRegione]["data"])
        text_tot_positivi = str(data_regione.loc[lastRegione]["totale_attualmente_positivi"])
        text_new_positivi = str(data_regione.loc[lastRegione]["nuovi_attualmente_positivi"])
        text_guariti = str(data_regione.loc[lastRegione]["dimessi_guariti"])
        text_deceduti = str(data_regione.loc[lastRegione]["deceduti"])
        text_tamponi = str(data_regione.loc[lastRegione]["tamponi"])

    elif(currentData == 2): #Caso Basilicata
        print("[INFO][updateData] Carico i dati Basilicata")

        for i in range(regione_int):
            print("[DEBUG]" + data_regione.loc[i]["denominazione_regione"])
            if(data_regione.loc[i]["denominazione_regione"] == "Basilicata"):
                print("[INFO][updateData - regions iterator] Trovata regione in csv:" + str(data_regione.loc[i]["denominazione_regione"]))
                found=0
                for j in range(province_int):
                    if(data_province.loc[j]["sigla_provincia"] == "MT"):
                        print("[INFO][updateData - iterator province] Trovati dati Matera: " + str(data_province.loc[j]["totale_casi"]))
                        found+=1
                        Nattuali_mt = data_province.loc[j]["totale_casi"]
                        mt_case = str(Nattuali_mt)
                    elif(data_province.loc[j]["sigla_provincia"] == "PZ"):
                        print("[INFO][updateData - iterator province] Trovati dati Potenza: " + str(data_province.loc[j]["totale_casi"]))
                        found+=1
                        Nattuali_pz = data_province.loc[j]["totale_casi"]
                        pz_case = str(Nattuali_pz)
                    if(found >= 2):
                        print("[INFO][updateData - iterator province] Tutte le province trovate. Interrompo iterazione.")
                        break

                Nattuali = data_regione.loc[i]["totale_attualmente_positivi"]
                Nguariti = data_regione.loc[i]["dimessi_guariti"]
                Ndeceduti = data_regione.loc[i]["deceduti"]
                Ntamponi = data_regione.loc[i]["tamponi"]
                nuovidatiBas = [Nattuali, Nattuali_pz, Nattuali_mt, Nguariti, Ndeceduti, Ntamponi]
                print("[INFO][updateData - Basilicata] carico i nuovi dati - att:" + str(Nattuali) + ", guar: " + str(Nguariti) + ", dec: " + str(Ndeceduti) + "tam: " + str(Ntamponi))

                for j in range(oldDataBasDF.shape[1]):
                    if(oldDataBasDF.loc[1][j] != nuovidatiBas[j]):
                        print("[INFO][updateData - csv updating] Nuovi dati, sostituisco")
                        oldDataBasDF.loc[0][j] = oldDataBasDF.loc[1][j]
                        oldDataBasDF.loc[1][j] = nuovidatiBas[j]
                print("[INFO][updateData] overwrite file csv Basilicata")
                oldDataBasDF.to_csv(BASILICATA_FILE, index = False, header=True) #salvo i nuovi dati

                text_data = str(data_regione.loc[i]["data"])
                text_tot_positivi = str(data_regione.loc[i]["totale_attualmente_positivi"]) + " PZ(" + pz_case + "), MT(" + mt_case + ")"
                print("[DEBUG] text_tot_positivi: " + text_tot_positivi)

                #text_new_positivi = str(data_regione.loc[i]["nuovi_attualmente_positivi"])
                print("data_regione.loc[i][totale_attualmente_positivi] :" + str(data_regione.loc[i]["totale_attualmente_positivi"]))
                text_new_positivi = "%s PZ(%s), MT(%s)" % (str(data_regione.loc[i]["nuovi_attualmente_positivi"]),
                    (str(oldDataBasDF.loc[1]['attuali_pz'] - oldDataBasDF.loc[0]['attuali_pz'])

                    if (oldDataBasDF.loc[1]['attuali_pz'] - oldDataBasDF.loc[0]['attuali_pz'])<0
                    else "+" + str(oldDataBasDF.loc[1]['attuali_pz'] - oldDataBasDF.loc[0]['attuali_pz'])),

                    (str(oldDataBasDF.loc[1]['attuali_mt'] - oldDataBasDF.loc[0]['attuali_mt'])

                    if (oldDataBasDF.loc[1]['attuali_mt'] - oldDataBasDF.loc[0]['attuali_mt'])<0
                    else "+" + str(oldDataBasDF.loc[1]['attuali_mt'] - oldDataBasDF.loc[0]['attuali_mt'])))
                print("data_regione.loc[i][nuovi_attualmente_positivi]: " + str(data_regione.loc[i]["nuovi_attualmente_positivi"]))
                #print("-------- DEBUG -------")
                #print(oldDataBasDF.loc[1]['attuali_pz'] - oldDataBasDF.loc[0]['attuali_pz'])
                #print(oldDataBasDF.loc[1]['attuali_mt'] - oldDataBasDF.loc[0]['attuali_mt'])
                #print("-------- DEBUG END -------")
                #text_guariti = str(data_regione.loc[i]["dimessi_guariti"])
                text_guariti = "%s (%s)" % (str(data_regione.loc[i]["dimessi_guariti"]),
                    (str(oldDataBasDF.loc[1]['guariti'] - oldDataBasDF.loc[0]['guariti'])
                    if (oldDataBasDF.loc[1]['guariti'] - oldDataBasDF.loc[0]['guariti'])<0
                    else "+" + str(oldDataBasDF.loc[1]['guariti'] - oldDataBasDF.loc[0]['guariti'])))
                print("data_regione.loc[i][dimessi_guariti]: " + str(data_regione.loc[i]["dimessi_guariti"]))
                #text_deceduti = str(data_regione.loc[i]["deceduti"])
                text_deceduti = "%s (%s)" % (str(data_regione.loc[i]['deceduti']),
                    (str(oldDataBasDF.loc[1]['deceduti'] - oldDataBasDF.loc[0]['deceduti'])
                    if (oldDataBasDF.loc[1]['deceduti'] - oldDataBasDF.loc[0]['deceduti'])<0
                    else "+" + str(oldDataBasDF.loc[1]['deceduti'] - oldDataBasDF.loc[0]['deceduti'])))
                #print("data_regione.loc[i][deceduti]: "+str(data_regione.loc[i]['deceduti'])
                text_tamponi = str(data_regione.loc[i]["tamponi"])
                text_tamponi = "%s (%s)" % (str(data_regione.loc[i]['tamponi']),
                    (str(oldDataBasDF.loc[1]['tamponi'] - oldDataBasDF.loc[0]['tamponi'])
                    if (oldDataBasDF.loc[1]['tamponi'] - oldDataBasDF.loc[0]['tamponi'])<0
                    else "+" + str(oldDataBasDF.loc[1]['tamponi'] - oldDataBasDF.loc[0]['tamponi'])))
                #print("data_regione.loc[i][tamponi]: " + str(data_regione.loc[i]['tamponi']))


                break


def incrementRegionCounter():
    global lastRegione
    global currentView

    if(currentView == 1):
        lastRegione +=1
        if(lastRegione>=regione_int):
            lastRegione = 0

        reload(currentView)
    th = threading.Timer(10, incrementRegionCounter)
    th.start()

def italy_button():
    global currentView
    currentView = 0
    reload(currentView)

def reg_button():
    global currentView
    global lastRegione
    lastRegione +=1
    if(lastRegione>=regione_int):
        lastRegione = 0
    currentView = 1
    reload(currentView)

def bas_button():
    global currentView
    currentView = 2
    reload(currentView)

def exit_button():
    win.destroy()
    os._exit(0)

def reload(curView):
    downloadData()
    updateData(curView)

    if(curView == 0):
        label_nazione["text"] = "Italia"
    elif(curView == 2):
        label_nazione["text"] = "Basilicata"
    else:
        label_nazione["text"] = text_regione

    label_data["text"] = text_data
    label_totale_positivi["text"] = "Tot. positivi: " + text_tot_positivi
    label_nuovi_positivi["text"] = "Nuovi: +"+text_new_positivi
    label_guariti["text"] = "Guariti: " + text_guariti
    label_deceduti["text"] = "Deceduti: "+text_deceduti
    label_tamponi["text"] = "Tamponi: "+text_tamponi

# ---------------------------------
# -- Primo download dati
# ---------------------------------

data_nazione = pd.read_csv(NAZIONE_URL_CSV)
data_regione = pd.read_csv(REGIONE_URL_CSV)
data_province = pd.read_csv(PROVINCE_URL_CSV)

nazione_int = data_nazione.shape[0]
regione_int = data_regione.shape[0]
province_int = data_province.shape[0]
lastRegione = regione_int

text_regione = ""
text_data = str(data_nazione.loc[0]["data"])
text_tot_positivi = str(data_nazione.loc[0]["totale_attualmente_positivi"])
text_new_positivi = str(data_nazione.loc[0]["nuovi_attualmente_positivi"])
text_guariti = str(data_nazione.loc[0]["dimessi_guariti"])
text_deceduti = str(data_nazione.loc[0]["deceduti"])
text_tamponi = str(data_nazione.loc[0]["tamponi"])

# ---------------------------------
# -- Apertura file dati
# ---------------------------------

# --------------------------------------------------- File nazione
if os.path.exists(NAZIONE_FILE) == False:
    print("[INFO][csv Italia] Il file Nazione non esiste. Lo creo")

    data = [[0, 0, 0, 0], [data_nazione.loc[0]["totale_attualmente_positivi"], data_nazione.loc[0]["dimessi_guariti"], data_nazione.loc[0]["deceduti"], data_nazione.loc[0]["tamponi"]]]
    oldDataItDF = pd.DataFrame(data, columns = ['attuali', 'guariti', 'deceduti', 'tamponi'])
    #print(oldDataItDF)
    oldDataItDF.to_csv(NAZIONE_FILE, index = False, header=True)
else:
    print("[INFO][csv Italia] Il file Nazione esiste.")
    oldDataItDF = pd.read_csv(NAZIONE_FILE)
    #print(oldDataItDF)

# ---------------------------------------------------- File regioni

#  - idea tutto su una riga per ogni regione: ['attuali', 'past_attuali', 'guariti', 'past_guariti', 'deceduti', 'past_deceduti' 'tamponi', 'past_tamponi']
#  - e per ogni riga ci sarà una regione (0: Abruzzo, 1: Basilicata, 2: P A Bolzano, 3: Calabria, ...)
if os.path.exists(REGIONE_FILE) == False:
    print("[INFO][csv Regioni] Il file Regione non esiste. Lo creo")
    #data = [[0, 0, 0, 0, 0, 0, 0, 0]]
    oldDataRegDF = pd.DataFrame(columns = ['regione', 'attuali', 'past_attuali', 'guariti', 'past_guariti', 'deceduti', 'past_deceduti', 'tamponi', 'past_tamponi'])
    print("[DEBUG] oldDataRegDF creation")
    print(oldDataRegDF)
    # Salvo i dati attuali nel file csv
    #dataTest = [[1, 2, 3, 4, 5, 6, 7, 8, 9]]
    #dataDF = pd.DataFrame(dataTest, columns = ['regione', 'attuali', 'past_attuali', 'guariti', 'past_guariti', 'deceduti', 'past_deceduti', 'tamponi', 'past_tamponi'])

    #print("[DEBUG] dataDF creation")
    #print(dataDF)
    #oldDataRegDF = pd.concat([oldDataRegDF, dataDF], axis=0)
    
    for i in range(regione_int):
        thisRegione = str(data_regione.loc[i]["denominazione_regione"])
        thisAttuali = data_regione.loc[i]["totale_attualmente_positivi"]
        thisGuariti = data_regione.loc[i]["dimessi_guariti"]
        thisDeceduti = data_regione.loc[i]["deceduti"]
        thisTamponi = data_regione.loc[i]["tamponi"]
        print("[DEBUG] i: %d, reg: %s, att: %d, guar: %d, dec: %d, tamp: %d"
            % (i, thisRegione, thisAttuali, thisGuariti, thisDeceduti, thisTamponi))
        thisData = [[thisAttuali, 0, thisAttuali, 0, thisGuariti, 0, thisDeceduti, 0, thisTamponi]]
        new_row = pd.DataFrame(thisData, columns = ['regione', 'attuali', 'past_attuali', 'guariti', 'past_guariti', 'deceduti', 'past_deceduti', 'tamponi', 'past_tamponi'])
        oldDataRegDF = pd.concat([oldDataRegDF, new_row], axis=0)
        #oldDataRegDF.loc[i] = [thisRegione, 0, thisAttuali, 0, thisGuariti, 0, thisDeceduti, 0, thisTamponi]
        """
        regionData = pd.Series([thisRegione, 0, thisAttuali, 0, thisGuariti, 0, thisDeceduti, 0, thisTamponi])
        new_row = pd.DataFrame([regionData], columns = ['regione', 'attuali', 'past_attuali', 'guariti', 'past_guariti', 'deceduti', 'past_deceduti' 'tamponi', 'past_tamponi'])
        oldDataRegDF = pd.concat([oldDataRegDF, new_row], ignore_index=True)
        """

    print(oldDataRegDF)
    #print(oldDataRegDF)
    oldDataRegDF.to_csv(REGIONE_FILE, index = False, header=True)
else:
    print("[INFO][csv Regioni] Il file Regione esiste.")
    oldDataRegDF = pd.read_csv(REGIONE_FILE)
    #print(oldDataRegDF)

# ----------------------------------------------------- File Basilicata
if os.path.exists(BASILICATA_FILE) == False:
    print("[INFO][csv Basilicata] Il file Basilicata non esiste. Lo creo")

    for i in range(regione_int):
        if(data_regione.loc[i]["denominazione_regione"] == "Basilicata"):

            found=0
            for j in range(province_int):
                if(data_province.loc[j]["sigla_provincia"] == "MT"):
                    found+=1
                    attuali_mt = str(data_province.loc[j]["totale_casi"])
                elif(data_province.loc[j]["sigla_provincia"] == "PZ"):
                    found+=1
                    attuali_pz = str(data_province.loc[j]["totale_casi"])
                if(found >= 2):
                    break

            tot_positivi = data_regione.loc[i]["totale_attualmente_positivi"]
            guariti = data_regione.loc[i]["dimessi_guariti"]
            deceduti = data_regione.loc[i]["deceduti"]
            tamponi = data_regione.loc[i]["tamponi"]
            break

    data = [[0, 0, 0, 0, 0, 0], [tot_positivi, attuali_pz, attuali_mt, guariti, deceduti, tamponi]]
    oldDataBasDF = pd.DataFrame(data, columns = ['attuali', 'attuali_pz', 'attuali_mt', 'guariti', 'deceduti', 'tamponi'])
    #print(oldDataBasDF)
    oldDataBasDF.to_csv(BASILICATA_FILE, index = False, header=True)
else:
    print("[INFO][csv Basilicata] Il file Basilicata esiste.")
    oldDataBasDF = pd.read_csv(BASILICATA_FILE)
    #print(oldDataBasDF)




"""
Creare il NAZIONE_file o caricarlo per
    Regioni
    Basilicata
"""

# ---------------------------------
# -- Creazione grafica
# ---------------------------------

genFont=("Helvetica", 15)

win = tk.Tk() #creo la finestra
win.geometry("480x250") #imposto risoluzione
win.title("COVID-19 Counter") #imposto titolo
win.resizable(False, False)
win.configure(background="black")

# configuro la griglia in modo che prenda l'intera finestra
for i in range(3):
    tk.Grid.columnconfigure(win, i, weight=1)
for i in range(7):
    tk.Grid.rowconfigure(win, i, weight=1)


# -- Pulsanti a SX
currentView = 0 #0 = IT, 1 = Reg, 2 = Bas
italy_icon = tk.PhotoImage(file=r"img/italy-80x.png")
italy_button = tk.Button(text="IT", font=genFont, command=italy_button, image=italy_icon, bg="gray23", borderwidth=0, width=50)
italy_button.grid(row=0, column=0, rowspan=2, sticky="NSEW")

reg_icon = tk.PhotoImage(file=r"img/regioni-80x.png")
regioni_button = tk.Button(text="Reg", font=genFont, command=reg_button, image=reg_icon, bg="gray23", borderwidth=0, width=50)
regioni_button.grid(row=2, column=0, rowspan=2, sticky="NSEW")

bas_icon = tk.PhotoImage(file=r"img/basilicata-80x.png")
basilicata_button = tk.Button(text="Bas", font=genFont, command=bas_button, image=bas_icon, bg="gray23", borderwidth=0, width=50)
basilicata_button.grid(row=4, column=0, rowspan=2, sticky="NSEW")

# -- Testi con dati
label_nazione = tk.Label(win, text="Italia", fg="white", bg="black", font=genFont)
label_nazione.grid(row=0, column=1, padx=10, pady=10)
label_data = tk.Label(win, text=text_data, fg="white", bg="black", font=genFont)
label_data.grid(row=1, column=1, padx=10, pady=3)
label_totale_positivi = tk.Label(win, text="Tot. positivi: " + text_tot_positivi, fg="orange", bg="black", font=genFont)
label_totale_positivi.grid(row=2, column=1, padx=10, pady=3)
label_nuovi_positivi = tk.Label(win, text="Nuovi: +"+text_new_positivi, fg="red", bg="black", font=genFont)
label_nuovi_positivi.grid(row=3, column=1, padx=10, pady=3)
label_guariti = tk.Label(win, text="Guariti: " + text_guariti, fg="green", bg="black", font=genFont)
label_guariti.grid(row=4, column=1, padx=10, pady=3)
label_deceduti = tk.Label(win, text="Deceduti: "+text_deceduti, fg="red", bg="black", font=genFont)
label_deceduti.grid(row=5, column=1, padx=10, pady=3)
label_tamponi = tk.Label(win, text="Tamponi: "+text_tamponi, fg="white", bg="black", font=genFont)
label_tamponi.grid(row=6, column=1, padx=10, pady=3)

# -- oggetti a dx

#aggiungere spacer per mettere il pulsante in fondo
#empty_spacer_label = tk.Label(win, text="")
#empty_spacer_label.grid(row=0, column=2, rowspan=6)
exit_icon = tk.PhotoImage(file=r"img/exit-80x.png")
exit_button = tk.Button(text="Esci", command=exit_button, font=genFont, image=exit_icon, bg="gray23", borderwidth=0, width=50)
exit_button.grid(row=0, column=2, rowspan=2, sticky="NSEW")

reload_icon = tk.PhotoImage(file=r"img/refresh-80x.png")
reload_button = tk.Button(text="Reload", command=lambda:reload(currentView), font=genFont, image=reload_icon, bg="gray23", borderwidth=0, width=50)
reload_button.grid(row=2, column=2, rowspan=2, sticky="NSEW")

reload(currentView) # Carico i dati alla prima esecuzione
incrementRegionCounter() # Avvio il thread per contare le regioni

if __name__ == "__main__":
    win.mainloop() #mostro la finestra
