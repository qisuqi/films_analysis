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

all_genre = ['Drama', 'Action', 'Horror', 'Comedy', 'Thriller', 'Sci-fi', 'Romance', 'Western', 'Crime', 'Adventure',
             'Fantasy', 'Historical', 'War', 'Noir', 'Mystery', 'Gangster', 'Psychological Thriller', 'Rom Com',
             'Superhero', 'Anime', 'Dark Comedy', 'Hidden Camera', 'Suspense']
genre = list(sorted(set(filter(None, all_genre))))
sub_genre = list(sorted(set(filter(None, all_genre))))
sub_genre.insert(0, 'N/A')

print(genre)
usr1_array = np.array(file['usr1'])
usr2_aray = np.array(file['usr2'])
usr1_average_score = np.average(usr1_array[usr1_array != 0])
usr2_average_score = np.average(usr2_aray[usr2_aray != 0])

st.set_page_config(
     layout="wide",
     initial_sidebar_state="expanded",
)

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)

with st.form(key='Submit Films'):
    with st.sidebar:
        st.sidebar.markdown("## Submit Films")
        Name = st.sidebar.text_input("Film Name", key="Name")
        Director = st.sidebar.text_input('Director', key='Director')
        Genre = st.sidebar.selectbox('Genre', genre)
        Sub_Genre = st.sidebar.selectbox('Sub-Genre', sub_genre)
        usr2 = st.sidebar.number_input("usr2's Score", key="usr2", min_value=0.0, max_value=10.0, step=0.5)
        usr1 = st.sidebar.number_input("usr1's Score", key="usr1", min_value=0.0, max_value=10.0, step=0.5)
        BoB = st.sidebar.radio('Based on Books?', ('Y', 'N'))
        submit_button = st.form_submit_button(label='Submit')

if submit_button:
    if usr1 == 0:
        mean = usr2
    elif usr2 == 0:
        mean = usr1
    else:
        mean = (Geousr2rge + usr1)/2
    if Sub_Genre == 'N/A':
        info = [Name, Genre, '', usr1, usr2, mean, Director, BoB]
    else:
        info = [Name, Genre, Sub_Genre, usr1, usr2, mean, Director, BoB]

    if Name in file['Name'].unique():
        st.write('You are updating the record')
        cell = sheet.find(Name)
        sheet.update_cell(cell.row, 4, usr1)
        sheet.update_cell(cell.row, 5, usr2)
        sheet.update_cell(cell.row, 6, mean)
        file = gsheet2df(sheet)
    else:
        sheet.append_row(info)
        file = gsheet2df(sheet)


st.title('Analysing Films Watched by Butler-Su')

#output_graphs = st.container()

col1, col2 = st.columns(2)

with col1:
    file_col1 = pd.melt(file, id_vars='Name', value_vars=['Genre', 'Sub-Genre'])
    file_col1['value'].replace('', np.nan, inplace=True)
    file_col1.dropna(subset=["value"], inplace=True)

    most_watched_genre = file_col1['value'].value_counts().index.tolist()[0]
    no_most_watched_genre = file_col1['value'].value_counts().values.tolist()[0]

    st.subheader("Number of Films Watched per Genre")
    st.markdown(f"So far, the most watched genre is {most_watched_genre} with "
                f"{no_most_watched_genre} {most_watched_genre} films out of a total of {total_films} watched.")

    st.vega_lite_chart(file_col1, {
            'height': 400,
            "mark": {"type": "arc", "innerRadius": 50},
            "encoding": {
                "theta": {"aggregate": "count", "title": "No. of Films"},
                "color": {
                    "field": "value",
                    "type": "nominal",
                    "legend": {"title": "Genre"},
                    "scale": {
                        "domain": [
                            'Action', 'Adventure', 'Anime', 'Comedy', 'Crime', 'Dark Comedy', 'Drama', 'Fantasy',
                            'Gangster', 'Hidden Camera', 'Historical', 'Horror', 'Mystery', 'Noir',
                            'Psychological Thriller', 'Rom Com', 'Romance', 'Sci-fi', 'Superhero', 'Suspense',
                            'Thriller', 'War', 'Western'
                        ],
                        "range": [
                            '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896',
                            '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7',
                            '#bcbd22', '#dbdb0e', '#17becf', '#9edae5', '#c85200', '#b10318', '#ff0055', '#1d539e'
                        ]
                    }
                },
                "tooltip": [
                    {"field": "value", "title": "Genre"},
                    {"aggregate": "count", "title": "No.of Films", "field": "value"}
                ],
            },
            "view": {"stroke": None}
        }, use_container_width=True)

    most_watched_genre_df = file[file['Genre'] == most_watched_genre]
    most_watched_genre_df = most_watched_genre_df.sort_values(by=['Mean'], ascending=False)

    with st.expander("See more info"):
        st.markdown(f"Some of the top rated {most_watched_genre} films include: "
                    f"**{most_watched_genre_df.values.tolist()[0][0]}**,"
                    f"**{most_watched_genre_df.values.tolist()[1][0]}**,"
                    f"and **{most_watched_genre_df.values.tolist()[2][0]}**.")

