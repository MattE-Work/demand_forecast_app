import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt 
import altair as alt

def detect_outliers(df, method='statistical', threshold=3):
    """
    Detect outliers in a DataFrame.

    Parameters:
    df : pandas.DataFrame
        DataFrame with a 'y' column containing numerical data.
    method : str
        Method to use for detecting outliers. Options are 'statistical' and 'iqr'.
    threshold : float
        For 'statistical', this is the number of standard deviations from the mean.
        For 'iqr', this is the multiplier for the IQR to define outliers.

    Returns:
    outliers : pandas.DataFrame
        DataFrame containing the detected outliers.
    """
    if method == 'statistical':
        mean_y = np.mean(df['y'])
        std_y = np.std(df['y'])
        outliers = df[(df['y'] > mean_y + threshold * std_y) | (df['y'] < mean_y - threshold * std_y)]
    elif method == 'iqr':
        Q1 = df['y'].quantile(0.25)
        Q3 = df['y'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = df[(df['y'] < lower_bound) | (df['y'] > upper_bound)]
    else:
        raise ValueError("Unsupported method. Use 'statistical' or 'iqr'.")
    
    return outliers


#------------------------

def find_missing_dates(df, date_column='ds', unit_of_measurement='day'):
    # Map the unit of measurement to pandas frequency string
    unit_to_freq = {
        'year': 'Y',    # Annual
        'quarter': 'Q', # Quarterly
        'month': 'M',   # Monthly
        'week': 'W',    # Weekly
        'day': 'D',     # Daily
        'hour': 'H',    # Hourly
        'minute': 'T',  # Minutely
        'second': 'S'   # Secondly
    }
    
    # Get the frequency code from the dictionary based on the user's selection
    frequency = unit_to_freq.get(unit_of_measurement, 'D')  # Default to daily if not found

    # Generate the full range of dates/times based on the specified frequency
    full_range = pd.date_range(start=df[date_column].min(), end=df[date_column].max(), freq=frequency)
    
    # Identify the missing dates/times
    missing_dates = full_range.difference(df[date_column])
    
    return missing_dates


#------------------------
"""
def interpret_outliers(df, outliers, datetime_field, activity_count_field, interpolation_preference, unit_of_measurement):
    st.write(f"Original data row count: {df.shape[0]}")
    
    # Sort the DataFrame by the datetime field
    df = df.sort_values(by=datetime_field)
    
    # Ensure the datetime field is the index for time series operations
    #df.set_index(datetime_field, inplace=True)
    
    # Identify and fill missing dates based on the unit of measurement
    #unit_of_measurement = st.selectbox('Select the unit of measurement for missing dates', 
    #                                   ['year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'], 
    #                                   index=3)
    missing_dates = find_missing_dates(df.reset_index(), datetime_field, unit_of_measurement)
    
    # Fill the DataFrame with missing dates as NaN
    df = df.reindex(df.index.union(missing_dates))

    #extract the index values of any identified outlier values
    outlier_indices = outliers.index
    #use those index values to isolate the outlier rows in the main df
    outlier_rows_in_main_df = df.loc[outlier_indices]
    st.write('outlier_rows_in_main_df')
    st.write(outlier_rows_in_main_df)
    
    #change the outlier values in df to None - so that these can then be replaced with interpolated values. 
    df.loc[outlier_indices, activity_count_field] = None

    #check the above has worked
    st.write('outlier_indices')
    st.write(outlier_indices)
    st.write('outlier_rows_in_main_df')
    st.write(outlier_rows_in_main_df)
    st.write('df with outliers replaced to nan')
    st.write(df.loc[outlier_indices])

    # Number of outliers
    
    num_outliers = len(outliers)
    outlier_summary_text = f"Detected {num_outliers} outliers in the data. "
    if num_outliers >0:
        outlier_summary_text += 'The identified outliers can be reviewed in the table below.'
        st.write(outlier_summary_text)
        st.dataframe(outliers)
    else:
        st.write(outlier_summary_text)
    

    # Tabs for organized review
    tab1, tab2 = st.tabs(["Visualization of Data", "Processed Data"])
    
    with tab1:
        # Reset index to use 'ds' as a column in Altair
        df_for_viz = df.reset_index()
        df_for_viz['Type'] = 'Regular'
        outliers_for_viz = outliers.reset_index()
        outliers_for_viz['Type'] = 'Outlier'
        combined = pd.concat([df_for_viz, outliers_for_viz], ignore_index=True)
        
        st.write(combined)
        
        # Altair plot with specified colors for each type and tooltip including date
        chart = alt.Chart(combined).mark_circle(size=60).encode(
            x=alt.X(datetime_field, title=datetime_field),
            y=alt.Y(activity_count_field, title=activity_count_field),
            color=alt.Color('Type', scale=alt.Scale(domain=['Regular', 'Outlier'], range=['lightgray', 'green']), legend=alt.Legend(title="Data Type")),
            tooltip=[datetime_field, activity_count_field]
        ).interactive()  # Enable zoom and pan
        
        st.altair_chart(chart, use_container_width=True)
    
    with tab2:
        # Replace outliers with NaN to maintain the structure
        df.loc[outliers.index, activity_count_field] = np.nan
        
        # Interpolate missing data based on user's preference
        df[activity_count_field] = df[activity_count_field].interpolate(method=interpolation_preference)
        
        st.write(f"Outliers processed and missing data handled using {interpolation_preference} method.")
        df.reset_index(inplace=True)  # Ensure consistent structure for display
        st.dataframe(df)
        st.write(f"Processed data shape: {df.shape}")
"""
#------------------------------------------

def process_and_visualize_outliers(
    df, 
    outliers, 
    datetime_field, 
    activity_count_field, 
    interpolation_preference, 
    interpolation_preference_text_string, 
    unit_of_measurement_parameter,
    polynomial_degree_value
    ):

    st.write(f"Original data row count: {df.shape[0]}")
    
    
    
    # Correctly mark the identified outlier rows as 'Outlier'
    df['Type'] = 'Regular'
    df.loc[outliers.index, 'Type'] = 'Outlier'
    
    # Create a deep copy of the original DataFrame for visualization to avoid altering the original data
    df_for_viz = df.copy(deep=True)

    # Initially mark all data as 'Regular'
    #df_for_viz['Type'] = 'Regular'
    
    # Correctly mark the identified outlier rows as 'Outlier'
    #df_for_viz.loc[outliers.index, 'Type'] = 'Outlier'

    
    # Tabs for organized review
    tab1, tab2 = st.tabs(["Visualization of Data", "Processed Data - interpolation applied"])
       
    with tab1:
        # Altair plot with specified colors for each type and tooltip including date
        chart = alt.Chart(df_for_viz.reset_index()).mark_circle(size=60).encode(
            x=alt.X(datetime_field, title=datetime_field),
            y=alt.Y(activity_count_field, title=activity_count_field),
            color=alt.Color('Type', scale=alt.Scale(domain=['Regular', 'Outlier'], range=['lightgray', 'green']), legend=alt.Legend(title="Data Type")),
            tooltip=[datetime_field, activity_count_field]
        ).interactive()  # Enable zoom and pan
        
        st.altair_chart(chart, use_container_width=True)
    
    with tab2:
        num_outliers = len(outliers)
        if num_outliers > 0:
            st.write('Outliers present. Replaced using chosen interpolation method, along with any missing values.')
        else:
            st.write('Outliers not present. Any missing values replaced using interpolation method chosen.')
        # Processing DataFrame: Replace outlier values with None
        df.loc[outliers.index, activity_count_field] = None
        
        with st.expander('Click to view identified outliers'):

            num_outliers = len(outliers)
            outlier_summary_text = f"Detected {num_outliers} outliers in the data."
            if num_outliers > 0:
                outlier_summary_text += f' The identified outliers can be reviewed in the table below. You should check your source data to validate the reasons behind the outliers. By default, this app removes outliers, replacing them using your chosen method ({interpolation_preference_text_string})'
                st.write(outlier_summary_text)
                st.dataframe(outliers, use_container_width=True)
            else:
                st.write(outlier_summary_text)

            #st.write('DataFrame after replacing outliers with None (ready for interpolation):')
            st.dataframe(df.loc[outliers.index])

        #logic to apply the user-chosen method for interpolation for outliers
        # Check and apply the appropriate interpolation method based on user preference
        
        #linear interpolation
        if interpolation_preference == 'linear':
            # Apply linear interpolation to the specified column
            df[activity_count_field] = df[activity_count_field].interpolate(method='linear')
            #st.write(f"Outliers processed and missing data handled using linear interpolation method.")
        
        #time series interpolation
        elif interpolation_preference == 'time':
            # Remember the original index to restore it later
            original_index = df.index
            # Ensure datetime field is used as index and in datetime format for time series interpolation
            df.index = pd.to_datetime(df[datetime_field])
            df = df.reindex(pd.date_range(start=df.index.min(), end=df.index.max(), freq=unit_of_measurement_parameter))
            # Apply time series interpolation
            df[activity_count_field] = df[activity_count_field].interpolate(method='time')
            # Restore the original index
            df.reset_index(inplace=True)
            df.set_index(original_index, inplace=True)
            df.drop('index', axis=1, inplace=True)

        #Polynomial Interpolation 
        elif interpolation_preference == 'polynomial':
            not_null_mask = df[activity_count_field].notnull()
            coefficients = np.polyfit(df[datetime_field][not_null_mask].index, 
                                        df[activity_count_field][not_null_mask], deg=polynomial_degree_value)
            poly = np.poly1d(coefficients)
            
            # Fill NaN values using the polynomial model
            nan_indices = df[activity_count_field].index[df[activity_count_field].isnull()]
            df.loc[nan_indices, activity_count_field] = poly(nan_indices)
            
            #st.write(f"Outliers processed and missing data handled using polynomial fit as an alternative to spline.")

        #Forward fill Interpolation 
        elif interpolation_preference == 'ffill':
            df[activity_count_field] = df[activity_count_field].interpolate(method='ffill')
            #st.write(f"Outliers processed and missing data handled using forward fill interpolation method.")

        #Backward fill Interpolation 
        elif interpolation_preference == 'bfill':
            df[activity_count_field] = df[activity_count_field].interpolate(method='bfill')
            #st.write(f"Outliers processed and missing data handled using backward fill interpolation method.")

        else:
            st.write("Unsupported interpolation method selected.")

        with st.expander('Click to view df with outliers and missing values replaced'):
            # Display the DataFrame after interpolation
            st.write("DataFrame after interpolation:")
            st.dataframe(df, use_container_width=True)

    return df