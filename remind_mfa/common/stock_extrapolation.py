import flodym as fd
import numpy as np
from typing import Tuple, Union, Type
from copy import deepcopy

from remind_mfa.common.data_extrapolations import Extrapolation
from remind_mfa.common.data_transformations import broadcast_trailing_dimensions, BoundList
from remind_mfa.common.assumptions_doc import add_assumption_doc


class StockExtrapolation:
    """
    Class for extrapolating stocks based on historical data and GDP per capita.
    """

    def __init__(
        self,
        historic_stocks: fd.StockArray,
        dims: fd.DimensionSet,
        parameters: dict[str, fd.Parameter],
        stock_extrapolation_class: Type[Extrapolation],
        target_dim_letters: Union[Tuple[str, ...], str] = "all",
        indep_fit_dim_letters: Union[Tuple[str, ...], str] = (),
        bound_list: BoundList = BoundList(),
        do_gdppc_accumulation: bool = True,
        stock_correction: str = "gaussian_first_order",
    ):
        """
        Initialize the StockExtrapolation class.

        Args:
            historic_stocks (fd.StockArray): Historical stock data.
            dims (fd.DimensionSet): Dimension set for the data.
            parameters (dict[str, fd.Parameter]): Parameters for the extrapolation.
            stock_extrapolation_class (Extrapolation): Class used for stock extrapolation.
            target_dim_letters (Union[Tuple[str, ...], str]): Sets the dimensions of the stock extrapolation output. If "all", the output will have the same shape as historic_stocks, except for the time dimension. Defaults to "all".
            indep_fit_dim_letters (Union[Tuple[str, ...]], str): Sets the dimensions across which an individual fit is performed, must be subset of target_dim_letters. If "all", all dimensions given in target_dim_letters are regressed individually. If empty (), all dimensions are regressed aggregately. Defaults to ().
            bound_list (BoundList): List of bounds for the extrapolation. Defaults to an empty BoundList.
            do_gdppc_accumulation (bool): Flag to perform GDP per capita accumulation. Defaults to True.
            stock_correction (str): Method for stock correction. Possible values are "gaussian_first_order", "shift_zeroth_order", "none". Defaults to "gaussian_first_order".
        """
        self.historic_stocks = historic_stocks
        self.dims = dims
        self.parameters = parameters
        self.stock_extrapolation_class = stock_extrapolation_class
        self.target_dim_letters = target_dim_letters
        self.set_dims(indep_fit_dim_letters)
        self.bound_list = bound_list
        self.do_gdppc_accumulation = do_gdppc_accumulation
        self.stock_correction = stock_correction
        self.extrapolate()

    def set_dims(self, indep_fit_dim_letters: Tuple[str, ...]):
        """
        Check target_dim_letters.
        Set fit_dim_letters and check:
        fit_dim_letters should be the same as target_dim_letters, but without the time dimension, except if otherwise defined.
        In this case, fit_dim_letters should be a subset of target_dim_letters.
        This check cannot be performed if self.target_dim_letters or self.fit_dim_letters is None.
        """
        if self.target_dim_letters == "all":
            self.historic_dim_letters = self.historic_stocks.dims.letters
            self.target_dim_letters = ("t",) + self.historic_dim_letters[1:]
        else:
            self.historic_dim_letters = ("h",) + self.target_dim_letters[1:]

        if indep_fit_dim_letters == "all":
            # fit_dim_letters should be the same as target_dim_letters, but without the time dimension
            self.indep_fit_dim_letters = tuple(x for x in self.target_dim_letters if x != "t")
        else:
            self.indep_fit_dim_letters = indep_fit_dim_letters
            if not set(self.indep_fit_dim_letters).issubset(self.target_dim_letters):
                raise ValueError("fit_dim_letters must be subset of target_dim_letters.")
        self.get_fit_idx()

    def get_fit_idx(self):
        """Get the indices of the fit dimensions in the historic_stocks dimensions."""
        self.fit_dim_idx = tuple(
            i
            for i, x in enumerate(self.historic_stocks.dims.letters)
            if x in self.indep_fit_dim_letters
        )

    def extrapolate(self):
        """Preprocessing and extrapolation."""
        self.per_capita_transformation()
        self.gdp_regression()

    def per_capita_transformation(self):
        self.pop = self.parameters["population"]
        self.gdppc = self.parameters["gdppc"]
        if self.do_gdppc_accumulation:
            self.gdppc_acc = np.maximum.accumulate(self.gdppc.values, axis=0)
        self.historic_pop = fd.Parameter(dims=self.dims[("h", "r")])
        self.historic_gdppc = fd.Parameter(dims=self.dims[("h", "r")])
        self.historic_stocks_pc = fd.StockArray(dims=self.dims[self.historic_dim_letters])
        self.stocks_pc = fd.StockArray(dims=self.dims[self.target_dim_letters])
        self.stocks = fd.StockArray(dims=self.dims[self.target_dim_letters])

        self.historic_pop[...] = self.pop[{"t": self.dims["h"]}]
        self.historic_gdppc[...] = self.gdppc[{"t": self.dims["h"]}]
        self.historic_stocks_pc[...] = self.historic_stocks / self.historic_pop

    def gdp_regression(self):
        """Updates per capita stock to future by extrapolation."""

        prediction_out = self.stocks_pc.values.copy()
        historic_in = self.historic_stocks_pc.values
        if self.do_gdppc_accumulation:
            gdppc = self.gdppc_acc
            add_assumption_doc(
                type="model assumption",
                name="Usage of cumulative GDP per capita",
                description=(
                    "Accumulated GDPpc is used for stock extrapolation to prevent "
                    "stock shrink in times of decreasing GDPpc. "
                ),
            )
        else:
            gdppc = self.gdppc
        gdppc = broadcast_trailing_dimensions(gdppc, prediction_out)
        n_historic = historic_in.shape[0]

        n_deriv = 5
        add_assumption_doc(
            type="integer number",
            name="n years for regression derivative correction",
            value=n_deriv,
            description=(
                "Number of historic years used for determination of regressed and actual "
                "growth rates of ins-use stocks, which are then used for a correction "
                "reconciling the two and blending from observed to regression."
            ),
        )

        add_assumption_doc(
            name="synthetic recent GDP for regression correction",
            type="ad-hoc fix",
            description=(
                "GDP per capita SSP curves assume a steady growth after 2025, which in some "
                "regions breaks historic trends. Here, we overwrite recent historic GDP per capita "
                "by extrapolating back from 2025 using the growth rates after 2025. "
                "This creates continuity between the recent historic GDP growth used for the "
                "gaussian correction and the future assumed growth rates and thereby prevents "
                "discontinuities in production."
            ),
        )
        i_2025 = self.dims["t"].index(2025)
        gdppc = deepcopy(gdppc)
        growth = gdppc[i_2025 + 1] / gdppc[i_2025 + 2]
        for i in range(n_deriv + 5):
            gdppc[i_2025 - i, ...] = gdppc[i_2025 - i + 1, ...] * growth

        extrapolation = self.stock_extrapolation_class(
            data_to_extrapolate=historic_in,
            predictor_values=gdppc,
            independent_dims=self.fit_dim_idx,
            bound_list=self.bound_list,
        )
        pure_prediction = extrapolation.regress()

        if self.stock_correction == "gaussian_first_order":
            prediction_out[...] = self.gaussian_correction(historic_in, pure_prediction, n_deriv)
            add_assumption_doc(
                type="model assumption",
                name="Usage of Gaussian correction",
                description=(
                    "Gaussian correction is used to blend histroric trends with the extrapolation."
                ),
            )
        elif self.stock_correction == "shift_zeroth_order":
            # match last point by adding the difference between the last historic point and the corresponding prediction
            prediction_out[...] = pure_prediction - (
                pure_prediction[n_historic - 1, :] - historic_in[n_historic - 1, :]
            )
            add_assumption_doc(
                type="model assumption",
                name="Usage of zeroth order correction",
                description=(
                    "Zeroth order correction is used to match the last historic point with the "
                    "extrapolated stock."
                ),
            )

        # save extrapolation data for later analysis
        self.pure_prediction = fd.FlodymArray(dims=self.stocks_pc.dims, values=pure_prediction)
        parameter_dims: fd.DimensionSet = self.dims[self.indep_fit_dim_letters]
        parameter_names = fd.Dimension(
            name="Parameter Names", letter="p", items=extrapolation.prm_names
        )
        parameter_dims = parameter_dims.expand_by([parameter_names])
        self.pure_parameters = fd.FlodymArray(dims=parameter_dims, values=extrapolation._fit_prms)

        prediction_out[:n_historic, ...] = historic_in
        self.stocks_pc.set_values(prediction_out)

        # transform back to total stocks
        self.stocks[...] = self.stocks_pc * self.pop

    def gaussian_correction(
        self, historic: np.ndarray, prediction: np.ndarray, n: int = 5
    ) -> np.ndarray:
        """
        Gaussian smoothing of extrapolation between the historic and future interface to remove discontinuities
        of 0th and 1st order derivatives. Multiplies Gaussian with a Taylor expansion around
        the difference beteween historic and fit.
        Args:
            historic (np.ndarray): Historical stock data.
            prediction (np.ndarray): Predicted stock data from regression.
            n (int): Number of years for the linear regression fit. Defaults to 5.
        Returns:
            np.ndarray: Corrected stock data after applying Gaussian smoothing.
        """
        time = np.array(self.dims["t"].items)
        last_history_idx = len(historic) - 1
        last_history_year = time[last_history_idx]
        # offset between historic and prediction at transition point
        difference_0th = historic[last_history_idx, :] - prediction[last_history_idx, :]

        def lin_fit(x, y, last_idx, n=n):
            """Linear fit of the last n points."""
            x_cut = np.vstack([x[last_idx - n : last_idx], np.ones(n)]).T
            y_cut = y[last_idx - n : last_idx, :]
            y_reshaped = y_cut.reshape(n, -1).T
            slopes = [np.linalg.lstsq(x_cut, y_dim, rcond=None)[0][0] for y_dim in y_reshaped]
            slopes_reshaped = np.array(slopes).reshape(y.shape[1:])
            return slopes_reshaped

        last_historic_1st = lin_fit(time, historic, last_history_idx)
        last_prediction_1st = lin_fit(time, prediction, last_history_idx)

        # offset of the 1st derivative at the transition point
        difference_1st = (last_historic_1st - last_prediction_1st) / (
            last_history_year - time[last_history_idx - 1]
        )

        def gaussian(t, approaching_time):
            """After the approaching time, the amplitude of the gaussian has decreased to 5%."""
            a = np.sqrt(np.log(20))
            return np.exp(-((a * t / approaching_time) ** 2))

        approaching_time_0th = 50
        add_assumption_doc(
            type="integer number",
            name="years for absolute blending to regression",
            value=approaching_time_0th,
            description=(
                "Number of years for the blending from historical to regressed in-use stocks. "
            ),
        )
        approaching_time_1st = 30
        add_assumption_doc(
            type="integer number",
            name="years for derivative blending to regression",
            value=approaching_time_1st,
            description=(
                "Number of years for the blending from historical to regressed in-use stock "
                "growth rates. "
            ),
        )
        time_extended = time.reshape(-1, *([1] * len(difference_0th.shape)))
        corr0 = difference_0th * gaussian(time_extended - last_history_year, approaching_time_0th)
        corr1 = (
            difference_1st
            * (time_extended - last_history_year)
            * gaussian(time_extended - last_history_year, approaching_time_1st)
        )
        correction = corr0 + corr1

        return prediction[...] + correction
