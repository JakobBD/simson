import numpy as np
from math import sqrt, pi, e
from sodym.classes.named_dim_arrays import NamedDimArray

def calc_steel_hist_stk_inflow(production, sector_splits, gi_distribution,
                               lifetime_mean, lifetime_std,
                               forming_yield, fabrication_yield, population):

    big_Y = 1 / np.einsum('g,gi,i->g', 1 / fabrication_yield, gi_distribution, 1 / forming_yield)
    trade=np.zeros((201,12,19))
    indirect_trade=np.zeros((201,12,4))
    sector_splits=sector_splits[:123]

    direct_trade_in_goods = distribute_intermediate_good(trade, 'tri', gi_distribution)
    agg_trade = np.einsum('trg,g->trg', direct_trade_in_goods, fabrication_yield) + indirect_trade

    lifetime_matrix = calc_lifetime_matrix(lifetime_mean, lifetime_std)
    l = np.einsum('trd,turg->turgd', sector_splits, 1 - lifetime_matrix)  # here 'u' denotes t_dash / t'
    d_0_dividend = l[0, 0]
    d_0 = np.einsum('rgd,rdg->rgd', d_0_dividend, 1 / d_0_dividend)
    initial_indirect_trade = np.repeat(np.expand_dims(agg_trade[0], axis=2), 4, axis=2)
    b_0_dividend = initial_indirect_trade * d_0 - np.swapaxes(initial_indirect_trade, 1, 2)
    b_0_divisor = np.einsum('r,g->rg', production[0], big_Y)
    b_0 = np.einsum('rgd,rd->rgd', b_0_dividend, 1 / b_0_divisor)
    b_0 = np.sum(b_0, axis=2)
    m_0_dividend = np.einsum('g,rgd->rgd', big_Y, d_0)
    m_0 = np.einsum('rgd,d->rgd', m_0_dividend, 1 / big_Y)
    m_0 = np.sum(m_0, axis=2)
    x_0 = (1 - b_0) / m_0
    x_0 = _adapt_x_t_to_avoid_negatives(x_0, agg_trade[0], production[0], big_Y)
    x_0 = _transform_x_from_g_to_i(x_0, production[0], big_Y, fabrication_yield, gi_distribution, forming_yield)

    i_0_prep = np.einsum('r,ri,i->ri', production[0], x_0, forming_yield)
    i_0_prep = distribute_intermediate_good(i_0_prep, 'ri', gi_distribution)
    i_0 = np.einsum('rg,g->rg', i_0_prep, fabrication_yield) + agg_trade[0]

    inflows = np.zeros_like(indirect_trade)
    inflows[0] = i_0
    production_sector_split = np.zeros((indirect_trade.shape[0],) + x_0.shape)
    production_sector_split[0] = x_0

    for t in range(1, 123):
        p = production[t]
        s_prepare = np.einsum('trg,trg->trg', inflows[:t], lifetime_matrix[t, :t])
        s_prepare = np.sum(s_prepare, axis=0)
        c = sector_splits[t]
        at = agg_trade[t]
        lt = lifetime_matrix[t, t]

        m_1 = p * big_Y[0] * (1 - lt[:, 0])
        m_2 = np.einsum('r,rg->rg', m_1, c)
        m_3 = np.einsum('rg,r->rg', m_2, 1 / c[:, 0])
        m_4 = np.einsum('rg,r,g->rg', (1 - lt), p, big_Y)
        m = m_3 / m_4

        b_1 = (at[:, 0] * (1 - lt[:, 0]) - s_prepare[:, 0]) / c[:, 0]
        b_2 = np.einsum('r,rg->rg', b_1, c)
        b_3 = b_2 + s_prepare
        b_4 = m_4
        b_5 = b_3 / b_4
        b_6 = np.einsum('rg,r,g->rg', at, 1 / p, 1 / big_Y)
        b = b_5 - b_6

        x_1 = (1 - np.sum(b, axis=1)) / np.sum(m, axis=1)
        x_t = np.einsum('r,rg->rg', x_1, m) + b

        x_t = _adapt_x_t_to_avoid_negatives(x_t, at, p, big_Y)

        x_t = _transform_x_from_g_to_i(x_t, p, big_Y, fabrication_yield, gi_distribution, forming_yield)

        production_sector_split[t] = x_t

        i_t_prep = np.einsum('r,ri,i->ri', p, x_t, forming_yield)
        i_t_prep = distribute_intermediate_good(i_t_prep, 'ri', gi_distribution)
        i_t = np.einsum('rg,g->rg', i_t_prep, fabrication_yield) + at

        inflows[t] = i_t

        p_test0 = np.einsum('rg,g,gi,i->r',
                            i_t - agg_trade[t],
                            1 / fabrication_yield,
                            gi_distribution,
                            1 / forming_yield)
        p_test1 = np.einsum('ri,i->r',
                            np.einsum('rg,g,gi->ri',
                                      i_t - indirect_trade[t],
                                      1 / fabrication_yield,
                                      gi_distribution) -
                            trade[t],
                            1 / forming_yield)
        p_test2 = p_test1 - production[t]
        p_test3 = np.all(np.abs(p_test2) < 2)
        p_test4 = p_test0 - production[t]
        p_test5 = np.all(np.abs(p_test4) < 2)
        if not p_test3 or not p_test5:
            a = 0

    p_test0 = np.einsum('trg,g,gi,i->tr',
                        inflows - agg_trade,
                        1 / fabrication_yield,
                        gi_distribution,
                        1 / forming_yield)
    p_test1 = np.einsum('tri,i->tr',
                        np.einsum('trg,g,gi->tri',
                                  inflows - indirect_trade,
                                  1 / fabrication_yield,
                                  gi_distribution) -
                        trade,
                        1 / forming_yield)
    p_test2 = p_test1[:123] - production
    p_test3 = np.all(np.abs(p_test2) < 4)
    p_test4 = p_test0[:123] - production
    p_test5 = np.all(np.abs(p_test4) < 4)

    if not p_test3 or not p_test5:
        print('Fail')

    inflows[np.logical_and(inflows < 0,
                           inflows > -0.1)] = 0  # make inflows which are -0 or otherwise slightly negative positive 0

    p_test0 = np.einsum('trg,g,gi,i->tr',
                        inflows - agg_trade,
                        1 / fabrication_yield,
                        gi_distribution,
                        1 / forming_yield)
    p_test1 = np.einsum('tri,i->tr',
                        np.einsum('trg,g,gi->tri',
                                  inflows - indirect_trade,
                                  1 / fabrication_yield,
                                  gi_distribution) -
                        trade,
                        1 / forming_yield)
    p_test2 = p_test1[:123] - production
    p_test3 = np.all(np.abs(p_test2) < 4)
    p_test4 = p_test0[:123] - production
    p_test5 = np.all(np.abs(p_test4) < 4)

    if not p_test3 or not p_test5:
        print('Fail')

    outflows = [np.einsum('trg,trg->rg', inflows[:t+1], lifetime_matrix[t, :t+1]) for t in range(123)]
    outflows = np.array(outflows)
    stock_change = inflows[:123] - outflows
    stocks = np.cumsum(stock_change, axis=0)

    stocks_pc = np.einsum('trg,tr->tr', stocks, 1/ population[:123, :, 1])

    last_stocks = stocks_pc[-1]

    return inflows


