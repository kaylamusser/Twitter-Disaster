# -*- coding: utf-8 -*-
"""Disasters_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Z2aOLDp3g7OPsMQwkn4LQ05OgPm_B6ZU

#Geolocating Digital Refugees: Twitter User Behavior During Disasters
"""

from google.colab import drive
drive.mount('/content/drive')

"""Import necessary libraries"""

import os
import pandas as pd
from geopy.distance import great_circle

"""Read our csv file that contains the human mobility data, mount google drive first, please upload your own file path."""

#open file csv as a dataframe
file_path = '/content/drive/MyDrive/natural_disaster_human_mobility.csv'
df = pd.read_csv(file_path)

# Display the first few rows of the DataFrame
print(df.head())
#make sure to separate this into different cells.

"""Next, let's explore the data and do some preprocessing to make sure the labels are understandable."""

#group by unique types of disaster.event
df['disaster.event'].unique()

"""Above, we can see that the unique values of the disaster.event column shows names of cities and the name of the unique weather events. We want to separate these into particular locations in a separate column.

Let's load a new dataset with csv data that includes the types of disaster events AND the location data on each of the events.
"""

file_path_reference= '/content/drive/MyDrive/disaster_tweets_data_corrected.csv'
#load this data into a dataframe and display the table
df_reference = pd.read_csv(file_path_reference)
df_reference.head(16)

"""Next step, we need to convert the strings of the 'disaster.event' column in the df dataframe, instead the names of the 'Name' column in the df_reference."""

# Create a mapping from the second dataframe (reference)
event_reference = {
    '01_Wipha': 'Wipha (Tokyo)',
    '02_Halong': 'Halong (Okinawa)',
    '06_Kalmaegi': 'Kalmaegi (Calasiao)',
    '08_Rammasun_Manila': 'Rammasun (Manila)',
    '12_Bohol': 'Bohol (Bohol)',
    '13_Iquique': 'Iquique (Iquique)',
    '14_Napa': 'Napa (Napa)',
    '21_Norfolk': 'Xaver (Norfolk)',
    '22_Hamburg': 'Xaver (Hamburg)',
    '23_Atlanta': 'Storm (Atlanta)',
    '31_Phoenix': 'Storm (Phoenix)',
    '32_Detroit': 'Storm (Detroit)',
    '33_Baltimore': 'Storm (Baltimore)',
    '41_AuFire1': 'New South Wales (1)',
    '42_AuFire2': 'New South Wales (2)'
}

# Replace the values in disaster.event with the mapping from event_reference
df['disaster.event'] = df['disaster.event'].replace(event_reference)

# Display the updated dataframe
print(df.head())

#let's check the new dataframe and see the unique values for the disaster.event
df['disaster.event'].unique()

"""Make new columns, being Type, or the type of storm, and the Location being the city/state or country."""

# Create the mapping dictionary from df_reference
# Assuming your columns are named 'Name', 'Type', and 'Location'
event_to_type_location = dict(zip(df_reference['Name'], zip(df_reference['Type'], df_reference['Location'])))  # Use 'Name' instead of 'Event'

# Replace the disaster.event column in df with the corresponding (Type, Location) from the dictionary
# This will add the 'Type' and 'Location' as two new columns
# Handle NaN values by filling with a default or removing them
# Use fillna with a dictionary to replace NaN in 'Type' and 'Location' columns separately
result = df['disaster.event'].map(event_to_type_location) # First, apply the mapping
df['Type'] = result.apply(lambda x: x[0] if isinstance(x, tuple) else '') # Extract Type, handling NaNs
df['Location'] = result.apply(lambda x: x[1] if isinstance(x, tuple) else '') # Extract Location, handling NaNs



# Display the updated dataframe
print(df.head())

df.shape

df['Type'].unique()

df['Location'].unique()

#return the number of unique values
df['Location'].nunique() #checks into 15 values like we want.

"""#CHECKPOINT

We are now saving the new dataframe as a new csv file. This will make it easier for us to analyze the data without having to do more processing. But for me, since we already have the dataframe on the runtime, let's continue to do the analysis.

New name: disasters_2_processed.csv

Errors: Found out that the original dataset switched the lat and lon columns... switch it back for this analysis.
"""

import pandas as pd

#save new datafr as a csv file?
df.to_csv('disasters_2_processed.csv', index=False)

"""**Hold** only do this step if you have the file and you want to skip the above steps."""