with col2:
    most_watched_genre_df = file_col1[file_col1['value'] == most_watched_genre]
    all_score = file[['Name', 'Mean']]
    all_genre_score = pd.merge(most_watched_genre_df, all_score, on='Name')
    rating_of_most_watched_genre = np.average(all_genre_score['Mean'])

    top5_genre = file_col1['value'].value_counts()[:5].index.tolist()
    file_col2_1 = file_col1[file_col1['value'].isin(top5_genre)]
    file_col2_2 = file[['Name', 'Mean']]
    file_col2 = pd.merge(file_col2_1, file_col2_2, on='Name')

    avg_score_per_genre = file_col2.groupby(['value'], as_index=False).mean()
    highest_avg_score_genre_score = avg_score_per_genre['Mean'].max()
    highest_avg_score_genre = avg_score_per_genre[avg_score_per_genre['Mean']
                                                  == highest_avg_score_genre_score].values.tolist()[0][0]

    st.subheader("Average Score of Top Five Genres")
    st.markdown(f"The average score of the most watched genre, {most_watched_genre}, is "
                f"{round(rating_of_most_watched_genre, 2)}. Whereas the genre with the highest "
                f"average score is {highest_avg_score_genre} with an average score of "
                f"{np.round(highest_avg_score_genre_score, 2)}.")

    st.vega_lite_chart(file_col2, {
        'width': 'container',
        'height': 376,
        "mark": {"type": "bar"},
        "encoding": {
            "y": {"field": "value",
                  "sort": "-x",
                  "title": None},
            "x": {"aggregate": "mean",
                  "field": "Mean",
                  "title": "Average Score",
                  "type": "quantitative"},
            "color": {
                "field": "value",
                "type": "nominal",
                "legend": None,
                "scale": {
                    "domain": [
                            'Action', 'Adventure', 'Anime', 'Comedy', 'Crime', 'Dark Comedy', 'Drama', 'Fantasy',
                            'Gangster', 'Hidden Camera', 'Historical', 'Horror', 'Mystery', 'Noir',
                            'Psychological Thriller', 'Rom Com', 'Romance', 'Sci-fi', 'Superhero', 'Suspense',
                            'Thriller', 'War', 'Western'
                    ],
                    "range": [
                        '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896',
                        '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7',
                        '#bcbd22', '#dbdb0e', '#17becf', '#9edae5', '#c85200', '#b10318', '#ff0055', '#1d539e'
                    ]
                }
            },
            "tooltip": [
                {"aggregate": "mean", "title": "Average Score", "field": "Mean", "format": ".2f"},
                {"aggregate": "count", "title": "No.of Films", "field": "value"}
            ],
        },

        "view": {"stroke": None}
    }, use_container_width=True)

    highest_avg_score_genre_df = file[file['Genre'] == highest_avg_score_genre]
    highest_avg_score_genre_df = highest_avg_score_genre_df.sort_values(by=['Mean'], ascending=False)

    with st.expander("See more info"):
        st.markdown(f"Some of the top rated {highest_avg_score_genre} films include: "
                    f"**{highest_avg_score_genre_df.values.tolist()[0][0]}**,"
                    f"**{highest_avg_score_genre_df.values.tolist()[1][0]}**,"
                    f"and **{highest_avg_score_genre_df.values.tolist()[2][0]}**.")


