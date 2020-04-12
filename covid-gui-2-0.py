# ------------------------------------------------------------------------------
# -- Covid 19 GUI 2.0
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# -- Librerie
# ------------------------------------------------------------------------------

import tkinter as tk
import csv
import pandas as pd
pd.options.mode.chained_assignment = None
import time
import threading
import os
from shutil import copyfile #usato per creare backup del csv
from datetime import date

# ------------------------------------------------------------------------------
# -- File
# ------------------------------------------------------------------------------

BACKUP_FOLDER = "./csv/backup/"
BACKUP_NAZ_FILE = BACKUP_FOLDER + "nazioneBkp_"
BACKUP_REG_FILE = BACKUP_FOLDER + "regioneBkp_"
BACKUP_BAS_FILE = BACKUP_FOLDER + "basilicataBkp_"
REGIONE_URL_CSV =  'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv'
PROVINCE_URL_CSV = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv'
NAZIONE_URL_CSV = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv'
NAZIONE_FILE = "./csv/nazioneData.csv"
REGIONE_FILE = "./csv/regioniData.csv"
BASILICATA_FILE = "./csv/basilicataData.csv"

# ------------------------------------------------------------------------------
# -- Variabili
# ------------------------------------------------------------------------------

# Dichiaro le variabili da utilizzare successivamente
data_nazione = pd.read_csv(NAZIONE_URL_CSV)
data_regione = pd.read_csv(REGIONE_URL_CSV)
data_province = pd.read_csv(PROVINCE_URL_CSV)

nazione_csv_rows = data_nazione.shape[0]
regione_csv_rows = data_regione.shape[0]
province_csv_rows = data_province.shape[0]
currentView = 0 # Parte con la view Italia
lastRegione = regione_csv_rows #lastRegione viene usato per iterare tra le regioni
timerIncremento = 10 # Numero di secondi per mostrare ogni regione nella GUI

nazione_data_rows = 0
nazione_data_columns = 0
regione_data_rows = 0
regione_data_columns = 0
basilicata_data_rows = 0
basilicata_data_columns = 0

debug_mode = False
backup_mode_nazione = True
backup_mode_regione = True
backup_mode_basilicata = True

text_nome = ""
text_data = ""
text_tot_positivi = ""
text_new_positivi = ""
text_dimessi = ""
text_deceduti = ""
text_tamponi = ""

if(debug_mode):
    print("[DEBUG] regione_csv_rows: " + str(regione_csv_rows))

ItDataFrame = pd.DataFrame()
regDataFrame = pd.DataFrame()
basDataFrame = pd.DataFrame()

# ------------------------------------------------------------------------------
# -- Nomi campi CSV Protezione civile
# ------------------------------------------------------------------------------

# NAZIONE
col_it_data = "data"
col_it_totale = "totale_positivi"
col_it_nuovi = "nuovi_positivi"
col_it_dimessi = "dimessi_guariti"
col_it_deceduti = "deceduti"
col_it_tamponi = "tamponi"

# REGIONI
col_reg_data = "data"
col_reg_nome = "denominazione_regione"
col_reg_totale = "totale_positivi"
col_reg_nuovi = "nuovi_positivi"
col_reg_dimessi = "dimessi_guariti"
col_reg_deceduti = "deceduti"
col_reg_tamponi = "tamponi"

# BASILICATA
col_bas_data = "data"
col_bas_sigla_prov = "sigla_provincia"
col_bas_tot_casi = "totale_casi"

# ------------------------------------------------------------------------------
# -- Funzioni
# ------------------------------------------------------------------------------

def downloadData():
    """
    Questa funzione scarica i dati dai CSV della pagina GitHub della Protezione Civile
    e aggiorna delle variabili contenenti il numero di righe di quei file
    """
    global data_nazione
    data_nazione = pd.read_csv(NAZIONE_URL_CSV)
    #Nome colonne: [data, stato, ricoverati_con_sintomi, terapia_intensiva, totale_ospedalizzati, isolamento_domiciliare, totale_positivi, nuovi_positivi, dimessi_guariti, deceduti, totale_casi, tamponi]
    global data_regione
    data_regione = pd.read_csv(REGIONE_URL_CSV)
    #Nome colonne: [data, stato, codice_regione, denominazione_regione, lat, long, ricoverati_con_sintomi, terapia_intensiva, totale_ospedalizzati, isolamento_domiciliare, totale_positivi, variazione_totale_positivi, nuovi_positivi, dimessi_guariti, deceduti, totale_casi, tamponi]
    global data_province
    data_province = pd.read_csv(PROVINCE_URL_CSV)
    #Nome colonne: [data, stato, codice_regione, denominazione_regione, codice_provincia, denominazione_provincia, sigla_provincia, lat, long, totale_casi]

    # Prendo il numero di righe di ogni csv, per il numero di colonne usare shape[1]
    global nazione_csv_rows
    nazione_csv_rows = data_nazione.shape[0]
    global regione_csv_rows
    regione_csv_rows = data_regione.shape[0]
    global province_csv_rows
    province_csv_rows = data_province.shape[0]
    # print("nazione: %d. regione: %d. province: %d." % (nazione_csv_rows, regione_csv_rows, province_csv_rows))

    #print(data_nazione.head())
    #print(data_regione.head())
    #print(data_province.head())