# only use this if you just want to load the new csv file as the new df

df=pd.read_csv('/content/drive/MyDrive/Disaster Project/Copy of disasters_2_processed.csv')
df.head()

#making sure to switch the column named of lon and lat to the right names
df.rename(columns={'latitude': 'longitude.anon', 'longitude.anon': 'latitude'}, inplace=True)

# Print the updated dataframe to confirm the column names are swapped
df.head()

"""Converting the time to the right datetime format

At least one time entry in the column (140024) doesn't contain the time part, just the date. We should try to figure out when this is happening... Because the error arised AFTER the function got to row 140024.
"""

df['time'] = pd.to_datetime(df['time'], errors='coerce')
df['time'] = df['time'].fillna(pd.to_datetime(df['time'].dt.date)) #If there are any NaT (Not a Time) values, this line replaces them with the date part of the original 'time' column values.

#find the NaT values and count them
df[df['time'].isna()].shape

"""There is only one NaT value, so now let's delete the one row that is showing the NaT value. For reference, this is position 140024 in Wipha(Tokyo)"""

#return the NaT value from the 'time' column
df[df['time'].isna()]

#delete position 140024 since it has an NaT value
df = df.drop(140024)

#print out the shape of the df
df.shape

"""The new shape of the dataframe, 'df' should be (4686153, 7)

#Research Questions

Q1: During disaster events, how far are Twitter users migrating on one disaster event? What is the averages of migration among the different types of disaster events...

To analyze the distance traveled by users over time (before one day, during, and 5 days after the disaster starts)
after the event), we will need to calculate the distance between the points in each user's journey.


---


Q2: Can we separate these migration routes among different days?


---



Q3: Can we compare different disaster events and how far in 8 days people are migrating from the epicenter of a disaster?

##Q1: Is the average distance users migrate from the epicenter of a disaster different from day 1?
"""

df.head()

#extract the year that each disaster.event happened from the df file
df['year'] = df['time'].dt.year
df.head()

#group by each unique value in disaster.event in the 'disaster.event' column, print out the years associated with them
df.groupby('disaster.event')['year'].unique()

"""###Create a new dataframe for each disaster that contains the disaster, the start time of the event (by one day before considering the warnings) and create a new column in the dataframe that contains the epicenter (long and lat) of the approximate disaster location

####df_event_start_location
is the new dataframe so we can reference all of the events' start dates, and the latitude and longitude.
"""

# Initialize the new dataframe manually
data = {
    "disaster.event": [
        "Wipha (Tokyo)", "Halong (Okinawa)", "Kalmaegi (Calasiao)", "Rammasun (Manila)",
        "Bohol (Bohol)", "Iquique (Iquique)", "Napa (Napa)", "Xaver (Norfolk)",
        "Xaver (Hamburg)", "Storm (Atlanta)", "Storm (Phoenix)", "Storm (Detroit)",
        "Storm (Baltimore)", "New South Wales (1)", "New South Wales (2)"
    ],
    "event_start_date": [
        "2013-10-09", "2014-08-07", "2014-09-13", "2014-07-11",
        "2013-10-15", "2014-04-01", "2014-08-24", "2013-12-05",
        "2013-12-04", "2014-01-28", "2014-09-08", "2014-08-11",
        "2014-07-28", "2013-10-13", "2013-10-13"
    ],
    "latitude": [
        35.689487, 26.212313, 16.0082453, 14.6042,
        9.880, -19.610, 38.217, 52.6140,
        53.5488, 33.7501, 33.4484, 42.3314,
        39.2904, -31.2532, -31.2532
    ],
    "longitude.anon": [
        139.691711, 127.679153, 120.3578634, 120.9822,
        124.117, -70.769, -122.3105, 0.8864,
        9.9872, -84.3885, -112.0740, -83.0458,
        -76.6122, 146.9211, 146.9211
    ]
}

# Creating the dataframe
df_event_start_location = pd.DataFrame(data)

# Display the dataframe
print(df_event_start_location)

"""Now that we have the reference dataframe for the disaster locations and start times, let's choose a disaster event, but first, let's initialize the disaster.event so we can reframe and replicate the analysis if we choose a different one later.

#####Important: Make sure to initialize the variables for analysis
"""

