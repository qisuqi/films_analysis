import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

file = pd.read_csv('Films.csv')

total_films = len(file)
highest_score = file['Mean'].max()
highest_rated_film = file.loc[file['Mean'] == highest_score, 'Name'].values.tolist()

most_watched_genre = file['Genre'].value_counts().index.tolist()[0]
no_most_watched_genre = file['Genre'].value_counts().values.tolist()[0]

most_watched_genre_df = file[file['Genre'] == most_watched_genre]
rating_of_most_watched_genre = np.average(most_watched_genre_df['Mean'])

st.set_page_config(layout="wide")

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)

query_params = st.experimental_get_query_params()
tabs = ["Home", "Submit Films"]

if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "Home"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="Home")
    active_tab = "Home"

li_items = "".join(
    f"""
    <li class="nav-item">
        <a class="nav-link{' active' if t==active_tab else ''}" href="/?tab={t}">{t}</a>
    </li>
    """
    for t in tabs
)
tabs_html = f"""
    <ul class="nav nav-tabs">
    {li_items}
    </ul>
"""

st.markdown(tabs_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if active_tab == 'Home':

    st.title('Analysing Films Watched by Butler-Su')

    output_graphs = st.container()

    with output_graphs:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Number of Films Watched per Genre")
            st.markdown(f"So far, the most watched genre is {most_watched_genre} with "
                        f"{no_most_watched_genre} {most_watched_genre} films out of a total of {total_films} watched.")
            st.vega_lite_chart(file, {
                'width': 'container',
                'height': 400,
                "mark": {"type": "arc", "tooltip": {"content": "encoding"}, "innerRadius": 70},
                "encoding": {
                    "theta": {"aggregate": "count", "title": "No. of Films"},
                    "color": {
                        "field": "Genre",
                        "type": "nominal",
                        "scale": {"scheme": "tableau20"}
                    }
                },
                "view": {"stroke": None}
            }, use_container_width=True)

        with col2:
            st.subheader("Total Score per Genre")
            st.markdown(f"The average score of the most watched genre, {most_watched_genre}, is "
                        f"{round(rating_of_most_watched_genre, 2)}.")

            st.vega_lite_chart(file, {
                'width': 'container',
                'height': 400,
                "mark": {"type": "bar"},
                "encoding": {
                    "y": {"field": "Genre", "sort": "-x"},
                    "x": {"aggregate": "sum", "field": "Mean", "title": "Total Score", "type": "quantitative"},
                    "color": {
                        "field": "Genre",
                        "type": "nominal",
                        "scale": {"scheme": "tableau20"}
                    },
                    "tooltip": [
                        {"aggregate": "mean", "title": "Average Score", "field": "Mean", "format": ".2f"},
                        {"field": "Genre", "title": "Genre"}
                    ],
                },

                "view": {"stroke": None}
            }, use_container_width=True)

        st.subheader("Density Plot of Ratings")
        st.markdown('George is a mean Bastard.')
        
        st.vega_lite_chart(file, {
            "width": 400,
            "height": 300,
            "transform": [
                {"filter": "datum.Qiqi != 0"},
                {"filter": "datum.George != 0"},
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
                            "type": "quantitative"
                        },
                        "color": {"datum": "Average"}
                    }
                },
                {
                    "transform": [
                        {
                            "density": "George",
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
                            "type": "quantitative"
                        },
                        "color": {"datum": "George"}
                    }
                },
                {
                    "transform": [
                        {
                            "density": "Qiqi",
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
                            "type": "quantitative"
                        },
                        "color": {"datum": "Qiqi"}
                    }
                }
            ]

        }, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Average Film Ratings for All Time")
            st.markdown(f'The highest rated films so far are {highest_rated_film[0]} and {highest_rated_film[1]}.')
            
            st.vega_lite_chart(file, {
                "width": "container",
                "height": 500,
                "mark": {"type": "bar", "cornerRadiusEnd": 4, "tooltip": {"content": "encoding"}},
                "encoding": {
                    "x": {"field": "Mean", "type": "quantitative", "title": "Score"},
                    "y": {"field": "Name", "sort": "-x", "title": "Film Names"}
                },
                "config": {"view": {"stroke": "transparent"}, "axis": {"domainWidth": 1}}
            }, use_container_width=True)

        with col4:
            st.subheader("Rating Difference of George Minus Qiqi")
            st.markdown('Films with red bars means Qiqi liked more than George, and green means George liked more than'
                        ' Qiqi.')

            st.vega_lite_chart(file, {
                "width": "container",
                "height": 500,
                "mark": {"type": "bar", "cornerRadiusEnd": 4, "tooltip": {"content": "encoding"}},
                "transform": [
                    {"calculate": "datum.George-datum.Qiqi", "as": "diff"},
                    {"filter": "datum.diff != 0"},
                    {"filter": "datum.Qiqi != 0"},
                    {"filter": "datum.George != 0"},
                    {"filter": "datum.Mean != 0"},
                ],
                "encoding": {
                    "x": {"field": "diff", "type": "quantitative", "title": "Score"},
                    "y": {"field": "Name", "sort": "-x", "title": "Film Names"},
                    "color": {
                        "condition": {"test": "datum.diff>0", "value": "green"},
                        "value": "red"
                    }
                },
                "config": {"view": {"stroke": "transparent"}, "axis": {"domainWidth": 1}}
            }, use_container_width=True)
