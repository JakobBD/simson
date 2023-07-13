import os
import pandas as pd
from numpy import nan
from src.read_data.read_REMIND_regions import get_region_to_countries_df
from src.tools.config import cfg
from src.tools.tools import read_processed_data


def load_un_pop(country_specific : bool):
    if country_specific:
        return _load_un_pop_countries()
    else: # region specific
        return _load_un_pop_regions()

# -- MAIN PUBLIC DATA LOADING FUNCTIONS --


def _load_un_pop_regions():
    pop_regions_path = os.path.join(cfg.data_path, 'processed', 'UN_pop_regions.csv')
    if os.path.exists(pop_regions_path) and not cfg.recalculate_data:
        df = read_processed_data(pop_regions_path)
    else:  # recalculate and store
        df = _group_country_data_to_regions()
        df.to_csv(pop_regions_path)
    return df


def _load_un_pop_countries():
    pop_countries_path = os.path.join(cfg.data_path, 'processed', 'UN_pop_countries.csv')
    if os.path.exists(pop_countries_path) and not cfg.recalculate_data:
        df = read_processed_data(pop_countries_path)
    else:  # recalculate and store
        df = _get_pop_countries()
        df.to_csv(pop_countries_path)
    return df


# -- FORMATTING DATA FUNCTIONS --


def _get_pop_countries():
    # load and merge current and future datasets

    df_pop_1900 = _read_1900_world_pop()
    df_1950 = _read_pop_1950_original()
    df_2022 = _read_pop_2022_original()
    df = pd.merge(df_1950, df_2022, on='country')
    df = df.set_index('country')
    df = df.mul(1000)  # as data is given in thousands, multiply by 1000

    # add past prediction

    df_1900 = _get_pop_past_prediction(df, df_pop_1900)
    df = pd.merge(df_1900, df, on='country')
    return df


def _get_pop_past_prediction(df, df_pop_1900):
    df_percentages = _get_1900_1949_percentages_of_1950_world_population(df_pop_1900)
    df_1950 = pd.DataFrame(df[1950])
    df_1950 = df_1950.rename(columns={1950: 'percentages'})  # column needs to be renamed for dot product

    df_1900 = df_1950.dot(df_percentages)
    df_1900 = df_1900.astype('int')

    return df_1900


def _get_1900_1949_percentages_of_1950_world_population(df_pop_1900):
    years = range(1900, 1951)
    world_pop_1950 = df_pop_1900.loc[1950][0]
    percentages = [df_pop_1900.loc[year][0] / world_pop_1950 if year in df_pop_1900.index else nan for year in years]
    df_percentages = pd.DataFrame.from_dict({
        'year': years,
        'percentages': percentages
    })
    df_percentages.interpolate(inplace=True)
    df_percentages.set_index('year', inplace=True)
    df_percentages.drop(1950, inplace=True)
    df_percentages = df_percentages.transpose()

    return df_percentages


# -- READ RAW/ORIGINAL DATA FUNCTIONS --

def _read_1900_world_pop():
    pop_1900_path = os.path.join(cfg.data_path, 'original', 'UN', "UN_Population_1900-1950.csv")
    df_pop_1900 = pd.read_csv(pop_1900_path)
    df_pop_1900.set_index('year', inplace=True)

    return df_pop_1900


def _read_pop_1950_original():
    # load population data 1950-2021

    pop_1950_path = os.path.join(cfg.data_path, 'original', 'UN', "UN_Population_1950-2021.xlsx")
    df_pop_1950 = pd.read_excel(pop_1950_path,
                                engine='openpyxl',
                                sheet_name='Estimates',
                                skiprows=16,
                                usecols=['ISO3 Alpha-code', 'Year', 'Total Population, as of 1 January (thousands)'])
    df_pop_1950.dropna(inplace=True)
    df_pop_1950.rename(columns={
        'ISO3 Alpha-code': 'country',
        'Year': 'year',
        'Total Population, as of 1 January (thousands)': 'population'
    }, inplace=True)

    # change to horizontal format
    df_pop_1950 = df_pop_1950.pivot(index='country', columns='year', values='population')

    # change year columns from float to int
    df_pop_1950.columns = df_pop_1950.columns.astype(int)

    return df_pop_1950


def _read_pop_2022_original():
    # population predictions 2022-2100

    pop_2022_path = os.path.join(cfg.data_path, 'original', 'UN', "UN_Population_2022-2100.xlsx")
    df_pop_2022 = pd.read_excel(pop_2022_path,
                                engine='openpyxl',
                                sheet_name='Median',
                                usecols="F,K:CK",
                                skiprows=16)

    df_pop_2022.dropna(inplace=True)
    df_pop_2022.rename(columns={'ISO3 Alpha-code': 'country'}, inplace=True)

    return df_pop_2022


# -- HELP FUNCTIONS --

def _group_country_data_to_regions():
    """
    Function needs to be seperately implemented (next to tools.py grouping function
    to avoid circular import error.
    """
    df_by_country = _load_un_pop_countries()
    regions = get_region_to_countries_df()
    df = pd.merge(regions, df_by_country, on='country')
    df = df.groupby('region').sum(numeric_only=False)

    return df


# -- TEST FILE FUNCTION --

def _test():
    regions = _load_un_pop_regions()
    countries = _load_un_pop_countries()
    print("Regions: ")
    print(regions)
    print("\nCountries: ")
    print(countries)


if __name__ == "__main__":
    _test()
