import streamlit as st
from streamlit_echarts import st_echarts
from leaflesiondetector.vis_data_pipeline import diseases, pie_data, boxplot_data

st.title(":chart_with_upwards_trend: Visualize the data")

st.write("")

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
