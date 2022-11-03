import streamlit as st
from streamlit_chat import message
import chatbot_class as cs

st.set_page_config(
    page_title="Movie Recommender chatbot",
    page_icon=":robot:"
)
st.header("Movie Recommender chatbot")

extracted_keywords = []
chatbot_frame = cs.MovieRecommender(extracted_keywords = extracted_keywords)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def query():
    pass

def get_text():
    input_text = st.text_input("You: ","Hello, how are you?", key="input")
    return input_text 

user_input = get_text()
st.write(user_input)

if user_input:
    #We want to take in user's latest response
    st.session_state['past'].append(user_input)

    responses = chatbot_frame.get_input_respond_message_for_movie_recommender(user_input)
    print(responses)
    #Append generated session state with updated chat bubble
    for response in responses:
        st.session_state['generated'].append(response)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
