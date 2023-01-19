import pandas as pd 
import fsspec
import streamlit as st
import json
import streamlit.components.v1 as components
import datetime


st.set_page_config(layout="wide",
                page_title="Pete's Rio Tracker",
                page_icon = ":wave:",
)

st.title(' Cape To Rio Tracker')

name_dic = {'Alexforbes ArchAngel': 'Alexforbes_ArchAngel',
            'Argonaut': 'Argonaut',
            'Atalanta': 'Atalanta',
            'Audaz II': 'Audaz_II',
            'Faros': 'Faros',
            'Felix': 'Felix',
            'Nemesis': 'Nemesis',
            'Nyamazela': 'Nyamazela',
            'Ray of Light': 'Ray_of_Light',
            'Sterna': 'Sterna',
            'Translated 9': 'Translated_9'}


option = st.selectbox(
    'View',
    ('Leaderboard', 'Routing Maps'),
    help = '')
    

if option == 'Leaderboard':
    fs = fsspec.filesystem('')
    files = fs.glob('/home/peter/Documents/rio_tracker/results/*.json')
    names = [' '.join(file.split('/')[-1].split('.')[0].split('_')) for file in files]
    data = []
    for file, name in zip(files,names):
        with fs.open(file, 'r') as f:
            data.append(pd.DataFrame(json.load(f), index = [name]))
    df = pd.concat(data).iloc[:,1:]
    df.columns = ['ETA', 'ORC handicap', 'Estimated Time Elapsed', 'Estimated Corrected Time']
    df.sort_values('Estimated Corrected Time')
    st.dataframe(df, use_container_width=True)
elif option == 'Routing Maps':
    fs = fsspec.filesystem('')
    files = fs.glob('/home/peter/Documents/rio_tracker/results/*.html')
    names = [' '.join(file.split('/')[-1].split('.')[0].split('_')) for file in files]
    team = st.selectbox(
                        'Team',
                        names,
                        help = '')
    map = st.selectbox(
                    'View',
                    ('Routing Chart', 'Road Book'),
                    help = '')
    dic = {names[i]: files[i] for i in range(len(files))}
    if map == 'Routing Chart':
        with fs.open(dic[team], 'rb', encoding = 'utf-8') as f:
            HtmlFile = f.read()
        components.html(HtmlFile, height=900, scrolling = False)
    elif map == 'Road Book':
        csv_url = f"{dic[team].split('.')[0]}.csv"
        with fs.open(csv_url, 'r') as f:
            road_book = pd.read_csv(f)[['time', 'lat', 'lon', 'twd', 'tws', 'heading', 'twa','boat_speed', 'days_elapsed']]
        start = datetime.datetime(2023,1,2,14)
        current = datetime.datetime.today().replace(hour=9, minute=0, second = 0, microsecond=0)
        elapsed = current - start
        road_book.days_elapsed = road_book.days_elapsed + elapsed.days-0.20 #start was at 1400
        st.dataframe(road_book, use_container_width=True)

