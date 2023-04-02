import streamlit as st
from streamlit_echarts import st_echarts

st.title(":chart_with_upwards_trend: Visualize the data")

diseases = {}
boxplot_data = [[]]

for leaf in st.session_state["leaves"].leaves:
    diseases[f"{leaf.name.split('_')[0]}"] = diseases.get(
        f"{leaf.name.split('_')[0]}", {"count": 0, "measurements": []}
    )
    diseases[f"{leaf.name.split('_')[0]}"]["count"] += 1
    diseases[f"{leaf.name.split('_')[0]}"]["measurements"].append(
        leaf.lesion_area_percentage
    )

pie_data = [{"value": v["count"], "name": k} for k, v in diseases.items()]
boxplot_data = [v["measurements"] for v in diseases.values()]

piechart = {
    "title": {
        "text": "Disease types",
        "subtext": "Shows all the types of diseases covered in image set",
        "left": "center",
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

subtext = "\n".join(
    ["Disease " + str(i) + ": " + k for i, k in enumerate(diseases.keys())]
)

boxplot = {
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