disaster_event_name='Wipha (Tokyo)' #insert the disaster_event_name you'd want
number_of_days=5 #insert the number of days you want to analyze
#make a new variable that is just the event_start_date value for the Wipha(Tokyo)/another disaster
event_start_date = df_event_start_location[df_event_start_location['disaster.event'] == disaster_event_name]['event_start_date'].values[0]
event_start_date = pd.to_datetime(event_start_date) #convert to datetime
event_start_date

df_Wipha = df[df['disaster.event'] == disaster_event_name]
df_Wipha.head()

#make a new dataframe for df_Wipha that only includes data during event_start_date and before 5 days by comparing days
df_Wipha = df_Wipha[df_Wipha['time'] >= event_start_date]
#df_Wipha = df_Wipha[df_Wipha['time'] < event_start_date + pd.Timedelta(days=number_of_days)]
df_Wipha.head()

df_Wipha.shape

# Epicenter coordinates for Wipha (Tokyo)
epicenter_row = df_event_start_location[df_event_start_location['disaster.event'] == disaster_event_name]
epicenter_coords = (epicenter_row['latitude'].values[0], epicenter_row['longitude.anon'].values[0])
epicenter_coords

# Calculate the great circle distance for each user
df_Wipha['distance_from_epicenter'] = df_Wipha.apply(
    lambda x: great_circle((x['latitude'], x['longitude.anon']), epicenter_coords).km,
    axis=1
)

# Create a column for the day based on the 'time' column
df_Wipha['days_since_disaster'] = (df_Wipha['time'] - pd.to_datetime(event_start_date)).dt.days
df_Wipha.head()

# Categorize days (Day 1, Day 2, etc.)
df_Wipha['day'] = df_Wipha['days_since_disaster'].apply(lambda x: f"Day {x + 1}" if x >= 0 else 'Pre-Disaster')

# View the updated dataframe
print(df_Wipha[['user.anon', 'time', 'distance_from_epicenter', 'day']].head())
df_Wipha.shape

"""Now that we made new columns for df_Wipha, let's groupby means per day of the users experiencing the Wipha typhoon in Tokyo."""

# Group by the 'day' and calculate the average distance for each day
avg_distance_by_day = df_Wipha.groupby('day')['distance_from_epicenter'].mean()

# Print the average distances for each day
print(avg_distance_by_day)

import matplotlib.pyplot as plt

# Sort the average distance by numerical day order
avg_distance_by_day.index = avg_distance_by_day.index.str.extract(r'(\d+)')[0].astype(int)  # Extract numeric part from 'Day X' and select the first column (series)
avg_distance_by_day = avg_distance_by_day.sort_index()

"""###Q1 Scatterplots

Below, we can see that we have plotted all of the recorded days for the Wipha Tokyo Typhoon disaster. We can see a lot of dips, but since we only care about the disaster responses by individuals on a few days after the disaster starts, I only want to use a week (7 days) for our data.
"""

import plotly.express as px

# Create a line chart using Plotly
fig = px.line(
    avg_distance_by_day,
    x=avg_distance_by_day.index,
    y=avg_distance_by_day.values,
    labels={'x': 'Day', 'y': 'Average Distance (km)'},
    title=f'Average Migration Distance from Epicenter by Day for {disaster_event_name}'
)

# Customize the traces and layout
fig.update_traces(marker=dict(symbol='circle', size=8), line=dict(width=2))
fig.update_layout(
    title_font_size=20,
    xaxis_title_font_size=15,
    yaxis_title_font_size=15,
    xaxis=dict(tickangle=45, gridcolor='lightgray'),
    yaxis=dict(gridcolor='lightgray'),
    template='plotly_white'
)

fig.show()

import plotly.io as pio

fig.write_html("Q1.html",full_html=False)

"""We can see below that when we zoom into the average migration distance, it seems to spike around day 4 since the start of the Wipha Typhoon."""

#plot the same plot above but only plot from days 0-8
plt.figure(figsize=(10, 6))
avg_distance_by_day[:8].plot(kind='line', marker='o')

plt.title(f'Average Migration Distance from Epicenter by Day (Limit 7 days) for {disaster_event_name}')
plt.xlabel('Day')
plt.ylabel('Average Distance (km)')
plt.xticks(rotation=45)
plt.grid(True)

"""### More analysis on Wipha Tokyo
Oh? You don't think migrating on average 1000+ km between the 3rd and 4th day since the landfall of the Wipha Typhoon in Tokyo is significant? What is the likelihood that this migration away from the epicenter of the Typhoon landfall in Tokyo a coincidence?
"""

