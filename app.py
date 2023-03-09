# Run app.py and visit http://127.0.0.1:8050/ in web browser

from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
from LiveMarketData import *
import yfinance as yf
from datetime import date, timedelta


# Set style sheet and declare app object.
external_stylesheets = ['style.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True


# Set nav html elements.
nav = html.Nav(children=(
    html.Li(
        children=(
            html.A('Stockview', href='/'),
            html.A('Watchlist', href='/'),
            html.A('Earnings', href='/'),
            html.A('Financial Statements', href='/'),
            html.A('Market Calendar', href='/'),
            html.A('Economic Data', href='/'),
        )
    )
)
)
# Set input table elements.
input_table = html.Table(children=(
    html.Thead(
        html.Tr(children=(
            html.Th('Ticker'),
            html.Th('Shares amount')
        )
        )
    ),
    html.Tbody(
        html.Tr(
            children=(
                html.Td(dcc.Input(id='ticker', value='SPY', type='text')),
                html.Td(dcc.Input(id='shares', value='100', type='number')),
                html.Td(html.Button('Search', id='search'))
            )
        )
    )
)
)

# Set output elements.
output_table = html.Table(id='output-table')

output_chart = dcc.Graph(id='output-chart')


# Set app layout with a parent div, and children divs of previously defined elements.
app.layout = html.Div(children=(html.Div(nav),
                      html.Div(id='panel1', children=input_table),
                      html.Div(id='panel2', children=output_table),
                      html.Div(id='panel3', children=output_chart)
                      )
                      )

# Define app callback wrapper for update_table function.
# Output is for id output-table.
# Takes in 2 state parameters, ticker and shares.
# Function runs based on (id search) button press.
@app.callback(
    Output('output-table', 'children'),
    State('ticker', 'value'),
    State('shares', 'value'),
    Input('search', 'n_clicks')
)
def update_table(ticker, shares, clicked):
    if clicked:

        # Create stock object using LiveMarketData.py
        stock = CurrentMarket(ticker, 'STOCK')

        # Format shares value to display 2 decimals. Shares can be fractional as a float,
        # and it is rounded to the nearest 2 decimal places.
        shares_value = '${:0.2f}'.format(round(float(shares) * stock.Price(), 2))

        # Check if ticker has a one year target. If not, set target to N/A
        try:
            target = stock.OneYearTarget()
        except:
            target = 'N/A'

        # Create html table.
        table = html.Table(children=(
            html.Thead(
                html.Tr(children=(
                    html.Th(html.H6('Ticker')),
                    html.Th(html.H6('Shares amount')),
                    html.Th(html.H6('Total value')),
                    html.Th(html.H6('Today\'s change')),
                    html.Th(html.H6('1 year estimate')),
                )
                )
            ),
            html.Tbody(
                html.Tr(
                    children=(
                        html.Td(html.P(ticker)),
                        html.Td(html.P(shares)),
                        html.Td(html.P(shares_value)),
                        html.Td(html.P(stock.Change())),
                        html.Td(html.P(target))
                    )
                )
            )
        )
        )
        return table
    else:
        pass


# Define app callback wrapper for update_chart function.
# Output is for id output-chart.
# Takes in 1 state parameter, ticker.
# Function runs based on (id search) button press.
@app.callback(
    Output('output-chart', 'figure'),
    State('ticker', 'value'),
    Input('search', 'n_clicks')
)
def update_chart(ticker, clicked):
    if clicked:
        # Define the start and end date for yf dataframe
        end_date = date.today()
        start_date = (date.today() - timedelta(days=365))

        # Set yf dataframe to df
        df = yf.download(ticker, start=start_date, end=end_date)

        # Create plotly candlestick figure
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                             open=df['Open'],
                                             high=df['High'],
                                             low=df['Low'],
                                             close=df['Close'])])

        # Format figure
        fig.update_layout(width=500, height=500)
        fig.update_layout(xaxis=dict(range=[end_date - timedelta(days=200), end_date]))
        fig.update_layout(
            margin=dict(l=0, r=0, t=35, b=0),
        )
        fig.update_layout(title=str(ticker) + ' YTD', xaxis_title='Date', yaxis_title='Price')
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='#eeeeee')

        return fig

    else:
        # If not pressed, return an empty dictionary.
        return {}

# Define app callback wrapper for show_chart function.
# Output is for id output-chart.
# Function runs based on (id search) button press.
@app.callback(
    Output('output-chart', 'style'),
    Input('search', 'n_clicks')
)
# show_chart function hides the default loaded empty chart figure until search button is pressed.
def show_chart(pressed):
    if pressed:
        # Delay the style change by 1 second to prevent seeing the empty figure chart
        time.sleep(1)
        return {'display': 'grid'}
    else:
        # If button is not pressed yet, don't display the chart.
        return {'display': 'none'}

if __name__ == '__main__':
    app.run_server(debug=True)