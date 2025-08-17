# app.py

import streamlit as st
import pandas as pd
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Policy Feedback Simulator",
    page_icon="�",
    layout="wide"
)

# --- API Configuration ---
API_URL = "http://127.0.0.1:8000"

# --- Example Policies ---
EXAMPLE_POLICIES = {
    "Return to Office": "Effective next quarter, all employees will be required to work from the physical office a minimum of 3 days per week to enhance collaboration and company culture.",
    "AI Tool Usage": "All employees are now required to log the use of any generative AI tools for work-related tasks in a central repository to ensure compliance and track productivity impacts.",
    "Performance Review Change": "The annual performance review process is being replaced with a quarterly review cycle, focusing on continuous feedback and goal setting."
}

# --- Helper Functions for Visualization ---

def generate_wordcloud(df: pd.DataFrame):
    """
    Generates and displays a word cloud from the 'comment' column of the DataFrame.
    Filters out any rows where the sentiment is 'error' to avoid plotting error messages.
    """
    # Combine all valid comments into a single string.
    comments = df[df['comment'].notna() & (df['sentiment'] != 'error')]['comment']
    text = ' '.join(comments)
    
    # If there's no text, display a warning instead of an empty plot.
    if not text.strip():
        st.warning("No comments available to generate a word cloud.")
        return

    # Create the word cloud object with specified dimensions and appearance.
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis'  # A visually appealing color scheme.
    ).generate(text)
    
    # Use matplotlib to display the generated image.
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off') # Hide the axes for a cleaner look.
    st.pyplot(fig)

def plot_pie_chart(df: pd.DataFrame):
    """
    Generates and displays a pie chart for the sentiment distribution.
    """
    sentiment_counts = df['sentiment'].value_counts()
    
    if sentiment_counts.empty:
        st.warning("No sentiment data available to plot.")
        return
        
    # Create the pie chart.
    fig, ax = plt.subplots()
    ax.pie(
        sentiment_counts, 
        labels=sentiment_counts.index, 
        autopct='%1.1f%%', # Format percentages to one decimal place.
        startangle=90,
        # Define colors for consistency.
        colors=['#66b3ff', '#ff9999', '#99ff99', '#c2c2c2'] 
    )
    ax.axis('equal')  # Ensures the pie chart is a perfect circle.
    st.pyplot(fig)

# --- Main Application UI ---

st.title("HR Policy Feedback Simulator 🤖")
st.markdown("Enter any company policy below to simulate employee reactions and visualize the feedback. You can also load an example from the sidebar.")

# Use session state to remember the text area content across reruns.
if 'policy_text_input' not in st.session_state:
    st.session_state.policy_text_input = EXAMPLE_POLICIES["Return to Office"]

# --- Sidebar for Loading Examples ---
st.sidebar.title("Policy Examples")
st.sidebar.markdown("Click a button to load an example policy into the text area.")
for name, text in EXAMPLE_POLICIES.items():
    if st.sidebar.button(name):
        st.session_state.policy_text_input = text
        # A small delay to give feedback that the button was clicked.
        time.sleep(0.1) 
        st.rerun()

# --- Main Policy Input Area ---
policy_input = st.text_area(
    "Enter the policy text here:",
    height=150,
    key="policy_text_input", # Link the text area to the session state variable.
    placeholder="e.g., All employees will receive a monthly stipend for wellness activities."
)

# --- Simulation Trigger ---
if st.button("🚀 Run Simulation", type="primary"):
    # Validate that the input is not empty.
    if policy_input and policy_input.strip():
        # The 'with' statement shows a spinner while the code inside it runs.
        with st.spinner("Simulating feedback... This may take a moment."):
            try:
                # Prepare the data payload for the POST request.
                payload = {"policy_text": policy_input}
                # Make the API call to the FastAPI backend.
                response = requests.post(f"{API_URL}/run-simulation/", json=payload, timeout=180)
                # Raise an HTTPError for bad responses (4xx or 5xx).
                response.raise_for_status()
                
                # Store results in session state to persist them.
                result_data = response.json()
                st.session_state.results_df = pd.DataFrame(result_data['data'])
                st.session_state.submitted_policy = result_data['policy_text']

            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Could not connect to the API at {API_URL}. Please ensure the backend server is running.")
            except requests.exceptions.RequestException as e:
                st.error(f"An API error occurred: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a policy text before running the simulation.")

# --- Display Results ---
# This section only runs if simulation results are present in the session state.
if 'results_df' in st.session_state:
    st.markdown("---")
    st.header("Simulation Results")
    
    df = st.session_state.results_df
    
    st.subheader("Policy Analyzed")
    # Display the policy that was submitted for the simulation.
    st.info(st.session_state.submitted_policy)

    # Use columns to organize visualizations side-by-side.
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sentiment Distribution")
        plot_pie_chart(df)
        
    with col2:
        st.subheader("Common Themes in Comments")
        generate_wordcloud(df)
    
    st.subheader("Detailed Feedback per Employee")
    # Display the raw data in a searchable, sortable table.
    st.dataframe(df[['employee_id', 'position', 'mbti_type', 'sentiment', 'comment']])