__author__ = "sibirrer"

# this file contains a class which describes the surface brightness of the light models

from lenstronomy.Util.util import convert_bool_list
from jax import jit, numpy as jnp
from lenstronomy.Conf import config_loader
from functools import partial

convention_conf = config_loader.conventions_conf()
sersic_major_axis_conf = convention_conf.get("sersic_major_axis", False)

__all__ = ["LightModelBase"]

_JAXXED_MODELS = [
    "CORE_SERSIC",
    "GAUSSIAN",
    "GAUSSIAN_ELLIPSE",
    "MULTI_GAUSSIAN",
    "MULTI_GAUSSIAN_ELLIPSE",
    "SERSIC",
    "SERSIC_ELLIPSE",
    "SERSIC_ELLIPSE_Q_PHI",
    "SHAPELETS",
]

_MODELS_SUPPORTED = [
    "GAUSSIAN",
    "GAUSSIAN_ELLIPSE",
    "ELLIPSOID",
    "MULTI_GAUSSIAN",
    "MULTI_GAUSSIAN_ELLIPSE",
    "SERSIC",
    "SERSIC_ELLIPSE",
    "SERSIC_ELLIPSE_Q_PHI",
    "CORE_SERSIC",
    "SHAPELETS",
    "SHAPELETS_POLAR",
    "SHAPELETS_POLAR_EXP",
    "SHAPELETS_ELLIPSE",
    "HERNQUIST",
    "HERNQUIST_ELLIPSE",
    "PJAFFE",
    "PJAFFE_ELLIPSE",
    "UNIFORM",
    "POWER_LAW",
    "NIE",
    "CHAMELEON",
    "DOUBLE_CHAMELEON",
    "TRIPLE_CHAMELEON",
    "INTERPOL",
    "SLIT_STARLETS",
    "SLIT_STARLETS_GEN2",
    "LINEAR",
    "LINEAR_ELLIPSE",
    "LINE_PROFILE",
]


