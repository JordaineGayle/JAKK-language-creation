import streamlit as st
from project_lexer_and_parser import main as process_code

# Set page layout to wide
st.set_page_config(layout="wide")

# Custom CSS to style the console area
st.markdown(
    """
    <style>
    .console {
        background-color: black;
        color: white;
        padding: 10px;
        border-radius: 5px;
        height: 335px;
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create columns for the layout
col1, col2 = st.columns([1, 2])  # Adjust the width ratios as needed

# Initialize output_result and console_output_str variables
output_result = ""
console_output_str = "<div class='console'>Waiting for compilation...</div>"

# Right column for Output and Console
with col2:
    st.title("OUTPUT")
    output_result = st.empty()
    output_result.text_area("", value="Hello World!", height=300, key="output_result", disabled=True)

    st.title("CONSOLE")
    console_output = st.empty()
    console_output.markdown(console_output_str, unsafe_allow_html=True)

# Left column for Input (IDE)
with col1:
    st.title("INPUT (IDE)")
    input_code = st.text_area("", height=745, key="input_code")

    if st.button("COMPILE"):
        # Process the input code
        console_output_str, final_result = process_code(input_code)

        # Update the console output
        console_output.markdown(f"<div class='console'>{console_output_str}</div>", unsafe_allow_html=True)

        # Display the final output result
        output_result.text_area("", value=f"Normal form: {final_result}", height=300, key="output_result_compiled", disabled=True)