def _adapt_x_t_to_avoid_negatives(x_t, at, p, big_Y):
    min_x = np.einsum('rg,r,g->rg', -at, 1 / p, 1 / big_Y)
    min_x = np.maximum(0, min_x)  # x should also never be zero
    if np.any(x_t < min_x):
        for region_idx in range(x_t.shape[0]):
            # TODO: avoid for loop
            xtr = x_t[region_idx]
            minxr = min_x[region_idx]
            if np.any(xtr < minxr):
                diff = xtr - minxr
                neg_pcts = np.minimum(0, diff)
                pos_pcts = np.maximum(0, diff)
                sum_factor = np.abs(np.sum(pos_pcts) / np.sum(neg_pcts))
                xtr = xtr - diff / sum_factor
                xtr[xtr < minxr] = minxr[xtr < minxr]
                x_t[region_idx] = xtr
    return x_t


def _transform_x_from_g_to_i(x, production, big_Y, fabrication_yield, gi_distribution, forming_yield):
    fabrication = np.einsum('r,rg,g->rg', production, x, big_Y)
    p_x = np.einsum('rg,g,gi,i->ri', fabrication, 1 / fabrication_yield, gi_distribution, 1 / forming_yield)
    x_result = np.einsum('ri,r->ri', p_x, 1 / np.sum(p_x, axis=1))

    return x_result


def distribute_intermediate_good(data: np.ndarray, dimensions: str, gi_distribution=None, do_test=True):  # TODO test?

    # choose linked IP categories
    i_index = dimensions.index('i')
    result = np.moveaxis(data, i_index, 0)
    result = np.array([result[12] / gi_distribution[0, 12],
                       result[6] / gi_distribution[1, 6],
                       result[1] / gi_distribution[2, 1],
                       result[2] / gi_distribution[3, 2]])
    result = np.moveaxis(result, 0, i_index)
    if do_test:
        new_dimensions = dimensions[:i_index] + 'g' + dimensions[i_index + 1:]
        reverse_data = np.einsum(f'{new_dimensions},gi->{dimensions}', result, gi_distribution)
        comparison = data - reverse_data
        test_passed = np.all(comparison < 1)
        if not test_passed:
            raise Exception('Something went wrong when distributing intermediate products to in-use goods.')
    return result


def calc_lifetime_matrix(mean, std_dev, n_years=123):
    t = np.arange(0, n_years)
    t_dash = np.arange(0, n_years)
    t_matrix = np.subtract.outer(t, t_dash)
    n_regions = 12
    new_t_matrix_shape = t_matrix.shape + (n_regions, 4)
    t_matrix = np.broadcast_to(np.expand_dims(t_matrix, axis=(2, 3)), new_t_matrix_shape)
    exponent = -(t_matrix - mean) ** 2 / (2 * std_dev ** 2)
    lifetime_matrix = 1 / (sqrt(2) * pi * std_dev) * e ** exponent

    # only use lower triangle of lifetime matrix as 'past' lifetimes of inflows are irrelevant
    tri = np.tri(*lifetime_matrix.shape[:2])
    lifetime_matrix = np.einsum('turg,tu->turg', lifetime_matrix, tri)

    return lifetime_matrix
