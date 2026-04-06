raise Exception("CANDIDATES FILE IS LOADED")
print("CANDIDATES FILE LOADED")
def render_candidates_page():
    import streamlit as st

    st.title("👥 Candidates Page")

    st.success("✅ FUNCTION IS RUNNING")

    st.write("If you can see this, routing is correct.")

    st.markdown("---")

    # Force something visible
    st.button("Test Button")

    st.write("End of page")