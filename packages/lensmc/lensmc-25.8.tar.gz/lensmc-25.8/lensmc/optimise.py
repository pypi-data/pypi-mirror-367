"""
LensMC - a Python package for weak lensing shear measurements.
This is a module containing core functions for LensMC.

Copyright 2015 Giuseppe Congedo
"""

import numpy as np
from math import log
from scipy.optimize import minimize
from scipy.signal import correlate

from lensmc.utils import Counter, LensMCError, logger


def sampler(data, log_likl_fcn, x, log_prior_fcn=None,
            maximisation=True, mode='slow',
            sampling=True, cov_matr=None,
            n_burnin=500, n_samples=200, n_update_cov=100, n_chains=1, n_swap=100,
            affine_invariant=False, n_ai_samples=20, n_ai_burnin=50, n_ai_chains=10,
            seed=None,
            intcal=True, model_fcn=None):
    """
    Lensmc core sampling function.
    It maximises/samples the posterior for given data ('data').
    It requires a log-likelihood ('log_likl_fcn') as a function of data and parameters array,
    and initial-guess parameters ('x').
    Additionally, the following optional parameter may be passed as well:
    a log-prior ('log_prior_fcn') as a function of parameters,
    an optional chi2 function ('chi2_fcn') [if the likelihood does not automatically generate a chi2
    as per log(L) = exp(-chi2/2)] as a function of parameters, a 'maximisation' boolean
    to decide whether to maximise the posterior, a 'sampling' boolean to decide whether to sample
    the posterior with a modified Metropolis-Hastings that includes an initial annealing scheme and
    an adaptive covariance optimisation; in this case, the MH parameters can be passed as well
    ('cov_matr', 'n_burnin' and 'n_samples'); as part of the MH sampling, an auto-calibration of parameters
    to account for bias mitigation is applied via the 'autocal' boolean and extra parameters
    ('model_fcn' containing the model as a function of parameters and 'log_post_threshold' for the
    nominal threshold that will be applied to trim the chain).
    It returns parameter estimates, uncertainties, goodness-of-fit, and other information
    in a Results class.

    :type data: ndarray
    :type log_likl_fcn: lambda
    :type x: ndarray
    :type log_prior_fcn: lambda
    :type maximisation: bool
    :type mode: str
    :type sampling: str or bool
    :type cov_matr: ndarray
    :type n_burnin: int
    :type n_samples: int
    :type n_update_cov: int
    :type n_chains: int
    :type n_swap: int
    :type affine_invariant: bool
    :type seed: Seed for the random sampler; see https://numpy.org/doc/stable/reference/random/generator.html
    :type intcal: bool
    :type model_fcn: lambda
    :rtype: Results
    """

    # Sanity checks
    x = np.atleast_1d(x)
    if not (maximisation or sampling):
        raise LensMCError('Please choose to maximise, sample the posterior, or do both.')
    if log_prior_fcn and not np.isfinite(log_prior_fcn(x)):
        raise LensMCError('Initial parameters must satisfy the prior constraint.')
    if not log_prior_fcn:
        # uninformative log-prior function
        def log_prior_fcn(x):
            return 0.
    if intcal and not model_fcn:
        raise LensMCError('Please provide a galaxy model as a function of parameters in \'model_fcn\'.')

    # decorate with the Counter class for keeping track of the number of function evaluations
    log_likl_fcn = Counter(log_likl_fcn)

    # log-posterior function
    def log_post_fcn(x):
        logp = log_prior_fcn(x)
        if logp > -np.inf:
            logp += log_likl_fcn(data, x)
        return logp

    # optimisation
    if maximisation:

        # reset likelihood function calls
        log_likl_fcn.reset_calls()

        # backup initial guess (may be used later on)
        x0 = np.copy(x)

        # negative log-posterior function
        def nlog_post_fcn(x):
            return -log_post_fcn(x)

        # constraint function (derived from prior)
        if not log_prior_fcn:
            constraint_fcn = None
        else:
            def constraint_fcn(x):
                pp = log_prior_fcn(x)
                if np.isfinite(pp):
                    return False
                else:
                    return True

        # max log-posterior (may be used by autocal) and best-fit parameters
        log_post_max, x_max = minimise(nlog_post_fcn, x, mode=mode, callback=constraint_fcn)
        log_post_max *= -1

        # set maximisation results
        results = Results(x=x_max)
        results.set_max(x=x_max, logp=log_post_max)

        # further check on maximum posterior for out of bounds
        if np.isfinite(log_post_max):
            x = x_max
        else:
            x = x0

        # keep track of likelihood function calls
        likl_calls_optim = log_likl_fcn.calls

    # sampling
    if sampling:

        # reset likelihood function calls
        log_likl_fcn.reset_calls()

        # initialise the RNG
        rng = np.random.default_rng(seed)

        # run Metropolis-Hastings
        results = mhsampler(x, lambda x: log_likl_fcn(data, x),
                            log_prior=log_prior_fcn, cov_matr=cov_matr,
                            n_samples=n_samples, n_burnin=n_burnin, n_update_cov=n_update_cov,
                            n_chains=n_chains, n_swap=n_swap, seed=rng)

        if affine_invariant:
            results = mhsampler(results.x, lambda x: log_likl_fcn(data, x),
                                log_prior=log_prior_fcn, cov_matr=cov_matr,
                                n_samples=n_ai_samples, n_burnin=n_ai_burnin,
                                n_chains=n_ai_chains, method='AI', seed=rng)

        # parameter estimates
        if results.x is not None:
            x = results.x
        else:
            return Results()

        # keep track of likelihood function calls
        likl_calls_mcmc = log_likl_fcn.calls

        # run internal calibration
        if intcal:

            # reset likelihood function calls
            log_likl_fcn.reset_calls()

            # make data proxy
            model = model_fcn(x)

            # define auxiliary posterior
            log_post_intcal_fcn = lambda x: log_likl_fcn(model, x) + log_prior_fcn(x)

            # run importance sampling
            likl_ratio, ess, has_succedeed = importance_sampling(results.x_samples, results.logp_samples,
                                                                 log_post_intcal_fcn)

            # derive autocal estimator
            if has_succedeed and ess > n_samples / 2:
                x_aux = np.average(results.x_samples, axis=0, weights=likl_ratio)
                x_ical = 2 * x - x_aux
            else:
                x_ical = x

            # set results
            results.set_ical(x_ical=x_ical, likl_ratio_samples=likl_ratio)

            # keep track of likelihood function calls
            likl_calls_intcal = log_likl_fcn.calls

        # store random seed
        results.seed = seed

        # set maximisation results
        if maximisation and np.isfinite(log_post_max):
            results.set_max(x=x_max, logp=log_post_max)

    # reset likelihood function calls
    log_likl_fcn.reset_calls()

    # store likelihood function calls
    if maximisation:
        results.likl_calls_optim += likl_calls_optim
    if sampling:
        results.likl_calls_mcmc += likl_calls_mcmc
        if intcal:
            results.likl_calls_intcal += likl_calls_intcal

    return results


