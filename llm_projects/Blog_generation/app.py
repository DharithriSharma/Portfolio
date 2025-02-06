import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Ensure your GROQ_API_KEY is set in the environment
if "GROQ_API_KEY" not in os.environ:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

# Function to get response from LLama 2 model
def getLLamaresponse(input_text, no_words, blog_style):
    # LLama2 model initialization
    llm = ChatGroq(
        temperature=0.01,
        model_name='llama3-8b-8192',
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Prompt Template
    template = """
        Write a blog for {blog_style} job profile for a topic {input_text}
        within {no_words} words.
    """
    
    prompt = PromptTemplate(
        input_variables=["blog_style", "input_text", 'no_words'],
        template=template
    )
    
    # Format the prompt
    formatted_prompt = prompt.format(blog_style=blog_style, input_text=input_text, no_words=no_words)

    # Create message object
    messages = [
        HumanMessage(content=formatted_prompt)
    ]
    
    # Generate the response
    response = llm(messages)
    
    # Extract and return the generated content
    return response.content

# Set the page configuration
st.set_page_config(
    page_title="Generate Blogs",
    page_icon='🤖',
    layout='centered',
    initial_sidebar_state='collapsed'
)

# Title of the Streamlit app
st.header("Generate Blogs 🤖")

# Input field for the blog topic
input_text = st.text_input("Enter the Blog Topic")

# Creating two columns for additional fields
col1, col2 = st.columns([5, 5])

with col1:
    no_words = st.text_input('Number of Words')

with col2:
    blog_style = st.selectbox(
        'Writing the blog for',
        ('Researchers', 'Data Scientist', 'Common People'),
        index=0
    )

# Button to generate the blog
submit = st.button("Generate")

# Display the generated blog content when the button is pressed
if submit:
    response = getLLamaresponse(input_text, no_words, blog_style)
    st.markdown(response)  # Display the generated content
