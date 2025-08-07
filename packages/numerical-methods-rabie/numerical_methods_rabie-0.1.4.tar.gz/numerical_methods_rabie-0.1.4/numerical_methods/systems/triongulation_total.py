from utils.linear_solvers import back_substitution
from utils.dispaly import afficher
from utils.num_help import maxM

def full_pivoting_elimination(A: list[list[float]], b: list[float], n: int) -> None:
    """
    Perform Gaussian elimination with full pivoting.

    :param A: Coefficient matrix of size n x n.
    :type A: list[list[float]]
    :param b: Right-hand side vector.
    :type b: list[float]
    :param n: Size of the system.
    :type n: int
    :return: None (modifies A and b in-place).
    """
    print("Initial system:")
    afficher(A, b, n)

    for k in range(n):
        print(f"Iteration k = {k+1}")
        pivot, row, col = maxM(A, k, n)

        if row != k:
            A[row], A[k] = A[k], A[row]
            b[row], b[k] = b[k], b[row]

        if col != k:
            for i in range(n):
                A[i][col], A[i][k] = A[i][k], A[i][col]

        for i in range(k + 1, n):
            factor = A[i][k] / pivot
            b[i] -= factor * b[k]
            A[i][k] = 0
            for j in range(k + 1, n):
                A[i][j] -= factor * A[k][j]

        afficher(A, b, n)

    back_substitution(A, b, n)