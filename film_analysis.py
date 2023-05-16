import streamlit as st
import pandas as pd
import numpy as np
from google.oauth2 import service_account
import gspread


def getgsheet(spreadsheet_url, sheet_num):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    client = gspread.authorize(credentials)
    gsheet = client.open_by_url(spreadsheet_url).get_worksheet(sheet_num)

    return gsheet


def gsheet2df(gsheet):
    gsheet = gsheet.get_all_records()
    df = pd.DataFrame.from_dict(gsheet)

    return df


sheet_url = st.secrets["private_gsheets_url"]

st.cache(ttl=660)
sheet = getgsheet(sheet_url, 0)
file = gsheet2df(sheet)

total_films = len(file)
highest_score = file['Mean'].max()
highest_rated_film = file.loc[file['Mean'] == highest_score, 'Name'].values.tolist()

most_watched_genre = file['Genre'].value_counts().index.tolist()[0]
no_most_watched_genre = file['Genre'].value_counts().values.tolist()[0]

most_watched_genre_df = file[file['Genre'] == most_watched_genre]
rating_of_most_watched_genre = np.average(most_watched_genre_df['Mean'])

most_watched_director = file['Director'].value_counts().index.tolist()[0]
no_most_watched_director = file['Director'].value_counts().values.tolist()[0]

most_watched_director_df = file[file['Director'] == most_watched_director]
rating_of_most_watched_director = np.average(most_watched_director_df['Mean'])

all_genre = [x for x in file['Genre'].unique()] or [x for x in file['Sub-Genre'].unique()]
all_genre = list(sorted(set(filter(None, all_genre))))

q_average_score = np.average(file['Q'])
g_average_score = np.average(file['G'])

if g_average_score < q_average_score:
    mean_bastard = 'G'
elif q_average_score < g_average_score:
    mean_bastard = 'Q'

else:
    mean_bastard = 'No one'

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)

with st.form(key='Submit Films'):
    with st.sidebar:
        st.sidebar.markdown("## Submit Films")
        Name = st.sidebar.text_input("Film Name", key="Name")
        Director = st.sidebar.text_input('Director', key='Director')
        Genre = st.sidebar.selectbox('Genre', all_genre)
        Sub_Genre = st.sidebar.selectbox('Sub-Genre', all_genre)
        G = st.sidebar.number_input("G's Score", key="G", min_value=0, max_value=10, step=1)
        Q = st.sidebar.number_input("Q's Score", key="Q", min_value=0, max_value=10, step=1)
        BoB = st.sidebar.radio('Based on Books?', ('Y', 'N'))
        submit_button = st.form_submit_button(label='Submit')

if submit_button:
    mean = (G + Q) / 2
    info = [Name, Genre, '', Q, G, mean, Director, BoB]
    sheet.append_row(info)
    file = gsheet2df(sheet)

st.title('Analysing Films Watched by Butler-Su')

output_graphs = st.container()

st.subheader("Number of Films Watched per Genre")
st.markdown(f"So far, the most watched genre is {most_watched_genre} with "
            f"{no_most_watched_genre} {most_watched_genre} films out of a total of {total_films} watched.")

st.vega_lite_chart(file, {
        'width': 'container',
        'height': 400,
        "mark": {"type": "arc", "tooltip": {"content": "encoding"}, "innerRadius": 50},
        "encoding": {
            "theta": {"aggregate": "count", "title": "No. of Films"},
            "color": {
                "field": "Genre",
                "type": "nominal",
                "scale": {"scheme": "tableau20"},
                "legend": {"orient": "left"}
            }
        },
        "view": {"stroke": None}
    }, use_container_width=True)

st.subheader("Average Score of Top Five Genres")
st.markdown(f"The average score of the most watched genre, {most_watched_genre}, is "
            f"{round(rating_of_most_watched_genre, 2)}.")

top5_genre = file['Genre'].value_counts()[:5].index.tolist()
file1 = file[file['Genre'].isin(top5_genre)]

st.vega_lite_chart(file1, {
        'width': 'container',
        'height': 400,
        "mark": {"type": "bar"},
        "encoding": {
            "y": {"field": "Genre",
                  "sort": "-x",
                  "title": None},
            "x": {"aggregate": "mean",
                  "field": "Mean",
                  "title": "Total Score",
                  "type": "quantitative"},
            "color": {
                "field": "Genre",
                "type": "nominal",
                "scale": {"scheme": "tableau20"},
                "legend": {"orient": "left"}
            },
            "tooltip": [
                {"aggregate": "mean", "title": "Average Score", "field": "Mean", "format": ".2f"},
                {"aggregate": "count", "title": "No.of Films", "field": "Genre"}
            ],
        },

        "view": {"stroke": None}
    }, use_container_width=True)

st.subheader("Average Score of Top Five Directors")
st.markdown(f"The average score of the most watched director, {most_watched_director}, is "
            f"{round(rating_of_most_watched_director, 2)}.")