from scipy.stats import ttest_ind

day1_distances = df_Wipha[df_Wipha['day'] == 'Day 1']['distance_from_epicenter']
other_days_distances = df_Wipha[df_Wipha['day'] == 'Day 4']['distance_from_epicenter']
t_stat, p_value = ttest_ind(day1_distances, other_days_distances, equal_var=False)

print(f"T-statistic: {t_stat}, P-value: {p_value}")

"""We can see above that assuming the distribution of average Twitter user distances from Tokyo Japan follows a normal distribution with a null value of 995 km from Tokyo, an average distance displacement of above 1003 km is statistically significant at a p-value of 0.000198... It would be unusual to see this distance by random error considering the averages of distances.

###Q3: Is there a difference among different types of disaster events and how long in time and how far people are migrating (or not migrating at all?)

The third question is more applicable to the first research question. Now that we figured out how to get the average distances among the users on day 1-end for one particular disaster (Wipha, Tokyo), we want to figure out if these changes in distances are different among all of the disasters.

---

1.   Fit scatterplots of each disaster.event AND find the lines of best fits only from day 0-day 8
2.   Use the slopes regardless of intercept values, since the slope would indicate a different change of distance among the same times displacements. The slopes values will represent each disaster.event, make the labels hoverable for the disaster.event
3.   Plot the slopes in a scatterplot:
*   using the GDP per Capita as x-axis
*   using the disaster event as the x-axis
*   using the type of disaster as the x-axis or color coded into the plot
"""

df.head() #we are using this dataframe from the original one

"""Since we're processing multiple disasters at once, let's make a function that creates a merged dataframe"""

# Create an empty list to store filtered data for each disaster event
filtered_data_list = []

# Loop through each unique disaster event in df_event_start_location
for disaster_event in df_event_start_location['disaster.event'].unique():
    # Get the event start date for the current disaster
    event_start_date = df_event_start_location[df_event_start_location['disaster.event'] == disaster_event]['event_start_date'].values[0]

    # Filter the main dataframe for the current disaster event
    df_event = df[df['disaster.event'] == disaster_event].copy()  # Use copy to avoid SettingWithCopyWarning

    # Calculate the days since the event started for each row
    df_event['days_since_disaster'] = (df_event['time'] - pd.to_datetime(event_start_date)).dt.days

    # Filter for data within day 0 to day 8
    df_filtered_event = df_event[(df_event['days_since_disaster'] >= 0) & (df_event['days_since_disaster'] <= 8)]

    # Append the filtered data for this disaster event to the list
    filtered_data_list.append(df_filtered_event)

# Concatenate all filtered dataframes into one
df_filtered_all = pd.concat(filtered_data_list)

# Check the head of the final filtered dataframe
df_filtered_all.head()

df_filtered_all['disaster.event'].nunique() #just checking the categories of disaster.events

# Now, merge with epicenter coordinates from df_event_start_location
df_merged = pd.merge(df_filtered_all, df_event_start_location[['disaster.event', 'latitude', 'longitude.anon']],
                     on='disaster.event', how='left', suffixes=('', '_epicenter'))
df_merged.head()

# Function to calculate the distance from the epicenter
import geopy.distance # Import geopy.distance

def calculate_distance_from_epicenter(lat, lon, epicenter_lat, epicenter_lon):
    return geopy.distance.distance((lat, lon), (epicenter_lat, epicenter_lon)).km

# Calculate the distance from the epicenter for each row
df_merged['distance_from_epicenter'] = df_merged.apply(
    lambda row: calculate_distance_from_epicenter(row['latitude'], row['longitude.anon'],
                                                  row['latitude_epicenter'], row['longitude.anon_epicenter']), axis=1
)

# Check the result
df_merged.head()

"""###Compare typhoons, one with a high GDP per capita and one with a low GDP per capita in the affected area. (Wipha (Tokyo)) vs. (Kalmeagi (Calasiao))"""

disaster_1 = "Wipha (Tokyo)"
disaster_2 = "Kalmaegi (Calasiao)"

df_two_disasters = df_merged[df_merged['disaster.event'].isin([disaster_1, disaster_2])]
df_two_disasters.head()

print(df_two_disasters.groupby('disaster.event')['distance_from_epicenter'].describe())

