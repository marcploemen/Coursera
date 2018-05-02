%matplotlib notebook
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import json as js 



load_pickle = 0

if load_pickle==0:
    df_pop = pd.read_pickle('dutch_population.pkl') #to load dutch_population.pkl back to the dataframe df
    df_gdp = pd.read_pickle('dutch_gdp.pkl') #to load dutch_population.pkl back to the dataframe df
else:   
    #numbers about population in the Netherlands
    json_pop = pd.read_json("https://opendata.cbs.nl/ODataApi/OData/37296ned/TypedDataSet", orient="columns")
    df_pop = pd.read_json((json_pop['value']).to_json(), orient='index')
    df_pop.to_pickle('dutch_population.pkl')    #to save the dataframe, df dutch_population.pkl
    #numbers about gross domestic product in the Netherlands
    json_gdp = pd.read_json("https://opendata.cbs.nl/ODataApi/OData/81170ned/TypedDataSet", orient="columns")
    df_gdp = pd.read_json((json_gdp['value']).to_json(), orient='index')
    df_gdp.to_pickle('dutch_gdp.pkl')

#clean and prepare GDP dataset
df_gdp = df_gdp[['Perioden', 'BrutoNationaalInkomen_77',
                 'TotaalConsumptieveBestedingen_82', 
                 'BrutoBinnenlandsProduct_2', 'Goederen_16', 
                 'Diensten_17' , 'BrutoBeschikbaarNationaalInkomen_81', 'ProductgebondenBelastingen_202' ]]
df_gdp = df_gdp[df_gdp['Perioden'].str.contains("JJ")]    
df_gdp['Perioden'] = df_gdp['Perioden'].astype(str).str[:-4].astype(np.int64)
df_gdp = df_gdp[df_gdp['Perioden'] > 2002 ]  
df_gdp = df_gdp.sort_values(by=['Perioden'])

df_gdp_grouped = df_gdp.groupby(['Perioden', 'BrutoNationaalInkomen_77',
                 'TotaalConsumptieveBestedingen_82', 
                 'BrutoBinnenlandsProduct_2', 'Goederen_16', 
                 'Diensten_17' , 'BrutoBeschikbaarNationaalInkomen_81'])['ProductgebondenBelastingen_202']


df_gdp = pd.DataFrame(df_gdp_grouped.size().reset_index(name = "Group_Count"))

df_gdp = df_gdp.rename(columns={'Perioden': 'Year', 
                                'BrutoBinnenlandsProduct_2': 'GDP',
                                'BrutoNationaalInkomen_77': 'GrossNationalIncome',
                                'TotaalConsumptieveBestedingen_82': 'TotalComsumption',                                
                                'Goederen_16': 'Goods',
                                'Diensten_17': 'Services',
                                'BrutoBeschikbaarNationaalInkomen_81': 'GrossAvailableIncome',
                                'Group_count': 'Group_count'})

#df_gdp = df_gdp.set_index('Perioden')
#clean and prepare population dataset 
df_pop = df_pop[['Perioden', 'TotaleBevolking_1',                 
                 'Mannen_2', 'Vrouwen_3', 'JongerDan20Jaar_10','k_20Tot40Jaar_11' ,
                 'k_40Tot65Jaar_12' , 'k_65Tot80Jaar_13',
                 'k_80JaarOfOuder_14' ]]
df_pop['Perioden'] = df_pop['Perioden'].astype(str).str[:-4].astype(np.int64)
df_pop = df_pop[(df_pop['Perioden'] > 2002 ) & ( df_pop['Perioden'] < 2014)]  

df_pop = df_pop.rename(columns={'Perioden': 'Year', 
                                'TotaleBevolking_1': 'TotalPopulation',
                                'Mannen_2': 'Men',
                                'Vrouwen_3': 'Women',
                                'JongerDan20Jaar_10' : '<20Years',
                                'k_20Tot40Jaar_11' : '20To40Years',
                                'k_40Tot65Jaar_12': '40To65Years',
                                'k_65Tot80Jaar_13': '65To80Years',
                                'k_80JaarOfOuder_14': '80AndOlder'})

