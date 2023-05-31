# Dashboard app using Flask and Plotly

Dashboard app created using Flask and Plotly that visualizes data from a PostgreSQL database.

## Note about implementation

1. I have implemented the following features. 
    1. Range slider and selector buttons provided to select the time window.
    2. Refresh button (green) provided to refresh the plot without refreshing the page (code can be easily modified to auto-refresh by sending the refresh request at regular intervals).
    3. Download button (grey) provided to download the data as a csv file.
2. Code follows PEP8, is fully type annotated, and has comments.
3. Package can be installed and dashboard can be viewed by running `docker compose up` and navigating to http://localhost:8888/.
4. The line colors of the plots will change when refreshed for the first time so that it is easy to see that the refresh works even if the data in the database has not changed.

