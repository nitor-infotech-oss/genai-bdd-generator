# Example Streamlit app structure
import streamlit as st
from constants import KEY_FEATURES

def main():
    st.write('''# TestCase Generator''')
    st.markdown("""Innovative application which harnesses 
                    the power of artificial intelligence to 
                    streamline and optimize your testing processes.
    """)
    st.markdown("""
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(KEY_FEATURES)   
    with col2:
        st.image("aibot1.webp", width=250)


if __name__ == '__main__':
    main()


