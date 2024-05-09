import streamlit as st
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt

#import modules
from functions import sidebar
from functions import detect_outliers as outliers
from functions import plots
from functions import render_warnings
from functions import forecast_functions

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#render the sidebar by calling the relevant function
#This will return all parameters as a dictionary
#try:
#    dict_params = sidebar.render_sidebar()
#except:
#    st.stop()



st.title(':green[Demand forecasting]')

st.subheader(':green[How to get started:]')
with st.expander(label='Click for overview'):
    st.subheader('Purpose:')
    st.write('This app is intended to support demand and capacity planning. It uses the Meta Prophet library to do this.')
    st.subheader('Getting started')
    st.write('To get started, set up the parameters for your demand forecasting model using the options in the sidebar 👈🏻. Once you are happy with the parameter selections, press "Run model" button.')

try:
    dict_params = sidebar.render_sidebar()
    #test print for model params - remove in final
    #st.write(dict_params)
except:
    render_warnings.render_warning_aggregate_activity_count()
    st.write('Please select the file you wish to use, using the "Browse files" button in the sidebar to the left 👈🏻')
    st.stop()

st.subheader(':green[Preview of your data set]')
with st.expander('Click to view your data set'):
    st.dataframe(dict_params['df'])

#add button to run the model
with st.sidebar:
    button_run_model = st.button(label='Run model')

if button_run_model:

    st.subheader(':green[Outlier detection and interpolation]')

    #ID outliers
    outlier_results = outliers.detect_outliers(
        dict_params['df'], 
        method=dict_params['outlier_detection_method'], 
        threshold=dict_params['outlier_detection_method_threshold']
        ) 

    #st.write(outlier_results)

    #function call to check presence of outliers using user method, render findings and 
    #advise user what they should do if outliers present
    #if outliers were detected and removed, advise the user of the number of outliers removed
    #and confirm the method applied to handle the gaps in data
    #similarly, advise if any data missing, volume of this, and method applied. 
    df_outliers_and_missing_values_interpolated = outliers.process_and_visualize_outliers(
        dict_params['df'], 
        outlier_results, 
        dict_params['datetime_field'], 
        dict_params['activity_count_field'],
        dict_params['outlier_handling_method_argument'],
        dict_params['outlier_handling_method'],
        dict_params['dict_unit_text_to_parameter_term'],
        dict_params['polynomial_degree_value']
        )


    st.subheader(':green[Fitting the model]')
    #create the model
    model = Prophet(interval_width=dict_params['confidence_limit'])

    #fit the model to the dataset
    model.fit(df_outliers_and_missing_values_interpolated)

    #Make future predictions
    future = model.make_future_dataframe(periods=dict_params['forecast_horizon'])  # Prediction horizon according to user selection

    forecast = model.predict(future)

    chart = plots.plot_forecast_with_components(df_outliers_and_missing_values_interpolated, forecast, dict_params['datetime_field'])

    #render the chart
    st.altair_chart(chart, use_container_width=True)


    if dict_params['num_appts_per_patient'] == "Single appt per patient":
        #isolate the forecast values to derive the demand value at the user-provided percentile value
        forecasted_values_only_yhat = forecast[forecast[dict_params['datetime_field']] > df_outliers_and_missing_values_interpolated[dict_params['datetime_field']].max()]['yhat'].values
        forecasted_values_only_yhat_upper = forecast[forecast[dict_params['datetime_field']] > df_outliers_and_missing_values_interpolated[dict_params['datetime_field']].max()]['yhat_upper'].values
        forecasted_values_only_yhat_lower = forecast[forecast[dict_params['datetime_field']] > df_outliers_and_missing_values_interpolated[dict_params['datetime_field']].max()]['yhat_lower'].values

        #calculate the demand and confidence interval at the given threshold values
        demand_threshold = np.percentile(forecasted_values_only_yhat, dict_params['demand_percentile'])
        demand_threshold_upper = np.percentile(forecasted_values_only_yhat_upper, dict_params['demand_percentile'])
        demand_threshold_lower = np.percentile(forecasted_values_only_yhat_lower, dict_params['demand_percentile'])
    else:
        adjusted_forecast = forecast_functions.adjust_forecast_for_appointments(
            df_outliers_and_missing_values_interpolated,
            forecast,
            dict_params['average_appointments_per_pt'],
            dict_params['dna_rate'] / 100,
            dict_params['dna_policy_used'],
            dict_params['max_num_dnas'],
            dict_params['unit_of_measurement']
        )
        
        #isolate the forecast values to derive the demand value at the user-provided percentile value
        forecasted_values_only_yhat = adjusted_forecast[adjusted_forecast[dict_params['datetime_field']] > df_outliers_and_missing_values_interpolated[dict_params['datetime_field']].max()]['final_adjusted_demand'].values
        forecasted_values_only_yhat_upper = adjusted_forecast[adjusted_forecast[dict_params['datetime_field']] > df_outliers_and_missing_values_interpolated[dict_params['datetime_field']].max()]['final_adjusted_demand_upper'].values
        forecasted_values_only_yhat_lower = adjusted_forecast[adjusted_forecast[dict_params['datetime_field']] > df_outliers_and_missing_values_interpolated[dict_params['datetime_field']].max()]['final_adjusted_demand_lower'].values

    #calculate the demand and confidence interval at the given threshold values
    demand_threshold = np.percentile(forecasted_values_only_yhat, dict_params['demand_percentile'])
    demand_threshold_upper = np.percentile(forecasted_values_only_yhat_upper, dict_params['demand_percentile'])
    demand_threshold_lower = np.percentile(forecasted_values_only_yhat_lower, dict_params['demand_percentile'])

    percentile_value_last_character = int(str(round(dict_params["demand_percentile"]*100,))[-1])
    if percentile_value_last_character in [0, 4, 5, 6, 7, 8, 9]:
        ending = 'th'
    elif percentile_value_last_character in [1]:
        ending = 'st'
    elif percentile_value_last_character in [2]:
        ending = 'nd'
    elif percentile_value_last_character in [3]:
        ending = 'rd'
    else:
        pass

    percentile_text = str(round(dict_params["demand_percentile"]*100,))+ending

    st.subheader(f':green[Forecast demand at {percentile_text} percentile]')
    st.write(f"""At a :green[**{dict_params['confidence_limit']*100}%**] confidence interval, the 
    :green[**{percentile_text}**] percentile of demand would be :green[**{round(demand_threshold,1)}**] 
    (:green[**{round(demand_threshold_lower,1)}**] to :green[**{round(demand_threshold_upper,1)}**])""")

    with st.expander(label='Click to view model output'):
        st.write(forecast)