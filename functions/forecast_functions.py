
import pandas as pd
import numpy as np
import streamlit as st


#---------------------------------------

def adjust_forecast_for_appointments(df, forecast, appointments_per_unit, dna_rate, dna_discharge_policy, max_num_dnas, unit_of_measurement):
    # Adjust demand by the number of appointments per unit
    forecast['adjusted_demand'] = forecast['yhat'] * appointments_per_unit
    # Adjust the upper and lower bounds of the confidence interval
    forecast['adjusted_demand_upper'] = forecast['yhat_upper'] * appointments_per_unit
    forecast['adjusted_demand_lower'] = forecast['yhat_lower'] * appointments_per_unit

    # Apply DNA rate adjustment
    forecast['adjusted_demand'] *= (1 - dna_rate)
    forecast['adjusted_demand_upper'] *= (1 - dna_rate)
    forecast['adjusted_demand_lower'] *= (1 - dna_rate)
    
    # Implement DNA discharge policy adjustment if applicable
    if dna_discharge_policy == 'Yes' and isinstance(max_num_dnas, int):
        # Calculate the discharge rate based on the policy
        discharge_rate = (1 - dna_rate) ** max_num_dnas
        forecast['final_adjusted_demand'] = forecast['adjusted_demand'] * discharge_rate
        forecast['final_adjusted_demand_upper'] = forecast['adjusted_demand_upper'] * discharge_rate
        forecast['final_adjusted_demand_lower'] = forecast['adjusted_demand_lower'] * discharge_rate
    else:
        # If no discharge policy, keep the adjusted demand as is
        forecast['final_adjusted_demand'] = forecast['adjusted_demand']
        forecast['final_adjusted_demand_upper'] = forecast['adjusted_demand_upper']
        forecast['final_adjusted_demand_lower'] = forecast['adjusted_demand_lower']

    return forecast


