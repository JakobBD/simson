import numpy as np
import scipy.optimize
from sodym.tools.config import cfg

def extrapolate_stock(historic_stocks, gdppc, prediction_out):
    """
    wrapper to choose extrapolation strategy from config
    """
    strategy = cfg.curve_strategy
    if strategy == "Sigmoid_GDP_regression":
        sigmoid_gdp_regression(historic_stocks,
                               gdppc,
                               prediction_out)
    elif strategy == "Exponential_GDP_regression":
        exponential_gdp_regression(historic_stocks,
                                   gdppc,
                                   prediction_out)
    else:
        raise RuntimeError(f"Prediction strategy {strategy} is not defined. "
                           f"It needs to be 'Sigmoid_GDP_regression' or 'Exponential_GDP_regression'.")
    return


def sigmoid_gdp_regression(historic_stocks_pc, gdppc, prediction_out):
    shape_out = prediction_out.shape
    assert len(shape_out) == 3, "Prediction array must have 3 dimensions: Time, Region, Good"
    pure_prediction = np.zeros_like(prediction_out)
    n_historic = historic_stocks_pc.shape[0]
    i_lh = n_historic - 1

    for i_region in range(shape_out[1]):
        for i_good in range(shape_out[2]):
            def fitting_function(prms):
                return prms[0] / (1. + np.exp(prms[1] / gdppc[:n_historic, i_region])) - historic_stocks_pc[:, i_region,
                                                                                         i_good]
                # Lagrangian multiplier to ensure matching last point:
                # + prms[2] * prms[0] / (1. + np.exp(prms[1]/gdppc[i_lh,0])) - stocks_pc[-1,0,i] )

            prms_out = scipy.optimize.least_squares(fitting_function, x0=np.array(
                [2. * gdppc[i_lh, i_region], historic_stocks_pc[-1, i_region, i_good]]), gtol=1.e-12)
            assert prms_out.success

            pure_prediction[:, i_region, i_good] = prms_out.x[0] / (1. + np.exp(prms_out.x[1] / gdppc[:, i_region]))

        # def fitting_function(prms):
        #     return 2.*gdppc[i_lh,0] / (1. + np.exp(prms[0]/gdppc[cfg.i_historic,0])) - stocks_pc[:,0,i]
        # prms_out = scipy.optimize.least_squares(fitting_function, x0=np.array([stocks_pc[-1,0,i]]))
        # prediction = 2.*gdppc[i_lh,0] / (1. + np.exp(prms_out.x[0]/gdppc[:,0]))

    # fit b to last historic value
    prediction_out[...] = pure_prediction - (pure_prediction[i_lh, :, :] - historic_stocks_pc[i_lh, :, :])
    prediction_out[:n_historic, :, :] = historic_stocks_pc

    # if cfg.do_visualize["stock_prediction"]:
    #     visualize_stock_prediction(gdppc, historic_stocks_pc, pure_prediction)
    return


def exponential_gdp_regression(stocks, gdp_data, prediction_out):
    past_stocks_by_category = stocks.copy()
    stocks = np.sum(stocks, axis=2)

    gdp_data_future = gdp_data[123:]
    gdp_data_past = gdp_data[:123, :, 1]
    # up until 2023 all scenarios are the same
    # gdp data is equal in the past for all 5 scenarios, for calculation of A+b we just need one

    # TODO Optional a, b = _calc_global_a_b(stocks, gdp_data_past)

    s_0 = stocks[-1]
    g_0 = gdp_data_past[-1]

    a = 80 # TODO last stocks (s_0) seem to be too high, should be below 17, check lifecycle implementation.. 17.4
    b_regions = -np.log(1 - (s_0 / a)) / g_0

    gdp_data_future = np.moveaxis(gdp_data_future, -1, 0)
    future_stocks = _duerrwaechter_stock_curve(gdp_data_future, a, b_regions)
    future_stocks = np.moveaxis(future_stocks, 0, -1)

    future_stocks = split_future_stocks_to_base_year_categories(past_stocks_by_category, future_stocks,
                                                                is_future_stocks_with_scenarios=True)
    past_stocks_by_category = copy_stocks_across_scenarios(past_stocks_by_category)

    stocks = np.concatenate([past_stocks_by_category, future_stocks], axis=0)
    stocks = np.moveaxis(stocks, 2, 3)

    prediction_out[:] = stocks

    return


def _calc_global_a_b(stocks, gdp, ignore_ref=True):
    if ignore_ref:
        stocks_to_use = np.delete(stocks, 9, 1)
        gdp_to_use = np.delete(gdp, 9, 1)
    else:
        stocks_to_use = stocks
        gdp_to_use = gdp
    flattened_stocks = stocks_to_use.flatten()
    flattened_gdp = gdp_to_use.flatten()

    def f(params):
        return _duerrwaechter_stock_curve(flattened_gdp, params[0], params[1]) - flattened_stocks

    predicted_highest_stock_development = 0.1  # assume saturation level to be 10 % over stock at current highest gdp
    x_h = np.argmax(flattened_gdp)
    A_0 = flattened_stocks[x_h] * (1 + predicted_highest_stock_development)
    b_0 = -np.log(predicted_highest_stock_development / (1 + predicted_highest_stock_development)) / x_h
    params = [A_0, b_0]

    result = scipy.optimize.least_squares(f, params).x

    a = result[0]
    b = result[1]

    return a, b


def _duerrwaechter_stock_curve(gdp, a, b):
    return a * (1 - np.exp(-b * gdp))


def copy_stocks_across_scenarios(stocks):
    stock_orig_shape = stocks.shape
    stocks = np.expand_dims(stocks, axis=-1)
    stocks = np.broadcast_to(stocks, stock_orig_shape + (5,))
    return stocks


def split_future_stocks_to_base_year_categories(past_stocks_by_category, future_stocks,
                                                is_future_stocks_with_scenarios=False):
    # Summarised category data needs to split into categoriy data according to 2008 shares.
    stocks_base_year = past_stocks_by_category[-1]
    base_year_category_pctgs = stocks_base_year / np.expand_dims(np.sum(stocks_base_year, axis=-1), axis=1)
    pos_scenario_idx = 's' if is_future_stocks_with_scenarios else ''
    einsum_op = f'tr{pos_scenario_idx},rg->trg{pos_scenario_idx}'
    future_stocks = np.einsum(f'tr{pos_scenario_idx},rg->trg{pos_scenario_idx}', future_stocks,
                              base_year_category_pctgs)
    return future_stocks
