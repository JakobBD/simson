import numpy as np
import scipy.optimize

def extrapolate_stock(curve_strategy, historic_stocks, gdppc, prediction_out):
    """
    wrapper to choose extrapolation strategy from config
    """
    if curve_strategy == "GDP_regression":
        gdp_regression(historic_stocks,
                       gdppc,
                       prediction_out)
    else:
        raise RuntimeError(f"Prediction strategy {curve_strategy} is not defined. "
                        f"It needs to be 'GDP_regression'.")
    return


def gdp_regression(historic_stocks_pc, gdppc, prediction_out):

    shape_out = prediction_out.shape
    assert len(shape_out) == 3, "Prediction array must have 3 dimensions: Time, Region, Good"
    pure_prediction = np.zeros_like(prediction_out)
    n_historic = historic_stocks_pc.shape[0]
    i_lh = n_historic - 1

    for i_region in range(shape_out[1]):
        for i_good in range(shape_out[2]):
            def fitting_function(prms):
                return prms[0] / (1. + np.exp(prms[1]/gdppc[:n_historic,i_region])) - historic_stocks_pc[:,i_region,i_good]
                        # Lagrangian multiplier to ensure matching last point:
                        # + prms[2] * prms[0] / (1. + np.exp(prms[1]/gdppc[i_lh,0])) - stocks_pc[-1,0,i] )
            prms_out = scipy.optimize.least_squares(fitting_function, x0=np.array([2.*gdppc[i_lh,i_region],historic_stocks_pc[-1,i_region,i_good]]), gtol=1.e-12)
            assert prms_out.success

            pure_prediction[:,i_region,i_good] = prms_out.x[0] / (1. + np.exp(prms_out.x[1]/gdppc[:,i_region]))

        # def fitting_function(prms):
        #     return 2.*gdppc[i_lh,0] / (1. + np.exp(prms[0]/gdppc[cfg.i_historic,0])) - stocks_pc[:,0,i]
        # prms_out = scipy.optimize.least_squares(fitting_function, x0=np.array([stocks_pc[-1,0,i]]))
        # prediction = 2.*gdppc[i_lh,0] / (1. + np.exp(prms_out.x[0]/gdppc[:,0]))

    # fit b to last historic value
    prediction_out[...] = pure_prediction - (pure_prediction[i_lh,:,:] - historic_stocks_pc[i_lh,:,:])
    prediction_out[:n_historic,:,:] = historic_stocks_pc

    # if cfg.do_visualize["stock_prediction"]:
    #     visualize_stock_prediction(gdppc, historic_stocks_pc, pure_prediction)
    return

