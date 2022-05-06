from re import I
import streamlit as st
import numpy as np
import pandas as pd
df = pd.DataFrame((100-1)*np.random.rand(100,6)+99)
st.dataframe(df)
st
