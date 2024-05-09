import streamlit as st
import pandas as pd
import numpy as np

def render_warning_aggregate_activity_count():
    st.subheader(':red[Warning!]⚠️')
    st.write(""":red[It is **your** responsibility to ensure the file you use 
    contains **only** aggregate counts of activity per time unit (e.g. min, hour, day, week, etc.), and **no other data**. 
    In choosing this option you are confirming you are doing so in accordance 
    with your organisation's Information Governance policies and all legal duties. 
    ]""")
    st.write(""":red[An example illustrating the required structure / content of the file is 
    provided below for your reference.]""")
    
    with st.container():
        # Seed for reproducibility
        np.random.seed(42)

        # Generate sequential dates
        dates = pd.date_range(start='2023-01-01', periods=3, freq='D')

        # Generate random activity counts between 25 and 100
        activity_counts = np.random.randint(25, 101, size=3)

        # Create the DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Activity Count': activity_counts
        })

        # Append a new row with both columns set to 'etc.'
        df.loc[len(df)] = ['etc.', 'etc.']
        
        st.dataframe(df)