#dataset about labor force in the netherlands (X1000)
df_labor = pd.read_csv('labor_force.csv', delimiter=";")
df_labor =df_labor.iloc[[0,1,2, -2],7:] #keep lines 0, 1, 2 and last 2, starting from col 7
cols = [c for c in df_labor.columns if c.lower()[8:] != 'kwartaal'] #remove columns with in header
df_labor = df_labor[cols] .T#.squeeze()

df_labor = df_labor.rename(columns={0: 'Year',
                                1: 'LaborForce',
                                2: 'Employed',
                                19: 'Unemployed'})
df_labor['Year'] = df_labor['Year'].astype('int')

#dataset about pension costs government
df_pension = pd.read_csv('pension_exp_gov.csv', delimiter=";")
df_pension =df_pension.iloc[:,4:] #keep line 1, starting from col 7
df_pension.columns = df_pension.columns.str.replace("*", "") #if column header contains * replace with empty str
df_pension = df_pension.T# transform table
df_pension = df_pension.rename(columns={0: 'Year', 1: 'PensionCosts'}) # rename columns
df_pension =df_pension.iloc[:-2,:] #remove last 2 lines
df_pension['Year'] = df_pension['Year'].astype(np.int64) # convert column year to integer
df_pension = df_pension[(df_pension['Year'] > 2002 ) & ( df_pension['Year'] < 2014)]  
 
#dataset about healtcare costs government
df_health = pd.read_csv('Costs_HealthCare_Gov.csv', delimiter=";")
df_health.drop(df_health.columns[[0, 2, -3, -2, -1]], axis=1, inplace=True)
df_health = df_health.set_index('Onderwerpen_2')
df_health = df_health.T
df_health = df_health.rename(columns={'Onderwerpen_3': 'Year',
                                'Totaal zorg en welzijn': 'TotalHealth',
                                'Geneeskundige en langdurige zorg': 'LongTermHealthCare',
                                'Welzijn, jeugdzorg en kinderopvang' : 'ChildDayCare',
                                'Beleid en beheer' : 'PolicyAndManagement',
                                'Zorguitgaven in prijzen van 2010' : 'RefYear2010',
                                'Uitgaven per hoofd van de bevolking': 'CostPerHeadPop',
                                'Uitgaven als percentage van het bbp': 'CostPercentageGDP',
                                'Totaal zorguitgaven': 'TotalPerc'})


#merge different tables into one
df_final_1 = pd.merge(df_gdp, df_pop, on='Year')
df_final_2 = pd.merge(df_final_1, df_labor, on='Year')
df_final_3 = pd.merge(df_final_2, df_pension, on='Year')
df_final = pd.merge(df_final_3, df_health, on='Year' )

#align (scale) column values
df_final['LaborForce']  = (df_final['LaborForce'] * 1000).astype('int') 
df_final['Unemployed']  = (df_final['Unemployed'] * 1000).astype('int') 
df_final['Employed']  = (df_final['Employed'] * 1000).astype('int') 
df_final['65AndOlder'] = df_final['65To80Years'] + df_final['80AndOlder']
df_final.drop(df_final.columns[[-7, -6, -5, -4, -3, -2]], axis=1, inplace=True)
df_final['%65AndOlder'] = df_final['65AndOlder'] / df_final['TotalPopulation']
df_final['%Employed'] = df_final['Employed'] / df_final['TotalPopulation']
df_final['EuroPerPens'] = (df_final['PensionCosts'] * 1000000) / df_final['65AndOlder']



#print(df_pop.head(15))
#print(df_gdp)
#print(type(df_labor))
#print(df_labor.head(15))
#print(df_final.head(15))
#print(df_final)
#df_final.plot('Employed','65AndOlder', kind = 'kde');
#df_final.plot.scatter('65AndOlder', '65AndOlder', c='PensionCosts', s=df_final['PensionCosts'], colormap='viridis')
#df_final.plot.box();
pd.tools.plotting.scatter_matrix(df_final);