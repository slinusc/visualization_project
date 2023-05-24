import streamlit as st
import pandas as pd
import holoviews as hv
from visualization_classes import relation_chord_chart as rcc
from visualization_classes import geo_map as gm
from visualization_classes.sent_sub_obj import SentimentPlot, SubjectivityPlot
from visualization_classes.wordclound import theWordCloud
from visualization_classes.linechart_categories import LinechartCategories
import plotly.express as px


def main():

    # layout streamlit app
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([1, 1])
    full_width_col1 = st.columns(1)
    col3, col4 = st.columns([1, 1])
    full_width_col2 = st.columns(1)
    col5, col6 = st.columns([1, 1])
    full_width_col3 = st.columns(1)

    # remove streamlit menu
    st.markdown("""
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """, unsafe_allow_html=True)
    # load data
    @st.cache_data
    def load_data():
        path = '../data/without_content.tsv.xz'
        df = pd.read_csv(path, sep='\t', compression='xz')
        df['countries'] = df['countries'].apply(eval)
        df['entities_header'] = df['entities_header'].apply(eval)
        df['people'] = df['people'].apply(eval)
        df['date'] = pd.to_datetime(df['date'])
        return df
    df = load_data()

    # Filter data by date with streamlit date input
    selected_date = col1.date_input("Wähle Datum",
                                  value=pd.to_datetime('2022-02-24'),
                                  min_value=pd.to_datetime('2022-01-01'),
                                  max_value=pd.to_datetime('2022-12-31'))
    selected_date = pd.to_datetime(selected_date)
    filtered_df = df[df['date'] == selected_date]

    # Filter data by category with streamlit dropdown
    categories = df['article_category'].unique()
    categories = ['Alle'] + list(categories)
    category = col2.selectbox('Wähle Kategorie', categories)
    if category != 'Alle':
        filtered_df = filtered_df[filtered_df['article_category'] == category]

    # Visualizations

    # Create linechart plot
    linechart_generator = LinechartCategories(selected_date)
    linechart_plot = linechart_generator.linechart_categories(df)
    with full_width_col1[0]:
        st.plotly_chart(linechart_plot)

    # Create chord diagram
    chord_chart = rcc.ChordCharts(filtered_df['countries']).country_chord_chart(threshold=5)
    with col3:
        st.bokeh_chart(hv.render(chord_chart, backend='bokeh'))

    # Create chord diagram
    chord_chart_people = rcc.ChordCharts(filtered_df['people']).country_chord_chart(threshold=1)
    with col4:
        st.bokeh_chart(hv.render(chord_chart_people, backend='bokeh'))

    # Create word cloud

    entities_header = filtered_df['entities_header'].dropna().tolist()
    word_cloud = theWordCloud(entities_header)
    generated_wordcloud = word_cloud.generate_wordcloud()
    with full_width_col2[0]:
        st.pyplot(word_cloud.display_wordcloud(generated_wordcloud))

    # Create sentiment plot
    sentiment_plot = SentimentPlot(filtered_df['sentiment'])
    sentiment_plot.create_plot()
    with col5:
        st.plotly_chart(sentiment_plot.fig)

    # Create subjectivity plot
    subjectivity_plot = SubjectivityPlot(filtered_df['subjectivity'])
    subjectivity_plot.create_plot()
    with col6:
        st.plotly_chart(subjectivity_plot.fig)
    """
    # Create world map
    data_country_series = filtered_df['countries_en']
    data_country_list = [eval(i) for i in data_country_series.dropna().tolist()]

    world_map = gm.WorldMap(data_country_list)
    world_map_chart = world_map.erstelle_weltkarte()
    with full_width_col3[0]:
        st.plotly_chart(world_map_chart)

    """
if __name__ == "__main__":
    main()
