import numpy as np
from src.read_data.load_data import load_trade_factor, load_scrap_trade_factor
from src.tools.tools import get_np_from_df
from src.model.load_dsms import load_dsms


def get_all_trade(country_specific):
    model_use = _get_model_use(country_specific)
    trade = _get_trade(country_specific, model_use)
    scrap_trade = _get_scrap_trade(country_specific, model_use, trade)

    return trade, scrap_trade


def _get_trade(country_specific, model_use):
    df_trade_factor = load_trade_factor(country_specific=country_specific)
    trade_factor = get_np_from_df(df_trade_factor, data_split_into_categories=False)
    trade = model_use * trade_factor
    trade = _balance_trade(trade)
    return trade


def _get_scrap_trade(country_specific, trade, model_use):
    df_scrap_trade_factor = load_scrap_trade_factor(country_specific=country_specific)
    scrap_trade_factor = get_np_from_df(df_scrap_trade_factor, data_split_into_categories=False)
    scrap_trade = (model_use - trade) * scrap_trade_factor
    scrap_trade = _balance_trade(scrap_trade)
    return scrap_trade


def _balance_trade(trade):
    net_trade = trade.sum(axis=0)
    sum_trade = np.abs(trade).sum(axis=0)
    balancing_factor = net_trade / sum_trade
    balanced_trade = trade * (1-np.sign(trade) * balancing_factor)

    return balanced_trade


def _get_model_use(country_specific):
    dsms = load_dsms(country_specific=country_specific)
    inflows_by_category = np.array(
        [np.array([dsm.i for dsm in dsms_by_category]).transpose() for dsms_by_category in dsms])
    model_use = inflows_by_category.sum(axis=2)
    return model_use


def _test():
    trade, scrap_trade = get_all_trade(country_specific=False)
    trade_balance = trade.sum(axis=0).sum(axis=0)
    scrap_trade_balance = scrap_trade.sum(axis=0).sum(axis=0)
    if trade_balance < 0.001:
        print('Trade is loaded and balanced.')
    if scrap_trade_balance < 0.001:
        print('Scrap trade_all_areas is loaded and balanced.')


if __name__=='__main__':
    _test()
