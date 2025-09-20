# 📦 Import required libraries
import streamlit as st
import pandas as pd
import altair as alt

# 📂 Load the dataset
df = pd.read_csv("1960-2010_Movies.csv")

# Sidebar filters: Year range
st.sidebar.header("Filters")
year_range = st.sidebar.slider("Select Year Range", 1960, 2010, (1960, 2010))

# Filter dataset based on year selection
df_filtered = df[(df["startyear"] >= year_range[0]) & (df["startyear"] <= year_range[1])]


# Clean the dataset:

# Remove episode titles (to avoid TV series noise)
df_filtered = df_filtered[~df_filtered['primarytitle'].str.startswith("Episode #")]


df_filtered = df_filtered[df_filtered['runtimeminutes'] >= 40]
df_filtered = df_filtered.dropna(subset=['genres', 'averagerating'])

# Split genre strings into lists, then "explode" them into rows
df_expanded = df_filtered.assign(genres=df_filtered['genres'].str.split(',')).explode('genres')
df_expanded['genres'] = df_expanded['genres'].str.strip()

# Sidebar filter: Genre
genre_options = ["All"] + sorted(df_expanded["genres"].unique())
selected_genre = st.sidebar.selectbox("Select Genre", genre_options)

# Dashboard Title & Intro
st.title("🎬 Movie Genre Dashboard (1960–2010)")
st.markdown("""
Explore movie genres over the years.  
Use the sidebar to filter by year range and genre.

Charts show: genre counts, average ratings, balance score, trends for individual genres, and top movies.
""")

# Case 1: Show overview if "All" genres are selected

if selected_genre == "All":
    st.subheader("Top Genres Overview")

    # Aggregate metrics: average rating, count, and balance score
    balance_df = df_expanded.groupby("genres").agg({'averagerating':'mean','genres':'count'}).rename(columns={'genres':'count'}).reset_index()
    balance_df['balance_score'] = balance_df['count'] * balance_df['averagerating']

    # Display side-by-side charts
    col1, col2 = st.columns(2)

    # Chart 1: Genres ranked by number of movies
    with col1:
        st.subheader("Top Genres by Number of Movies")
        chart1 = alt.Chart(balance_df).mark_bar().encode(
            x=alt.X('genres', sort='-y', title='Genres'),
            y=alt.Y('count', title='Number of Movies'),
            color='genres',
            tooltip=['genres','count']
        ).properties(width=400, height=400)
        st.altair_chart(chart1, use_container_width=True)

    # Chart 2: Genres ranked by average rating
    with col2:
        st.subheader("Top Genres by Average Rating")
        chart2 = alt.Chart(balance_df).mark_bar().encode(
            x=alt.X('genres', sort='-y', title='Genres'),
            y=alt.Y('averagerating', title='Average Rating'),
            color='genres',
            tooltip=['genres','averagerating']
        ).properties(width=400, height=400)
        st.altair_chart(chart2, use_container_width=True)

    # Chart 3: Genres ranked by balance score
    st.subheader("Genres Ranked by Balance Score (Count × Avg Rating)")
    chart3 = alt.Chart(balance_df).mark_bar().encode(
        y=alt.Y('genres', sort='-x'),
        x=alt.X('balance_score', title='Balance Score'),
        color='genres',
        tooltip=['genres','count','averagerating','balance_score']
    ).properties(width=800, height=500)
    st.altair_chart(chart3, use_container_width=True)



# Case 2: Show detailed trends if a specific genre is selected

else:
    # Filter dataset for the chosen genre
    genre_df = df_expanded[df_expanded["genres"] == selected_genre]

    # Aggregate yearly movie counts and average ratings
    yearly_stats = genre_df.groupby("startyear").agg(
        movie_count=('primarytitle', 'count'),
        avg_rating=('averagerating', 'mean')
    ).reset_index()

    # Line charts: Number of movies & average ratings over time
    if not yearly_stats.empty:
        st.subheader(f"{selected_genre} Movie Trends Over Time")

        count_chart = alt.Chart(yearly_stats).mark_line(point=True).encode(
            x='startyear',
            y='movie_count',
            tooltip=['startyear', 'movie_count']
        ).properties(title=f"Number of {selected_genre} Movies Over Time", width=700, height=300)

        rating_chart = alt.Chart(yearly_stats).mark_line(point=True, color='orange').encode(
            x='startyear',
            y='avg_rating',
            tooltip=['startyear', 'avg_rating']
        ).properties(title=f"Average Rating of {selected_genre} Movies Over Time", width=700, height=300)

        st.altair_chart(count_chart, use_container_width=True)
        st.altair_chart(rating_chart, use_container_width=True)

    else:
        st.write(f"No data available for {selected_genre} in the selected year range.")

    # Top 10 highest-rated movies in the selected genre
    top_movies = genre_df.sort_values(by="averagerating", ascending=False).head(10)
    if not top_movies.empty:
        st.subheader(f"Top Movies in {selected_genre}")
        st.table(top_movies[['primarytitle','startyear','averagerating','runtimeminutes']].reset_index(drop=True))
    else:
        st.write(f"No top movies to display for {selected_genre} in the selected year range.")

