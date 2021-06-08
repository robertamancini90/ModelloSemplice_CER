import pandas as pd 
import numpy as np 

def Detailed_Economic_Analysis(economy_inputs, years, Tasso_Attualizzazione):
    
    years = 20
    
    df_economic = pd.DataFrame()
    
    df_economic['year'] = range(1,21)
    
    df_economic['Ricavi, eur/anno'] = np.ones(len(df_economic))*(economy_inputs['Totale_Ricavi'])
    
    df_economic['Detrazioni 50%, eur/anno'] = np.zeros(len(df_economic))
    df_economic.at[0:10,'Detrazioni 50%, eur/anno']=min((economy_inputs['CAPEX_PV']+economy_inputs['CAPEX_battery']), 96000)/10*0.5
    df_economic['OPEX, eur/anno'] = np.ones(len(df_economic))*(economy_inputs['OPEX'])
    df_economic.at[10,'OPEX, eur/anno'] = economy_inputs['InverterCost']+economy_inputs['OPEX']
    df_economic['Ricavi cumulati, eur'] = df_economic['Ricavi, eur/anno'].cumsum()
    
    df_economic['OPEX cumulati, eur'] = df_economic['OPEX, eur/anno'].cumsum()
    df_economic['Detrazioni cumulate, eur'] = df_economic['Detrazioni 50%, eur/anno'].cumsum()
    
    df_economic['FCC (Investimento 100 %), eur'] =- (economy_inputs['CAPEX_PV']+economy_inputs['CAPEX_battery'])*np.ones(len(df_economic)) + df_economic['Ricavi cumulati, eur'] - df_economic['OPEX cumulati, eur']
    df_economic['FCC (Investimento 50 %), eur'] = -(economy_inputs['CAPEX_PV']+economy_inputs['CAPEX_battery'])*np.ones(len(df_economic)) + df_economic['Ricavi cumulati, eur'] - df_economic['OPEX cumulati, eur'] +df_economic['Detrazioni cumulate, eur']
    
    df_economic['Fattore di attualizzazione'] = 1/((1+Tasso_Attualizzazione/100)**(df_economic['year']-1))
    df_economic['Ricavi - scontati, eur/anno'] = df_economic['Ricavi, eur/anno']*df_economic['Fattore di attualizzazione']
    df_economic['Detrazioni 50% - scontate, eur/anno'] = df_economic['Detrazioni 50%, eur/anno']*df_economic['Fattore di attualizzazione']
    df_economic['OPEX - scontati, eur/anno']  = df_economic['OPEX, eur/anno'] *df_economic['Fattore di attualizzazione'] 
    df_economic['Ricavi cumulati - scontati, eur'] = df_economic['Ricavi - scontati, eur/anno'].cumsum()
    df_economic['OPEX cumulati - scontati, eur'] = df_economic['OPEX - scontati, eur/anno'].cumsum()
    df_economic['Detrazioni cumulate - scontate, eur'] =df_economic['OPEX - scontati, eur/anno'].cumsum()
    
    df_economic['VAN (Investimento 100 %), eur'] =- (economy_inputs['CAPEX_PV']+economy_inputs['CAPEX_battery'])*np.ones(len(df_economic)) + df_economic['Ricavi cumulati - scontati, eur'] - df_economic['OPEX cumulati - scontati, eur']
    df_economic['VAN (Investimento 50 %), eur'] = -(economy_inputs['CAPEX_PV']+economy_inputs['CAPEX_battery'])*np.ones(len(df_economic)) + df_economic['Ricavi cumulati - scontati, eur'] - df_economic['OPEX cumulati - scontati, eur'] +df_economic['Detrazioni cumulate - scontate, eur']
    
    return df_economic