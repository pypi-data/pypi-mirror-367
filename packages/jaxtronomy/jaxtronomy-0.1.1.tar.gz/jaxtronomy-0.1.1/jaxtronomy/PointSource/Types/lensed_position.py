from jax import jit, numpy as jnp
from jaxtronomy.PointSource.Types.base_ps import PSBase, _expand_to_array
from functools import partial

__all__ = ["LensedPositions"]


class LensedPositions(PSBase):
    """
    class of a lensed point source parameterized as the (multiple) observed image positions
    Name within the PointSource module: 'LENSED_POSITION'
    parameters:
        ra_image: list or array of floats
        dec_image: list or array of floats
        point_amp: list or array of floats
    If fixed_magnification=True, then 'source_amp' is a parameter instead of point_amp
        source_amp: float

    """

    @partial(jit, static_argnums=(0, 5))
    def image_position(
        self,
        kwargs_ps,
        kwargs_lens=None,
        magnification_limit=None,
        kwargs_lens_eqn_solver=None,
        additional_images=False,
    ):
        """On-sky image positions.

        :param kwargs_ps: keyword arguments of the point source model
        :param kwargs_lens: keyword argument list of the lens model(s), only used when
            requiring the lens equation solver
        :param magnification_limit: float >0 or None, if float is set and additional
            images are computed, only those images will be computed that exceed the
            lensing magnification (absolute value) limit
        :param kwargs_lens_eqn_solver: keyword arguments specifying the numerical
            settings for the lens equation solver see LensEquationSolver() class for
            details
        :param additional_images: if True, solves the lens equation for additional
            images
        :type additional_images: bool
        :return: image positions in x, y as arrays
        """
        if self.additional_images is True or additional_images:
            raise ValueError("additional images not supported in jaxtronomy")
        #    if kwargs_lens_eqn_solver is None:
        #        kwargs_lens_eqn_solver = {}
        #    ra_source, dec_source = self.source_position(kwargs_ps, kwargs_lens)
        #    # TODO: this solver does not distinguish between different frames/bands with partial lens models
        #    self._solver.change_source_redshift(self._redshift)
        #    ra_image, dec_image = self._solver.image_position_from_source(
        #        ra_source,
        #        dec_source,
        #        kwargs_lens,
        #        magnification_limit=magnification_limit,
        #        **kwargs_lens_eqn_solver
        #    )
        else:
            ra_image = kwargs_ps["ra_image"]
            dec_image = kwargs_ps["dec_image"]
        return jnp.array(ra_image), jnp.array(dec_image)

    @partial(jit, static_argnums=(0))
    def source_position(self, kwargs_ps, kwargs_lens=None):
        """Original source position (prior to lensing)

        :param kwargs_ps: point source keyword arguments
        :param kwargs_lens: lens model keyword argument list (required to ray-trace back
            in the source plane)
        :return: x, y position (as numpy arrays)
        """
        ra_image = jnp.array(kwargs_ps["ra_image"], dtype=float)
        dec_image = jnp.array(kwargs_ps["dec_image"], dtype=float)
        # self._lens_model.change_source_redshift(self._redshift)

        if self.k_list is None:
            x_source, y_source = self._lens_model.ray_shooting(
                ra_image, dec_image, kwargs_lens
            )
        else:
            x_source, y_source = jnp.zeros_like(ra_image), jnp.zeros_like(ra_image)
            for i in range(ra_image.size):
                x, y = self._lens_model.ray_shooting(
                    ra_image[i], dec_image[i], kwargs_lens, k=self.k_list[i]
                )
                x_source = x_source.at[i].set(x)
                y_source = y_source.at[i].set(y)
        x_source = jnp.mean(x_source)
        y_source = jnp.mean(y_source)
        return x_source, y_source

    @partial(jit, static_argnums=(0))
    def image_amplitude(
        self,
        kwargs_ps,
        kwargs_lens=None,
        x_pos=None,
        y_pos=None,
        magnification_limit=None,
        kwargs_lens_eqn_solver=None,
    ):
        """Image brightness amplitudes.

        :param kwargs_ps: keyword arguments of the point source model
        :param kwargs_lens: keyword argument list of the lens model(s), only used when
            requiring the lens equation solver
        :param x_pos: pre-computed image position (no lens equation solver applied)
        :param y_pos: pre-computed image position (no lens equation solver applied)
        :param magnification_limit: float >0 or None, if float is set and additional
            images are computed, only those images will be computed that exceed the
            lensing magnification (absolute value) limit
        :param kwargs_lens_eqn_solver: keyword arguments specifying the numerical
            settings for the lens equation solver see LensEquationSolver() class for
            details
        :return: array of image amplitudes
        """
        # self._lens_model.change_source_redshift(self._redshift)
        if self._fixed_magnification:
            if x_pos is not None and y_pos is not None:
                x_pos = jnp.array(x_pos, dtype=float)
                y_pos = jnp.array(y_pos, dtype=float)
                ra_image, dec_image = x_pos, y_pos
            else:
                ra_image, dec_image = self.image_position(
                    kwargs_ps,
                    kwargs_lens,
                    magnification_limit=magnification_limit,
                    kwargs_lens_eqn_solver=kwargs_lens_eqn_solver,
                )

            if self.k_list is None:
                mag = self._lens_model.magnification(ra_image, dec_image, kwargs_lens)
            else:
                mag = jnp.zeros_like(ra_image)
                for i in range(ra_image.size):
                    mag = mag.at[i].set(
                        self._lens_model.magnification(
                            ra_image[i], dec_image[i], kwargs_lens, k=self.k_list[i]
                        )
                    )
            point_amp = jnp.array(kwargs_ps["source_amp"], dtype=float) * jnp.abs(mag)
        else:
            point_amp = jnp.array(kwargs_ps["point_amp"], dtype=float)
            if x_pos is not None:
                x_pos = jnp.array(x_pos, dtype=float)
                point_amp = _expand_to_array(point_amp, x_pos.size)
        return point_amp

    @partial(jit, static_argnums=(0))
    def source_amplitude(self, kwargs_ps, kwargs_lens=None):
        """Intrinsic brightness amplitude of point source When brightnesses are defined
        in magnified on-sky positions, the intrinsic brightness is computed as the mean
        in the magnification corrected image position brightnesses.

        :param kwargs_ps: keyword arguments of the point source model
        :param kwargs_lens: keyword argument list of the full lens model(s), used when
            brightness are defined in magnified on-sky positions
        :return: brightness amplitude (as numpy array)
        """
        if self._fixed_magnification:
            source_amp = jnp.array(kwargs_ps["source_amp"], dtype=float)
        else:
            # self._lens_model.change_source_redshift(self._redshift)
            ra_image, dec_image = jnp.array(
                kwargs_ps["ra_image"], dtype=float
            ), jnp.array(kwargs_ps["dec_image"], dtype=float)
            if self.k_list is None:
                mag = self._lens_model.magnification(ra_image, dec_image, kwargs_lens)
            else:
                mag = jnp.zeros_like(ra_image)
                for i in range(ra_image.size):
                    mag = mag.at[i].set(
                        self._lens_model.magnification(
                            ra_image[i], dec_image[i], kwargs_lens, k=self.k_list[i]
                        )
                    )
            point_amp = kwargs_ps["point_amp"]
            source_amp = jnp.mean(jnp.array(point_amp) / jnp.abs(mag))
        return source_amp