def updateCSV():

    """
    Questa funzione aggiorna i CSV locali contenenti i vari dati letti nell'arco dei giorni dal GitHub della Protezione Civile
    Durante la prima esecuzione, se i file non esistono, si prelevano i dati dai CSV di GitHub e si inseriscono nei CSV locali.
    Durante le esecuzioni successive viene confrontata l'ultima data salvata sul file:
        - se è uguale a quella del CSV di GitHub non si fa nulla
        - se è diversa, si prelevano i nuovi dati e si aggiorna il CSV locale
    """

    downloadData() #Scarico prima i dati

    global nazione_data_rows
    global nazione_data_columns
    global regione_data_rows
    global regione_data_columns
    global basilicata_data_rows
    global basilicata_data_columns

    global ItDataFrame
    global regDataFrame
    global basDataFrame

    # File Nazione
    if os.path.exists(NAZIONE_FILE) == False: #il file non esiste
        print("[INFO][updateCSV - NAZIONE_FILE] Il file non esiste. Lo creo.")
        itData=[[
            data_nazione.loc[0][col_it_data],
            data_nazione.loc[0][col_it_totale],
            data_nazione.loc[0][col_it_nuovi],
            data_nazione.loc[0][col_it_dimessi],
            data_nazione.loc[0][col_it_deceduti],
            data_nazione.loc[0][col_it_tamponi]
            ]]
        ItDataFrame = pd.DataFrame(itData, columns = ['data', 'totali', 'nuovi', 'dimessi', 'deceduti', 'tamponi'])
        #print(ItDataFrame)
        ItDataFrame.to_csv(NAZIONE_FILE, index = False, header = True)
    else: #il fine esiste
        print("[INFO][updateCSV - NAZIONE_FILE] Il file esiste. Leggo.")
        ItDataFrame = pd.read_csv(NAZIONE_FILE)
        nazione_data_rows = ItDataFrame.shape[0]
        nazione_data_columns = ItDataFrame.shape[1]
        #print(ItDataFrame)

        # Controllo se ci sono nuovi dati. Se sì, li inserisco
        if(data_nazione.loc[0][col_it_data] != ItDataFrame.loc[nazione_data_rows-1]["data"]):
            print("[INFO][updateCSV - NAZIONE_FILE] Dati diversi rilevati, carico i nuovi.")

            if(backup_mode_nazione):
                print("[INFO] Backup file Nazione abilitato.")
                if(os.path.exists(BACKUP_NAZ_FILE + str(date.today()) + ".csv") == False): # Se il file di backup odierno non esiste, lo crea
                    print("[INFO] Backup csv Nazione.")
                    copyfile(NAZIONE_FILE, BACKUP_NAZ_FILE + str(date.today()) + ".csv")
                else:
                    print("[INFO] File backup già odierno già presente. Salto backup.")

            if(debug_mode):
                print("[DEBUG] " + str(data_nazione.loc[0][col_it_data]) + ", "
                + str(ItDataFrame.loc[nazione_data_rows-1]["data"]))
            itNewData=[[
                data_nazione.loc[0][col_it_data],
                data_nazione.loc[0][col_it_totale],
                data_nazione.loc[0][col_it_nuovi],
                data_nazione.loc[0][col_it_dimessi],
                data_nazione.loc[0][col_it_deceduti],
                data_nazione.loc[0][col_it_tamponi]
                ]]

            ItNewDataFrame = pd.DataFrame(itNewData, columns = ['data', 'totali', 'nuovi', 'dimessi', 'deceduti', 'tamponi']) # itNewData deve essere 2D list [[...]]
            ItDataFrame = ItDataFrame.append(ItNewDataFrame, ignore_index=True)

            if(debug_mode):
                print("[DEBUG] ItDataFrame: ")
                print(ItDataFrame)

            ItDataFrame.to_csv(NAZIONE_FILE, index = False, header = True)


    # File Regioni
    if os.path.exists(REGIONE_FILE) == False: #il file non esiste
        print("[INFO][updateCSV - REGIONE_FILE] Il file non esiste. Lo creo.")
        regData=[[data_regione.loc[0][col_reg_data]]]

        for regNum in range(regione_csv_rows): #Aggiungo i dati di ogni regione alla lista
            regData[0].append(data_regione.loc[regNum][col_reg_nome])
            regData[0].append(data_regione.loc[regNum][col_reg_totale])
            regData[0].append(data_regione.loc[regNum][col_reg_nuovi])
            regData[0].append(data_regione.loc[regNum][col_reg_dimessi])
            regData[0].append(data_regione.loc[regNum][col_reg_deceduti])
            regData[0].append(data_regione.loc[regNum][col_reg_tamponi])

        if(debug_mode):
            print("[DEBUG] regData len: " + str(len(regData)))
            print("[DEBUG] regData: ")
            print(regData)

        regDataFrame = pd.DataFrame(regData, columns = ['data',
            '1_nome', '1_totali', '1_nuovi', '1_dimessi', '1_deceduti', '1_tamponi',
            '2_nome', '2_totali', '2_nuovi', '2_dimessi', '2_deceduti', '2_tamponi',
            '3_nome', '3_totali', '3_nuovi', '3_dimessi', '3_deceduti', '3_tamponi',
            '4_nome', '4_totali', '4_nuovi', '4_dimessi', '4_deceduti', '4_tamponi',
            '5_nome', '5_totali', '5_nuovi', '5_dimessi', '5_deceduti', '5_tamponi',
            '6_nome', '6_totali', '6_nuovi', '6_dimessi', '6_deceduti', '6_tamponi',
            '7_nome', '7_totali', '7_nuovi', '7_dimessi', '7_deceduti', '7_tamponi',
            '8_nome', '8_totali', '8_nuovi', '8_dimessi', '8_deceduti', '8_tamponi',
            '9_nome', '9_totali', '9_nuovi', '9_dimessi', '9_deceduti', '9_tamponi',
            '10_nome', '10_totali', '10_nuovi', '10_dimessi', '10_deceduti', '10_tamponi',
            '11_nome', '11_totali', '11_nuovi', '11_dimessi', '11_deceduti', '11_tamponi',
            '12_nome', '12_totali', '12_nuovi', '12_dimessi', '12_deceduti', '12_tamponi',
            '13_nome', '13_totali', '13_nuovi', '13_dimessi', '13_deceduti', '13_tamponi',
            '14_nome', '14_totali', '14_nuovi', '14_dimessi', '14_deceduti', '14_tamponi',
            '15_nome', '15_totali', '15_nuovi', '15_dimessi', '15_deceduti', '15_tamponi',
            '16_nome', '16_totali', '16_nuovi', '16_dimessi', '16_deceduti', '16_tamponi',
            '17_nome', '17_totali', '17_nuovi', '17_dimessi', '17_deceduti', '17_tamponi',
            '18_nome', '18_totali', '18_nuovi', '18_dimessi', '18_deceduti', '18_tamponi',
            '19_nome', '19_totali', '19_nuovi', '19_dimessi', '19_deceduti', '19_tamponi',
            '20_nome', '20_totali', '20_nuovi', '20_dimessi', '20_deceduti', '20_tamponi',
            '21_nome', '21_totali', '21_nuovi', '21_dimessi', '21_deceduti', '21_tamponi'])

        if(debug_mode):
            print("[DEBUG] regDataFrame:")
            print(regDataFrame)
        regDataFrame.to_csv(REGIONE_FILE, index = False, header = True)

    else: #il fine esiste
        print("[INFO][updateCSV - REGIONE_FILE] Il file esiste. Leggo.")
        regDataFrame = pd.read_csv(REGIONE_FILE)
        regione_data_rows = regDataFrame.shape[0]
        regione_data_columns = regDataFrame.shape[1]
        #print(regDataFrame)

        # ----- TEST
        """
        for i in range(regione_csv_rows):
            colonna = str(i+1) + "_nome"
            print(regDataFrame.loc[0][colonna])
        """

        # Controllo se ci sono nuovi dati. Se sì, li inserisco
        if(data_regione.loc[0][col_reg_data] != regDataFrame.loc[regione_data_rows-1]["data"]):
            print("[INFO][updateCSV - REGIONE_FILE] Dati diversi rilevati, carico i nuovi.")

            if(debug_mode):
                print("[DEBUG][updateCSV - REGIONE_FILE] " + str(data_regione.loc[0][col_reg_data])
                + str(regDataFrame.loc[regione_data_rows-1]["data"]))

            if(backup_mode_regione):
                print("[INFO] Backup file Regione abilitato.")
                if(os.path.exists(BACKUP_REG_FILE + str(date.today()) + ".csv") == False): # Se il file di backup odierno non esiste, lo crea
                    print("[INFO] Backup csv Regione.")
                    copyfile(REGIONE_FILE, BACKUP_REG_FILE + str(date.today()) + ".csv")
                else:
                    print("[INFO] File backup già odierno già presente. Salto backup.")

            regNewData=[[data_regione.loc[0][col_reg_data]]]
            for regNewNum in range(regione_csv_rows): #Aggiungo i dati di ogni regione alla lista
                regNewData[0].append(data_regione.loc[regNewNum][col_reg_nome])
                regNewData[0].append(data_regione.loc[regNewNum][col_reg_totale])
                regNewData[0].append(data_regione.loc[regNewNum][col_reg_nuovi])
                regNewData[0].append(data_regione.loc[regNewNum][col_reg_dimessi])
                regNewData[0].append(data_regione.loc[regNewNum][col_reg_deceduti])
                regNewData[0].append(data_regione.loc[regNewNum][col_reg_tamponi])

            regNewDataFrame = pd.DataFrame(regNewData, columns = ['data',
                '1_nome', '1_totali', '1_nuovi', '1_dimessi', '1_deceduti', '1_tamponi',
                '2_nome', '2_totali', '2_nuovi', '2_dimessi', '2_deceduti', '2_tamponi',
                '3_nome', '3_totali', '3_nuovi', '3_dimessi', '3_deceduti', '3_tamponi',
                '4_nome', '4_totali', '4_nuovi', '4_dimessi', '4_deceduti', '4_tamponi',
                '5_nome', '5_totali', '5_nuovi', '5_dimessi', '5_deceduti', '5_tamponi',
                '6_nome', '6_totali', '6_nuovi', '6_dimessi', '6_deceduti', '6_tamponi',
                '7_nome', '7_totali', '7_nuovi', '7_dimessi', '7_deceduti', '7_tamponi',
                '8_nome', '8_totali', '8_nuovi', '8_dimessi', '8_deceduti', '8_tamponi',
                '9_nome', '9_totali', '9_nuovi', '9_dimessi', '9_deceduti', '9_tamponi',
                '10_nome', '10_totali', '10_nuovi', '10_dimessi', '10_deceduti', '10_tamponi',
                '11_nome', '11_totali', '11_nuovi', '11_dimessi', '11_deceduti', '11_tamponi',
                '12_nome', '12_totali', '12_nuovi', '12_dimessi', '12_deceduti', '12_tamponi',
                '13_nome', '13_totali', '13_nuovi', '13_dimessi', '13_deceduti', '13_tamponi',
                '14_nome', '14_totali', '14_nuovi', '14_dimessi', '14_deceduti', '14_tamponi',
                '15_nome', '15_totali', '15_nuovi', '15_dimessi', '15_deceduti', '15_tamponi',
                '16_nome', '16_totali', '16_nuovi', '16_dimessi', '16_deceduti', '16_tamponi',
                '17_nome', '17_totali', '17_nuovi', '17_dimessi', '17_deceduti', '17_tamponi',
                '18_nome', '18_totali', '18_nuovi', '18_dimessi', '18_deceduti', '18_tamponi',
                '19_nome', '19_totali', '19_nuovi', '19_dimessi', '19_deceduti', '19_tamponi',
                '20_nome', '20_totali', '20_nuovi', '20_dimessi', '20_deceduti', '20_tamponi',
                '21_nome', '21_totali', '21_nuovi', '21_dimessi', '21_deceduti', '21_tamponi'])

            regDataFrame = regDataFrame.append(regNewDataFrame, ignore_index = True, sort=False)
            if(debug_mode):
                print("[DEBUG] regDataFrame updated: ")
                print(regDataFrame)

            regDataFrame.to_csv(REGIONE_FILE, index = False, header = True)

    # File Basilicata
    if os.path.exists(BASILICATA_FILE) == False: #il file non esiste
        print("[INFO][updateCSV - BASILICATA_FILE] Il file non esiste. Lo creo.")
        for regNum in range(regione_csv_rows):
            if(data_regione.loc[regNum][col_reg_nome] == "Basilicata"):

                found = 0
                for provNum in range(province_csv_rows):
                    if(data_province.loc[provNum][col_bas_sigla_prov] == "MT"):
                        found += 1
                        attuali_mt = data_province.loc[provNum][col_bas_tot_casi]
                    elif(data_province.loc[provNum][col_bas_sigla_prov] == "PZ"):
                        found += 1
                        attuali_pz = data_province.loc[provNum][col_bas_tot_casi]
                    if(found>=2):
                        break
                basData = [[
                    data_regione.loc[regNum][col_reg_data],
                    data_regione.loc[regNum][col_reg_totale],
                    attuali_pz,
                    attuali_mt,
                    data_regione.loc[regNum][col_reg_nuovi],
                    data_regione.loc[regNum][col_reg_dimessi],
                    data_regione.loc[regNum][col_reg_deceduti],
                    data_regione.loc[regNum][col_reg_tamponi]
                    ]]
                break

        basDataFrame = pd.DataFrame(basData, columns = ['data', 'totali', 'attuali_pz', 'attuali_mt', 'nuovi', 'dimessi', 'deceduti', 'tamponi'])
        basDataFrame.to_csv(BASILICATA_FILE, index = False, header = True)

        if(debug_mode):
            print("[DEBUG] basDataFrame:")
            print(basDataFrame)

    else: #il file esiste
        print("[INFO][updateCSV - BASILICATA_FILE] Il file esiste. Leggo.")
        basDataFrame = pd.read_csv(BASILICATA_FILE)
        basilicata_data_rows = basDataFrame.shape[0]
        basilicata_data_columns = basDataFrame.shape[1]

        # Controllo se ci sono nuovi dati. Se sì, li inserisco
        for regBasNum in range(regione_csv_rows):
            if(data_regione.loc[regBasNum][col_reg_nome] == "Basilicata"):
                if(data_regione.loc[regBasNum][col_reg_data] != basDataFrame.loc[basilicata_data_rows-1]["data"]):
                    print("[INFO][updateCSV - BASILICATA_FILE] Dati diversi rilevati, carico i nuovi.")
                    if(debug_mode):
                        print("[DEBUG][updateCSV - BASILICATA_FILE] " +
                        str(data_regione.loc[regBasNum][col_reg_data]) + ", " +
                        str(basDataFrame.loc[basilicata_data_rows-1]["data"]))

                    if(backup_mode_basilicata):
                        print("[INFO] Backup file Nazione abilitato.")
                        if(os.path.exists(BACKUP_BAS_FILE + str(date.today()) + ".csv") == False): # Se il file di backup odierno non esiste, lo crea
                            print("[INFO] Backup csv Basilicata.")
                            copyfile(BASILICATA_FILE, BACKUP_BAS_FILE + str(date.today()) + ".csv")
                        else:
                            print("[INFO] File backup già odierno già presente. Salto backup.")

                    found = 0
                    for provNewNum in range(province_csv_rows):
                        if(data_province.loc[provNewNum][col_bas_sigla_prov] == "MT"):
                            found += 1
                            attuali_mt = data_province.loc[provNewNum][col_bas_tot_casi]
                        elif(data_province.loc[provNewNum][col_bas_sigla_prov] == "PZ"):
                            found += 1
                            attuali_pz = data_province.loc[provNewNum][col_bas_tot_casi]
                        if(found>=2):
                            break
                    basNewData = [[
                        data_regione.loc[regBasNum][col_reg_data],
                        data_regione.loc[regBasNum][col_reg_totale],
                        attuali_pz,
                        attuali_mt,
                        data_regione.loc[regBasNum][col_reg_nuovi],
                        data_regione.loc[regBasNum][col_reg_dimessi],
                        data_regione.loc[regBasNum][col_reg_deceduti],
                        data_regione.loc[regBasNum][col_reg_tamponi]
                        ]]

                    basNewDataFrame = pd.DataFrame(basNewData, columns = ['data', 'totali', 'attuali_pz', 'attuali_mt', 'nuovi', 'dimessi', 'deceduti', 'tamponi'])
                    basDataFrame = basDataFrame.append(basNewDataFrame, ignore_index=True)
                    basDataFrame.to_csv(BASILICATA_FILE, index = False, header = True)

                    break

    if(debug_mode):
        print("[DEBUG] IT DATA - rows: " + str(nazione_data_rows) + ", col: " + str(nazione_data_columns) + ", "
            + "REG DATA - rows: " + str(regione_data_rows) + ", col: " + str(regione_data_columns) + ", "
            + "BAS DATA - rows: " + str(basilicata_data_rows) + ", col: " + str(basilicata_data_columns))


