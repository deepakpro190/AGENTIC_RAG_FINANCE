import yfinance as yf
import matplotlib.pyplot as plt

def plot_stock_trend(tickers):
    """
    Plots stock price trends for given tickers.
    :param tickers: List of stock tickers (e.g., ["AAPL", "TSLA"])
    :return: Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 5))  # ✅ Create a figure & axis

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        history = stock.history(period="6mo")

        if not history.empty:
            ax.plot(history.index, history["Close"], label=f"{ticker}")

    ax.set_xlabel("Date")
    ax.set_ylabel("Stock Price (USD)")
    ax.set_title("Stock Performance Over Last 6 Months")
    ax.legend()
    ax.grid()

    return fig  # ✅ Return Matplotlib Figure object
