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



# Function to create a chart for a specific component
def create_dict_of_component_charts(date_column, forecast):
    # Base chart for main forecast
    base_chart = alt.Chart(forecast).encode(
        x=alt.X(f"{date_column}:T", title='Date')
    ).interactive()

    def component_chart(component_name, color):
        return base_chart.mark_line(color=color).encode(
            y=alt.Y(f"{component_name}:Q", title=component_name.capitalize()),
            tooltip=[f"{date_column}", f"{component_name}:Q"]
        )

    # Initialize a list to collect all component charts
    dict_of_charts = {}
    dict_of_explanations_for_charts = {}

    # Check and plot each component if it exists in the forecast DataFrame
    for component in ['trend', 'weekly', 'yearly', 'additive_terms', 'multiplicative_terms']:
        if component in forecast.columns:
            #charts.append(component_chart(component, 'green' if component == 'trend' else 'orange'))
            dict_of_charts[component] = component_chart(component, 'green' if component == 'trend' else 'orange')

            # Explanation dictionary
            if component == 'trend':
                dict_of_explanations_for_charts[component] = "Shows the long-term movement in data, removing shorter fluctuations to reveal underlying patterns."
            elif component == 'weekly':
                dict_of_explanations_for_charts[component] = "Represents the weekly cycle in the data, showing how values change on different days of the week."
            elif component == 'yearly':
                dict_of_explanations_for_charts[component] = "Highlights annual patterns, useful for understanding seasonal effects across the year."
            elif component == 'additive_terms':
                dict_of_explanations_for_charts[component] = """
                Sum of all the additive model components, including seasonal 
                effects not captured in main terms. A positive value means an 
                increase over the base trend, while a negative value indicates a 
                decrease. 
                \n**Interpretation example:** If you see that during mid-year, the additive terms spike up, 
                it could be due to increased patient visits typically seen during summer months, 
                possibly related to common seasonal ailments or injuries for that time of year, that the 
                model has learned. By observing this chart, you can understand 
                when and how much these factors are expected to change the 
                forecast beyond the underlying trend. 
                \nThere is no need to adjust the forecast values, additive trend is accounted for already."""

            elif component == 'multiplicative_terms':
                dict_of_explanations_for_charts[component] = """
                Shows how certain effects scale the trend multiplicatively, often 
                related to more complex interactions in the data.
                \n**Impact on the forecast:** Multiplicative terms can significantly alter the forecast, 
                especially in situations with high variability. They can lead to 
                exponential increases or decreases based on the model's understanding 
                of underlying patterns.
                \n**Magnitude and direction:** The exact value of these terms tells 
                you by how much the base forecast is being scaled. A consistent 
                value close to 1 suggests minimal multiplicative impact, while 
                significant deviations show strong seasonal or event-driven effects.
                \nThere is no need to adjust the forecast values, multiplicative trend is accounted for already."""


    # Combine all charts vertically
    #combined_chart = alt.vconcat(*charts).resolve_scale(y='independent')

    #return combined_chart
    return dict_of_charts, dict_of_explanations_for_charts
#-----------------------------------------------