def updateData(currentData):

    """
    Questa funzione aggiorna le stringhe globali utilizzate dalla GUI per mostrare i Dati
    arguments: currentData - int del valore di: 0 - View Italia, inserisce nelle str i dati per Italia
                                                1 - View Regioni, inserisce nelle str i dati per le regioni
                                                2 - View Basilicata, inserisce nelle str i dati per la Basilicata
    """

    global text_nome
    global text_data
    global text_tot_positivi
    global text_new_positivi
    global text_dimessi
    global text_deceduti
    global text_tamponi
    global lastRegione

    global ItDataFrame
    global regDataFrame
    global basDataFrame

    print("[INFO][updateData] View corrente: " + str(currentData))

    if(currentData == 0): # Caso Italia

        if(debug_mode):
            print("[DEBUG] nazione_data_rows: " + str(nazione_data_rows))

        if(nazione_data_rows>1): # Durante la prima esecuzione nazione_data_rows=1, quindi salto il calcolo della differenza
            past_dimessi = (str(ItDataFrame.loc[nazione_data_rows-1]["dimessi"] - ItDataFrame.loc[nazione_data_rows-2]["dimessi"])
                if (ItDataFrame.loc[nazione_data_rows-1]["dimessi"] - ItDataFrame.loc[nazione_data_rows-2]["dimessi"]) < 0
                else "+" + str(ItDataFrame.loc[nazione_data_rows-1]["dimessi"] - ItDataFrame.loc[nazione_data_rows-2]["dimessi"]))

            past_deceduti = (str(ItDataFrame.loc[nazione_data_rows-1]["deceduti"] - ItDataFrame.loc[nazione_data_rows-2]["deceduti"])
                if (ItDataFrame.loc[nazione_data_rows-1]["deceduti"] - ItDataFrame.loc[nazione_data_rows-2]["deceduti"]) < 0
                else "+" + str(ItDataFrame.loc[nazione_data_rows-1]["deceduti"] - ItDataFrame.loc[nazione_data_rows-2]["deceduti"]))

            past_tamponi = (str(ItDataFrame.loc[nazione_data_rows-1]["tamponi"] - ItDataFrame.loc[nazione_data_rows-2]["tamponi"])
                if (ItDataFrame.loc[nazione_data_rows-1]["tamponi"] - ItDataFrame.loc[nazione_data_rows-2]["tamponi"]) < 0
                else "+" + str(ItDataFrame.loc[nazione_data_rows-1]["tamponi"] - ItDataFrame.loc[nazione_data_rows-2]["tamponi"]))
        else:
            past_dimessi = "+0"
            past_deceduti = "+0"
            past_tamponi = "+0"



        text_nome = "Italia"
        text_data = data_nazione.loc[0][col_it_data]
        text_tot_positivi = str(data_nazione.loc[0][col_it_totale])
        text_new_positivi = str(data_nazione.loc[0][col_it_nuovi])
        text_dimessi = str(data_nazione.loc[0][col_it_dimessi]) + " (" + past_dimessi + ")"
        text_deceduti = str(data_nazione.loc[0][col_it_deceduti]) + " (" + past_deceduti + ")"
        text_tamponi = str(data_nazione.loc[0][col_it_tamponi]) + " (" + past_tamponi + ")"



    elif(currentData == 1): # Caso regioni

        if(debug_mode):
            print("[DEBUG] regione_data_rows: " + str(regione_data_rows))

        if(regione_data_rows>1):  # Durante la prima esecuzione regione_data_rows=1, quindi salto il calcolo della differenza
            past_dimessi = (str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_dimessi"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_dimessi"])
                if (regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_dimessi"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_dimessi"]) < 0
                else "+" + str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_dimessi"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_dimessi"]))

            past_deceduti = (str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_deceduti"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_deceduti"])
                if (regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_deceduti"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_deceduti"]) < 0
                else "+" + str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_deceduti"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_deceduti"]))

            past_tamponi = (str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_tamponi"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_tamponi"])
                if (regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_tamponi"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_tamponi"]) < 0
                else "+" + str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_tamponi"] - regDataFrame.loc[regione_data_rows-2][str(lastRegione) + "_tamponi"]))
        else:
            past_dimessi = "+0"
            past_deceduti = "+0"
            past_tamponi = "+0"

        text_nome = str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_nome"])
        text_data = str(regDataFrame.loc[regione_data_rows-1]["data"])
        text_tot_positivi = str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_totali"])
        text_new_positivi = str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_nuovi"])
        text_dimessi = str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_dimessi"]) + " (" + past_dimessi + ")"
        text_deceduti = str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_deceduti"]) + " (" + past_deceduti + ")"
        text_tamponi = str(regDataFrame.loc[regione_data_rows-1][str(lastRegione) + "_tamponi"]) + " (" + past_tamponi + ")"

    elif(currentData == 2): # Caso Basilicata


        for regNum in range(regione_csv_rows):
            if(data_regione.loc[regNum][col_reg_nome] == "Basilicata"):

                found = 0
                for provNum in range(province_csv_rows):
                    if(data_province.loc[provNum][col_bas_sigla_prov] == "MT"):
                        found += 1
                        attuali_mt = data_province.loc[provNum][col_bas_tot_casi]
                    elif(data_province.loc[provNum][col_bas_sigla_prov] == "PZ"):
                        found += 1
                        attuali_pz = data_province.loc[provNum][col_bas_tot_casi]
                    if(found>=2):
                        break

                if(debug_mode):
                    print("[DEBUG] basilicata_data_rows: " + str(basilicata_data_rows))

                if(basilicata_data_rows>1): # Durante la prima esecuzione basilicata_data_rows=1, quindi salto il calcolo della differenza
                    past_nuovi_pz = (str(basDataFrame.loc[basilicata_data_rows-1]["attuali_pz"] - basDataFrame.loc[basilicata_data_rows-2]["attuali_pz"])
                        if(basDataFrame.loc[basilicata_data_rows-1]["attuali_pz"] - basDataFrame.loc[basilicata_data_rows-2]["attuali_pz"]) < 0
                        else "+"+str(basDataFrame.loc[basilicata_data_rows-1]["attuali_pz"] - basDataFrame.loc[basilicata_data_rows-2]["attuali_pz"]))

                    past_nuovi_mt = (str(basDataFrame.loc[basilicata_data_rows-1]["attuali_mt"] - basDataFrame.loc[basilicata_data_rows-2]["attuali_mt"])
                        if(basDataFrame.loc[basilicata_data_rows-1]["attuali_mt"] - basDataFrame.loc[basilicata_data_rows-2]["attuali_mt"]) < 0
                        else "+" + str(basDataFrame.loc[basilicata_data_rows-1]["attuali_mt"] - basDataFrame.loc[basilicata_data_rows-2]["attuali_mt"]))

                    past_dimessi = (str(basDataFrame.loc[basilicata_data_rows-1]["dimessi"] - basDataFrame.loc[basilicata_data_rows-2]["dimessi"])
                        if (basDataFrame.loc[basilicata_data_rows-1]["dimessi"] - basDataFrame.loc[basilicata_data_rows-2]["dimessi"]) < 0
                        else "+" + str(basDataFrame.loc[basilicata_data_rows-1]["dimessi"] - basDataFrame.loc[basilicata_data_rows-2]["dimessi"]))

                    past_deceduti = (str(basDataFrame.loc[basilicata_data_rows-1]["deceduti"] - basDataFrame.loc[basilicata_data_rows-2]["deceduti"])
                        if (basDataFrame.loc[basilicata_data_rows-1]["deceduti"] - basDataFrame.loc[basilicata_data_rows-2]["deceduti"]) < 0
                        else "+" + str(basDataFrame.loc[basilicata_data_rows-1]["deceduti"] - basDataFrame.loc[basilicata_data_rows-2]["deceduti"]))

                    past_tamponi = (str(basDataFrame.loc[basilicata_data_rows-1]["tamponi"] - basDataFrame.loc[basilicata_data_rows-2]["tamponi"])
                        if (basDataFrame.loc[basilicata_data_rows-1]["tamponi"] - basDataFrame.loc[basilicata_data_rows-2]["tamponi"]) < 0
                        else "+" + str(basDataFrame.loc[basilicata_data_rows-1]["tamponi"] - basDataFrame.loc[basilicata_data_rows-2]["tamponi"]))
                else:
                    past_nuovi_pz = "+0"
                    past_nuovi_mt = "+0"
                    past_dimessi = "+0"
                    past_deceduti = "+0"
                    past_tamponi = "+0"

                text_nome = data_regione.loc[regNum][col_reg_nome]
                text_data = data_regione.loc[regNum][col_reg_data]
                text_tot_positivi = str(data_regione.loc[regNum][col_reg_totale]) + " (PZ " + str(attuali_pz) + ") (MT " + str(attuali_mt) + ")"
                text_new_positivi = str(data_regione.loc[regNum][col_reg_nuovi]) + " (PZ: " + past_nuovi_pz + ") (MT:" + past_nuovi_mt + ")"
                text_dimessi = str(data_regione.loc[regNum][col_reg_dimessi]) + " (" + past_dimessi + ")"
                text_deceduti = str(data_regione.loc[regNum][col_reg_deceduti]) + " (" + past_deceduti + ")"
                text_tamponi = str(data_regione.loc[regNum][col_reg_tamponi]) + " (" + past_tamponi + ")"

                break

    else: #dati errati
        print("[ERROR] Valore currentView errato: " + str(currentData))
        os._exit(currentData)