df_avg_distance = (
    df_two_disasters
    .groupby(['disaster.event', 'days_since_disaster'])
    .agg({'distance_from_epicenter': 'mean'})
    .reset_index()
)

#print each head of the df split with the 2 disasters
print(df_avg_distance[df_avg_distance['disaster.event'] == disaster_1].head())
print(df_avg_distance[df_avg_distance['disaster.event'] == disaster_2].head())

import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# Create the figure
fig = go.Figure()

# Iterate through the disaster events
for disaster_event in [disaster_1, disaster_2]:
    # Filter data for the current disaster
    df_event = df_avg_distance[df_avg_distance['disaster.event'] == disaster_event]

    # Extract X and y
    X = df_event[['days_since_disaster']]
    y = df_event['distance_from_epicenter']

    # Scatterplot of the average distances
    fig.add_trace(go.Scatter(
        x=df_event['days_since_disaster'],
        y=df_event['distance_from_epicenter'],
        mode='markers',
        name=f"{disaster_event} (scatter)"
    ))

    # Fit a linear regression line
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    # Plot the line of best fit
    fig.add_trace(go.Scatter(
        x=df_event['days_since_disaster'],
        y=y_pred,
        mode='lines',
        line=dict(dash='dash'),
        name=f"{disaster_event} (fit)"
    ))

# Add layout details
fig.update_layout(
    title='Comparison of Migration Patterns for Typhoons in Japan and Philippines (based on different GDP levels)',
    xaxis_title='Days Since Disaster Started',
    yaxis_title='Average Distance from Epicenter (km)',
    legend_title='Legend',
    template='plotly_white',
    xaxis=dict(tickmode='array', tickvals=np.arange(0, 9, 1)),
    title_font_size=20,
    xaxis_title_font_size=15,
    yaxis_title_font_size=15
)

# Show the figure
fig.show()

import plotly.io as pio

fig.write_html("Q2.html",full_html=False)

"""###Compare earthquakes, one with a high GDP per capita and one with a low GDP per capita in the affected area (Napa (Napa/SF, CA)) vs. (Bohol (Bohol))"""

#earthquake
disaster_1='Bohol (Bohol)' #low GDP
disaster_2='Napa (Napa)' #high GDP

df_two_disasters = df_merged[df_merged['disaster.event'].isin([disaster_1, disaster_2])]

print(df_two_disasters.groupby('disaster.event')['distance_from_epicenter'].describe())

df_avg_distance = (
    df_two_disasters
    .groupby(['disaster.event', 'days_since_disaster'])
    .agg({'distance_from_epicenter': 'mean'})
    .reset_index()
)

print(df_avg_distance.head())

import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# Create the figure
fig = go.Figure()

# Iterate through the disaster events
for disaster_event in [disaster_1, disaster_2]:
    # Filter data for the current disaster
    df_event = df_avg_distance[df_avg_distance['disaster.event'] == disaster_event]

    # Extract X and y
    X = df_event[['days_since_disaster']]
    y = df_event['distance_from_epicenter']

    # Scatterplot of the average distances
    fig.add_trace(go.Scatter(
        x=df_event['days_since_disaster'],
        y=df_event['distance_from_epicenter'],
        mode='markers',
        name=f"{disaster_event} (scatter)"
    ))

    # Fit a linear regression line
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    # Plot the line of best fit
    fig.add_trace(go.Scatter(
        x=df_event['days_since_disaster'],
        y=y_pred,
        mode='lines',
        line=dict(dash='dash'),
        name=f"{disaster_event} (fit)"
    ))

# Add layout details
fig.update_layout(
    title='Comparison of Migration Patterns for Earthquakes in Bohol (Low GDP) and Napa, CA (High GDP)',
    xaxis_title='Days Since Disaster Started',
    yaxis_title='Average Distance from Epicenter (km)',
    legend_title='Legend',
    template='plotly_white',
    xaxis=dict(tickmode='array', tickvals=np.arange(0, 9, 1)),
    title_font_size=20,
    xaxis_title_font_size=15,
    yaxis_title_font_size=15
)

# Show the figure
fig.show()

import plotly.io as pio

fig.write_html("Q3.html",full_html=False)

"""###Compare storms, one with a high GDP per capita and one with a low GDP per capita in the affected area. (Xaver (Norfolk, Britain)) vs (Storm (Baltimore, Maryland))"""

