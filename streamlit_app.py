# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie!🥤")

st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on Smoothie will be", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options from Snowflake
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col("FRUIT_NAME"))

# Choose up to 5 ingredients
ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:

    # Get nutrition information for each selected fruit
    sf_df = pd.DataFrame()

    for fruit_chosen in ingredients_list:

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen.lower()
        )

        smoothiefroot_response_json = smoothiefroot_response.json()

        fruit_df = pd.DataFrame([smoothiefroot_response_json])

        sf_df = pd.concat(
            [sf_df, fruit_df],
            ignore_index=True
        )

    # Display nutrition information
    st.dataframe(sf_df, use_container_width=True)

    # Create ingredients string
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Insert order into Snowflake
    my_insert_stmt = """INSERT INTO smoothies.public.orders
                    (ingredients, name_on_order)
                    VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon="✅"
        )