def incrementRegionCounter():

    """
    Questa funzione avvia un thread che, ogni 'timerIncremento' secondi incrementa il valore di lastRegione,
    utilizzato per la selezione della regione nella gui "Regioni",
    in modo da mostrare una regione diversa ogni 'timerIncremento' secondi.
    """
    global lastRegione
    global currentView

    if(currentView == 1):
        lastRegione +=1
        if(lastRegione>=regione_csv_rows):
            lastRegione = 1

        reload(currentView)
    th = threading.Timer(timerIncremento, incrementRegionCounter)
    th.start()

# ------------------------------------------------------------------------------
# -- Funzioni Pulsanti
# ------------------------------------------------------------------------------

def italy_button():
    global currentView
    currentView = 0
    reload(currentView)

def reg_button():
    global currentView
    global lastRegione
    lastRegione +=1
    if(lastRegione>=regione_csv_rows):
        lastRegione = 1
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

    updateCSV()
    updateData(curView)

    label_nazione["text"] = text_nome
    label_data["text"] = text_data
    label_totale_positivi["text"] = "Totale: " + text_tot_positivi
    label_nuovi_positivi["text"] = "Nuovi: +" + text_new_positivi
    label_guariti["text"] = "Guariti: " + text_dimessi
    label_deceduti["text"] = "Deceduti: " + text_deceduti
    label_tamponi["text"] = "Tamponi: " + text_tamponi

