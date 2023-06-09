import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from classes.linechart_categories import LinechartCategories
from classes.multiple_line_chart_medium import NewspaperCategoryPlot
from classes.topic_analysis import TopicAnalysis

st.set_page_config(layout="wide", menu_items={}, )


def main():
    """
    Die Hauptfunktion der Streamlit-Anwendung zur Medienanalyse. Sie liest den Datensatz ein,
    ermöglicht die Datenfilterung basierend auf den Benutzereingaben und erzeugt verschiedene Visualisierungen
    basierend auf den gefilterten Daten.

    Die Visualisierungen umfassen:
    1. Eine Zeitreihenanalyse der Anzahl von Artikeln nach Kategorien.
    2. Eine Analyse der Anzahl von Artikeln nach Zeitungen.
    3. Eine Themenanalyse, die die 20 häufigsten Wörter in den Artikeln anzeigt.
    4. Eine Tabelle mit Artikeldaten basierend auf den Filtereinstellungen des Benutzers.

    Darüber hinaus enthält die Funktion auch Code zum Stylen und Layouten der Streamlit-App.

    Funktion ist mit dem @st.cache_data Decorator versehen, um die Daten nur einmal zu laden
    und sie danach im Cache zu speichern. Dies verbessert die Effizienz der Streamlit-App erheblich, indem sie
    redundantes Laden und Verarbeiten von Daten verhindert.
    """
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
    df.columns = ['Medium', 'Headline', 'Datum', 'Länder', 'sentiment', 'subjectivity',
                  'Entitäten Header', 'Kategorie', 'Länder (englisch)', 'Personen']

    # layout streamlit app
    st.header('Medienanalyse')
    st.button('ℹ️', help="Mit den Filteroptionen können "
                         "Sie die angezeigten Daten nach spezifischen "
                         "Kriterien einschränken. Die verfügbaren Filteroptionen "
                         "sind: \n"
                         "1. Datum: Mit dieser Option können Sie den "
                         "Zeitraum, für den die Daten angezeigt werden sollen, "
                         "einschränken. Wählen Sie einfach das gewünschte Start- "
                         "und Enddatum aus. In dieser Version der App ist es möglich, "
                         "Daten für jeden beliebigen Zeitraum im Jahr 2022 zu analysieren, "
                         "und jeder Tag kann einzeln analysiert werden. \n\n"
                         "2. Kategorie: Hier können Sie auswählen, "
                         "welche Artikelkategorien in den Daten enthalten sein sollen. "
                         "Sie können eine oder mehrere Kategorien auswählen, "
                         "und die Daten werden entsprechend gefiltert. \n"
                         "3. Zeitungen: Mit dieser Option können Sie auswählen, "
                         "von welchen Zeitungen die Daten angezeigt werden sollen. "
                         "Es stehen acht verschiedene Zeitungen zur Auswahl, "
                         "und Sie können eine oder mehrere davon auswählen.\n\n"
                         " Für weitere Informationen besuchen Sie: "
                         "https://github.com/slinusc/visualization_project/blob/main/README.md")

    col1, col2, col3 = st.columns([1, 1, 1])  # Widgets
    full_width_col0 = st.columns(1)  # Line charts
    full_width_col1 = st.columns(1)  # Line chart
    full_width_col2 = st.columns(1)  # Topic analysis
    full_width_col3 = st.columns(1)  # Dataframe

    # KONFIGURATION FÜR ALLE PLOTS
    config = dict({'displayModeBar': False})

    # STREAMLIT-MENÜ AUSBLENDEN & FARBE ANPASSEN (BLAU)
    st.markdown("""
                            <style>
                            #MainMenu {visibility: hidden;}
                            footer {visibility: hidden;}
                            .st-dd {color: white; background-color: #1f77b4;}
                            </style>
                            """, unsafe_allow_html=True)

    # Daten nach Datum filtern mit Streamlit Datumseingabe
    with col1:
        dates = st.date_input(
            "Wähle Datum",
            [pd.to_datetime('2022-02-01'), pd.to_datetime('2022-02-28')],
            min_value=pd.to_datetime('2022-01-01'),
            max_value=pd.to_datetime('2022-12-31')
        )
        start_date = pd.Timestamp(dates[0])
        if len(dates) == 1:
            end_date = start_date
            st.error('Bitte wählen Sie ein Enddatum aus.')
        elif len(dates) == 2:
            end_date = pd.Timestamp(dates[1])

        filtered_df = df[(df['Datum'] >= start_date) & (df['Datum'] <= end_date)]

    # Daten nach Kategorie mit streamlit multiselect filtern
    with col2:
        categories = df['Kategorie'].unique()
        categories_options = ['Alle'] + list(categories)
        selected_categories = st.multiselect('Wähle Kategorie', categories_options, default=['Alle'])
        if 'Alle' in selected_categories:
            # alle Kategorien sind ausgewählt, keine Filterung erforderlich
            pass
        else:
            filtered_df = filtered_df[filtered_df['Kategorie'].isin(selected_categories)]

    # Daten nach Medium_name mit streamlit multiselect filtern
    with col3:
        newspapers = df['Medium'].unique()
        newspapers_options = ['Alle'] + list(newspapers)
        selected_newspapers = st.multiselect('Wähle Zeitung', newspapers_options, default=['Alle'])

        if 'Alle' in selected_newspapers:
            # alle Zeitungen werden ausgewählt
            selected_newspapers = newspapers
        else:
            filtered_df = filtered_df[filtered_df['Medium'].isin(selected_newspapers)]

    # Prüfen, ob Anfangs- und Enddatum übereinstimmen
    if start_date != end_date:
        # Liniendiagramm erstellen
        linechart_generator = LinechartCategories()
        linechart_plot = linechart_generator.linechart_categories(filtered_df)
        with full_width_col0[0]:
            st.subheader('Anzahl Artikel nach Kategorien')
            st.button('ℹ️', help="Es werden die Anzahl der Artikel pro Kategorie angezeigt.\n\n"
                                 " Für weitere Informationen besuchen Sie: "
                                 "https://github.com/slinusc/visualization_project/blob/main/README.md")
            st.plotly_chart(linechart_plot, config=config)

        # Liniendiagramm Medium erstellen
        line_chart = NewspaperCategoryPlot(filtered_df, selected_categories)
        line_medium = line_chart.plot_newspaper_category()
        with full_width_col1[0]:
            st.subheader('Anzahl Artikel nach Zeitung')
            st.button('ℹ️', help="Es werden die Anzahl der Artikel pro Zeitung angezeigt.\n\n"
                                 " Für weitere Informationen besuchen Sie: "
                                 "https://github.com/slinusc/visualization_project/blob/main/README.md")
            st.plotly_chart(line_medium, config=config)
    else:
        fig = go.Figure()
        for newspaper in selected_newspapers:
            newspaper_df = filtered_df[filtered_df['Medium'] == newspaper]
            category_frequencies = newspaper_df['Kategorie'].value_counts().sort_values(ascending=False)
            fig.add_trace(go.Bar(
                x=category_frequencies.index,
                y=category_frequencies.values,
                name=newspaper
            ))

        fig.update_layout(xaxis_title='Kategorie',
                          yaxis_title='Häufigkeit',
                          barmode='stack',
                          width=1100, height=500)
        with full_width_col1[0]:
            st.subheader('Häufigkeiten nach Kategorien')
            st.button('ℹ️', help="Es werden die Anzahl der Artikel pro Zeitung angezeigt. \n\n"
                                 " Für weitere Informationen besuchen Sie: "
                                 "https://github.com/slinusc/visualization_project/blob/main/README.md")
            st.plotly_chart(fig, config=config)

    # THEMENANALYSE
    with full_width_col2[0]:
        bar_chart = TopicAnalysis(filtered_df)
        fig = bar_chart.plot()
        st.subheader('Themen Analyse')
        st.button('ℹ️', help="Die Themen Analyse zeigt die 20 häufigsten vorkommenden Wörter "
                             "in den Artikeln an.\n\n"
                             " Für weitere Informationen besuchen Sie: "
                             "https://github.com/slinusc/visualization_project/blob/main/README.md")
    #    topic_analysis = TopicAnalysis()
    #    st.plotly_chart(topic_analysis.plot_most_common_words(filtered_df['Entitäten Header'], 20), config=config)
        st.plotly_chart(fig, config=config)

    # DATAFRAME
    with full_width_col3[0]:
        filtered_df['Datum'] = filtered_df['Datum'].dt.strftime('%d.%m.%Y')
        st.subheader('Artikeltabelle')
        st.button('ℹ️', help='Die Tabelle zeigt die Artikel an, nach denen die Filter gesetzt wurden.'
                             " Für weitere Informationen besuchen Sie: "
                             "https://github.com/slinusc/visualization_project/blob/main/README.md"
                  )
        st.dataframe(filtered_df.loc[:, ['Medium', 'Headline', 'Kategorie', 'Datum']], width=1100)


if __name__ == "__main__":
    main()
