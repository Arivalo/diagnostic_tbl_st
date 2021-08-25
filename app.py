import streamlit as st
import requests
import pandas as pd
import datetime as dt
import base64
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


@st.cache(suppress_st_warning=True)
def download_data(url, haslo=st.secrets['password'], login=st.secrets['username'], retry=5):

    i = 0

    while i < retry:
        r = requests.get(url,auth=(login, haslo))

        try:
            j = r.json()
            break
        except:
            i += 1
            print(f"Try no.{i} failed")

    if i == retry:
        print(f"Failed to fetch data for: {url}")
        return pd.DataFrame()
        
    df = pd.DataFrame.from_dict(j['entities'])
    if not df.empty:
        try:
            df['longtitude'] = [x['coordinates']['x'] for x in df['_meta']]
            df['latitude'] = [y['coordinates']['y'] for y in df['_meta']]
            df.pop('_meta')   
            
        except KeyError:
            print(f'Url error: {url}')
            
        df.ffill(inplace=True)
        df['Data_czas'] = pd.to_datetime(df['startDate']).dt.tz_localize(None)         
            
    return przygotuj_dane(df)


def utworz_url(data_od, data_do):
    str_base = st.secrets['url']
    data_do_parted = str(data_do).split("-")
    data_jutro = dt.date(int(data_do_parted[0]), int(data_do_parted[1]), int(data_do_parted[2])) + dt.timedelta(days=1)
    str_out = f"{str_base}?from={data_od}T02%3A00%3A00%2B02%3A00&to={data_jutro}T02%3A00%3A00.000%2B02%3A00&definitionId=6&label=Test_06+-%3E+speed_stats&monitoredId=1&limit=10000000"
    return str_out
    
def przygotuj_dane(dane):
    dane = dane[['Data_czas'] + [kolumna for kolumna in dane.columns if kolumna.startswith("_diag")]].astype(str)
    dane.rename(columns={kolumna:kolumna[6:] for kolumna in dane.columns if kolumna.startswith("_diag")}, inplace=True)
    
    return dane
    
    
def get_table_download_link(df, nazwa_pliku):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{nazwa_pliku}.csv">Download csv file</a>'
    
    return href
    
 ######################################################################################################################
 
 
st.title("Dashboard 1176 diagnostics")
 
st.header("Date choice:")
data_od = st.date_input("From:", value=dt.date(2021,8,11), min_value=dt.date(2021,8,11), max_value=dt.date.today())
data_do = st.date_input("To:", min_value=data_od)

url = utworz_url(data_od, data_do)

try:
    df = download_data(url)


    #st.write(df.columns)

    #st.help(px.line)
    
    st.write(df)
    
    st.write(" ")
    st.markdown(get_table_download_link(df, f'diagnostics_{data_od}_{data_do}'), unsafe_allow_html=True)

    
except KeyError:
    
    st.write("No data for selected date")