__author__ = "sibirrer"

# this file contains a class which describes the surface brightness of the light models
# used for the linear solver only

from functools import partial
from jax import jit, lax, numpy as jnp
import numpy as np
from jaxtronomy.LightModel.light_model_base import LightModelBase

__all__ = ["LinearBasis"]


class LinearBasis(LightModelBase):
    """Class to handle source and lens light models."""

    def __init__(self, **kwargs):
        """

        :param kwargs: keyword arguments for LightModelBase class
        """
        super(LinearBasis, self).__init__(**kwargs)

    @partial(jit, static_argnums=(0, 4))
    def functions_split(self, x, y, kwargs_list, k=None):
        """Split model in different components.

        :param x: coordinate in units of arcsec relative to the center of the image
        :param y: coordinate in units of arcsec relative to the center of the image
        :param kwargs_list: keyword argument list of light profile
        :param k: integer or tuple of integers for selecting subsets of light profiles
        """
        response = []
        n = 0
        bool_list = self._bool_list(k=k)
        for i, model in enumerate(self.profile_type_list):
            if bool_list[i] is True:
                if model in [
                    "SERSIC",
                    "SERSIC_ELLIPSE",
                    "SERSIC_ELLIPSE_Q_PHI",
                    "CORE_SERSIC",
                    "HERNQUIST",
                    "HERNQUIST_ELLIPSE",
                    "PJAFFE",
                    "PJAFFE_ELLIPSE",
                    "GAUSSIAN",
                    "GAUSSIAN_ELLIPSE",
                    "POWER_LAW",
                    "NIE",
                    "CHAMELEON",
                    "DOUBLE_CHAMELEON",
                    "TRIPLE_CHAMELEON",
                    "UNIFORM",
                    "INTERPOL",
                    "ELLIPSOID",
                    "LINEAR",
                    "LINEAR_ELLIPSE",
                    "LINE_PROFILE",
                ]:
                    kwargs_new = kwargs_list[i].copy()
                    new = {"amp": 1}
                    kwargs_new.update(new)
                    response += [self.func_list[i].function(x, y, **kwargs_new)]
                    n += 1
                elif model in ["MULTI_GAUSSIAN", "MULTI_GAUSSIAN_ELLIPSE"]:
                    num = len(kwargs_list[i]["sigma"])
                    new = {"amp": np.ones(num)}
                    kwargs_new = kwargs_list[i].copy()
                    kwargs_new.update(new)
                    response += self.func_list[i].function_split(x, y, **kwargs_new)
                    n += num
                elif model in [
                    "SHAPELETS",
                    "SHAPELETS_POLAR",
                    "SHAPELETS_POLAR_EXP",
                    "SHAPELETS_ELLIPSE",
                ]:
                    num_param = self.func_list[i].num_param
                    new = {"amp": np.ones(num_param)}
                    kwargs_new = kwargs_list[i].copy()
                    kwargs_new.update(new)
                    response += self.func_list[i].function_split(x, y, **kwargs_new)
                    n += num_param
                # elif model in ["SLIT_STARLETS", "SLIT_STARLETS_GEN2"]:
                #     raise ValueError(
                #         "'{}' model does not support function split".format(model)
                #     )
                else:
                    raise ValueError("model type %s not valid!" % model)
        return response, n

    @partial(jit, static_argnums=(0, 2))
    def num_param_linear(self, kwargs_list, list_return=False):
        """

        :param kwargs_list: list of keyword arguments of the light profiles
        :param list_return: bool, if True returns list of individual number of parameters
        :return: number of linear basis set coefficients
        """
        n_list = self.num_param_linear_list(kwargs_list)
        if not list_return:
            return jnp.sum(jnp.array(n_list))
        return n_list

    @partial(jit, static_argnums=(0,))
    def num_param_linear_list(self, kwargs_list):
        """Returns the list (in order of the light profiles) of the number of linear
        components per model.

        :param kwargs_list: list of keyword arguments of the light profiles
        :return: number of linear basis set coefficients
        """
        n_list = []
        for i, model in enumerate(self.profile_type_list):
            if model in [
                "SERSIC",
                "SERSIC_ELLIPSE",
                "CORE_SERSIC",
                "HERNQUIST",
                "HERNQUIST_ELLIPSE",
                "PJAFFE",
                "PJAFFE_ELLIPSE",
                "GAUSSIAN",
                "GAUSSIAN_ELLIPSE",
                "POWER_LAW",
                "NIE",
                "CHAMELEON",
                "DOUBLE_CHAMELEON",
                "TRIPLE_CHAMELEON",
                "UNIFORM",
                "INTERPOL",
                "ELLIPSOID",
                "LINEAR",
                "LINEAR_ELLIPSE",
                "LINE_PROFILE",
            ]:
                n_list += [1]
            elif model in ["MULTI_GAUSSIAN", "MULTI_GAUSSIAN_ELLIPSE"]:
                num = len(kwargs_list[i]["sigma"])
                n_list += [num]
            elif model in [
                "SHAPELETS",
                "SHAPELETS_POLAR",
                "SHAPELETS_POLAR_EXP",
                "SHAPELETS_ELLIPSE",
            ]:
                num_param = self.func_list[i].num_param
                n_list += [num_param]
            # elif model in ["SLIT_STARLETS", "SLIT_STARLETS_GEN2"]:
            #     n_scales = kwargs_list[i]["n_scales"]
            #     n_pixels = kwargs_list[i]["n_pixels"]
            #     num_param = int(n_scales * n_pixels)
            #     n_list += [
            #         num_param
            #     ]  # TODO : find a way to make it the number of source pixels
            else:
                raise ValueError("model type %s not valid!" % model)
        return n_list

    @partial(jit, static_argnums=(0,))
    def update_linear(self, param, i, kwargs_list):
        """

        :param param: array of linear amplitude coefficients in the order of the linear minimization of the ImSim module
        :param i: index of first coefficient to start reading out the linear parameters associated with the model
         components of this class
        :param kwargs_list: list of keyword arguments of the model components
        :return: kwargs list with over-written or added 'amp' parameters according to the coefficients in param
        """
        param = jnp.asarray(param)
        for k, model in enumerate(self.profile_type_list):
            if model in [
                "SERSIC",
                "SERSIC_ELLIPSE",
                "SERSIC_ELLIPSE_Q_PHI",
                "CORE_SERSIC",
                "HERNQUIST",
                "PJAFFE",
                "PJAFFE_ELLIPSE",
                "HERNQUIST_ELLIPSE",
                "GAUSSIAN",
                "GAUSSIAN_ELLIPSE",
                "POWER_LAW",
                "NIE",
                "CHAMELEON",
                "DOUBLE_CHAMELEON",
                "TRIPLE_CHAMELEON",
                "UNIFORM",
                "INTERPOL",
                "ELLIPSOID",
                "LINEAR",
                "LINEAR_ELLIPSE",
                "LINE_PROFILE",
            ]:
                kwargs_list[k]["amp"] = param.at[i].get()
                i += 1
            elif model in ["MULTI_GAUSSIAN", "MULTI_GAUSSIAN_ELLIPSE"]:
                num_param = len(kwargs_list[k]["sigma"])
                kwargs_list[k]["amp"] = lax.dynamic_slice(param, [i], (num_param,))
                i += num_param
            elif model in [
                "SHAPELETS",
                "SHAPELETS_POLAR",
                "SHAPELETS_POLAR_EXP",
                "SHAPELETS_ELLIPSE",
            ]:
                num_param = self.func_list[k].num_param
                kwargs_list[k]["amp"] = lax.dynamic_slice(param, [i], (num_param,))
                i += num_param
            # elif model in ["SLIT_STARLETS", "SLIT_STARLETS_GEN2"]:
            #     n_scales = kwargs_list[k]["n_scales"]
            #     n_pixels = kwargs_list[k]["n_pixels"]
            #     num_param = int(n_scales * n_pixels)
            #     kwargs_list[k]["amp"] = lax.dynamic_slice(param, [i], (num_param,))
            #     i += num_param
            else:
                raise ValueError("model type %s not valid!" % model)
        return kwargs_list, i

    # This function is called in the initialization of LightParam, outside of JIT
    def add_fixed_linear(self, kwargs_fixed_list):
        """

        :param kwargs_fixed_list: list of fixed keyword arguments
        :return: updated kwargs_fixed_list with additional linear parameters being fixed.
        """
        for k, model in enumerate(self.profile_type_list):
            kwargs_fixed = kwargs_fixed_list[k]
            param_names = self.param_name_list[k]
            if "amp" in param_names:
                if "amp" not in kwargs_fixed:
                    kwargs_fixed["amp"] = 1
        return kwargs_fixed_list

    @partial(jit, static_argnums=0)
    def linear_param_from_kwargs(self, kwargs_list):
        """Inverse function of update_linear() returning the linear amplitude list for
        the keyword argument list.

        :param kwargs_list: model parameters including the linear amplitude parameters
        :type kwargs_list: list of keyword arguments
        :return: list of linear amplitude parameters
        :rtype: list
        """
        param = []
        for k, model in enumerate(self.profile_type_list):
            kwargs_ = kwargs_list[k]
            param_names = self.param_name_list[k]
            if "amp" in param_names:
                amp = kwargs_["amp"]
                amp_list = jnp.atleast_1d(amp)
                for a in amp_list:
                    param.append(a)
        return param

    @partial(jit, static_argnums=0)
    def check_positive_flux_profile(self, kwargs_list):
        """Check whether linear amplitude parameter are non-negative for specified list
        of lens models that have a physical amplitude interpretation.

        :param kwargs_list: light model parameter keyword argument list
        :return: bool, if True, no specified model has negative flux
        """
        pos_bool = True
        for k, model in enumerate(self.profile_type_list):
            if "amp" in kwargs_list[k]:
                if model in [
                    "SERSIC",
                    "SERSIC_ELLIPSE",
                    "CORE_SERSIC",
                    "HERNQUIST",
                    "PJAFFE",
                    "PJAFFE_ELLIPSE",
                    "HERNQUIST_ELLIPSE",
                    "GAUSSIAN",
                    "GAUSSIAN_ELLIPSE",
                    "POWER_LAW",
                    "NIE",
                    "CHAMELEON",
                    "DOUBLE_CHAMELEON",
                ]:
                    pos_bool = jnp.where(kwargs_list[k]["amp"] < 0, False, pos_bool)
        return pos_bool
