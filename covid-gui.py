# ---------------------------------
# -- Librerie
# ---------------------------------

import tkinter as tk
import csv
import pandas as pd
import time 
import threading
import os

# ---------------------------------
# -- Costanti
# ---------------------------------

REGIONE_URL_CSV =  'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv'
PROVINCE_URL_CSV = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv'
NAZIONE_URL_CSV = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv'

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

    print("View corrente: " + str(currentData))
    if(currentData == 0): #Caso Italia
        print("Carico i dati Italia")
        
        text_data = str(data_nazione.loc[0]["data"])
        text_tot_positivi = str(data_nazione.loc[0]["totale_attualmente_positivi"])    
        text_new_positivi = str(data_nazione.loc[0]["nuovi_attualmente_positivi"])        
        text_guariti = str(data_nazione.loc[0]["dimessi_guariti"])        
        text_deceduti = str(data_nazione.loc[0]["deceduti"])        
        text_tamponi = str(data_nazione.loc[0]["tamponi"])
    
    elif(currentData == 1): #Caso regioni
        print("Carico i dati regione")

        text_regione = str(data_regione.loc[lastRegione]["denominazione_regione"])     
        text_data = str(data_regione.loc[lastRegione]["data"])     
        text_tot_positivi = str(data_regione.loc[lastRegione]["totale_attualmente_positivi"])
        text_new_positivi = str(data_regione.loc[lastRegione]["nuovi_attualmente_positivi"])
        text_guariti = str(data_regione.loc[lastRegione]["dimessi_guariti"])
        text_deceduti = str(data_regione.loc[lastRegione]["deceduti"])
        text_tamponi = str(data_regione.loc[lastRegione]["tamponi"])

    elif(currentData == 2): #Caso Basilicata
        print("Carico i dati Basilicata")

        for i in range(regione_int):
            if(data_regione.loc[i]["denominazione_regione"] == "Basilicata"):
                
                found=0
                for j in range(province_int):
                    if(data_province.loc[j]["sigla_provincia"] == "MT"):
                        found+=1
                        mt_case = str(data_province.loc[j]["totale_casi"])
                    elif(data_province.loc[j]["sigla_provincia"] == "PZ"):
                        found+=1
                        pz_case = str(data_province.loc[j]["totale_casi"])
                    if(found >= 2):
                        break

                text_data = str(data_regione.loc[i]["data"])     
                text_tot_positivi = str(data_regione.loc[i]["totale_attualmente_positivi"]) + " PZ(" + pz_case + "), MT(" + mt_case + ")"
                text_new_positivi = str(data_regione.loc[i]["nuovi_attualmente_positivi"])
                text_guariti = str(data_regione.loc[i]["dimessi_guariti"])
                text_deceduti = str(data_regione.loc[i]["deceduti"])
                text_tamponi = str(data_regione.loc[i]["tamponi"])
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

incrementRegionCounter()  

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
italy_button = tk.Button(text="IT", font=genFont, command=italy_button, image=italy_icon, bg="gray23", borderwidth=0)
italy_button.grid(row=0, column=0, rowspan=2, sticky="NSEW")

reg_icon = tk.PhotoImage(file=r"img/regioni-80x.png")
regioni_button = tk.Button(text="Reg", font=genFont, command=reg_button, image=reg_icon, bg="gray23", borderwidth=0)
regioni_button.grid(row=2, column=0, rowspan=2, sticky="NSEW")

bas_icon = tk.PhotoImage(file=r"img/basilicata-80x.png")
basilicata_button = tk.Button(text="Bas", font=genFont, command=bas_button, image=bas_icon, bg="gray23", borderwidth=0)
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
exit_button = tk.Button(text="Esci", command=exit_button, font=genFont, image=exit_icon, bg="gray23", borderwidth=0)
exit_button.grid(row=0, column=2, rowspan=2, sticky="NSEW")       

reload_icon = tk.PhotoImage(file=r"img/refresh-80x.png")
reload_button = tk.Button(text="Reload", command=lambda:reload(currentView), font=genFont, image=reload_icon, bg="gray23", borderwidth=0)
reload_button.grid(row=2, column=2, rowspan=2, sticky="NSEW")


if __name__ == "__main__":
    win.mainloop() #mostro la finestra