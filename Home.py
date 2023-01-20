import pandas as pd 
import fsspec
import streamlit as st
import json
import streamlit.components.v1 as components
import datetime


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

@st.cache()
def get_leaderboard():
    data = []
    for name in names:
        file = f"s3://riotrackerlambdastack-cape2riotrackingbucket493cd-ax0w0veyvbks/results/{name_dic[name]}.json"
        with fs.open(file, 'r') as f:
            data.append(pd.DataFrame(json.load(f), index = [name]))
    df = pd.concat(data).iloc[:,1:]
    df.columns = ['ETA', 'IRC handicap', 'Estimated Time Elapsed', 'Estimated Corrected Time']
    return df.sort_values('Estimated Corrected Time')

@st.cache()
def get_html(name):
    file = f"s3://riotrackerlambdastack-cape2riotrackingbucket493cd-ax0w0veyvbks/results/{name_dic[name]}.html"
    with fs.open(file, 'rb', encoding = 'utf-8') as f:
        HtmlFile = f.read()
    return HtmlFile

@st.cache()
def get_roadbook(name):
    file = f"s3://riotrackerlambdastack-cape2riotrackingbucket493cd-ax0w0veyvbks/results/{name_dic[name]}.csv"
    with fs.open(file, 'r') as f:
        road_book = pd.read_csv(f)[['time', 'lat', 'lon', 'twd', 'tws', 'heading', 'twa','boat_speed', 'days_elapsed']]
    start = datetime.datetime(2023,1,2,12)
    #if datetime.datetime.today().hour > 9:
    current = datetime.datetime.today().replace(hour=8, minute=0, second = 0, microsecond=0)
    elapsed = current - start
    road_book.days_elapsed = road_book.days_elapsed + elapsed.days-0.2 #start was at 1200 UTC
    return road_book


st.set_page_config(layout="wide",
                page_title="Pete's Rio Tracker",
                page_icon = ":sailboat:",
)

st.title(":blue[Pete's Cape To Rio Tracker] :flag-za: -> :flag-br:")

st.write(':green[The Tracker will update at 9:30 am SAST daily.]')

option = st.selectbox(
    'View:',
    ('Leaderboard', 'Routing Maps'),
    help = '')

fs = fsspec.filesystem('s3')
names = list(name_dic)

if option == 'Leaderboard':
    df = get_leaderboard()
    st.dataframe(df, use_container_width=True)
    st.write(':blue[This forecasted leaderboard has been determined by weather routing each yacht individually to the finish using a polar file derived from the ORC handicap. It represents the expected finishing order if each team were to sail at 100% of their handicap from now until the finish. I have used IRC to determine the final rankings as this is what will be used to determine the overall winner.]')
    st.write(':blue[The rankings here may differ significantly from the official tracker as that determines the final rankings by extrapolating each boats VMG, usually favoring those taking the mose direct course.]')
    st.write(':blue[All times are UTC]')
elif option == 'Routing Maps':
    team = st.selectbox(
                        'Team:',
                        names,
                        help = '')
    map = st.selectbox(
                    'Style:',
                    ('Routing Chart', 'Road Book'),
                    help = '')
    if map == 'Routing Chart':
        st.write('Please note these maps do not render nicely on mobile devices')
        HtmlFile = get_html(team)
        components.html(HtmlFile, height=900, scrolling = False)
        st.write(':blue[The weather displayed here is the latest 00z GFS forecast]')
    elif map == 'Road Book':
        road_book = get_roadbook(team)
        st.dataframe(road_book, use_container_width=True)
        st.write(":blue[The polar filed used to calculate the expected route has been derived from the yacht's ORC handicap]")


st.write(':red[This tracker has no affiliation with Cape to Rio Race, or the official YellowBrick tracker.]')


st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')

st.write('For any enquires contact me at petermarsh790@gmail.com')