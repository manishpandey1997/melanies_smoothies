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

# Get fruit names and API search terms
fruit_data = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
).collect()

# Create lookup dictionary
fruit_lookup = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_data
}

# Choose up to 5 ingredients
ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    list(fruit_lookup.keys()),
    max_selections=5
)

if ingredients_list:

    # Get nutrition data from SmoothieFroot
    sf_df = pd.DataFrame()

    for fruit_chosen in ingredients_list:

        search_term = fruit_lookup[fruit_chosen]

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_term
        )

        if smoothiefroot_response.status_code == 200:

            smoothiefroot_response_json = smoothiefroot_response.json()

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
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

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
