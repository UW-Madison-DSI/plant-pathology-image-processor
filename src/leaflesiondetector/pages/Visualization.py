import streamlit as st
from streamlit_echarts import st_echarts

st.title(":chart_with_upwards_trend: Visualize the data")

st.markdown(
    """
#### For the below to work, please upload files with the following naming convention:
`<disease_name>_<leaf_number>.<file_extension>`
"""
)
st.write("")

if len(st.session_state["leaves"].leaves) == 0 or "leaves" not in st.session_state:
    st.warning("Please upload an image set first")
    st.stop()

diseases = {}
boxplot_data = [[]]

for leaf in st.session_state["leaves"].leaves:
    disease_name = leaf.name.split("_")[0]
    leaf_number = leaf.name.split("_")[1]
    # day = leaf.name.split('_')[3]
    diseases[f"{disease_name}"] = diseases.get(
        f"{disease_name}", {"count": 0, "measurements": [], "leaves": {}}
    )
    diseases[f"{disease_name}"]["count"] += 1
    diseases[f"{disease_name}"]["measurements"].append(leaf.lesion_area_percentage)
    # diseases[f"{disease_name}"]["leaves"][disease_name + leaf_number] = diseases[f"{disease_name}"]["leaves"].get(disease_name + leaf_number, {"name": f"{disease_name+leaf_number}","type": "line","stack": "Total","data": [],})["data"].insert(int(day-1),leaf.lesion_area_percentage)

pie_data = [{"value": v["count"], "name": k} for k, v in diseases.items()]

piechart = {
    "title": {
        "text": "Disease types",
        "subtext": "Shows all the types of diseases covered in image set",
        "left": "center",
    },
    "toolbox": {
        "show": "true",
        "feature": {
            "saveAsImage": {"title": "Save"},
        },
    },
    "tooltip": {"trigger": "item"},
    "legend": {
        "orient": "vertical",
        "left": "left",
    },
    "series": [
        {
            "name": "Disease",
            "type": "pie",
            "radius": "50%",
            "data": pie_data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                }
            },
        }
    ],
}
st_echarts(
    options=piechart,
    height="600px",
)

boxplot_data = [v["measurements"] for v in diseases.values()]

subtext = ", ".join(
    ["Disease " + str(i) + ": " + k for i, k in enumerate(diseases.keys())]
)

boxplot = {
    "toolbox": {
        "show": "true",
        "feature": {
            "saveAsImage": {"title": "Save"},
        },
    },
    "title": [
        {
            "text": "Boxplot of lesion area calculations",
            "subtext": subtext,
            "left": "center",
        },
        {
            "text": "Upper: Q3 + 1.5 * IQR \nLower: Q1 - 1.5 * IQR",
            "borderColor": "#999",
            "borderWidth": 0.5,
            "textStyle": {"fontWeight": "light", "fontSize": 12, "lineHeight": 20},
            "left": "10%",
            "top": "90%",
        },
    ],
    "dataset": [
        {"source": boxplot_data},
        {
            "transform": {
                "type": "boxplot",
                "config": {"itemNameFormatter": "Disease {value}"},
            }
        },
        {"fromDatasetIndex": 1, "fromTransformResult": 1},
    ],
    "tooltip": {"trigger": "item", "axisPointer": {"type": "shadow"}},
    "grid": {"left": "10%", "right": "10%", "bottom": "15%"},
    "xAxis": {
        "type": "category",
        "boundaryGap": True,
        "nameGap": 30,
        "splitArea": {"show": False},
        "splitLine": {"show": False},
    },
    "yAxis": {
        "type": "value",
        "name": "% lesion area",
        "splitArea": {"show": True},
    },
    "series": [
        {"name": "Boxplot", "type": "boxplot", "datasetIndex": 1},
        {"name": "Outlier", "type": "scatter", "datasetIndex": 2},
    ],
}
st_echarts(boxplot, height="500px")
