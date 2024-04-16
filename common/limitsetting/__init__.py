import numpy as np

import cabinetry
import pyhf

from common.misc.logger import logger


def GetObsLimitBisection(
    poi_bracket_init,
    tolerance,
    maxiter,
    data,
    model,
    par_bounds,
    init_pars,
    fix_pars,
):
    cls_obs_exp = []
    poi_bracket = poi_bracket_init.copy()
    pois_all = []
    for poi in poi_bracket:
        pois_all.append(poi)
        logger.debug(f"Limit Bisection: testing POI {poi}")
        cls_obs_exp.append(
            pyhf.infer.hypotest(
                poi,
                data,
                model,
                test_stat="qtilde",
                return_expected_set=True,
                par_bounds=par_bounds,
                fixed_params=fix_pars,
            )
        )
    cls_obs_low = cls_obs_exp[0][0]
    cls_obs_high = cls_obs_exp[1][0]
    if (cls_obs_low - 0.05) * (cls_obs_high - 0.05) > 0.0:
        raise ValueError("Limit computation poi bracket inappropriate.")
    niter = 1
    while (poi_bracket[1] - poi_bracket[0]) / (
        0.5 * (poi_bracket[1] + poi_bracket[0])
    ) > tolerance:
        niter += 1
        if niter > maxiter:
            raise ValueError("Reached max. iterations in limit computation.")
        poi_mean = 0.5 * (poi_bracket[1] + poi_bracket[0])
        logger.debug(
            f"Limit Bisection (iteration {niter}): using POI value of {poi_mean}."
        )
        cls_obs_exp_new = pyhf.infer.hypotest(
            poi_mean,
            data,
            model,
            test_stat="qtilde",
            return_expected_set=True,
            par_bounds=par_bounds,
            init_pars=init_pars,
            fixed_params=fix_pars,
        )
        pois_all.append(poi_mean)
        cls_obs_exp.append(cls_obs_exp_new)
        cls_poiMean = cls_obs_exp_new[0]
        if (cls_poiMean - 0.05) * (cls_obs_low - 0.05) < 0.0:
            poi_bracket[1] = poi_mean
        else:
            poi_bracket[0] = poi_mean
            cls_obs_low = cls_poiMean
    return cls_obs_exp, pois_all


