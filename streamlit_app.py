# Import Python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App title
st.title("Customize Your Smoothie!🥤")

st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

# Customer name
name_on_order = st.text_input("Name on Smoothie:")

st.write(
    "The name on Smoothie will be",
    name_on_order
)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names and API search values
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowpark dataframe to Pandas
pd_df = my_dataframe.to_pandas()

# Choose up to 5 ingredients
ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    # Create dataframe for nutrition information
    sf_df = pd.DataFrame()

    # Get nutrition information for each selected fruit
    for fruit_chosen in ingredients_list:

        # Find SEARCH_ON value for selected fruit
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Call SmoothieFroot API
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/"
            + search_on
        )

        # Only process successful responses
        if smoothiefroot_response.status_code == 200:

            smoothiefroot_response_json = (
                smoothiefroot_response.json()
            )

            fruit_df = pd.DataFrame(
                [smoothiefroot_response_json]
            )

            sf_df = pd.concat(
                [sf_df, fruit_df],
                ignore_index=True
            )

    # Display nutrition information
    if not sf_df.empty:
        st.subheader("Nutrition Information")
        st.dataframe(
            sf_df,
            use_container_width=True
        )

    # Create ingredients string
    # IMPORTANT: trailing space is required by the DORA grader
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # Insert order into Snowflake
    my_insert_stmt = """INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    # Submit order
    if st.button("Submit Order"):

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon="✅"
        )
