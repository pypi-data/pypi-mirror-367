from utils.dispaly import afficher
def partial_pivoting_elimination(A: list[list[float]], b: list[float], n: int) -> None:
    """
    Perform Gaussian elimination with partial pivoting.

    :param A: Coefficient matrix of size n x n.
    :type A: list[list[float]]
    :param b: Right-hand side vector.
    :type b: list[float]
    :param n: Size of the system.
    :type n: int
    :return: None (modifies A and b in-place).

    This function modifies matrix A and vector b to transform A into an upper triangular matrix.
    """
    print("Initial system:")
    afficher(A, b, n)

    for k in range(n):
        print(f"Iteration k = {k+1}")
        pivot = A[k][k]
        pivot_row = k

        for i in range(k, n):
            if abs(A[i][k]) > abs(pivot):
                pivot = A[i][k]
                pivot_row = i

        if pivot_row != k:
            A[k], A[pivot_row] = A[pivot_row], A[k]
            b[k], b[pivot_row] = b[pivot_row], b[k]

        for i in range(k + 1, n):
            factor = A[i][k] / A[k][k]
            A[i][k] = 0
            for j in range(k + 1, n):
                A[i][j] -= factor * A[k][j]
            b[i] -= factor * b[k]

        afficher(A, b, n)