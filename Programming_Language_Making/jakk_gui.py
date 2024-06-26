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

# Function to process input code
def process_code(input_code):
    # Example: Simulate compilation and execution
    console_messages = []

    # Add initial console message
    console_messages.append("Compiling...\n")

    if "error" in input_code.lower():
        console_messages.append("Syntax error: detected in input code\n")
        output_result = ""
    else:
        # Example: Execute code (replace with actual execution logic)
        output_result = f"jakk >> '{input_code}'"
        console_messages.append("Compilation successful\n")

    return console_messages, output_result

# Create columns for the layout
col1, col2 = st.columns([1, 2])  # Adjust the width ratios as needed

# Initialize output_result variable
output_result = ""

# Left column for Input (IDE)
with col1:
    st.title("INPUT (IDE)")
    input_code = st.text_area("Input Code", height=745, key="input_code")

    if st.button("COMPILE"):
        # Process the input code
        console_messages, output_result = process_code(input_code)

        # Update console and output areas
        with st.expander("Console", expanded=True):
            st.markdown("<br>".join(console_messages), unsafe_allow_html=True)

# Right column for Output and Console
with col2:
    output_container = st.container()
    console_container = st.container()

    with output_container:
        st.title("OUTPUT")
        st.text_area("Output Result", value=output_result, height=300, key="output_result", disabled=True)

    with console_container:
        st.title("CONSOLE")
        console_output = st.empty()
        console_html = """
        <div class="console">
       
        </div>
        """
        console_output.markdown(console_html, unsafe_allow_html=True)

