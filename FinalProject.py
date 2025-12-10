"""
Class: CS230-5
Name: Samantha Nelson
Description: (Give a brief description for Exercise name--See below)
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""
import streamlit as st
import pandas as pd
import plotly.express as px


# Streamlit page configuration
st.set_page_config(
    page_title="NYC Apartment Finder",
    layout="wide",
    initial_sidebar_state = "expanded"
)

#styling
st.markdown(
    """
    <h1 style='color: navy;'>NYC APARTMENT FINDER</h1>
            <style>
            .stApp {
        background-color: #f0f8ff; 
    }
    </style>
    """,
    unsafe_allow_html=True)


df = pd.read_csv("NY-House-Dataset.csv")

# filter properties based on user inputs on sidebar
#[FUNC2P]
def filter_properties(df, types = None, min_price = 0, max_price = 10000000, min_beds = 0, min_baths = 0,
                      sublocality = None, broker = None, min_sqft = 0, max_sqft = 50000):

    # filtered by all data
    filtered = df.copy()

    # filter by property type
    if types and len(types) > 0:
        filtered = filtered[filtered['TYPE'].isin(types)]

    #filter by price and bedrooms
    #[FILTER2]
    filtered = filtered[
                    (filtered['PRICE'] >= min_price) &
                    (filtered['PRICE'] <= max_price) &
                    (filtered['BEDS'] >= min_beds) &
                    (filtered['BATH'] >= min_baths)
    ]

    if sublocality != 'All':
        # [FILTER1]
        filtered = filtered[filtered['SUBLOCALITY'] == sublocality]
    return filtered

#[FUNCCALL2]
def format_price(price):
    if pd.isna(price):
        return "N/A"
    return f"${price:,.0f}"


#[ST3] - sidebar
st.sidebar.header("Filter Your Search")

# Multi-select house type
#[ST1]
house_types = st.sidebar.multiselect("Which house type? ",
              ["Coming Soon", "Condo for sale", "Condop for sale",
               "Contigent", "Co-op for sale", "For Sale", "Foreclosure",
               "House for sale", "Land for sale", "Mobile house for sale",
               "Multi-family home for sale", "Pending", "Townhouse for sale"])

#[ST2]
price_range = st.sidebar.slider(
    "Price Range ($)",
    0, 65000000,
    (100000, 2000000),
    10000,
    format = "$%d")

min_beds = st.sidebar.number_input("Min Bedrooms", 0, 10, 1)

min_baths = st.sidebar.number_input("Min Bathrooms", 0.0, 10.0, 1.0, step = 0.5)

#[LISTCOMP]
#https://www.geeksforgeeks.org/python/get-unique-values-from-a-column-in-pandas-dataframe/
sublocalities = ['All'] + sorted([x for x in df['SUBLOCALITY'].unique().tolist()
                                  if pd.notna(x) and x != 'Unknown'])
sublocality = st.sidebar.selectbox("Neighborhood", sublocalities)

filtered_df = filter_properties(df, house_types, price_range[0], price_range[1], min_beds, min_baths,sublocality)

#[FUNCRETURN2]
def get_stats(df):
    if len(df) == 0:
        return 0,0,0
    avg_price = df['PRICE'].mean()
    median_price = df['PRICE'].median()
    count = len(df)
    return avg_price, median_price, count
avg_price, median_price, count = get_stats(filtered_df)

#st.title("NYC APARTMENT FINDER")
st.subheader(f"{count} Properties")

tab1, tab2, tab3 = st.tabs(["Map", "Data", "Charts"])

with tab1:
    if not filtered_df.empty:
        map_data = filtered_df[['LATITUDE', 'LONGITUDE', 'PRICE', 'ADDRESS', 'SUBLOCALITY']].dropna()
        if not map_data.empty:
            #[MAXMIN]
            min_price = map_data['PRICE'].min()
            max_price = map_data['PRICE'].max()

            #Proud of this: used for coloring points on a map based on price on a 0-1 scale
            #https://www.geeksforgeeks.org/python/python-map-with-lambda/
            map_data['color'] = map_data['PRICE'].apply(
                lambda p: (p - min_price) / (max_price - min_price)
            )

            #https://towardsdatascience.com/make-beautiful-spatial-visualizations-with-plotly-and-mapbox-fd5a638d6b3c/
            fig_map = px.scatter_mapbox(
                #[MAP]
                map_data,
                lat= "LATITUDE",
                lon= "LONGITUDE",
                hover_name= "ADDRESS",
                hover_data={"PRICE": True, "SUBLOCALITY": True, "LATITUDE": False, "LONGITUDE": False},
                color= "PRICE",
                color_continuous_scale="Viridis",
                size_max = 15,
                zoom = 10,
                height = 600
            )
            fig_map.update_layout(mapbox_style = "open-street-map")
            fig_map.update_layout(margin={"r":0,"t":0, "l":0, "b":0})
            st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No properties found. Try adjusting your filters.")

with tab2:
    if not filtered_df.empty:
        display_data = []

        # [ITERLOOP]
        for _, row in filtered_df.head(20).iterrows():
            display_data.append({
                'ADDRESS': row['ADDRESS'][:50],
                'Neighborhood': row['SUBLOCALITY'],
                'TYPE':row['TYPE'],
                'BEDS': row['BEDS'],
                'BATHS': row['BATH'],
                'PRICE': format_price(row['PRICE']) #[FUNCCALL2]
        })

        display_df = pd.DataFrame(display_data)
        sort_option = st.selectbox(
            "Sort by:",
            ["Price (High to Low)", "Price (Low to High)", "Bedrooms", "Neighborhood"]
        )
        if sort_option == "Price (High to Low)":
            display_df = display_df.sort_values('PRICE', ascending = False)
        elif sort_option == "Price (Low to High)":
            display_df = display_df.sort_values('PRICE', ascending=True)
        elif sort_option == "Bedrooms":
            display_df = display_df.sort_values('BEDS', ascending=True)
        elif sort_option == "Neighborhood":
            display_df = display_df.sort_values('Neighborhood', ascending=True)

        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No data to display")

with tab3:
    if not filtered_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            #https://www.geeksforgeeks.org/python/histogram-using-plotly-in-python/
            #[CHART1]
            fig = px.histogram(
                filtered_df,
                x = 'PRICE',
                title = 'Price Distribution',
                labels={'PRICE': 'Price ($)', 'count': 'Number of Properties'},
                nbins=30
            )

            fig.update_layout(xaxis_tickprefix = '$', xaxis_tickformat = ',.0f')
            st.plotly_chart(fig, use_container_width=True)

        with col2:

            neighborhood_counts = {
                area: filtered_df[filtered_df['SUBLOCALITY'] == area].shape[0]
                for area in filtered_df['SUBLOCALITY'].unique()
                if filtered_df[filtered_df['SUBLOCALITY'] == area].shape[0] > 0
            }

            #[DICTMETHOD]
            sorted_counts = dict(sorted(neighborhood_counts.items(),
                                        key = lambda x: x[1], reverse = True)[:10])
            if sorted_counts:
                #[CHART2]
                fig2 = px.bar(
                    x=list(sorted_counts.keys()),
                    y=list(sorted_counts.values()),
                    title='Listings by Neighborhood',
                    labels = {'x':'Neighborhood', 'y': 'Number of listings'}
                )
                st.plotly_chart(fig2, use_container_width=True)

#https://discuss.streamlit.io/t/change-backgroud/5653/5

col1, col2, col3 = st.columns(3)

col1.metric("Average Price", format_price(avg_price)) #[FUNCCALL2]
col2.metric("Median Price", format_price(median_price))
col3.metric("Total Listings", f"{count:,}")

def main():
    pass
if __name__ == "__main__":
    main()
