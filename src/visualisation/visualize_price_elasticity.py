import numpy as np
from src.model.simson_model import load_simson_model
from src.read_data.load_data import load_steel_prices
import matplotlib.pyplot as plt



def main():
    df_prices = load_steel_prices()
    model = load_simson_model()
    inflow = model.FlowDict['F_2_4'].Values[1:, :, -1, :]  # 2 -> EUR
    prices = df_prices.to_numpy()
    prices = prices.transpose()
    inflow = np.sum(inflow, axis=2)
    plt.plot(prices[1:], inflow, 'ro')
    plt.xlabel("Prices (98 USD)")
    plt.ylabel("Steel demand (t/pc)")
    plt.title("USA steel demand over steel price")
    plt.show()

if __name__=='__main__':
    main()