top5_director = file['Director'].value_counts()[:5].index.tolist()
file2 = file[file['Director'].isin(top5_director)]

st.vega_lite_chart(file2, {
        'width': 'container',
        'height': 400,
        "mark": {"type": "bar"},
        "encoding": {
            "y": {"field": "Director",
                  "sort": "-x",
                  "title": None},
            "x": {"aggregate": "mean",
                  "field": "Mean",
                  "title": "Total Score",
                  "type": "quantitative"},
            "color": {
                "field": "Director",
                "type": "nominal",
                "scale": {"scheme": "tableau20"},
                "legend": {"orient": "left"}
            },
            "tooltip": [
                {"aggregate": "mean", "title": "Average Score", "field": "Mean", "format": ".2f"},
                {"aggregate": "count", "title": "No.of Films", "field": "Genre"}
            ],
        },

        "view": {"stroke": None}
    }, use_container_width=True)

st.subheader("Density Plot of Ratings")
st.markdown(f"Q's average score is {np.round(q_average_score, 2)} and "
            f"G's average score is {np.round(g_average_score, 2)}. "
            f"Therefore, {mean_bastard} is a mean Bastard.")

st.vega_lite_chart(file, {
        "width": 400,
        "height": 300,
        "transform": [
            {"filter": "datum.Q != 0"},
            {"filter": "datum.G != 0"},
            {"filter": "datum.Mean != 0"},
        ],
        "layer": [
            {
                "transform": [
                    {
                        "density": "Mean",
                        "bandwidth": 0.3
                    }
                ],
                "mark": "line",
                "encoding": {
                    "x": {
                        "field": "value",
                        "title": "Scores",
                        "type": "quantitative"
                    },
                    "y": {
                        "field": "density",
                        "type": "quantitative",
                        "title": None
                    },
                    "color": {"datum": "Average",
                              "legend": {"orient": "left"}}
                }
            },
            {
                "transform": [
                    {
                        "density": "G",
                        "bandwidth": 0.3
                    }
                ],
                "mark": "line",
                "encoding": {
                    "x": {
                        "field": "value",
                        "title": "Scores",
                        "type": "quantitative"
                    },
                    "y": {
                        "field": "density",
                        "type": "quantitative",
                        "title": None
                    },
                    "color": {"datum": "G", "legend": {"orient": "left"}}
                }
            },
            {
                "transform": [
                    {
                        "density": "Q",
                        "bandwidth": 0.3
                    }
                ],
                "mark": "line",
                "encoding": {
                    "x": {
                        "field": "value",
                        "title": "Scores",
                        "type": "quantitative"
                    },
                    "y": {
                        "field": "density",
                        "type": "quantitative",
                        "title": None
                    },
                    "color": {"datum": "Q", "legend": {"orient": "left"}}
                }
            }
        ]

    }, use_container_width=True)

st.subheader("Average Film Ratings for All Time")
st.markdown(f'The highest rated film so far is {highest_rated_film[0]}.')

st.vega_lite_chart(file, {
        "width": "container",
        "height": 500,
        "mark": {"type": "bar", "cornerRadiusEnd": 4, "tooltip": {"content": "encoding"}},
        "encoding": {
            "x": {"field": "Mean",
                  "type": "quantitative",
                  "title": "Score"},
            "y": {"field": "Name",
                  "sort": "-x",
                  "title": None},
            "color": {"field": "Genre",
                      "scale": {"scheme": "tableau20"},
                      "legend": {"orient": "left"}}
        },
        "config": {"view": {"stroke": "transparent"}, "axis": {"domainWidth": 1}}
    }, use_container_width=True)

st.subheader("Rating Difference of G Minus Q")
st.markdown('Films with red bars means Q liked more than G, and green means G liked more than Q.')

st.vega_lite_chart(file, {
        "width": "container",
        "height": 500,
        "mark": {"type": "bar", "cornerRadiusEnd": 4, "tooltip": {"content": "encoding"}},
        "transform": [
            {"calculate": "-datum.G", "as": "george_minus"}
        ],
        "layers": [
            {
                "mark": "bar",
                "encoding": {
                    "x": {"field": "george_minus",
                          "type": "quantitative",
                          "title": "Score",
                          },
                    "y": {"field": "Name",
                          "sort": "-x",
                          "title": None},
                    "color": {"datum": "G", "legend": {"orient": "left"}}
                }
            },
            {
                "mark": "bar",
                "encoding": {
                    "x": {"field": "Q",
                          "type": "quantitative",
                          "title": "Score"},
                    "y": {"field": "Name",
                          "sort": "-x",
                          "title": None},
                    "color": {"datum": "Q", "legend": {"orient": "left"}}
                }
            }
        ],
        "config": {"view": {"stroke": "transparent"}, "axis": {"domainWidth": 1}}
    }, use_container_width=True)