#winter storm and thunderstorms
disaster_1='Xaver (Norfolk)' #high GDP
disaster_2='Storm (Baltimore)' #low GDP

df_two_disasters = df_merged[df_merged['disaster.event'].isin([disaster_1, disaster_2])]

print(df_two_disasters.groupby('disaster.event')['distance_from_epicenter'].describe())

df_avg_distance = (
    df_two_disasters
    .groupby(['disaster.event', 'days_since_disaster'])
    .agg({'distance_from_epicenter': 'mean'})
    .reset_index()
)

print(df_avg_distance.head())

import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# Create the figure
fig = go.Figure()

# Iterate through the disaster events
for disaster_event in [disaster_1, disaster_2]:
    # Filter data for the current disaster
    df_event = df_avg_distance[df_avg_distance['disaster.event'] == disaster_event]

    # Extract X and y
    X = df_event[['days_since_disaster']]
    y = df_event['distance_from_epicenter']

    # Scatterplot of the average distances
    fig.add_trace(go.Scatter(
        x=df_event['days_since_disaster'],
        y=df_event['distance_from_epicenter'],
        mode='markers',
        name=f"{disaster_event} (scatter)"
    ))

    # Fit a linear regression line
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    # Plot the line of best fit
    fig.add_trace(go.Scatter(
        x=df_event['days_since_disaster'],
        y=y_pred,
        mode='lines',
        line=dict(dash='dash'),
        name=f"{disaster_event} (fit)"
    ))

# Add layout details
fig.update_layout(
    title='Comparison of Migration Patterns for Storms in Britain (Low GDP) and Baltimore, Maryland (High GDP)',
    xaxis_title='Days Since Disaster Started',
    yaxis_title='Average Distance from Epicenter (km)',
    legend_title='Legend',
    template='plotly_white',
    xaxis=dict(tickmode='array', tickvals=np.arange(0, 9, 1)),
    title_font_size=20,
    xaxis_title_font_size=15,
    yaxis_title_font_size=15
)

# Show the figure
fig.show()

import plotly.io as pio

fig.write_html("Q4.html",full_html=False)

"""#Checkpoint

So above is the last plot I have done, this actually doesn't tell much for me, so I have to change how we're analyzing these disaster.events. Maybe we should just compare a couple of disaster.events instead.
"""

df = df_Wipha  # Ensure df is the correct dataframe

df['days_since_disaster'].unique()

#make new dataframes for each day since the disaster in the df_Wipha
df_day_1 = df[df['days_since_disaster'] == 0]
df_day_1.head()
df_day_2 = df[df['days_since_disaster'] == 1]
df_day_2.head()
df_day_3 = df[df['days_since_disaster'] == 2]
df_day_3.head()
df_day_4 = df[df['days_since_disaster'] == 3]
df_day_4.head()

df_day_4.shape

# Convert 'time' column to datetime with dynamic format handling
df['time'] = pd.to_datetime(df['time'], errors='coerce', format='mixed')

# Create a Mapbox plot with routes for all users separated by days

def create_mapbox_plot(df):
  fig = px.scatter_mapbox(
      df,
      lat='latitude',  # Ensure the column 'latitude' exists
      lon='longitude.anon',  # Ensure the column 'longitude.anon' exists
      #color="user.anon",  # Different colors for each user
      hover_data={"time": True},  # Add timestamp to hover info
      title="Migration Routes for All Users",
      mapbox_style="open-street-map",  # Change style to Open Street Map
      zoom=3,
      center={"lat":df_event_start_location.loc[df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'latitude'].iloc[0], "lon":df_event_start_location.loc[df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'longitude.anon'].iloc[0]}
  )

  fig.add_scattermapbox(
      lat=[df_event_start_location.loc[df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'latitude'].iloc[0]],  # Extract latitude for Wipha (Tokyo)
      lon=[df_event_start_location.loc[df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'longitude.anon'].iloc[0]],  # Extract longitude for Wipha (Tokyo)
      mode='markers',  # Set mode to 'markers' to show a point
      marker=dict(size=10, color='red'),  # Customize marker appearance
      name='Epicenter'  # Add a name for the epicenter trace
  )
  # Update layout for better display
  fig.update_layout(
      height=600,
      margin={"r": 0, "t": 30, "l": 0, "b": 0},
      legend_title="User"
  )
  fig.show()

