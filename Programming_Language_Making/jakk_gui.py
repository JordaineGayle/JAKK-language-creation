import streamlit as st

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

# Left column for Input (IDE)
with col1:
    st.title("INPUT (IDE)")
    input_code = st.text_area("Input Code", height=745, key="input_code")

# Right column for Output and Console
with col2:
    output_container = st.container()
    console_container = st.container()

    with output_container:
        st.title("OUTPUT")
        output_result = st.text_area("Output Result", height=300, key="output_result")

    with console_container:
        st.title("CONSOLE")
        console_output = st.empty()
        console_html = """
        <div class="console">
       
        </div>
        """
        console_output.markdown(console_html, unsafe_allow_html=True)

# Example of processing the input code and updating the output and console areas
if st.button("COMPILE"):
    # Example: Just echo the input code to output and console
    output_result = input_code
    console_output_str = "<div class='console'>compiling...<br>"
    if "error" in input_code:
        console_output_str += "<span style='color: red;'>syntax error: detected in input code</span><br>"
    else:
        console_output_str += "<span style='color: green;'>compilation successful</span><br>"
    console_output_str += "</div>"

    # Update the text areas with the results
    st.session_state.output_result = output_result
    console_output.markdown(console_output_str, unsafe_allow_html=True)
