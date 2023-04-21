import streamlit as st

if len(st.session_state["leaves"].leaves) == 0 or "leaves" not in st.session_state:
    st.warning("Please upload an image set first")
    st.stop()

diseases = {}
boxplot_data = [[]]

try:
    for leaf in st.session_state["leaves"].leaves:
        disease_name, leaf_number, _ = leaf.name.split("_")
        diseases[f"{disease_name}"] = diseases.get(
            disease_name, {"count": 0, "measurements": [], "leaves": {}}
        )
        diseases[disease_name]["count"] += 1
        diseases[disease_name]["measurements"].append(leaf.lesion_area_percentage)

    pie_data = [{"value": v["count"], "name": k} for k, v in diseases.items()]
    boxplot_data = [v["measurements"] for v in diseases.values()]
except:
    st.markdown(
        """
    #### Please upload files with the following naming convention:
    `<disease_name>_<leaf_number>.<file_extension>`
    """
    )
    st.stop()