# -----------------
# Temp function call

if(debug_mode):
    print("[DEBUG] Dati " + text_nome + ", " + str(text_data)
    + ": Tot: " + str(text_tot_positivi) + "(+" + str(text_new_positivi)
    + "), dimessi: " + str(text_dimessi) + ", deceduti: " + str(text_deceduti)
    + ", tamponi: " + str(text_tamponi))

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
label_nazione = tk.Label(win, text=text_nome, fg="white", bg="black", font=genFont)
label_nazione.grid(row=0, column=1, padx=10, pady=10)
label_data = tk.Label(win, text=text_data, fg="white", bg="black", font=genFont)
label_data.grid(row=1, column=1, padx=10, pady=3)
label_totale_positivi = tk.Label(win, text="Totale: " + text_tot_positivi, fg="orange", bg="black", font=genFont)
label_totale_positivi.grid(row=2, column=1, padx=10, pady=3)
label_nuovi_positivi = tk.Label(win, text="Nuovi: +"+ text_new_positivi, fg="red", bg="black", font=genFont)
label_nuovi_positivi.grid(row=3, column=1, padx=10, pady=3)
label_guariti = tk.Label(win, text="Guariti: " + text_dimessi, fg="green", bg="black", font=genFont)
label_guariti.grid(row=4, column=1, padx=10, pady=3)
label_deceduti = tk.Label(win, text="Deceduti: "+ text_deceduti, fg="red", bg="black", font=genFont)
label_deceduti.grid(row=5, column=1, padx=10, pady=3)
label_tamponi = tk.Label(win, text="Tamponi: "+ text_tamponi, fg="white", bg="black", font=genFont)
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

incrementRegionCounter() # Avvio il thread per l'incremento del numero delle regioni
reload(currentView) # Carico i dati alla prima esecuzione

if __name__ == "__main__":
    win.mainloop() #mostro la finestra
