def fixed_point(tolerance, g_func, initial_guess=1.0, max_iterations=1000, verbose=True):
    """
    Fixed-point iteration method to find a solution of x = g(x).

    :param float tolerance: Accepted error margin.
    :param callable g_func: Function g(x) such that x = g(x).
    :param float initial_guess: Starting value.
    :param int max_iterations: Maximum number of iterations.
    :param bool verbose: If True, prints each iteration step.
    :return: Approximate fixed point and list of iterations (i, x0, x).
    :rtype: tuple[float, list[tuple[int, float, float]]]
    :raises RuntimeError: If the max number of iterations is reached.
    """
    x0 = initial_guess
    iterations = []
    for i in range(1, max_iterations + 1):
        x = g_func(x0)
        iterations.append((i, x0, x))
        if verbose:
            print(f"[Fixed Point] Iteration {i}: x0 = {x0:.6f}, x = {x:.6f}")
        if abs(x - x0) < tolerance:
            return x, iterations
        x0 = x

    raise RuntimeError("Maximum number of iterations reached.")