class LightModelBase(object):
    """Class to handle source and lens light models."""

    def __init__(self, light_model_list, profile_kwargs_list=None):
        """

        :param light_model_list: list of light models
        :param profile_kwargs_list: list of dicts, keyword arguments used to initialize light model
            profile classes in the same order of the light_model_list. If any of the profile_kwargs
            are None, then that profile will be initialized using default settings.
        """
        self.profile_type_list = light_model_list
        self.func_list = []
        if profile_kwargs_list is None:
            profile_kwargs_list = [{} for _ in range(len(light_model_list))]

        for profile_type, profile_kwargs in zip(light_model_list, profile_kwargs_list):
            if profile_kwargs is None:
                profile_kwargs = {}
            if profile_type == "GAUSSIAN":
                from jaxtronomy.LightModel.Profiles.gaussian import Gaussian

                self.func_list.append(Gaussian(**profile_kwargs))
            elif profile_type == "GAUSSIAN_ELLIPSE":
                from jaxtronomy.LightModel.Profiles.gaussian import GaussianEllipse

                self.func_list.append(GaussianEllipse(**profile_kwargs))
            # elif profile_type == "ELLIPSOID":
            #     from lenstronomy.LightModel.Profiles.ellipsoid import Ellipsoid

            #     self.func_list.append(Ellipsoid(**profile_kwargs))
            elif profile_type == "MULTI_GAUSSIAN":
                from jaxtronomy.LightModel.Profiles.gaussian import MultiGaussian

                self.func_list.append(MultiGaussian(**profile_kwargs))
            elif profile_type == "MULTI_GAUSSIAN_ELLIPSE":
                from jaxtronomy.LightModel.Profiles.gaussian import (
                    MultiGaussianEllipse,
                )

                self.func_list.append(MultiGaussianEllipse(**profile_kwargs))
            elif profile_type == "SERSIC":
                from jaxtronomy.LightModel.Profiles.sersic import Sersic

                self.func_list.append(Sersic(**profile_kwargs))
            elif profile_type == "SERSIC_ELLIPSE":
                from jaxtronomy.LightModel.Profiles.sersic_ellipse import SersicElliptic

                self.func_list.append(SersicElliptic(**profile_kwargs))
            elif profile_type == "SERSIC_ELLIPSE_Q_PHI":
                from jaxtronomy.LightModel.Profiles.sersic_ellipse import (
                    SersicElliptic_qPhi,
                )

                self.func_list.append(SersicElliptic_qPhi(**profile_kwargs))
            elif profile_type == "CORE_SERSIC":
                from jaxtronomy.LightModel.Profiles.core_sersic import CoreSersic

                self.func_list.append(CoreSersic(**profile_kwargs))

            elif profile_type == "SHAPELETS":
                if profile_kwargs.get("n_max", None) is not None:
                    from jaxtronomy.LightModel.Profiles.shapelets import (
                        ShapeletSetStatic,
                    )

                    self.func_list.append(ShapeletSetStatic(**profile_kwargs))
                else:
                    from jaxtronomy.LightModel.Profiles.shapelets import ShapeletSet

                    self.func_list.append(ShapeletSet(**profile_kwargs))
            # elif profile_type == "SHAPELETS_ELLIPSE":
            #     from lenstronomy.LightModel.Profiles.shapelets_ellipse import (
            #         ShapeletSetEllipse,
            #     )

            #     self.func_list.append(ShapeletSetEllipse(**profile_kwargs))
            # elif profile_type == "SHAPELETS_POLAR":
            #     from lenstronomy.LightModel.Profiles.shapelets_polar import (
            #         ShapeletSetPolar,
            #     )

            #     profile_kwargs["exponential"] = False
            #     self.func_list.append(ShapeletSetPolar(**profile_kwargs))
            # elif profile_type == "SHAPELETS_POLAR_EXP":
            #     from lenstronomy.LightModel.Profiles.shapelets_polar import (
            #         ShapeletSetPolar,
            #     )

            #     profile_kwargs["exponential"] = True
            #     self.func_list.append(ShapeletSetPolar(**profile_kwargs))
            # elif profile_type == "HERNQUIST":
            #     from lenstronomy.LightModel.Profiles.hernquist import Hernquist

            #     self.func_list.append(Hernquist(**profile_kwargs))
            # elif profile_type == "HERNQUIST_ELLIPSE":
            #     from lenstronomy.LightModel.Profiles.hernquist import HernquistEllipse

            #     self.func_list.append(HernquistEllipse(**profile_kwargs))
            # elif profile_type == "PJAFFE":
            #     from lenstronomy.LightModel.Profiles.pseudo_jaffe import PseudoJaffe

            #     self.func_list.append(PseudoJaffe(**profile_kwargs))
            # elif profile_type == "PJAFFE_ELLIPSE":
            #     from lenstronomy.LightModel.Profiles.pseudo_jaffe import (
            #         PseudoJaffeEllipse,
            #     )

            #     self.func_list.append(PseudoJaffeEllipse(**profile_kwargs))
            # elif profile_type == "UNIFORM":
            #     from lenstronomy.LightModel.Profiles.uniform import Uniform

            #     self.func_list.append(Uniform(**profile_kwargs))
            # elif profile_type == "POWER_LAW":
            #     from lenstronomy.LightModel.Profiles.power_law import PowerLaw

            #     self.func_list.append(PowerLaw(**profile_kwargs))
            # elif profile_type == "NIE":
            #     from lenstronomy.LightModel.Profiles.nie import NIE

            #     self.func_list.append(NIE(**profile_kwargs))
            # elif profile_type == "CHAMELEON":
            #     from lenstronomy.LightModel.Profiles.chameleon import Chameleon

            #     self.func_list.append(Chameleon(**profile_kwargs))
            # elif profile_type == "DOUBLE_CHAMELEON":
            #     from lenstronomy.LightModel.Profiles.chameleon import DoubleChameleon

            #     self.func_list.append(DoubleChameleon(**profile_kwargs))
            # elif profile_type == "TRIPLE_CHAMELEON":
            #     from lenstronomy.LightModel.Profiles.chameleon import TripleChameleon

            #     self.func_list.append(TripleChameleon(**profile_kwargs))
            # elif profile_type == "INTERPOL":
            #     from lenstronomy.LightModel.Profiles.interpolation import Interpol

            #     self.func_list.append(Interpol(**profile_kwargs))
            # elif profile_type == "SLIT_STARLETS":
            #     from lenstronomy.LightModel.Profiles.starlets import SLIT_Starlets

            #     profile_kwargs["fast_inverse"] = True
            #     profile_kwargs["second_gen"] = False
            #     self.func_list.append(SLIT_Starlets(**profile_kwargs))

            # elif profile_type == "SLIT_STARLETS_GEN2":
            #     from lenstronomy.LightModel.Profiles.starlets import SLIT_Starlets

            #     profile_kwargs["second_gen"] = True
            #     self.func_list.append(SLIT_Starlets(**profile_kwargs))
            # elif profile_type == "LINEAR":
            #     from lenstronomy.LightModel.Profiles.linear import Linear

            #     self.func_list.append(Linear(**profile_kwargs))
            # elif profile_type == "LINEAR_ELLIPSE":
            #     from lenstronomy.LightModel.Profiles.linear import LinearEllipse

            #     self.func_list.append(LinearEllipse(**profile_kwargs))
            # elif profile_type == "LINE_PROFILE":
            #     from lenstronomy.LightModel.Profiles.lineprofile import LineProfile

            #     self.func_list.append(LineProfile(**profile_kwargs))

            else:
                raise ValueError(
                    "Light model of type %s not supported by jaxtronomy! Please use lenstronomy instead.\n"
                    "Supported models in jaxtronomy are %s"
                    % (profile_type, _JAXXED_MODELS)
                )
        self._num_func = len(self.func_list)

    @partial(jit, static_argnums=(0, 4))
    def surface_brightness(self, x, y, kwargs_list, k=None):
        """
        :param x: coordinate in units of arcsec relative to the center of the image
        :type x: set or single 1d numpy array
        :param y: coordinate in units of arcsec relative to the center of the image
        :type y: set or single 1d numpy array
        :param kwargs_list: keyword argument list of light profile
        :param k: integer or tuple of integers for selecting subsets of light profiles
        """
        kwargs_list_standard = self._transform_kwargs(kwargs_list)
        x = jnp.array(x, dtype=float)
        y = jnp.array(y, dtype=float)

        flux = jnp.zeros_like(x)
        bool_list = self._bool_list(k=k)
        for i, func in enumerate(self.func_list):
            if bool_list[i] is True:
                out = jnp.array(
                    func.function(x, y, **kwargs_list_standard[i]), dtype=float
                )
                flux += out
        return flux

    # TODO: Re-implement this when other profiles are added to jaxtronomy

    # def light_3d(self, r, kwargs_list, k=None):
    #     """Computes 3d density at radius r (3D radius) such that integrated in
    #     projection in units of angle results in the projected surface brightness.

    #     :param r: 3d radius units of arcsec relative to the center of the light profile
    #     :param kwargs_list: keyword argument list of light profile
    #     :param k: integer or list of integers for selecting subsets of light profiles.
    #     :return: flux density
    #     """
    #     kwargs_list_standard = self._transform_kwargs(kwargs_list)
    #     r = np.array(r, dtype=float)
    #     flux = np.zeros_like(r)
    #     bool_list = self._bool_list(k=k)
    #     for i, func in enumerate(self.func_list):
    #         if bool_list[i] is True:
    #             kwargs = {
    #                 k: v
    #                 for k, v in kwargs_list_standard[i].items()
    #                 if k not in ["center_x", "center_y"]
    #             }
    #             if self.profile_type_list[i] in [
    #                 "DOUBLE_CHAMELEON",
    #                 "CHAMELEON",
    #                 "HERNQUIST",
    #                 "HERNQUIST_ELLIPSE",
    #                 "PJAFFE",
    #                 "PJAFFE_ELLIPSE",
    #                 "GAUSSIAN",
    #                 "GAUSSIAN_ELLIPSE",
    #                 "MULTI_GAUSSIAN",
    #                 "MULTI_GAUSSIAN_ELLIPSE",
    #                 "NIE",
    #                 "POWER_LAW",
    #                 "TRIPLE_CHAMELEON",
    #             ]:
    #                 flux += func.light_3d(r, **kwargs)
    #             else:
    #                 raise ValueError(
    #                     "Light model %s does not support a 3d light distribution!"
    #                     % self.profile_type_list[i]
    #                 )
    #     return flux

    @partial(jit, static_argnums=(0, 2, 3))
    def total_flux(self, kwargs_list, norm=False, k=None):
        """Computes the total flux of each individual light profile. This allows to
        estimate the total flux as well as lenstronomy amp to magnitude conversions. Not
        all models are supported. The units are linked to the data to be modelled with
        associated noise properties (default is count/s).

        :param kwargs_list: list of keyword arguments corresponding to the light
            profiles. The 'amp' parameter can be missing.
        :param norm: bool, if True, computes the flux for amp=1
        :param k: int or tuple of ints, if set, only evaluates the specific light model
        :return: list of (total) flux values attributed to each profile
        """
        kwargs_list_standard = self._transform_kwargs(kwargs_list)
        norm_flux_list = []
        bool_list = self._bool_list(k=k)
        for i, model in enumerate(self.profile_type_list):
            if bool_list[i] is True:
                if model in [
                    "SERSIC",
                    "SERSIC_ELLIPSE",
                    "INTERPOL",
                    "GAUSSIAN",
                    "GAUSSIAN_ELLIPSE",
                    "MULTI_GAUSSIAN",
                    "MULTI_GAUSSIAN_ELLIPSE",
                    "LINE_PROFILE",
                ]:
                    kwargs_new = kwargs_list_standard[i].copy()
                    if norm is True:
                        if model in ["MULTI_GAUSSIAN", "MULTI_GAUSSIAN_ELLIPSE"]:
                            new = {
                                "amp": jnp.array(kwargs_new["amp"])
                                / kwargs_new["amp"][0]
                            }
                        else:
                            new = {"amp": 1}
                        kwargs_new.update(new)
                    norm_flux = self.func_list[i].total_flux(**kwargs_new)
                    norm_flux_list.append(norm_flux)
                else:
                    raise ValueError(
                        "profile %s does not support flux normlization." % model
                    )
                #  TODO implement total flux for e.g. 'HERNQUIST', 'HERNQUIST_ELLIPSE', 'PJAFFE', 'PJAFFE_ELLIPSE',
                # 'GAUSSIAN', 'GAUSSIAN_ELLIPSE', 'POWER_LAW', 'NIE', 'CHAMELEON', 'DOUBLE_CHAMELEON' ,
                # 'TRIPLE_CHAMELEON', 'UNIFORM'
        return norm_flux_list

    @property
    def param_name_list(self):
        """Returns the list of all parameter names. Should be used outside of JIT.

        :return: list of lists of strings (for each light model separately)
        """
        name_list = []
        for i, func in enumerate(self.func_list):
            name_list.append(func.param_names)
        return name_list

    @property
    def param_name_list_latex(self):
        """Returns the list of all parameter names in LateX style. Should be used
        outside of JIT.

        :return: list of lists of strings (for each light model separately)
        """
        name_list = []
        for i, func in enumerate(self.func_list):
            # TODO: Currently there are no profiles in jaxtronomy with LaTeX param names
            # if hasattr(func, "param_names_latex"):
            #     #name_list.append(func.param_names_latex)
            # else:
            name_list.append(func.param_names)
        return name_list

    def check_parameters(self, kwargs_list):
        """Checks whether the parameter list is consistent with the parameters required
        by the light model. Should be used outside of JIT.

        :param kwargs_list: keyword argument list as parameterised models
        :return: None or raise ValueError with error message of what parameter is not
            supported.
        """

        name_list = self.param_name_list
        if len(kwargs_list) != len(name_list):
            raise ValueError(
                "length of input parameter list %s does not match length of light models %s"
                % (len(kwargs_list), len(name_list))
            )
        for i, names in enumerate(name_list):
            for key in kwargs_list[i]:
                if key not in names:
                    raise ValueError(
                        "parameter %s in light model is not part of model %s (%s). "
                        "Parameters allowed are %s"
                        % (key, i, self.profile_type_list[i], names)
                    )
            for name in names:
                if name not in kwargs_list[i]:
                    raise ValueError(
                        "Light model %s (%s) requires parameter %s which is not provided in input."
                        % (i, self.profile_type_list[i], name)
                    )

    # TODO: Re-implement when these profiles are added to jaxtronomy
    # def delete_interpol_caches(self):
    #     """Call the delete_cache method of INTERPOL profiles."""
    #     for i, model in enumerate(self.profile_type_list):
    #         if model in ["INTERPOL", "SLIT_STARLETS", "SLIT_STARLETS_GEN2"]:
    #             self.func_list[i].delete_cache()

    def _transform_kwargs(self, kwargs_list):
        """

        :param kwargs_list: keyword argument list as parameterised models
        :return: keyword argument list as used in the individual models
        """
        return kwargs_list

    def _bool_list(self, k=None):
        """Returns a bool list of the length of the lens models if k = None: returns
        bool list with True's if k is int, returns bool list with False's but k'th is
        True if k is a list of int, e.g. [0, 3, 5], returns a bool list with True's in
        the integers listed and False elsewhere if k is a boolean list, checks for size
        to match the numbers of models and returns it.

        :param k: None, int, or list of ints
        :return: bool list
        """
        return convert_bool_list(n=self._num_func, k=k)
