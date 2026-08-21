# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f"Customize Your Smoothie!🥤")

st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on Smoothie will be", name_on_order)

session = get_active_session()

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

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    my_insert_stmt = """INSERT INTO smoothies.public.orders
                    (ingredients, name_on_order)
                    VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered!',
            icon="✅"
        )
