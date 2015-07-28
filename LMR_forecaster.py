from abc import ABCMeta, abstractmethod
import numpy as  np

import pylim.LIM as LIM
import pylim.DataTools as DT
from LMR_utils2 import class_docs_fixer, augment_docstr, regrid_sphere


class BaseForecaster:
    """
    Class defining methods for LMR forecasting
    """

    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def forecast(self, t0_data):
        """
        Perform forecast

        Parameters
        ----------
        t0_data: ndarray-like
            Initial data to forecast from (stateDim x nens)

        Returns
        -------
        ndarray-like
            Forecast results (stateDim x nens)
        :return:
        """
        pass


@class_docs_fixer
class LIMForecaster:
    """
    Linear Inverse Model Forecaster
    """

    def __init__(self, config):
        cfg = config.forecaster.LIM
        infile = cfg.calib_filename
        varname = cfg.calib_varname
        fmt = cfg.dataformat

        if fmt == 'NCD':
            data_obj = DT.netcdf_to_data_obj(infile, varname, force_flat=False)
        else:
            raise TypeError('Unsupported calibration data'
                            ' type for LIM: {}'.format(fmt))

        coords = data_obj.get_dim_coords(['lat', 'lon', 'time'])

        # TODO: May want to tie this more into LMR regridding
        # Truncate the calibration data
        lat_new, lon_new, dat_new = regrid_sphere(len(coords['lat'][1]),
                                                  len(coords['lon'][1]),
                                                  len(coords['time'][1]),
                                                  data_obj.data,
                                                  42)

        new_coords = {'time': coords['time'],
                      'lat': (1, lat_new[:, 0]),
                      'lon': (2, lon_new[0])}

        calib_obj = DT.BaseDataObject(dat_new, dim_coords=new_coords,
                                      force_flat=True)

        self.lim = LIM(calib_obj, cfg.wsize, cfg.fcast_times,
                       cfg.fcast_num_pcs, detrend_data=cfg.detrend)

    def forecast(self, t0_data):

        # dummy time coordinate
        time_coord = {'time': (0, range(t0_data.shape[1]))}
        fcast_obj = DT.BaseDataObject(t0_data.T, dim_coords=time_coord,
                                      force_flat=True)

        fcast, eofs = self.lim.forecast(fcast_obj)

        # return physical forecast (dimensions of stateDim x nens)
        return np.dot(eofs, fcast)


_forecaster_classes = {'lim': LIMForecaster}


def get_forecaster_class(key):
    """
    Retrieve forecaster class type to be instantiated.

    Parameters
    ----------
    key: str
        Dict key to retrieve correct Forecaster class type.

    Returns
    -------
    BaseForecaster-like:
        Forecaster class to be instantiated
    """
    return _forecaster_classes[key]



