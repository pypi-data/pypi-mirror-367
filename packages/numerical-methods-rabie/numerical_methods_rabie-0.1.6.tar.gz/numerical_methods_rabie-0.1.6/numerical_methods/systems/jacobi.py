def jacobi_method(A: list[list[float]], b: list[float], n: int, num_iterations: int, x_init: list[float]) -> list[float]:
    """
    Solve a linear system using the Jacobi iterative method.

    :param A: Coefficient matrix of size n x n.
    :type A: list[list[float]]
    :param b: Right-hand side vector.
    :type b: list[float]
    :param n: Size of the system (number of equations).
    :type n: int
    :param num_iterations: Number of iterations to perform.
    :type num_iterations: int
    :param x_init: Initial guess for the solution vector.
    :type x_init: list[float]
    :return: The approximated solution vector after iterations.
    :rtype: list[float]

    :Example:
    >>> A = [[4, -1, 0], [-1, 4, -1], [0, -1, 3]]
    >>> b = [15, 10, 10]
    >>> x_init = [0, 0, 0]
    >>> jacobi_method(A, b, 3, 10, x_init)
    [3.75, 4.375, 4.7917]  # Approximated output
    """
    x = x_init[:]
    for k in range(num_iterations):
        x_new = x[:]
        print(f"Iteration {k}:")
        for i in range(n):
            s = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x_new[i] = (b[i] - s) / A[i][i]
            print(f"x{i} = {x_new[i]}")
        x = x_new
    return x