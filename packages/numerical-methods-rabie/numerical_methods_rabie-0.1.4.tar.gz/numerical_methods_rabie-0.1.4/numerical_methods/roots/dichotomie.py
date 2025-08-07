def dichotomy(start, end, tolerance, func, verbose=True):
    """
    Bisection method to find a root of a continuous function in [start, end].

    :param float start: Lower bound of the interval.
    :param float end: Upper bound of the interval.
    :param float tolerance: Accepted error margin for the root.
    :param callable func: Continuous function f(x) such that f(start) * f(end) < 0.
    :param bool verbose: If True, prints each iteration step.
    :return: Approximate root and list of iterations (a, b, midpoint).
    :rtype: tuple[float, list[tuple[float, float, float]]]
    :raises ValueError: If f(start) * f(end) >= 0.
    """
    if func(start) * func(end) >= 0:
        raise ValueError("Function must change sign over the interval (f(a) * f(b) < 0).")

    iterations = []

    while (end - start) > tolerance:
        mid = (start + end) / 2
        if verbose:
            print(f"[Bisection] a = {start:.6f}, b = {end:.6f}, mid = {mid:.6f}")
        iterations.append((start, end, mid))
        if func(mid) * func(start) < 0:
            end = mid
        else:
            start = mid

    return mid, iterations