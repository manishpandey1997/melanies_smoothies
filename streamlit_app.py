# Import python packages
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

st.write("The name on Smoothie will be", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names and search values
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowpark dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()

# Multiselect uses the friendly fruit name
ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

if ingredients_list:

    sf_df = pd.DataFrame()

    for fruit_chosen in ingredients_list:

        # Find the API search value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            "."
        )

        # Call SmoothieFroot API
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/"
            + search_on.lower()
        )

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
    st.dataframe(
        sf_df,
        use_container_width=True
    )

    # Create ingredients string
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # Insert order
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
