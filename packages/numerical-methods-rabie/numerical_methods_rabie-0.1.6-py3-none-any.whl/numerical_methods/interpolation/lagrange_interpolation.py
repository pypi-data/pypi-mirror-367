def lagrange_interpolation(n: int, x: float, points: list[list[float]]) -> None:
    """
    Evaluate the Lagrange interpolating polynomial at a given point.

    :param n: Number of data points.
    :type n: int
    :param x: The value at which to evaluate the polynomial.
    :type x: float
    :param points: List of [xi, yi] data points.
    :type points: list[list[float]]

    :Example:

    >>> points = [[1, 2], [2, 3], [4, 7]]
    >>> lagrange_interpolation(3, 2.5, points)
    """
    for i in range(n):
        if x == points[i][0]:
            p = points[i][1]
            print(f"The value of the Lagrange polynomial at x = {x} is {p}")
            return

    p = 0
    for i in range(n):
        d = 1
        for j in range(n):
            if i != j:
                d *= (points[i][0] - points[j][0])
        q = 1
        for j in range(n):
            if i != j:
                q *= (x - points[j][0])
        p += points[i][1] * q / d
        print(f"l{i} = {q / d}")
    
    print(f"The value of the Lagrange polynomial at x = {x} is {p}")
