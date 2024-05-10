import streamlit as st
from functions import create_dummy_data
import numpy as np
import pandas as pd

def render_sidebar():
    dict_params = {}

    #set up the sidebar for parameter control
    with st.sidebar:
        st.subheader('Select data source')
        with st.expander('File upload'):
            use_dummy_data = st.radio(label='Use test data to preview functionality?',
            options=['Yes', 'No'], horizontal=True, index=0)
            
            if use_dummy_data == 'Yes':
                df = create_dummy_data.create_data()
            else:
                df_path = st.file_uploader(label='Select file')
                df = pd.read_csv(df_path)
                

        #provide column names
        with st.popover('Set columns'):
            datetime_field = st.selectbox(label='Select the date/time field', options=list(df.columns))
            activity_count_field = st.selectbox(label='Select the field containing activity counts', options=list(df.columns))
            unit_of_measurement = st.selectbox(label='What is the unit of measurement', options=['year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'], index=4)

            dict_unit_text_to_parameter_term = {
                'year': 'Y', #year end
                'quarter': 'Q', #quarter end
                'month': 'M', #month end
                'week': 'W-MON', #weekly, anchored to Mondays
                'day': 'D', #daily
                'hour': 'H', #hourly
                'minute': 'T', #minute
                'second': 'S' #seconds
            }

        # Appointment Types and DNA Rate
        st.subheader('Demand Configuration')
        num_appts_per_patient = st.radio(
            label="Type of Service",
            options=["Single appt per patient", "Multiple appt per patient"],
            horizontal=True
        )
        dict_params['num_appts_per_patient'] = num_appts_per_patient

        # Multiple Appointments per Demand Unit
        if num_appts_per_patient == "Multiple appt per patient":
            
            with st.popover('Appt details'):
                average_appointments_per_unit = st.number_input('Average no. appts. per patient', min_value=1, value=3)
                #average_interval_between_appts = st.number_input(f'Average no. {unit_of_measurement}s between appts.', min_value=1, value=3)

                dict_params['average_appointments_per_pt'] = average_appointments_per_unit
                #dict_params['average_interval_between_appts'] = average_interval_between_appts
        else:
            dict_params['average_appointments_per_unit'] = 1  # Default for single appointment

        # DNA Rate and Policy
        with st.popover(label='DNA parameters'):
            dna_rate = st.slider('Typical DNA %', min_value=1, max_value=99, value=5, step=1)
            dna_policy_used = st.radio(label='Is a DNA policy used?', options=['Yes', 'No'], horizontal=True)
            if dna_policy_used == 'Yes':
                max_num_dnas = st.select_slider(
                    'No. of DNAs before discharge',
                    options=[1,2,3,4,5],
                    help="Set how many DNAs can occur before a patient is discharged from the service."
                )
                dict_params['max_num_dnas'] = int(max_num_dnas)
            else:
                dict_params['max_num_dnas'] = 'NA'
            

            dict_params['dna_rate'] = dna_rate
            dict_params['dna_policy_used'] = dna_policy_used



        st.subheader('Handle outliers')
        with st.popover(label='Detecting outliers'):
            outlier_detection_method = st.radio(
                label='How should the model detect outliers?',
                options=['iqr', 'statistical'],
                help="""
                **The IQR method:**\n
                The IQR method identifies outliers by defining an acceptable range 
                based on the interquartile range (IQR). Outliers are those data points 
                that fall outside the range [Q1 - 1.5 * IQR, Q3 + 1.5 * IQR], where 
                Q1 and Q3 are the 25th and 75th percentiles, respectively. 
                This method is robust against skewed data and is ideal for distributions 
                not bound by normality.\n
                **The statistical method:**\n
                The statistical method detects outliers by measuring how far data 
                points deviate from the mean, in terms of standard deviations. 
                Points lying more than a certain threshold (commonly 3, as is the case in this app) standard 
                deviations away from the mean are considered outliers. This approach 
                is best suited for data that approximates a normal distribution but 
                can be influenced by extremely skewed data or heavy tails.
                """,
                horizontal=True
                )

            outlier_detection_method_threshold = [3 if outlier_detection_method=='statistical' else 1.5][0]

        with st.popover(label='Handling missing data', disabled=False):
            outlier_handling_method = st.radio(
            label='How should the model handle outliers or missing data, if detected?',
            options=[
                'Linear interpolation', #linear
                'Time series interpolation', #time
                'Polynomial interpolation', #polynomial
                #'Spline interpolation', #spline
                'Forward fill the previous value', #ffill
                'Backward fill the next value', #bfill
                #'Remove the outliers without replacement' #delete the rows
                ],
                help="""
                **Linear Interpolation**
                Linear interpolation is a simple way to fill missing data by drawing straight lines between known data points. This method assumes that the change between two points is consistent and straightforward. It is most effective when the data changes at a steady rate between observations.

                **Time Series Interpolation**
                Time series interpolation considers the time gaps between data points to fill missing values. This method is particularly useful when data points are recorded over time and you want to maintain the integrity of time-related trends. It adjusts for the fact that time intervals may influence how data should be interpolated.

                **Polynomial Interpolation**
                Polynomial interpolation uses polynomial equations to estimate missing values. This method fits a smooth curve that goes through or near the known data points. It is more complex than linear interpolation and can better handle varying rates of change in the data, but it requires careful selection of the polynomial degree to avoid overfitting.

                **Forward Fill (ffill)**
                Forward fill is a method where missing values are replaced with the last known value before the gap. This approach is straightforward and useful when it is reasonable to assume that data remains unchanged until a new measurement is taken.

                **Backward Fill (bfill)**
                Backward fill works by filling missing values with the next known value after the gap. This method is used when it is expected that the upcoming data point is a continuation of the missing data, providing a simple way to ensure that gaps are filled with the most immediately relevant data.

                    """
            )

            if outlier_handling_method == 'Polynomial interpolation':
                polynomial_degree_value = st.slider(label='Set polynomial degree value', min_value=1, max_value=10, value=3)
                dict_params['polynomial_degree_value'] = polynomial_degree_value
            else:
                dict_params['polynomial_degree_value'] = 'NA'

        st.subheader('Set demand theshold')
        demand_percentile = st.slider(
            label='What percentage of the time do you want to have enough capacity?',
            min_value=1, max_value=100, step=1, value=85,
            help="""This requires a balance, and will be influenced by the consistency 
            and urgency of the activity you are planning for - the more variable or 
            urgent / critical, the higher the percentage. Remember, demand will be 
            unlikely to exactly fall at the threshold you set. You could of course set 
            the threshold to 100% but then this will be wasteful most of the time."""
        ) / 100

        # Dictionary to set baseline horizon based on unit of measurement
        baseline_horizon = {
            'year': 2,   # Forecast 2 additional years by default
            'quarter': 4,  # Forecast 4 additional quarters (1 year) by default
            'month': 12,  # Forecast 12 additional months (1 year) by default
            'week': 52,  # Forecast 52 weeks (1 year) by default
            'day': 30,   # Forecast 30 days (1 month) by default
            'hour': 24 * 7,  # Forecast 7 days (168 hours) by default
            'minute': 60 * 24,  # Forecast 1 day (1440 minutes) by default
            'second': 60 * 60 * 24,  # Forecast 1 day (86400 seconds) by default
        }

        # Adjust the default forecast horizon based on the number of records in the data
        num_records = len(df)
        if num_records < 100:
            scale_factor = 0.5  # Scale down if less data
        elif num_records > 1000:
            scale_factor = 2  # Scale up if more data
        else:
            scale_factor = 1  # Use default if moderate amount of data

        st.subheader('Set forecast horizon')
        forecast_horizon = st.number_input(label=f"""How many :green[**{unit_of_measurement}s**] 
        should the forecast consist of?""", 
        help="The value entered here needs to align to the source data. It defines how far into the future the forecast will be.",
        value=int(baseline_horizon[unit_of_measurement] * scale_factor))

        st.subheader('Confidence limits')
        with st.popover('Set confidence interval'):
            confidence_limit = st.radio(label='Set the confidence interval for the model', 
            options=['90%', '95%', '99%'], 
            horizontal=True,
            index=1)

            dict_confidence_interval_decimal = {
                '90%': 0.9, 
                '95%': 0.95, 
                '99%': 0.99
                }



    dict_interpolation_parameter = {
        'Linear interpolation': 'linear',
        'Time series interpolation': 'time',
        'Polynomial interpolation': 'polynomial',
        'Spline interpolation': 'spline',
        'Forward fill the previous value': 'ffill',
        'Backward fill the next value': 'bfill',
        'Remove the outliers without replacement': 'delete rows'
    }

    
    dict_params['use_dummy_data'] = use_dummy_data
    dict_params['df'] = df
    dict_params['outlier_detection_method'] = outlier_detection_method
    dict_params['outlier_detection_method_threshold'] = outlier_detection_method_threshold
    dict_params['outlier_handling_method'] = outlier_handling_method
    dict_params['outlier_handling_method_argument'] = dict_interpolation_parameter[outlier_handling_method] #use this as the argument to the function that will handle outliers
    dict_params['demand_percentile'] = demand_percentile
    dict_params['datetime_field'] = datetime_field
    dict_params['activity_count_field'] = activity_count_field
    dict_params['unit_of_measurement'] = unit_of_measurement
    dict_params['dict_unit_text_to_parameter_term'] = dict_unit_text_to_parameter_term[unit_of_measurement]
    dict_params['forecast_horizon'] = forecast_horizon
    dict_params['confidence_limit'] = dict_confidence_interval_decimal[confidence_limit]

    return dict_params