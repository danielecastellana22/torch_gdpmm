from typing import Any, Type, Collection
import torch as th
from ..constraints import *


class ConjugatePriorDistribution:

    _exp_distr_class = None
    _theta_names = None
    _theta_shape_list = None
    _theta_constraints_list = None

    @staticmethod
    def __validate_params(name: str, value: Any,
                          expected_shape: Collection[int], constraint: BaseConstraint):
        expected_shape = tuple(expected_shape)

        if not isinstance(value, th.Tensor):
            value = th.tensor(value).float()

        #if value.ndim == 0:
        #    value = value.view((1,) * len(expected_shape)).expand(expected_shape)

        # check the shape
        if value.ndim > len(expected_shape):
            raise ValueError(f'{name} has too many dimensions: we got {value.shape} but we expected {expected_shape}!')
        elif value.ndim == len(expected_shape)-1:
            value = value.unsqueeze(0).expand(expected_shape[:1] + tuple([-1]*(len(expected_shape)-1)))
        elif value.ndim < len(expected_shape)-1:
            raise ValueError(f'{name} has too few dimensions! We broadcast only along the first dimension:'
                             f' we got {value.shape} but we expected {expected_shape}!')

        assert value.ndim == len(expected_shape)
        if value.shape != expected_shape:
            raise ValueError(f'{name} has the wrong shape: we got {value.shape} but we expected {expected_shape}!')

        # check the constraint
        if not constraint(value):
            raise ValueError(constraint.message(name, 'Gaussian-DPMM'))

        return value

    @classmethod
    def validate_common_params(cls, K: int, D: int, theta: list[th.Tensor]) -> list[th.Tensor]:
        out = []
        for i in range(len(theta)):
            out.append(cls.__validate_params(cls._theta_names[i], theta[i],
                                             eval(cls._theta_shape_list[i]), eval(cls._theta_constraints_list[i])))
        return out

    @classmethod
    def expected_log_params(cls, eta: list[th.Tensor]) -> list[th.Tensor]:
        r"""
        Let Q(phi | eta), where Q is the conjugate prior distribution of P.
        This method returns the expected log value of phi w.r.t. the prior Q: E_Q[log phi].
        The computation is batched.

        Args:
            eta (list[th.Tensor]): natural params of a prior distribution. It is a list tensor K x ?, where K is the
                number of distribution that we consider.

        Returns:
            list[th.Tensor]: the expected log params
        """

        raise NotImplementedError('Should be implemented in subclasses!')

    @classmethod
    def expected_params(cls, eta: list[th.Tensor]) -> list[th.Tensor]:
        r"""
        Let Q(phi | eta), where Q is the conjugate prior distribution of P.
        This method returns the expected value of phi w.r.t. the prior Q: E_Q[phi].
        The computation is batched.

        Args:
            eta (list[th.Tensor]): natural params of a prior distribution. It is a list tensor K x ?, where K is the
                number of distribution that we consider.

        Returns:
            list[th.Tensor]: the expected params
        """

        raise NotImplementedError('Should be implemented in subclasses!')

    @classmethod
    def expected_data_loglikelihood(cls, obs_data: th.Tensor, eta: list[th.Tensor]) -> th.Tensor:
        r"""
        Let data ~ P(x | param) and param ~ Q(phi | eta), where Q is the conjugate prior distribution of P.
        This method returns the expected loglikelihood of the data w.r.t. the prior Q: E_Q[log data].
        The computation is batched.

        Args:
            obs_data (th.Tensor): the data observed. It is a tensor BS x D,
                BS is the batch size and D is the event shape.
            eta (list[th.Tensor]): natural params of a prior distribution. It is a list tensor K x ?, where K is the
                number of distribution that we consider.

        Returns:
            th.Tensor: the expected loglikelihood of data
        """

        raise NotImplementedError('Should be implemented in subclasses!')

    @classmethod
    def compute_posterior_suff_stats(cls, assignments: th.Tensor, obs_data: th.Tensor) -> list[th.Tensor]:
        """
        Compute the sufficient statistics of the posterior given the observed data.
        The assignments are needed since we consider K distribution togethers to speed up the computation.
        Args:
            assignments (th.Tensor): the assignment of the observed data to the K distributions.
            obs_data (th.Tensor): the observed data.

        Returns:
            list[th.Tensor]: a list containing the sufficient statistics for the natural parameters' posterior.

        """
        raise NotImplementedError('Should be implemented in subclasses!')

    @classmethod
    def kl_div(cls, p_eta: list[th.Tensor], q_eta: list[th.Tensor]) -> th.Tensor:
        return cls._exp_distr_class.kl_div(p_eta, q_eta)

    @classmethod
    def common_to_natural(cls, theta: list[th.Tensor]) -> list[th.Tensor]:
        return cls._exp_distr_class.common_to_natural(theta)

    @classmethod
    def natural_to_common(cls, eta: list[th.Tensor]) -> list[th.Tensor]:
        return cls._exp_distr_class.natural_to_common(eta)


