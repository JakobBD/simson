from sodym.classes.mfa_system import MFASystem
from sodym.classes.stocks_in_mfa import StockWithDSM
from src.model_extensions.extrapolate_stock import extrapolate_stock


class InflowDrivenHistoric_StockDrivenFuture(MFASystem):
    """
    Extension of the MFASystem class to calculate in-use stock based on historic production data,
    which is extrapolated to future years based on GDP pC.

    Assumes dimensions
    - time (t) or historic time (h)
    - region (r)
    - good (g)
    """

    def compute_in_use_stock(self):
        hist_stk = self.compute_historic_from_demand()
        stock = self.get_extrapolation(hist_stk.stock)
        stk = self.compute_future_demand(stock)
        self.transfer_to_mfa_stock(stk)
        # if cfg.do_visualize["future_production"]:
        #     visualize_future_production(dsms, production)
        return

    def compute_historic_from_demand(self):

        prm = self.parameters
        hist_stk = self.get_new_stock(with_dsm=True, dim_letters=('h','r','g'))

        hist_stk.inflow[...] = prm['production']
        hist_stk.set_lifetime(self.ldf_type, prm['lifetime_mean'], prm['lifetime_std'])

        hist_stk.compute_inflow_driven()

        return hist_stk

    def get_extrapolation(self, historic_stocks):
        """
        Interfaces to the extrapolation function, by performing the per-capita transformation and the
        NamedDimArray <-> numpy array transformation.
        """

        # transform to per capita
        pop = self.parameters['population']
        transform_t_thist  = self.get_subset_transformer(('t', 'h'))
        historic_pop       = self.get_new_array(dim_letters=('h','r'))
        historic_gdppc     = self.get_new_array(dim_letters=('h','r'))
        historic_stocks_pc = self.get_new_array(dim_letters=('h','r','g'))
        stocks_pc          = self.get_new_array(dim_letters=('t','r','g'))
        stocks             = self.get_new_array(dim_letters=('t','r','g'))

        historic_pop[...] = pop * transform_t_thist
        historic_gdppc[...] = self.parameters['gdppc'] * transform_t_thist
        historic_stocks_pc[...] = historic_stocks / historic_pop

        extrapolate_stock(
            curve_strategy=self.curve_strategy,
            historic_stocks=historic_stocks_pc.values,
            gdppc=self.parameters['gdppc'].values,
            prediction_out=stocks_pc.values
        )

        # transform back to total stocks
        stocks[...] = stocks_pc * pop

        #visualize_stock(self, self.parameters['gdppc'], historic_gdppc, stocks, historic_stocks, stocks_pc, historic_stocks_pc)

        return stocks

    def compute_future_demand(self, stock):
        prm = self.parameters
        stk = self.get_new_stock(with_dsm=True, dim_letters=('t','r','g'))

        stk.stock[...] = stock
        stk.set_lifetime(self.ldf_type, prm['lifetime_mean'], prm['lifetime_std'])

        stk.compute_stock_driven()

        return stk

    def transfer_to_mfa_stock(self, stk: StockWithDSM):
        # We use an auxiliary stock for the prediction step to save dimensions and computation time
        # Therefore, we have to transfer the result to the higher-dimensional stock in the MFA system
        prm = self.parameters
        self.stocks['in_use'].stock[...]   = stk.stock * prm['material_shares_in_goods'] * prm['carbon_content_materials']
        self.stocks['in_use'].inflow[...]  = stk.inflow * prm['material_shares_in_goods'] * prm['carbon_content_materials']
        self.stocks['in_use'].outflow[...] = stk.outflow * prm['material_shares_in_goods'] * prm['carbon_content_materials']
        return
