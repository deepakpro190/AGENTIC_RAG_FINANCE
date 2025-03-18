import yfinance as yf
import matplotlib.pyplot as plt

def analyze_stock_trends(companies):
    """
    Compares stock price trends of multiple companies.
    :param companies: List of dicts [{"name": "Tesla", "ticker": "TSLA"}]
    :return: Matplotlib Figure (stock comparison chart)
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    for company in companies:
        ticker = company["ticker"]
        stock = yf.Ticker(ticker)
        history = stock.history(period="6mo")

        if not history.empty:
            ax.plot(history.index, history["Close"], label=f"{company['name']} ({ticker})")

    ax.set_xlabel("Date")
    ax.set_ylabel("Stock Price (USD)")
    ax.set_title("Stock Performance Over Last 6 Months")
    ax.legend()
    ax.grid()

    return fig  # ✅ Return the Matplotlib Figure object