def limit_customScan(
    model: pyhf.pdf.Model,
    data: list[float],
    bracket: list[float] | tuple[float, float] | None = None,
    toleranceObs: float = 0.05,
    maxiterObs: int = 50,
    nIterExp: int = 50,
    init_pars: list[float] | None = None,
    par_bounds: list[tuple[float, float]] | None = None,
    fix_pars: list[bool] | None = None,
) -> cabinetry.fit.LimitResults:
    """
    Calculates observed and expected 95% confidence level
    upper parameter limits.
    Limits are calculated for the parameter of interest (POI)
    defined in the model.
    Linear scan of POI values to be tested.
    Args:
        model (pyhf.pdf.Model):
            model to use in fits
        data (List[float]):
            data (including auxdata) the model is fit to
        bracket (Optional[Union[List[float], Tuple[float, float]]], optional):
            the two POI values used to start the observed limit determination,
            the limit must lie between these values,
            and the values must not be the same,
            defaults to None (then uses ``0.1`` as default lower value,
            and the upper POI bound specified in the measurement
            as default upper value)
        toleranceObs (float, optional):
            rel. tolerance in POI value for convergence to
            CLs=0.05 - observed limit, defaults to 0.01
        maxiter (int, optional):
            maximum number of steps for limit finding,
            defaults to 100
    Raises:
        ValueError:
            if lower and upper bracket value are the same
    Returns:
        LimitResults:
            observed and expected limits, CLs values, and scanned points
    """
    ###########################################################################
    #
    # Assumption: CLs values fall monotonically as the poi increases.
    #             This is not true in general,
    #             so be sure that it's true in the case at hand.
    #
    ###########################################################################

    pyhf.set_backend(
        "pytorch", precision="64b"
    )  # much faster to run than numpy
    if model.config.poi_index is None:
        raise RuntimeError("Could not retrieve POI index.")
    if not par_bounds:
        par_bounds = model.config.suggested_bounds()
        if par_bounds is None:
            raise RuntimeError("Could not retrieve list of parameter bounds.")
        par_bounds[model.config.poi_index] = (
            0,
            par_bounds[model.config.poi_index][1],
        )

    # set default bracket to (0.1, upper POI bound in measurement) if needed
    bracket_left_default = 0.1
    bracket_right_default = par_bounds[model.config.poi_index][1]
    if bracket is None:
        bracket = (bracket_left_default, bracket_right_default)
    elif bracket[0] == bracket[1]:
        raise ValueError(
            f"the two bracket values must not be the same: " f"{bracket}"
        )

    poi_bracket = [bracket[0], bracket[1]]

    results_obs, poi_values_obs = GetObsLimitBisection(
        poi_bracket,
        toleranceObs,
        maxiterObs,
        data,
        model,
        par_bounds,
        init_pars,
        fix_pars,
    )
    cls_obs_indices = np.argsort(np.array(poi_values_obs))
    list_of_observed = []
    list_of_expected_minus2sigma = []
    list_of_expected_plus2sigma = []
    for i_cls_obs in cls_obs_indices:
        list_of_observed.append(results_obs[i_cls_obs][0])
        list_of_expected_minus2sigma.append(results_obs[i_cls_obs][1][0])
        list_of_expected_plus2sigma.append(results_obs[i_cls_obs][1][4])
    poi_values_obs.sort()
    observed = np.asarray(list_of_observed).ravel()

    #
    # Determine the poi range for expected limits
    # including +/1 and +/-2 sigma bands
    #
    poi_bracket_exp = poi_bracket
    for iPoi, poi in enumerate(poi_values_obs):
        if list_of_expected_minus2sigma[iPoi] > 0.05:
            poi_bracket_exp[0] = poi
        if list_of_expected_plus2sigma[iPoi] < 0.05:
            poi_bracket_exp[1] = poi
            break
    scan_lowerBound = poi_bracket_exp[0]
    scan_upperBound = poi_bracket_exp[1]
    scan_resolution = (scan_upperBound - scan_lowerBound) / nIterExp
    poi_values_exp = np.arange(
        scan_lowerBound, scan_upperBound + scan_resolution, scan_resolution
    )
    logger.debug(f"poi_values_exp = {poi_values_exp}")
    results_exp = [
        pyhf.infer.hypotest(
            poi,
            data,
            model,
            test_stat="qtilde",
            return_expected_set=True,
            par_bounds=par_bounds,
            fixed_params=fix_pars,
        )
        for poi in poi_values_exp
    ]

    expected_minus2sigma = np.asarray([h[1][0] for h in results_exp]).ravel()
    expected_minus1sigma = np.asarray([h[1][1] for h in results_exp]).ravel()
    expected = np.asarray([h[1][2] for h in results_exp]).ravel()
    expected_plus1sigma = np.asarray([h[1][3] for h in results_exp]).ravel()
    expected_plus2sigma = np.asarray([h[1][4] for h in results_exp]).ravel()

    # exit if the 2 sigma band is not Ok - todo

    if max(expected_minus2sigma) < 0.05 or min(expected_plus2sigma) > 0.05:
        raise ValueError(
            "Could not determine expected limit bands. \
                POI range inappropriate."
        )

    all_limits = []
    all_limits.append(np.interp(0.05, observed[::-1], poi_values_obs[::-1]))
    all_limits.append(
        np.interp(0.05, expected_minus2sigma[::-1], poi_values_exp[::-1])
    )
    all_limits.append(
        np.interp(0.05, expected_minus1sigma[::-1], poi_values_exp[::-1])
    )
    all_limits.append(np.interp(0.05, expected[::-1], poi_values_exp[::-1]))
    all_limits.append(
        np.interp(0.05, expected_plus1sigma[::-1], poi_values_exp[::-1])
    )
    all_limits.append(
        np.interp(0.05, expected_plus2sigma[::-1], poi_values_exp[::-1])
    )

    logger.info(f"Upper limit (obs): μ = {all_limits[0]}")
    logger.info(f"Upper limit (expminus2sigma): μ = {all_limits[1]}")
    logger.info(f"Upper limit (expminus1sigma): μ = {all_limits[2]}")
    logger.info(f"Upper limit (exp): μ = {all_limits[3]}")
    logger.info(f"Upper limit (expplus1sigma): μ = {all_limits[4]}")
    logger.info(f"Upper limit (expplus2sigma): μ = {all_limits[5]}")

    limit_results = cabinetry.fit.LimitResults(
        float(all_limits[0]),
        np.asarray(all_limits[1:]),
        results_obs,
        results_exp,
        poi_values_obs,
        # poi_values_exp,
        0.95,
    )
    return limit_results
