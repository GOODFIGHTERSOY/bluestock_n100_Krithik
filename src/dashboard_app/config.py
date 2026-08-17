import streamlit as st


# =====================================================
# PAGE CONFIGURATION
# =====================================================

def configure_page():

    st.set_page_config(
        page_title="Bluestock N100 Analytics",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
<style>

/* =====================================================
   Hide Streamlit Header
===================================================== */

header[data-testid="stHeader"]{
    display:none;
}

[data-testid="stToolbar"]{
    display:none;
}

[data-testid="stDecoration"]{
    display:none;
}

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}


/* =====================================================
   Main Page
===================================================== */

.stApp{
    background:#FFFFFF;
}


/* =====================================================
   Text
===================================================== */

html, body, p, span, div, label{
    color:#000000 !important;
}


/* =====================================================
   Sidebar
===================================================== */

section[data-testid="stSidebar"]{
    background:#012970;
}

section[data-testid="stSidebar"] *{
    color:white !important;
}


/* =====================================================
   Headings
===================================================== */

h1,h2,h3,h4,h5,h6{
    color:#000000 !important;
    font-weight:700;
}


/* =====================================================
   Buttons
===================================================== */

.stButton>button{

    background:#6F42C1;
    color:white;
    border:none;
    border-radius:10px;
    font-weight:600;
    padding:10px 20px;

}

.stButton>button:hover{

    background:#F05537;
    color:white;

}


/* =====================================================
   Metric Cards
===================================================== */

div[data-testid="stMetric"]{

    background:white;

    border-left:6px solid #F05537;

    border-radius:12px;

    padding:20px;

    box-shadow:0px 4px 15px rgba(0,0,0,.08);

}

div[data-testid="stMetricLabel"]{

    color:#012970 !important;

    font-weight:700;

}

div[data-testid="stMetricValue"]{

    color:#000000 !important;

    font-size:32px;

}


/* =====================================================
   Dataframes
===================================================== */

[data-testid="stDataFrame"]{

    border-radius:12px;

    border:2px solid #012970;

}


/* =====================================================
   Selectbox (Closed)
===================================================== */

div[data-baseweb="select"] > div{

    background:white !important;

    color:black !important;

    border:2px solid #F05537 !important;

    border-radius:10px;

}

div[data-baseweb="select"] span{

    color:black !important;

}


/* =====================================================
   Inputs
===================================================== */

.stTextInput input{

    background:white !important;

    color:black !important;

}

.stNumberInput input{

    background:white !important;

    color:black !important;

}


/* =====================================================
   Slider
===================================================== */

.stSlider{

    color:#012970;

}


/* =====================================================
   Tabs
===================================================== */

button[data-baseweb="tab"]{

    color:#012970;

    font-weight:600;

}

button[data-baseweb="tab"][aria-selected="true"]{

    color:#6F42C1;

    border-bottom:4px solid #F05537;

}


/* =====================================================
   Expanders
===================================================== */

details{

    border-radius:10px;

}


/* =====================================================
   Success / Warning
===================================================== */

[data-testid="stAlert"]{

    border-radius:10px;

}


/* =====================================================
   Hyperlinks
===================================================== */

a{

    color:#6F42C1;

}

a:hover{

    color:#F05537;

}

</style>
""",
        unsafe_allow_html=True,
    )


# =====================================================
# SIDEBAR
# =====================================================

def sidebar():

    with st.sidebar:

        st.markdown(
            """
# 📈 Bluestock N100
### Financial Analytics Platform
"""
        )

        st.divider()

        st.markdown(
            """
### Navigation

Use the pages above to explore:

- 📊 Dashboard
- 🏢 Company Analysis
- 🔍 Stock Screener
- 📈 Peer Comparison
- 🏆 Rankings
"""
        )

        st.divider()

        st.markdown(
            """
### Technology Stack

- 🐍 Python
- 📊 Streamlit
- 📈 Plotly
- 🗄 SQLite
- 📑 Pandas
- 📚 OpenPyXL
"""
        )

        st.divider()

        st.markdown(
            """
**Theme**

🔷 Midnight Blue  
🟣 Fuchsia Blue  
🟧 Flamingo
"""
        )

        st.divider()

       

        st.caption("Developed by Krithik")