col3, col4 = st.columns(2)

with col3:
    top10_director = file['Director'].value_counts()[:10].index.tolist()
    top10_director_df = file[file['Director'].isin(top10_director)]
    top10_director_df['Director'].replace('', np.nan, inplace=True)
    top10_director_df.dropna(subset=["Director"], inplace=True)

    most_watched_director = top10_director_df['Director'].value_counts().index.tolist()[0]
    no_most_watched_director = top10_director_df['Director'].value_counts().values.tolist()[0]

    st.subheader("Number of Films Watched per Top Ten Director")
    st.markdown(f"So far, the most watched Director is {most_watched_director} with "
                f"{no_most_watched_director} films out of a total of {total_films} watched.")

    st.vega_lite_chart(top10_director_df, {
        'height': 400,
        "mark": {"type": "arc", "innerRadius": 50},
        "encoding": {
            "theta": {"aggregate": "count", "title": "No. of Films"},
            "color": {
                "field": "Director",
                "type": "nominal",
                "scale": {"scheme": "tableau20"},
                "legend": {"title": "Director"}
            },
            "tooltip": [
                {"field": "Director", "title": "Director"},
                {"aggregate": "count", "title": "No.of Films", "field": "value"}
            ],
        },
        "view": {"stroke": None}
    }, use_container_width=True)

with col4:
    avg_score_per_director = top10_director_df.groupby(['Director'], as_index=False).mean()
    highest_avg_score_director_score = avg_score_per_director['Mean'].max()
    highest_avg_score_director = avg_score_per_director[avg_score_per_director['Mean']
                                                        == highest_avg_score_director_score].values.tolist()[0][0]

    st.subheader("Average Score of Top Ten Directors")
    st.markdown(f"The average score of the most watched Director, {highest_avg_score_director}, is "
                f"{round(highest_avg_score_director_score, 2)}.")

    st.vega_lite_chart(top10_director_df, {
        'height': 400,
        "mark": {"type": "bar"},
        "encoding": {
            "y": {"field": "Director",
                  "sort": "-x",
                  "title": None},
            "x": {"aggregate": "mean",
                  "field": "Mean",
                  "title": "Average Score",
                  "type": "quantitative"},
            "color": {
                "field": "Director",
                "type": "nominal",
                "scale": {"scheme": "tableau20"},
                "legend": {"title": "Director"}
            },
            "tooltip": [
                {"aggregate": "mean", "title": "Average Score", "field": "Mean", "format": ".2f"},
                {"aggregate": "count", "title": "No.of Films", "field": "value"}
            ],
        },

        "view": {"stroke": None}
    }, use_container_width=True)

highest_avg_score_director_df = file[file['Director'] == highest_avg_score_director]
highest_avg_score_director_df = highest_avg_score_director_df.sort_values(by=['Mean'], ascending=False)

with st.expander("See more info"):
    st.markdown(f"Some of the top rated {highest_avg_score_director}'s films include: "
                f"**{highest_avg_score_director_df.values.tolist()[0][0]}**,"
                f"**{highest_avg_score_director_df.values.tolist()[1][0]}**,"
                f"and **{highest_avg_score_director_df.values.tolist()[2][0]}**.")

st.subheader("Density Plot of Ratings")
st.markdown(f"usr1's average score is {np.round(usr1_average_score, 2)} and "
            f"usr2's average score is {np.round(usr2_average_score, 2)}. "
            f"Therefore, {mean_bastard} is a mean Bastard.")

st.vega_lite_chart(file, {
        "width": 400,
        "height": 300,
        "transform": [
            {"filter": "datum.usr1 != 0"},
            {"filter": "datum.usr2 != 0"},
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
                    "color": {"datum": "Average"}
                }
            },
            {
                "transform": [
                    {
                        "density": "usr2",
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
                    "color": {"datum": "usr2"}
                }
            },
            {
                "transform": [
                    {
                        "density": "usr1",
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
                    "color": {"datum": "usr1"}
                }
            }
        ]

    }, use_container_width=True)

st.subheader("Average Film Ratings for All Time")
st.markdown(f'The highest rated film so far is {highest_rated_film[0]}.')

