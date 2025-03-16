from typing import Literal, List

from langchain_core.tools import tool
import yfinance as yf
import plotly.graph_objects as go


@tool
def get_current_stock_price(symbol: str) -> str:
    """Gets the latest stock price of the symbol, returns an error if the symbol is invalid.

    Parameters:
        - symbol (str): A stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        stock_data = ticker.history(period='1d')
        if not stock_data.empty:
            current_price = stock_data['Close'].iloc[stock_data.shape[0]-1]
            return f"{current_price:.2f} USD."
        else:
            return "The symbol or the period is invalid. The period should be in the format of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max, etc."
    except Exception as e:
        return f"An error occurred while fetching the stock price: {str(e)}"


@tool
def get_stock_price(symbol: str, period: str = '1d', entry_period: Literal['day', 'week', 'month'] = 'day') -> List[float]:
    """Gets the latest stock price of the symbol, returns an error if the symbol is invalid.

    Parameters:
        - symbol (str): A stock symbol.
        - period (str): The amount of time for which you want the price
        - entry_period (str, optional): either 'day', 'week', or 'month', represents how long each price is for
    """
    ticker = yf.Ticker(symbol)
    stock_data = ticker.history(period=period)
    if not stock_data.empty:
        if entry_period == 'day':
            time_period = 1
        elif entry_period == 'week':
            time_period = 7
        elif entry_period == 'month':
            time_period = 30
        stock_prices = list(stock_data['Close'])
        res = []
        for i in range(0, len(stock_prices), time_period):
            res.append(stock_prices[i])

        return res


@tool
def get_trend(symbol: str, period: str = '1d') -> str:
    """Gets the current average trend of the symbol throughout the period, returns an error if the symbol or period is invalid.

    Parameters:
        - symbol (str): A stock symbol.
        - period (str): The amount of time for which you want the trend
    """
    try:
        ticker = yf.Ticker(symbol)
        stock_data = ticker.history(period=period)
        if not stock_data.empty:
            dif = stock_data['Close'].iloc[stock_data.shape[0]-1]-stock_data['Open'].iloc[0]
            dif_percentage = (dif/stock_data['Open'].iloc[0])*100

            return dif_percentage
        else:
            return "The symbol or the period is invalid. The period should be in the format of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max, etc."
    except Exception as e:
        return f"An error occurred while fetching the stock price: {str(e)}"

@tool
def show_graph(x_values, y_values, title="Graph", xlabel="Time", ylabel="Price"):
    """
    Plots a simple line graph.
    Pass get_stock_price directly into y_values.

    Parameters:
        x_values (list or array-like): The values for the X-axis.
        y_values (list or array-like): The values for the Y-axis, corresponding to x_values.
        title (str, optional): The title of the graph. Default is "Graph".
        xlabel (str, optional): Label for the X-axis. Default is "Time".
        ylabel (str, optional): Label for the Y-axis. Default is "Price".

    Returns:
        None. Displays the plot.

    Example:
        plot_graph([1, 2, 3, 4, 5], [541.2, 543.4, 540.0, 542.9, 546.8], "Stock price of apple", "Time", "Price")
    """

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines+markers'))

    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title=ylabel)

    fig.show()


@tool
def show_multiline_graph(x_values, y_values, labels=None, title="Graph", xlabel="Time", ylabel="Price"):
    """
    Plots multiple lines on a single graph.
    Pass the values of get_stock_price as one of the lists of y_values.

    Parameters:
        x_values (list): The values for the X-axis.
        y_values (list[list]): A list containing lists which each represent a line on the graph.
        labels (list, optional): A list of labels for the lines.
        title (str, optional): Title of the graph.
        xlabel (str, optional): Label for X-axis.
        ylabel (str, optional): Label for Y-axis.
    """

    fig = go.Figure()

    if labels is None:
        labels = [f"Line {i + 1}" for i in range(len(y_values))]

    for i, y_values_line in enumerate(y_values):
        fig.add_trace(go.Scatter(x=x_values, y=y_values_line, mode='lines+markers', name=labels[i]))

    fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel)

    fig.show()
