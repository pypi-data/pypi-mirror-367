import numpy as np
import xarray as xr
import pytest
import datetime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature import BORDERS
import datetime as dtmod

import src.general_tamsat_alert as gta


def make_example_forecast(init_date, poi_start_date, poi_end_date, field_name, datafile, period=12, scale=0.1,
                          do_increments=1, weights_flag=0, weighting_strength=1):
    # poi_clim = calc_poi_clim(datafile, poi_start_date, poi_end_date, field_name)
    # poi_obs = calc_poi_obs(datafile, poi_start_date, poi_end_date, field_name)

    vmin = scale * -1
    vmax = scale
    nrows = 1
    ncols = 1
    lons = xr.open_dataset(datafile)['lon'].values
    lats = xr.open_dataset(datafile)['lat'].values

    forecast_xr = gta.do_forecast(datafile=datafile, field_name=field_name, init_date=init_date,
                                  poi_start=poi_start_date, poi_end=poi_end_date, period=period,
                                  do_increments=do_increments, weights_flag=weights_flag,
                                  weighting_strength=weighting_strength, weighting_data_file='oni.data')
    ens_mean_orig = forecast_xr['ens_mean']
    # plt.clf()
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
                            subplot_kw={'projection': ccrs.PlateCarree()},
                            figsize=(5, 5))

    plt.pcolormesh(lons, lats, forecast_xr['ens_mean'], cmap='BrBG')
    plt.colorbar(orientation='horizontal')
    plt.title('Ensemble mean\nInitiation: ' + init_date.strftime("%Y/%m") + str('\n POI ') \
              + poi_start_date.strftime("%Y/%m") + '-' + poi_end_date.strftime("%Y/%m"))

    axs.coastlines()
    axs.add_feature(BORDERS, lw=2)

    return forecast_xr

def test_bug():
    datafile = "drought-model-driving-data_senegal_19830101-present_0.05.nc"

    yearin = 2011
    init_month = 7
    init_date = dtmod.datetime(yearin, init_month, 1)
    poi_start_date = dtmod.datetime(yearin, 7, 1)  # For now keep the forecast init in the same year as the poi
    poi_end_date = dtmod.datetime(yearin, 8, 1)
    field_name = 'ndvi'
    period = 24

    make_example_forecast(init_date, poi_start_date, poi_end_date, field_name,
                                                              datafile, period=24, scale=0.25, do_increments=1,
                                                              weights_flag=0, weighting_strength=1)
    make_example_forecast(init_date, poi_start_date, poi_end_date, field_name,
                          datafile, period=24, scale=0.25, do_increments=0,
                          weights_flag=0, weighting_strength=1)
    plt.show()
