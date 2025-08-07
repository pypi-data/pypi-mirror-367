def soigner_dd(d: list[list[float]]) -> None:
    """
    Nicely display the divided differences table.

    :param d: Divided difference matrix.
    :type d: list[list[float]]
    """
    for row in d:
        print([f"{x:.6f}" if x != 0 else "0" for x in row])

def newton_interpolation(n: int, x: float, points: list[list[float]]) -> list[list[float]]:
    """
    Evaluate the Newton interpolating polynomial at a given point using divided differences.

    :param n: Number of data points.
    :type n: int
    :param x: The value at which to evaluate the polynomial.
    :type x: float
    :param points: List of [xi, yi] data points.
    :type points: list[list[float]]
    :return: The divided difference table.
    :rtype: list[list[float]]

    :Example:

    >>> points = [[1, 2], [2, 3], [4, 7]]
    >>> newton_interpolation(3, 2.5, points)
    """
    d = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        d[i][0] = points[i][1]

    for j in range(1, n):
        for i in range(j, n):
            if (points[i][0] - points[i - j][0]) != 0:
                d[i][j] = (d[i][j - 1] - d[i - 1][j - 1]) / (points[i][0] - points[i - j][0])

    print("Divided difference matrix:")
    soigner_dd(d)

    p = d[0][0]
    term = 1
    for i in range(1, n):
        term *= (x - points[i - 1][0])
        p += term * d[i][i]

    print(f"The Newton interpolating polynomial at x = {x} is {p}")
    return d
