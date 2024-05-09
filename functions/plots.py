import streamlit as st
import altair as alt
import pandas as pd



# Forecast Plot
def plot_forecast(df, forecast, date_column):
    # Combine actual and forecast data for plotting
    actual_data = df[['ds', 'y']]
    forecast_data = forecast[[date_column, 'yhat', 'yhat_lower', 'yhat_upper']]
    
    # Merge and mark the data type (actual or forecast)
    actual_data['Type'] = 'Actual'
    forecast_data['Type'] = 'Forecast'
    
    combined = pd.concat([actual_data, forecast_data], ignore_index=True)
    
    # Base chart for observations
    base = alt.Chart(combined).encode(
        x=alt.X('ds:T', title='Date')
    ).interactive()
    
    # Points for actual and forecast data
    points = base.mark_circle().encode(
        y=alt.Y('y:Q', title='Value'),
        color=alt.Color('Type:N', scale=alt.Scale(domain=['Actual', 'Forecast'], range=['blue', 'green']))
    )
    
    # Lines for forecasts (yhat)
    lines = base.mark_line().encode(
        y=alt.Y('yhat:Q', title='Forecast'),
        color=alt.Color('Type:N', scale=alt.Scale(domain=['Actual', 'Forecast'], range=['blue', 'red']))
    )
    
    # Confidence interval areas
    area = base.mark_area(opacity=0.3).encode(
        y=alt.Y('yhat_lower:Q'),
        y2=alt.Y2('yhat_upper:Q'),
        color=alt.Color('Type:N', scale=alt.Scale(domain=['Actual', 'Forecast'], range=['blue', 'red']))
    )
    
    # Combine all layers
    chart = alt.layer(area, lines, points).resolve_scale(y='independent')
    
    return chart

#-----------------------------------------------


def plot_forecast_with_components(df, forecast, date_column):
    # Split forecast into historical and future parts
    forecast_past = forecast[forecast[date_column] <= df[date_column].iloc[-1]]
    forecast_future = forecast[forecast[date_column] > df[date_column].iloc[-1]]

    # Add a 'Type' column to each segment for legend
    df['Type'] = 'Historical Data'
    forecast_past['Type'] = 'Fitted Forecast'
    forecast_future['Type'] = 'Future Forecast'
    
    # Merge all data for unified handling and legend
    all_data = pd.concat([df, forecast_past, forecast_future], ignore_index=True)
    
    # Base chart configuration
    base_chart = alt.Chart(all_data).encode(
        x=alt.X(f"{date_column}:T", title='Date')
    )

    # Historical Data Line
    historical_data = base_chart.mark_line().encode(
        y=alt.Y('y:Q', title='Data Value'),
        color=alt.Color('Type:N', legend=alt.Legend(title="Data Type"), scale=alt.Scale(domain=['Historical Data', 'Fitted Forecast', 'Future Forecast'], range=['lightgrey', 'black', 'green'])),
        tooltip=[f"{date_column}", 'y']
    )

    # Fitted Forecast on Historical Data
    fitted_forecast = base_chart.mark_line(strokeDash=[5, 5]).encode(
        y='yhat:Q',
        color=alt.Color('Type:N', scale=alt.Scale(domain=['Fitted Forecast'], range=['black'])),
        tooltip=[f"{date_column}", 'yhat']
    )

    # Future Forecast Line
    future_forecast = base_chart.mark_line().encode(
        y='yhat:Q',
        color=alt.Color('Type:N', scale=alt.Scale(domain=['Future Forecast'], range=['green'])),
        tooltip=[f"{date_column}", 'yhat', 'yhat_lower', 'yhat_upper']
    )

    # Future Uncertainty Interval
    future_uncertainty = alt.Chart(forecast_future).mark_area(opacity=0.3).encode(
        x=f"{date_column}:T",
        y='yhat_lower:Q',
        y2='yhat_upper:Q',
        color=alt.value('lightgreen')  # Static color without separate legend entry
    ).properties(
        title="Future Uncertainty"
    )

    # Combine all layers
    chart = alt.layer(
        historical_data,
        fitted_forecast,
        future_forecast,
        future_uncertainty
    ).resolve_scale(y='shared').interactive()  # Ensure entire chart is interactive

    return chart

#-----------------------------------------------
