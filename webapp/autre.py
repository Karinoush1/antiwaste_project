

####################################################################
#st.sidebar.download_button("Submit image", "fixed.png", "image/png")

"""with st.spinner(text='In progress'):
   time.sleep(5)
   st.sidebar.success('Done')"""

"""st.sidebar.error('Error message')
st.sidebar.warning('Warning message')
st.sidebar.info('Info message')
st.sidebar.success('Success message')"""

#st.balloons()
#st.snow()
#st.exception(e)
####################################################################






####################################################################
"""progress_text = "Your image is in the oven."
my_bar = st.sidebar.progress(0, text=progress_text)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1, text=progress_text)"""
####################################################################






####################################################################
"""
# widget ingredients
id = recipe['id']
query = f"https://api.spoonacular.com/recipes/{id}/ingredientWidget?apiKey=c135fe564b084d9bb1eedd248a56d637"
response = requests.get(query)
html_response = response.text

# Display the HTML widget in your Streamlit app
st.components.v1.html(html_response)
"""
####################################################################


# lien image
# st.write(recipe['image'])

# lien recette si existe dans le schema
#st.write(recipe['sourceUrl'])














