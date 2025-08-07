from utils.dispaly import afficher
from utils.linear_solvers import back_substitution

def forward_elimination_non_null(A: list[list[float]], b: list[float], n: int) -> list[float] | int:
    """
    Perform Gaussian elimination with a non-zero pivot constraint and solve the system using back substitution.

    This function assumes that no pivot will be zero (i.e., A[k][k] ≠ 0). Otherwise, it prints an error.

    :param A: Coefficient matrix of size n x n.
    :type A: list[list[float]]
    :param b: Right-hand side vector.
    :type b: list[float]
    :param n: Number of equations/unknowns.
    :type n: int
    :return: Solution vector X if successful, or 0 if a zero pivot is encountered.
    :rtype: list[float] | int
    """
    print("System:")
    afficher(A, b, n)
    for k in range(n - 1):
        print(f"Iteration k = {k + 1}")
        pivot = A[k][k]
        if pivot != 0:
            for i in range(k + 1, n):
                q = A[i][k]
                A[i][k] = 0
                b[i] -= (q / pivot) * b[k]
                for j in range(k + 1, n):
                    A[i][j] -= A[k][j] * q / pivot
        else:
            print("Zero pivot encountered. Aborting.")
            return 0
        afficher(A, b, n)
    
    X = back_substitution(A, b, n)
    return X
