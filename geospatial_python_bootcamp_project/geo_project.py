# Imports
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Page Configuration
st.set_page_config(
    page_title="World Population Dashboard",
    layout="wide"
)

# Title
st.title('**:blue[World Population Dashboard]**')

@st.cache_data # caching data

# Fetching data
def get_data():
    url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world_population.csv"
    geo_url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/main/13_final_project_data/world.geojson"
    try:
        df = pd.read_csv(url)
        gdf = gpd.read_file(geo_url)
        return df, gdf
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None

# Loading Data
data, geodata = get_data()

if data is not None and geodata is not None:
    st.write("***Select a country to view its population data and geospatial information***")

    # Country Selector
    country = st.selectbox(
        label="**Select a Country**",
        placeholder="Please select a country to view its data.",
        options=[""] + list(data["Country/Territory"])
    )
    if country == "":
        st.info('Please select a country to view its data.')
    else:
        st.header("Population Over Selected Years", divider=True)
        
    if country: 
        col1, col2 = st.columns([1, 1])

        with col1:
            # Interactive Bar chart, Population variation by years of the selected country
            country_data = data[data["Country/Territory"] == country].iloc[0]
            target_years = ["1970", "1980", "1990", "2000", "2010", "2015", "2020", "2022"]
            
            selection = {
                "Year": target_years,
                "Population": [country_data[f"{year} Population"] for year in target_years]
            }
            population_years = st.multiselect(
                label="**Select Population Years**",
                options=[f"{year} Population" for year in target_years]
            )

            population_df = pd.DataFrame(selection)
            population_df = population_df[population_df['Year'].isin(
                [year.split()[0] for year in population_years])]

            fig = px.bar(
                population_df,
                x="Year",
                y="Population",
                title=f"Population of {country} Over Selected Years"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("Country Statistics", divider=True)
            # Display Stats in Card
            st.markdown('<div class="card">', unsafe_allow_html=True)
            area = data.loc[data['Country/Territory'] == country, 'Area (km²)'].values[0]
            density = data.loc[data['Country/Territory'] == country, 'Density (per km²)'].values[0]
            growth_rate = data.loc[data['Country/Territory'] == country, 'Growth Rate'].values[0]
            world_population_percentage = data.loc[data['Country/Territory'] == country, 'World Population Percentage'].values[0]
            
            # Display the statistics
            st.write(f"**Area (km²):** {area} km²")
            st.write(f"**Density (per km²):** {density} people/km²")
            st.write(f"**Growth Rate:** {growth_rate} %")
            st.write(f"**World Population Percentage:** {world_population_percentage} %")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Map Display of the selected country
            st.header("Country Map", divider=True)
            country_geo = geodata[geodata['name'] == country]
            
            if not country_geo.empty:
                bounds = country_geo.geometry.total_bounds
                map = folium.Map()
                folium.GeoJson(
                    data=country_geo,
                    
                    style_function= lambda x: {
                        "fillColor": "red",
                        "fillOpcity":0.7,
                        },
                    tooltip= country                     
                ).add_to(map)

                map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
                st_folium(map, width=700, height=500)
            else:
                st.write("No geospatial data available for the selected country.")
else:
    st.write("Fetching data...")
