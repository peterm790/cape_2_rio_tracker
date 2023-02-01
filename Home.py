import pandas as pd 
import fsspec
import streamlit as st
import json
import streamlit.components.v1 as components
import datetime

st.set_page_config(layout="wide",
                page_title="Pete's Rio Tracker",
                page_icon = ":sailboat:",
)


date_hour = datetime.datetime.today().strftime('%Y-%m-%d:%H') 

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

day_dic =  {'Day: 17': '20230120',
            'Day: 19': '20230122',
            'Day: 20': '20230123',
            'Day: 22': '20230125',
            'Day: 23': '20230126',
            'Final Results': 'final'}

finish_times = {'Ray of Light':datetime.datetime(2023,1,24,4,12),
                'Atalanta':datetime.datetime(2023,1,24,5,13),
                'Audaz II': datetime.datetime(2023,1,24,7,5),
                'Translated 9': datetime.datetime(2023,1,24,7,34),
                'Nemesis': datetime.datetime(2023,1,26,1,31),
                'Alexforbes ArchAngel': datetime.datetime(2023,1,26,21,36),
                'Argonaut': datetime.datetime(2023,1,26,21,59),
                'Sterna': datetime.datetime(2023,1,28,3,32),
                'Felix':datetime.datetime(2023,1,30,2,6),
                'Nyamazela': datetime.datetime(2023,1,30,2,36),
                'Faros': datetime.datetime(2023,1,30,2,56)}


final_df = pd.DataFrame({"IRC handicap":{"Atalanta":"1.007","Ray of Light":"1.118","Alexforbes ArchAngel":"0.997","Audaz II":"1.126","Translated 9":"1.134","Nemesis":"1.081","Felix":"0.932","Argonaut":"1.055","Nyamazela":"0.948","Sterna":"1.071","Faros":"1.000"},"Time Elapsed":{"Atalanta":"21 days 17:13:00","Ray of Light":"21 days 16:12:00","Alexforbes ArchAngel":"24 days 09:36:00","Audaz II":"21 days 19:05:00","Translated 9":"21 days 19:34:00","Nemesis":"23 days 13:31:00","Felix":"27 days 14:06:00","Argonaut":"24 days 09:59:00","Nyamazela":"27 days 14:36:00","Sterna":"25 days 15:32:00","Faros":"27 days 14:56:00"},"Corrected Time":{"Atalanta":"21 days 20:51:54.660000","Ray of Light":"24 days 05:35:00.960000","Alexforbes ArchAngel":"24 days 07:50:35.520000","Audaz II":"24 days 12:59:30.600000","Translated 9":"24 days 17:43:28.560000","Nemesis":"25 days 11:19:24.660000","Felix":"25 days 17:04:37.920000","Argonaut":"25 days 18:12:44.700000","Nyamazela":"26 days 04:08:41.280000","Sterna":"27 days 11:14:10.320000","Faros":"27 days 14:56:00"}})

@st.cache()
def get_leaderboard(date_hour, day):
    data = []
    for name in names:
        file = f"s3://riotrackerlambdastack-cape2riotrackingbucket493cd-ax0w0veyvbks/results/{day}/{name_dic[name]}.json"
        with fs.open(file, 'r') as f:
            data.append(pd.DataFrame(json.load(f), index = [name]))
    df = pd.concat(data).iloc[:,1:]
    if len(df.columns) == 4:
        df['Finished'] = False * len(df)
    df.columns = ['ETA', 'IRC handicap', 'Estimated Time Elapsed', 'Estimated Corrected Time', 'Finished']
    sortby = []
    for d in df['Estimated Corrected Time']:
        sortby.append(pd.Timedelta(d).asm8)
    df['sort_col'] = sortby
    finished = []
    for i, name in enumerate(names):
        if df.iloc[i]['Finished'] == 'true':
            finished.append(True)
        else:
            finished.append(False)
    df['Finished'] = finished
    return df.sort_values('sort_col').iloc[:,:-1], date_hour

@st.cache()
def get_html(name, date_hour, day):
    file = f"s3://riotrackerlambdastack-cape2riotrackingbucket493cd-ax0w0veyvbks/results/{day}/{name_dic[name]}.html"
    with fs.open(file, 'rb', encoding = 'utf-8') as f:
        HtmlFile = f.read()
    return HtmlFile, date_hour

@st.cache()
def get_roadbook(name, date_hour, day):
    file = f"s3://riotrackerlambdastack-cape2riotrackingbucket493cd-ax0w0veyvbks/results/{day}/{name_dic[name]}.csv"
    with fs.open(file, 'r') as f:
        road_book = pd.read_csv(f)[['time', 'lat', 'lon', 'twd', 'tws', 'heading', 'twa','boat_speed', 'days_elapsed']]
    start = datetime.datetime(2023,1,2,12)
    current = datetime.datetime.strptime(road_book.time[0], '%Y-%m-%d %H:%M:%S')
    elapsed = current - start
    road_book.days_elapsed = road_book.days_elapsed + elapsed.days - round((12 - current.hour)/24,1)  #start was at 1200 UTC
    return road_book, date_hour


st.title(":blue[Pete's Cape To Rio Tracker] :flag-za: -> :flag-br:")

st.write(':green[The Tracker updated at 10am SAST daily. Now that the race is over this site provides a way to check how well the forecasts worked]')

day_label = st.selectbox(
    'As forcasted on:',
    ['Day: 17', 'Day: 19', 'Day: 20', 'Day: 22', 'Day: 23', 'Final Results'],
    help = '')

day = day_dic[day_label]

fs = fsspec.filesystem('s3')
names = list(name_dic)

if not day_label == 'Final Results':
    option = st.selectbox(
        'View:',
        ('Leaderboard', 'Routing Maps'),
        help = '')
    if option == 'Leaderboard':
        df, _ = get_leaderboard(date_hour, day)
        st.dataframe(df, use_container_width=True)
        st.write(':blue[This forecasted leaderboard has been determined by weather routing each yacht individually to the finish using a polar file derived from the ORC handicap. It represents the expected finishing order if each team were to sail at 100% of their handicap from now until the finish. I have used IRC to determine the final rankings as this is what will be used to determine the overall winner.]')
        st.write(':blue[The rankings here may differ significantly from the official tracker as that determines the final rankings by extrapolating each boats VMG, usually favoring those taking the most direct course.]')
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
            HtmlFile, _ = get_html(team, date_hour, day)
            components.html(HtmlFile, height=900, scrolling = False)
            st.write(':blue[The weather displayed here is the latest 00z GFS forecast]')
        elif map == 'Road Book':
            road_book, _ = get_roadbook(team, date_hour, day)
            st.dataframe(road_book, use_container_width=True)
            st.write(":blue[The polar filed used to calculate the expected route has been derived from the yacht's ORC handicap, some yachts do not yet have handicaps available on the ORC website and so a sistership or similar yacht has been used in place. ]")
else:
    st.dataframe(final_df, use_container_width=True)

    

st.write('')
st.write(':blue[All times are UTC.]')
st.write('')

st.write(':red[This tracker has no affiliation with the Cape to Rio Race, or the official YellowBrick tracker.]')


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