create_mapbox_plot(df_day_1)
create_mapbox_plot(df_day_2)
create_mapbox_plot(df_day_3)
create_mapbox_plot(df_day_4)

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Convert 'time' column to datetime with dynamic format handling
df['time'] = pd.to_datetime(df['time'], errors='coerce')

# Function to create a Mapbox plot with routes for all users separated by days
def create_mapbox_plot(df):
    # Create the base scatter mapbox plot
    fig = px.scatter_mapbox(
        df,
        lat='latitude',  # Ensure the column 'latitude' exists
        lon='longitude.anon',  # Ensure the column 'longitude.anon' exists
        # color="user.anon",  # Uncomment for user-wise color differentiation
        hover_data={"time": True},  # Add timestamp to hover info
        title="Migration Routes for All Users",
        mapbox_style="open-street-map",  # Map style
        zoom=3,
        center={
            "lat": df_event_start_location.loc[
                df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'latitude'
            ].iloc[0],
            "lon": df_event_start_location.loc[
                df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'longitude.anon'
            ].iloc[0]
        }
    )

    # Add the epicenter marker
    fig.add_trace(go.Scattermapbox(
        lat=[df_event_start_location.loc[
            df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'latitude'
        ].iloc[0]],
        lon=[df_event_start_location.loc[
            df_event_start_location['disaster.event'] == 'Wipha (Tokyo)', 'longitude.anon'
        ].iloc[0]],
        mode='markers',
        marker=dict(size=12, color='red'),
        name='Epicenter'
    ))

    # Update layout for aesthetics
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        legend_title="Legend"
    )

    return fig

# Generate the figure
fig = create_mapbox_plot(df_day_1)

# Show the plot
fig.show()

import plotly.io as pio

fig.write_html("Q7.html",full_html=False)

"""##Additional question:

Does GDP per Capita matter for disaster migration?
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

#load a new file with the GDP per capita for each disaster.event
df_gdp = pd.read_csv('/content/drive/MyDrive/GDP_per_Capita.csv')
df_gdp.head()

df_gdp.shape

# Convert 'GDP per Capita (USD)' column from string to integers
df_gdp['GDP per Capita (USD)'] = pd.to_numeric(df_gdp['GDP per Capita (USD)'], errors='coerce').astype('Int64')
df_gdp.head()

#merge GDP per Capita (USD) column from df_gdp into corresponding disaster.event in df_merged
df_merged = df_merged.merge(df_gdp[['disaster.event', 'GDP per Capita (USD)']], on='disaster.event', how='left')
df_merged.head()

df_day3 = df_merged[df_merged['days_since_disaster'] == 3]
df_day3.head()

"""Examine whether GDP is correlated with the average migration distance for disasters by creating a "disaster_summary" variable that calculates the averages for GDP per capita and distance from the epicenters.

A correlation coefficient will indicate whether there’s a linear relationship (positive or negative) between GDP and migration distance.

Below, we can see that the correlation coefficient shows a weak negative correlation between GDP per Capita (USD) and distance from the disaster epicenter.
"""

disaster_summary = df_day3.groupby('disaster.event').agg(
    avg_distance=('distance_from_epicenter', 'mean'),
    avg_gdp=('GDP per Capita (USD)', 'mean') # Changed 'GDP_per_capita (USD)' to 'GDP per Capita (USD)'
)

# Calculate correlation
correlation = disaster_summary.corr()
print(correlation)

"""We can calculate the Pearson's R coefficient and its p-value. Since the p-value is not statistically significant at 0.38 compared to an alpha value of 0.05, the correlation coefficient could be showing an association where there may not be an association due to sampling errors."""

from scipy.stats import pearsonr

corr, p_value = pearsonr(disaster_summary['avg_gdp'], disaster_summary['avg_distance'])
print(f"Pearson Correlation: {corr}")
print(f"P-value: {p_value}")

"""The plot below shows a linear regression fitted around the distribution of GDP per Capita vs the migration distance, showing a slight negative correlation. However, the averages show an outlier (like San Francisco) for GDP. Otherwise, GDP doesn't seem to matter for the average migration distance (at day 3)."""

import matplotlib.pyplot as plt
import seaborn as sns

# Scatter plot
sns.regplot(x='avg_gdp', y='avg_distance', data=disaster_summary)
plt.xlabel('Average GDP Per Capita')
plt.ylabel('Average Distance from Epicenter (km)')
plt.title('Relationship Between GDP and Migration Distance')
plt.show()