select_graph = st.radio('Sort by:', ('Alphabetical', 'Score'))

if select_graph == 'Score':
    st.vega_lite_chart(file, {
            "width": "container",
            "mark": {"type": "bar", "cornerRadiusEnd": 4, "tooltip": {"content": "encoding"}},
            "encoding": {
                "x": {"field": "Mean",
                      "type": "quantitative",
                      "title": "Score"},
                "y": {"field": "Name",
                      "sort": "-x",
                      "title": None},
                "color": {
                    "field": "Genre",
                    "type": "nominal",
                    "scale": {
                        "domain": [
                                'Action', 'Adventure', 'Anime', 'Comedy', 'Crime', 'Dark Comedy', 'Drama', 'Fantasy',
                                'Gangster', 'Hidden Camera', 'Historical', 'Horror', 'Mystery', 'Noir',
                                'Psychological Thriller', 'Rom Com', 'Romance', 'Sci-fi', 'Superhero', 'Suspense',
                                'Thriller', 'War', 'Western'
                        ],
                        "range": [
                            '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896',
                            '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7',
                            '#bcbd22', '#dbdb0e', '#17becf', '#9edae5', '#c85200', '#b10318', '#ff0055', '#1d539e'
                        ]
                    }
                },
            },
            "config": {"view": {"stroke": "transparent"}, "axis": {"domainWidth": 1}}
        }, use_container_width=True)
else:
    st.vega_lite_chart(file, {
        "width": "container",
        "mark": {"type": "bar", "cornerRadiusEnd": 4, "tooltip": {"content": "encoding"}},
        "encoding": {
            "x": {"field": "Mean",
                  "type": "quantitative",
                  "title": "Score"},
            "y": {"field": "Name",
                  "title": None},
            "color": {
                "field": "Genre",
                "type": "nominal",
                "scale": {
                    "domain": [
                            'Action', 'Adventure', 'Anime', 'Comedy', 'Crime', 'Dark Comedy', 'Drama', 'Fantasy',
                            'Gangster', 'Hidden Camera', 'Historical', 'Horror', 'Mystery', 'Noir',
                            'Psychological Thriller', 'Rom Com', 'Romance', 'Sci-fi', 'Superhero', 'Suspense',
                            'Thriller', 'War', 'Western'
                    ],
                    "range": [
                        '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896',
                        '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7',
                        '#bcbd22', '#dbdb0e', '#17becf', '#9edae5', '#c85200', '#b10318', '#ff0055', '#1d539e'
                    ]
                }
            },
        },
        "config": {"view": {"stroke": "transparent"}, "axis": {"domainWidth": 1}}
    }, use_container_width=True)

file_diff = file[~(file == 0).any(axis=1)]
file_diff['Diff'] = (file_diff['usr2'] - file_diff['usr1']).abs()
max_diff = file_diff['Diff'].max()
most_disagreed_film = file_diff[file_diff['Diff'] == max_diff].values.tolist()[0][0]

st.subheader("Rating Difference of usr2 Minus usr1")
st.markdown('Films with red bars means usr1 liked more than usr2, and green means usr2 liked more than '
            f'usr1. The most disagreed film so far is {most_disagreed_film}.')

st.vega_lite_chart(file_diff, {
        "width": "container",
        "height": 500,
        "mark": {"type": "bar", "cornerRadiusEnd": 4},
        "transform": [
            {"calculate": "datum.usr2-datum.usr1", "as": "diff"},
            {"filter": "datum.diff != 0"},
            {"filter": "datum.usr1 != 0"},
            {"filter": "datum.usr2 != 0"},
            {"filter": "datum.Mean != 0"},
        ],
        "encoding": {
            "x": {"field": "diff",
                  "type": "quantitative",
                  "title": "Score"},
            "y": {"field": "Name",
                  "sort": "-x",
                  "title": None},
            "color": {
                "condition": {"test": "datum.diff>0", "value": "green"},
                "value": "red"
            },
            "tooltip": [
                {"field": "usr1"},
                {"field": "usr2"}
            ]
        },
        "config": {"view": {"stroke": "transparent"}, "axis": {"domainWidth": 1}}
    }, use_container_width=True)
