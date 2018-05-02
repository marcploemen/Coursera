import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

''' Assignment 4 - Hypothesis Testing
This assignment requires more individual learning than previous assignments - you are encouraged to check out the pandas documentation to find functions or methods you might not have used yet, or ask questions on Stack Overflow and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.

Definitions:

A quarter is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
A recession is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
A recession bottom is the quarter within a recession which had the lowest GDP.
A university town is a city which has a high percentage of university students compared to the total population of the city.
Hypothesis: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (price_ratio=quarter_before_recession/recession_bottom)

The following data files are available for this assignment:

From the Zillow research data site there is housing data for the United States. In particular the datafile for all homes at a city level, City_Zhvi_AllHomes.csv, has median home sale prices at a fine grained level.
From the Wikipedia page on college towns is a list of university towns in the United States which has been copy and pasted into the file university_towns.txt.
From Bureau of Economic Analysis, US Department of Commerce, the GDP over time of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file gdplev.xls. For this assignment, only look at GDP data from the first quarter of 2000 onward.
Each function in this assignment below is worth 10%, with the exception of run_ttest(), which is worth 50%. ''''

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    uni_towns_df = pd.read_csv('university_towns.txt', delimiter='\t', names=['Rawtext'])
    uni_towns_df = pd.DataFrame(uni_towns_df.Rawtext.str.split('(', 1).tolist())
    uni_towns_df.columns = ["RegionName", "drop"]
    uni_towns_df.drop('drop', axis=1, inplace=True)
    #massk the state
    mask = uni_towns_df.RegionName.str[-6:] != '[edit]'
    #filter by mask and replace NaN by forward filling
    uni_towns_df['State'] = uni_towns_df.RegionName.mask(mask).ffill()    
    #remove same values in both columns
    uni_towns_df = uni_towns_df[uni_towns_df.State != uni_towns_df.RegionName]
    #remove [edit] from state name
    uni_towns_df['State'] = uni_towns_df['State'].str[:-6]
    #exchange columns 
    columnsTitles=["State","RegionName"]
    uni_towns_df=uni_towns_df.reindex(columns=columnsTitles)
    
    return  uni_towns_df  



def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdplev = pd.ExcelFile('gdplev.xls')
    gdplev = gdplev.parse("Sheet1", skiprows=219)
    gdplev = gdplev[['1999q4', 9926.1]]
    gdplev.columns = ['Quarter','GDP']
            
    return gdplev[(gdplev['GDP'] > gdplev['GDP'].shift(-1)) & (gdplev['GDP'].shift(-1) > gdplev['GDP'].shift(-2))].iloc[0]['Quarter'] 

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdplev = pd.ExcelFile('gdplev.xls')
    gdplev = gdplev.parse("Sheet1", skiprows=219)
    gdplev = gdplev[['1999q4', 9926.1]]
    gdplev.columns = ['Quarter','GDP']
    
    start = get_recession_start()
    start_index = gdplev[gdplev['Quarter'] == start].index.tolist()[0]
    gdplev=gdplev.iloc[start_index:]
    
    return gdplev[(gdplev['GDP'] > gdplev['GDP'].shift(1)) & (gdplev['GDP'].shift(1) > gdplev['GDP'].shift(2))].iloc[0]['Quarter']

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdplev = pd.ExcelFile('gdplev.xls')
    gdplev = gdplev.parse("Sheet1", skiprows=219)
    gdplev = gdplev[['1999q4', 9926.1]]
    gdplev.columns = ['Quarter','GDP']
    
    start = get_recession_start()
    start_index = gdplev[gdplev['Quarter'] == start].index.tolist()[0]
    end = get_recession_end()
    end_index = gdplev[gdplev['Quarter'] == end].index.tolist()[0]
    gdplev=gdplev.iloc[start_index:end_index+1]
    gdplev.set_index('Quarter', inplace=True)
    return (gdplev['GDP']).idxmin()

def create_quarterly_dict():
    Compare_Buckets = {'2000q1':('2000-01','2000-02','2000-03')}
    years = list(range(2000,2017))
    quars = ['q1','q2','q3','q4']
    months = ['01','02','03','04', '05', '06', '07','08','09','10', '11', '12']
    quar_years = []
    for i in years:
        j = 0
        for x in quars:
            if str(i)+x != '2016q4':
                Compare_Buckets[str(i)+x] = (str(i) + '-' + months[j * 3 ] , str(i) + '-' + months[(j * 3 )+1], str(i) + '-' + months[(j*3)+2])
            j += 1
            
    return Compare_Buckets

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    housing_data_df = pd.read_csv("City_Zhvi_AllHomes.csv")
    housing_data_df['State'] = housing_data_df['State'].map(states)
    housing_data_df.drop(['Metro','CountyName','RegionID','SizeRank'],axis=1,inplace=True)
    housing_data_df.drop(housing_data_df.columns[2:47], axis=1, inplace=True)
    #housing_data_df['avg'] = housing_data_df.mean(axis=1)
    housing_data_df.set_index(['State', 'RegionName'], inplace=True)

    Compare_Buckets = create_quarterly_dict()
    #print(Compare_Buckets)
    for group, individuals in Compare_Buckets.items():
        housing_data_df[group] = housing_data_df.filter(items=individuals).mean(axis=1)
    
    housing_data_df.drop(housing_data_df.columns[0:200], axis=1, inplace=True)
    
    return housing_data_df