def minimise(fcn, x, mode='fast', package='scipy', loopmethod='Powell', callback=None,
             ftol=1e-2, niter=1, out_of_bound_fval=1e100):

    if not np.isfinite(fcn(x)):
        raise LensMCError('Function is not finite at initial guess.')

    # make a wrapper function to handle the annoying warnings about out-of-bound fcn values
    def fcn_wrapper(x):
        f = fcn(x)
        if np.isfinite(f):
            return f
        else:
            return out_of_bound_fval

    # only scipy for now
    if package == 'scipy':

        # Powell
        res = minimize(fcn_wrapper, x, method='Powell', options={'maxfev': 100}, callback=callback)

        # return now if fast mode
        if mode == 'fast':
            return res.fun, res.x

        # simplex
        res = minimize(fcn_wrapper, res.x, method='Nelder-Mead', callback=callback)

        # loop
        for ii in range(niter):
            fval0 = res.fun
            res = minimize(fcn_wrapper, res.x, method=loopmethod, callback=callback)
            if abs((res.fun - fval0) / fval0) < ftol:
                return res.fun, res.x
        else:
            return res.fun, res.x


def mhsampler(x, log_likl, log_prior=None, cov_matr=None,
              n_samples=1000, n_burnin=1000, n_thin=1, n_cooling=100, heat=10,
              n_update_cov=100, n_chains=1, n_swap=100, a=2., return_burnin=False, method='PA', seed=None):
    """
    Sample a posterior [log-likelihood and an optional log-prior] via modified Metropolis-Hastings.
    The algorithm is based on simulated annealing where temeprature is slowly decreased during the burn-in, and
    the covariance of the Gaussian proposal distribution is updated as the sampling progresses.
    An initial proposal covariance matrix may be supplied.
    It can run either on single chain or parallel chains (parallel annealing or parallel tempering).
    Optional parameters are: number of samples in a chain, number of burnin samples,
    number of samples to thin the chain, number of samples during the likelihood cooling off, heat factor,
    number of samples to update covariance during the burnin phase.
    It returns samples for parameters, log-posterior, and acceptance rate.

    :type x: ndarray
    :type log_likl: lambda
    :type log_prior: lambda
    :type cov_matr: ndarray
    :type n_samples: int
    :type n_burnin: int
    :type n_thin: int
    :type n_cooling: int
    :type heat: float
    :type n_update_cov: int
    :type n_chains: int
    :type n_swap: int
    :type return_burnin: bool
    :type method: str
    :type seed: see https://numpy.org/doc/stable/reference/random/generator.html
    :rtype: Results
    """

    # initialise the RNG
    rng = np.random.default_rng(seed)

    # total number of samples beeing drawn
    n_tot_samples = n_burnin + n_samples

    # dimensionality
    d = len(x)

    x = np.atleast_1d(x)

    if log_prior is None:
        log_prior = lambda x: 0.

    if cov_matr is None:
        cov_matr = 1e-4 * np.eye(d)

    # Gelman et al 2006 [2.4^2/d]
    gelman_const = 2.4 / np.sqrt(d)

    # cholesky decomposition
    cov_matr0 = np.copy(cov_matr)
    R = gelman_const * np.sqrt(np.diag(np.diag(cov_matr)))

    # check burn-in length
    if n_burnin < n_cooling and method == 'PA':
        raise LensMCError('\'n_burnin\' must be greater than \'n_cooling\'.')

    # number of chain pairs for parallel swap
    if n_swap > 1 and n_chains > 1 and n_chains % 2:
        raise LensMCError('\'n_chains\' must be even in order for the parallel swap to work.')
    elif method == 'AI' and n_chains <= 1:
        raise LensMCError('\'n_chains\' must be greater than 1 in order for affine invariant to work.')

    n_chain_pairs = n_chains // 2

    # annealing scheme
    itemp = np.ones((n_chains, n_tot_samples))
    if method == 'PA':
        for cc in range(n_chains):
            itemp[cc, :n_cooling] = 10 ** -(heat * (1. - np.arange(n_cooling, dtype=float) / n_cooling))
    elif method == 'PT':
        for cc in range(1, n_chains):
            itemp[cc, :] *= 2 ** -cc
    elif method == 'AI':
        pass
    else:
        raise LensMCError('Unknown MCMC method.')

    # initial sample in a ball around the provided initial sample
    # 0th chain starts from the provided initial sample
    x0 = np.copy(x)
    x = np.copy(np.broadcast_to(x, (n_chains, d)))
    lx, px = np.empty((n_chains,)), np.empty((n_chains,))
    # start by checking the initial sample
    ii = 0
    lx[0], px[0] = log_likl(x0), log_prior(x0)
    while (not np.isfinite(px[0])) or (not np.isfinite(lx[0])):
        x[0] = np.dot(R, rng.standard_normal(d)) + x0
        lx[0], px[0] = log_likl(x[0]), log_prior(x[0])
        if ii >= 1000:
            logger.warning('Out-of-bound initial guess.')
            return Results()
        ii += 1

    # now draw the other ones
    for cc in range(1, n_chains):
        ii = 0
        lx[cc], px[cc] = -np.inf, -np.inf
        while (not np.isfinite(px[cc])) or (not np.isfinite(lx[cc])):
            x[cc] = np.dot(R, rng.standard_normal(d)) + x[0]
            lx[cc], px[cc] = log_likl(x[cc]), log_prior(x[cc])
            if ii >= 1000:
                logger.warning('Out-of-bound initial guess.')
                return Results()
            ii += 1

    # initialise arrays
    xc = np.empty((n_chains, d))
    lxc, pxc = np.empty((n_chains,)), np.empty((n_chains,))
    n_accepted = np.zeros((n_chains,))

    # run
    d1 = d - 1
    a1 = a - 1
    do_AI = method == 'AI'
    do_update_cov = n_update_cov > 0 and not do_AI
    do_swap = n_chains > 1 and n_swap > 0 and not do_AI
    eps = np.finfo(float).eps
    chains = list(range(n_chains))
    steps = np.arange(n_tot_samples)
    x_samples = np.empty((n_chains, n_tot_samples, d))
    logp_samples = np.empty((n_chains, n_tot_samples, ))
    a_samples = np.empty((n_chains, n_tot_samples, ))
    for ii in steps:
        for cc in chains:
            # propose new sample
            if not do_AI:
                xc[cc] = np.dot(R, rng.standard_normal(d)) + x[cc]
            else:
                # draw sample from complementary ensemble
                chains_compl = chains[:]
                chains_compl.remove(cc)
                xcompl = x[rng.choice(chains_compl)]
                # propose candidate through affine stretch move
                z = (1 + a1 * rng.random()) ** 2 / a
                xc[cc] = xcompl + z * (x[cc] - xcompl)
            # proposed log-prior
            pxc[cc] = log_prior(xc[cc])
            if np.isfinite(pxc[cc]):
                # proposed log-likelihood
                lxc[cc] = log_likl(xc[cc])
                # acceptance probability
                if np.isfinite(lxc[cc]):
                    logr = itemp[cc, ii] * (lxc[cc] - lx[cc]) + pxc[cc] - px[cc]
                    if do_AI:
                        logr += d1 * log(z)
                    logr = min(0, logr)
                    if log(rng.random()) < logr:
                        # accept
                        x[cc] = xc[cc]
                        lx[cc] = lxc[cc]
                        px[cc] = pxc[cc]
                        n_accepted[cc] += 1
            x_samples[cc, ii] = x[cc]
            logp_samples[cc, ii] = lx[cc] + px[cc]
            a_samples[cc, ii] = n_accepted[cc]

            # after a few samples update covariance
            if do_update_cov and n_cooling <= ii < n_burnin and not ii % n_update_cov and ii and cc == 0:
                x_samples_segment = np.reshape(x_samples[:, (ii - n_update_cov):ii], (n_chains * n_update_cov, d))
                cov_matr = np.diag(np.std(x_samples_segment, 0) ** 2)
                if any(np.isclose(np.diag(cov_matr), eps)):
                    cov_matr = np.copy(cov_matr0)
                R = gelman_const * np.sqrt(cov_matr)

        # propose swap between chains
        # first index in chain_pairs is the target chain, second is the candidate
        if do_swap and not ii % n_swap and ii:
            if method == 'PA':
                # pick chain pairs at random
                chain_pairs = rng.choice(chains, size=(n_chain_pairs, 2), replace=False)
            else:
                # pick contiguous chain pairs
                if (ii // n_swap) % 2:
                    chain_pairs = np.empty((n_chain_pairs, 2), dtype=int)
                    chain_pairs[:, 0] = chains[1::2]
                    chain_pairs[:, 1] = chains[:-1:2]
                else:
                    chain_pairs = np.empty((n_chain_pairs - 1, 2), dtype=int)
                    chain_pairs[:, 0] = chains[2::2]
                    chain_pairs[:, 1] = chains[1:-1:2]
            # accept/reject swap
            for pp in range(chain_pairs.shape[0]):
                # acceptance probability
                cc0, cc1 = chain_pairs[pp]
                logr = min(0, itemp[cc1, ii] * lx[cc1] - itemp[cc0, ii] * lx[cc0] + px[cc1] - px[cc0])
                if log(rng.random()) < logr:
                    # accept
                    x[cc0] = x[cc1]
                    lx[cc0] = lx[cc1]
                    px[cc0] = px[cc1]
            x_samples[cc0, ii] = x[cc0]
            logp_samples[cc0, ii] = lx[cc0] + px[cc0]

    # acceptance rate
    a_samples /= 1 + steps

    # cut burn-in and thin the chain
    if not return_burnin:
        start = n_burnin
    else:
        start = 0
    x_samples = x_samples[:, start::n_thin, :]
    logp_samples = logp_samples[:, start::n_thin]
    a_samples = a_samples[:, start::n_thin]

    # reshape to a 1D chain
    # and swap axis
    x_samples = np.swapaxes(x_samples, 0, 1)
    logp_samples = np.swapaxes(logp_samples, 0, 1)
    a_samples = np.swapaxes(a_samples, 0, 1)
    if not return_burnin:
        dim = n_samples
    else:
        dim = n_tot_samples
    dim *= n_chains
    dim //= n_thin
    x_samples = np.reshape(x_samples, (dim, d))
    logp_samples = np.reshape(logp_samples, (dim,))
    a_samples = np.reshape(a_samples, (dim,))

    # compute final statistics
    x = np.mean(x_samples, 0)
    acc = np.mean(a_samples)
    cov_matr = np.cov(x_samples, rowvar=False)
    dx = np.sqrt(np.diag(cov_matr))

    # output results
    res = Results(x=x, dx=dx, acc=acc, cov=cov_matr)
    res.set_samples(x=x_samples, logp=logp_samples, acc=a_samples)

    return res


def importance_sampling(p_samples, logp_samples, log_post_fcn, normalise=True):

    # evaluate new posterior at chain samples
    logp_samples_new = np.empty(logp_samples.shape)

    # evaluate at first sample
    logp_samples_new[0] = log_post_fcn(p_samples[0])

    # number of samples
    n_samples = p_samples.shape[0]

    # loop until the end of the chain while checking for redundancy
    for ii in range(1, n_samples):
        if not all(p_samples[ii] == p_samples[ii - 1]):
            logp_samples_new[ii] = log_post_fcn(p_samples[ii])
        else:
            logp_samples_new[ii] = logp_samples_new[ii - 1]

    # importance weights
    logw = logp_samples_new - logp_samples
    with np.errstate(over='raise', under='raise'):  # catch over/overflows
        try:
            # likelihood ratio, i.e. importance weights
            w = np.exp(logw - logw.max())
            if normalise:
                w /= w.sum()

            # effective sample size
            ess = 1. / (w ** 2).sum()

            # has it succeeded?
            success = True

        except FloatingPointError:
            w = np.full(logw.shape, fill_value=np.nan)
            ess = np.nan
            success = False

    return w, ess, success


def autocorr(x):
    """
    Autocorrelation function.
    :param x: Data series
    :return: Normalised one-sided autocorrelation function
    """
    xm = x - np.mean(x)
    y = correlate(xm, xm, mode='full')
    n = x.size - 1
    if y[n] > 0:
        return y[n:] / y[n]
    else:
        return np.full_like(x, np.nan)


def autocorr_time(x):
    """
    Initial positive sequence estimator by Geyer (1992); see Thompson (2010).
    Truncate autocorrelation function when the sum of adjacient values is negative.
    :param x: Data series
    :return: Estimated autocorrelation time
    """
    y = autocorr(x)
    s = y[:-1] + y[1:]
    ix = np.argmax(s < 0)
    if ix == 0:
        ix = -1
    return 1 + 2 * np.sum(y[:ix + 1])


def eff_sample_size(x):
    """
    Effective sample size.
    :param x: Data series
    :return: Estimated effective sample size
    """
    return x.size / autocorr_time(x)


class Results:
    """
    Class for returning LensMC results.
    """

    def __init__(self, x=None, dx=None, acc=None, cov=None):
        self.x = x
        self.dx = dx
        self.acc = acc
        self.cov = cov
        self.x_max = None
        self.logp_max = None
        self.x_samples = None
        self.logp_samples = None
        self.acc_samples = None
        self.n_eff = None
        self.x_ical = None
        self.likl_ratio_samples = None
        self.likl_calls_optim = 0
        self.likl_calls_mcmc = 0
        self.likl_calls_intcal = 0

    def set_max(self, x, logp):
        self.x_max = x
        self.logp_max = logp

    def set_samples(self, x, logp, acc):
        self.x_samples = x
        self.logp_samples = logp
        self.acc_samples = acc
        self.n_eff = [eff_sample_size(x[:, ii]) for ii in range(x.shape[1])]

    def set_ical(self, x_ical, likl_ratio_samples):
        self.x_ical = x_ical
        self.likl_ratio_samples = likl_ratio_samples
