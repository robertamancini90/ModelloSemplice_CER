import time
import numpy as np
import pandas as pd

def Yearly_Calculations(PV_plant, battery, consumption, economy):
        
    df = pd.DataFrame()
    
    # Import battery input
    SOC_min = battery['SOC_min']   
    eta_BC = battery['eta_BC']   
    eta_BD = battery['eta_BD']   
    SOC_0 = battery['SOC_0']   
    Capacity_Battery = battery['Capacity_Battery']   
    Maximum_Power = battery['Maximum_Power']
    
    # Import consumption data
    df['Consumo carichi, kWh'] = consumption['Consumption_Vector']
    
    # Import production data    
    df['Produzione PV, kWh'] =  PV_plant['Production_Vector']
    PV_kWp = PV_plant['PV_kWp']
 
    # Import economic data
    
    CAPEX_PV_specifico = economy['CAPEX_PV_specifico']
    CAPEX_battery_specifico = economy['CAPEX_battery_specifico']
    OPEX_Perc = economy['OPEX_Perc']
    Inverter = economy['Inverter']
    Incentivo_MISE = economy['Incentivo_MISE']
    Sgravio_ARERA = economy['Sgravio_ARERA']
    Prezzo_El_Mercato = economy['Prezzo_El_Mercato']


    
    DOD = 100-SOC_min                               # Massimo Depth of Discharge, %
    Min_Charge_Battery = SOC_min*Capacity_Battery/100
    Useful_Capacity = DOD*Capacity_Battery/100      # Capacità utile, kWh
    
    df['timestamp'] = pd.date_range('01/1/2021',periods=len(consumption['Consumption_Vector']), freq='1H')
    df.set_index('timestamp', drop=True, inplace=True)


    # Inizializza i vettori per il calclo
    df['Energia condivisa, kWh'] = np.zeros(len(df))
    df['Energia condivisa batteria, kWh'] = np.zeros(len(df))
    df['Energia condivisa PV, kWh'] = np.zeros(len(df))
    df['Energia disponibile PV, kWh'] = np.zeros(len(df))
    df['Energia ricarica batteria, kWh'] = np.zeros(len(df))
    df['Energia scarica batteria, kWh'] = np.zeros(len(df))
    df['Energia immagazzinata in batteria, kWh'] = np.zeros(len(df))
    df['Stato di carica batteria, %'] = np.zeros(len(df))
    df['Energia immessa in rete extra, kWh'] = np.zeros(len(df))
    df['Energia prelevata dalla rete extra, kWh'] = np.zeros(len(df))
    df['Energia immessa in rete tot, kWh'] = np.zeros(len(df))
    df['Energia prelevata dalla rete tot, kWh'] = np.zeros(len(df))

    # Definisce la stato iniziale al tempo 0
    df['Stato di carica batteria, %'][df.index[0]] = SOC_0
    df['Energia immagazzinata in batteria, kWh'][df.index[0]] = Capacity_Battery*SOC_0/100
    df['Energia condivisa PV, kWh'][df.index[0]] = min(df['Consumo carichi, kWh'][df.index[0]], df['Produzione PV, kWh'][df.index[0]])
    df['Energia disponibile PV, kWh'][df.index[0]] = max(0,df['Produzione PV, kWh'][df.index[0]]-df['Consumo carichi, kWh'][df.index[0]])
    df['Energia immessa in rete extra, kWh'][df.index[0]] = df['Energia disponibile PV, kWh'][df.index[0]]
    df['Energia prelevata dalla rete extra, kWh'][df.index[0]] = df['Consumo carichi, kWh'][df.index[0]]-df['Produzione PV, kWh'][df.index[0]]
    df['Energia immessa in rete tot, kWh'][df.index[0]] = df['Energia immessa in rete extra, kWh'][df.index[0]] +df['Produzione PV, kWh'][df.index[0]]
    df['Energia prelevata dalla rete tot, kWh'][df.index[0]] = df['Consumo carichi, kWh'][df.index[0]]

    for i in range(1,len(df)):

        df['Energia condivisa PV, kWh'][i] = min(df['Consumo carichi, kWh'][i], df['Produzione PV, kWh'][i])
        df['Energia disponibile PV, kWh'][i] = max(0,df['Produzione PV, kWh'][i]-df['Consumo carichi, kWh'][i])

        if df['Consumo carichi, kWh'][i]>df['Produzione PV, kWh'][i]:
            df['Energia scarica batteria, kWh'][i] = eta_BD*min(df['Consumo carichi, kWh'][i]-df['Produzione PV, kWh'][i], min(df['Energia immagazzinata in batteria, kWh'][i-1]-Min_Charge_Battery,Maximum_Power))
            if (df['Consumo carichi, kWh'][i]-df['Energia scarica batteria, kWh'][i]-df['Produzione PV, kWh'][i])>0:
                df['Energia prelevata dalla rete extra, kWh'][i] = df['Consumo carichi, kWh'][i]-df['Energia scarica batteria, kWh'][i]-df['Produzione PV, kWh'][i]
        else:
            df['Energia ricarica batteria, kWh'][i] = eta_BC*min(df['Energia disponibile PV, kWh'][i],  min(Capacity_Battery - df['Energia immagazzinata in batteria, kWh'][i-1], Maximum_Power))
            if df['Energia ricarica batteria, kWh'][i]<df['Energia disponibile PV, kWh'][i]:
                df['Energia immessa in rete extra, kWh'][i] = df['Energia disponibile PV, kWh'][i]-df['Energia ricarica batteria, kWh'][i]   

        df['Energia condivisa batteria, kWh'][i] = df['Energia scarica batteria, kWh'][i]
        df['Energia condivisa, kWh'][i] = df['Energia condivisa batteria, kWh'][i]+df['Energia condivisa PV, kWh'][i]
        df['Energia immagazzinata in batteria, kWh'][i] = df['Energia immagazzinata in batteria, kWh'][i-1]-df['Energia scarica batteria, kWh'][i] +df['Energia ricarica batteria, kWh'][i]
        df['Stato di carica batteria, %'][i] = df['Energia immagazzinata in batteria, kWh'][i]/Capacity_Battery*100

        df['Energia immessa in rete tot, kWh'][i] =df['Produzione PV, kWh'][i]+df['Energia scarica batteria, kWh'][i]
        df['Energia prelevata dalla rete tot, kWh'][i] = df['Consumo carichi, kWh'][i]

    df_hourly = df       

    df_daily = df.resample('1D').sum()
    df_weekly = df.resample('1W').sum()
    df_monthly = df.resample('1M').sum()
    df_yearly = df.resample('1Y').sum()

    List_Months = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
    df_monthly['Months'] = List_Months

    
    
    # Investimento totale

    CAPEX_PV      = PV_kWp * CAPEX_PV_specifico   # eur
    CAPEX_battery = Capacity_Battery * CAPEX_battery_specifico # eur
    OPEX          = (CAPEX_PV)*OPEX_Perc/100
    InverterCost  = Inverter/100*CAPEX_PV


    Energia_Condivisa_PV = df_hourly['Energia condivisa PV, kWh'].sum()
    Energia_Condivisa_Batteria = df_hourly['Energia condivisa batteria, kWh'].sum()
    Energia_Condivisa = df_hourly['Energia condivisa batteria, kWh'].sum()+df_hourly['Energia condivisa PV, kWh'].sum()
    Energia_Consumi = df_hourly['Consumo carichi, kWh'].sum()
    Energia_Immessa_In_Rete = df_hourly['Energia immessa in rete tot, kWh'].sum()
    Energia_Prelevata_tot = df_hourly['Energia prelevata dalla rete tot, kWh'].sum()

    Ritorno_MISE  = Incentivo_MISE * Energia_Condivisa               # eur/anno
    Ritorno_ARERA = Sgravio_ARERA * Energia_Condivisa                # eur/anno
    Ritorno_RID   = Prezzo_El_Mercato * Energia_Immessa_In_Rete      # eur/anno
    Totale_Ricavi = Ritorno_MISE +Ritorno_ARERA+Ritorno_RID            # eur/anno
    
    Perc_EnergiaCondivisa = Energia_Condivisa/Energia_Consumi*100
    Perc_EnergiaCondivisa_PV =Energia_Condivisa_PV/Energia_Consumi*100
    Perc_EnergiaCondivisa_Batteria = Energia_Condivisa_Batteria/Energia_Consumi*100
    
    # Aggiunge come output la produzione V
    Energia_Prodotta_PV = df_hourly['Produzione PV, kWh'].sum()
    Energia_Prelevata_Extra = df_hourly['Energia prelevata dalla rete extra, kWh'].sum()
    Energia_Ricarica_Batteria = df_hourly['Energia ricarica batteria, kWh'].sum()
    Energia_Scarica_Batteria = df_hourly['Energia scarica batteria, kWh'].sum()
    Energia_Immessa_In_Rete_extra= df_hourly['Energia immessa in rete extra, kWh'].sum()

    # Controlli di bilanci energetici!
    energy_balance = df['Produzione PV, kWh']-df['Consumo carichi, kWh']-df['Energia ricarica batteria, kWh']+df['Energia scarica batteria, kWh'] - df['Energia immessa in rete extra, kWh'] +df['Energia prelevata dalla rete extra, kWh']
    # Controlla che l'energia rimanente in batteria sia il netto del totale ricaricato e scaricato (rispetto allo stato iniziale)
    Bilancio_Batteria_ = df['Energia ricarica batteria, kWh']-df['Energia scarica batteria, kWh']
    Bilancio_Batteria_1 =(df['Energia immagazzinata in batteria, kWh'][0]-SOC_min/100*Capacity_Battery)+Bilancio_Batteria_.sum()

    Bilancio_Batteria = df['Energia immagazzinata in batteria, kWh'][-1]-df['Energia immagazzinata in batteria, kWh'][0] -Bilancio_Batteria_.sum()
    
    if Useful_Capacity == 0:
        CICLI_Batteria = 0
    else:
        
        CICLI_Batteria = df['Energia ricarica batteria, kWh'].sum()/Useful_Capacity

    
    energy_balance = {'Conservazione Energia':energy_balance.sum(), 'Bilanci batteria': [Bilancio_Batteria, Bilancio_Batteria_1] }
    
    economy_output = {'Capacity_Battery':Capacity_Battery, 'CAPEX_battery_specifico':CAPEX_battery_specifico, 'PV_kWp':PV_kWp, 'Energia_Prodotta_PV':Energia_Prodotta_PV , 'Energia_Scarica_Batteria':Energia_Scarica_Batteria, 'Energia_Ricarica_Batteria':Energia_Ricarica_Batteria, 'Energia_Prelevata_Extra':Energia_Prelevata_Extra, 
'Energia_Prelevata_tot': Energia_Prelevata_tot, 'Energia_Immessa_In_Rete_extra':Energia_Immessa_In_Rete_extra, 'Energia_Consumi':Energia_Consumi,'Energia_Condivisa_PV':Energia_Condivisa_PV,'Energia_Condivisa_Batteria':Energia_Condivisa_Batteria,'Energia_Condivisa':Energia_Condivisa,'Energia_Immessa_In_Rete':Energia_Immessa_In_Rete,'Ritorno_MISE':Ritorno_MISE,'Ritorno_ARERA':Ritorno_ARERA,'Ritorno_RID':Ritorno_RID,'Totale_Ricavi':Totale_Ricavi,'Perc_EnergiaCondivisa':Perc_EnergiaCondivisa,'Perc_EnergiaCondivisa_PV':Perc_EnergiaCondivisa_PV,'Perc_EnergiaCondivisa_Batteria':Perc_EnergiaCondivisa_Batteria,'CAPEX_PV':CAPEX_PV,'CAPEX_battery':CAPEX_battery,'OPEX':OPEX,'InverterCost':InverterCost, 'Cicli batteria': CICLI_Batteria}
    
    
    return df, energy_balance, economy_output