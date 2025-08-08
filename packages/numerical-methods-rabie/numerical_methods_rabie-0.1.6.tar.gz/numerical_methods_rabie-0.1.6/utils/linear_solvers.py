def forward_substitution(A: list[list[float]], b: list[float], n: int) -> list[float]:
    """
    Solve a lower triangular linear system using forward substitution.(c'est bien la methode de resolution decenter en francais)

    This function solves the system `AX = b` where `A` is a lower triangular matrix.

    :param A: Lower triangular coefficient matrix of size n x n.
    :type A: list[list[float]]
    :param b: Right-hand side vector.
    :type b: list[float]
    :param n: The size of the system (number of equations/unknowns).
    :type n: int
    :return: The solution vector X.
    :rtype: list[float]

    :Example:

    >>> A = [[2, 0, 0],
    ...      [3, 1, 0],
    ...      [1, -1, 1]]
    >>> b = [2, 5, 1]
    >>> forward_substitution(A, b, 3)
    [1.0, 2.0, 2.0]
    """
    X = [0.0 for _ in range(n)]
    X[0] = b[0] / A[0][0]

    for i in range(1, n):
        sum_ax = 0.0
        for j in range(i):
            sum_ax += A[i][j] * X[j]
        X[i] = (b[i] - sum_ax) / A[i][i]

    return X


def back_substitution(A: list[list[float]], b: list[float], n: int) -> list[float]:
    """
    Solve an upper triangular linear system using back substitution.(c'est bien la methode de resolution rementer en francais)

    This function solves the system `AX = b` where `A` is an upper triangular matrix.

    :param A: Upper triangular coefficient matrix of size n x n.
    :type A: list[list[float]]
    :param b: Right-hand side vector.
    :type b: list[float]
    :param n: The size of the system (number of equations/unknowns).
    :type n: int
    :return: The solution vector X.
    :rtype: list[float]

    :Example:

    >>> A = [[2, -1, 1],
    ...      [0, 1, 2],
    ...      [0, 0, 3]]
    >>> b = [2, 4, 9]
    >>> back_substitution(A, b, 3)
    [1.0, 2.0, 3.0]
    """
    X = [0.0 for _ in range(n)]
    X[n - 1] = b[n - 1] / A[n - 1][n - 1]

    for i in range(n - 2, -1, -1):
        sum_ax = 0.0
        for j in range(i + 1, n):
            sum_ax += A[i][j] * X[j]
        X[i] = (b[i] - sum_ax) / A[i][i]

    return X

def verify_determinant(A: list[list[float]], n: int) -> float:
    """
    Estimate a determinant-like value by multiplying upper triangle elements.

    **Note:** This is not the formal determinant but an approximate product of upper diagonal terms.

    :param A: Matrix of size n x n.
    :type A: list[list[float]]
    :param n: Matrix size.
    :type n: int
    :return: The product of the upper triangle elements.
    :rtype: float
    """
    det = 1
    for i in range(n):
        for j in range(n):
            if j > i:
                det *= A[i][j]
    return det

