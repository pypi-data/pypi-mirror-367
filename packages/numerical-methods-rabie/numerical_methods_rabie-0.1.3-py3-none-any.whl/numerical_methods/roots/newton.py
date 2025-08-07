def newton(tolerance, func, func_derivative, initial_guess=1.0, max_iterations=1000, verbose=True):
    """
    Newton-Raphson method to find a root of a function.

    :param float tolerance: Accepted error margin.
    :param callable func: Function f(x).
    :param callable func_derivative: Derivative f'(x).
    :param float initial_guess: Starting value.
    :param int max_iterations: Maximum number of iterations.
    :param bool verbose: If True, prints each iteration step.
    :return: Approximate root and list of iterations (i, x0, x).
    :rtype: tuple[float, list[tuple[int, float, float]]]
    :raises ZeroDivisionError: If f'(x) = 0 during an iteration.
    :raises RuntimeError: If the max number of iterations is reached.
    """
    x0 = initial_guess
    iterations = []
    for i in range(1, max_iterations + 1):
        fx = func(x0)
        dfx = func_derivative(x0)
        if dfx == 0:
            raise ZeroDivisionError("Derivative is zero. No convergence possible.")
        
        x = x0 - fx / dfx
        iterations.append((i, x0, x))
        if verbose:
            print(f"[Newton] Iteration {i}: x0 = {x0:.6f}, x = {x:.6f}")
        if abs(x - x0) < tolerance:
            return x, iterations
        x0 = x

    raise RuntimeError("Maximum number of iterations reached.")