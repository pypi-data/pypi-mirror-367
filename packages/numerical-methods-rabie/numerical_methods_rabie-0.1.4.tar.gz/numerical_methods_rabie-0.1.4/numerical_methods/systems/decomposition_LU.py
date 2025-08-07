from utils.linear_solvers import forward_substitution,back_substitution
from utils.dispaly import afficheNormale

def identite(N):
    M = [[0 for i in range(N)]for i in range(N)]
    for i in range(N):
        for j in range(N):
            if i == j:
                M[i][j] = 1
            else:
                M[i][j] = 0

    return M
def lu_decomposition(A: list[list[float]], b: list[float], n: int) -> None:
    """
    Perform LU decomposition of matrix A and solve the system AX = b.

    :param A: Coefficient matrix.
    :type A: list[list[float]]
    :param b: Right-hand side vector.
    :type b: list[float]
    :param n: Size of the system.
    :type n: int
    :return: None
    """
    print("Initial system:")
    U = [row[:] for row in A]
    L = identite(n)

    for k in range(n):
        print(f"U{k}:")
        afficheNormale(U)
        print(f"L{k}:")
        afficheNormale(L)

        pivot = U[k][k]
        print("Pivot:", pivot)

        for i in range(k + 1, n):
            factor = U[i][k] / pivot
            U[i][k] = 0
            L[i][k] = factor
            for j in range(k + 1, n):
                U[i][j] -= U[k][j] * factor

    back_substitution(U, b, n)
    forward_substitution(L, b, n)