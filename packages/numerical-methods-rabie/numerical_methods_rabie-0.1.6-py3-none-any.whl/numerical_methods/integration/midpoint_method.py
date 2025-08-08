from utils.dispaly import afficher_entete_simple, afficher_ligne_resultat_simple, afficher_fin_simple

def midpoint_method(f, x_end, x0, y0, h, n, f_exact):
    """
    Solve a differential equation using Midpoint method (RK2).

    Parameters
    ----------
    f : Callable
        Function f(x, y).
    x_end : float
        Final x value.
    x0 : float
        Initial x value.
    y0 : float
        Initial y value.
    h : float
        Step size.
    n : int
        Number of steps.
    f_exact : Callable
        Exact solution.

    Returns
    -------
    float
        Final y value at x_end.
    """
    y = y0
    x = x0
    n = int(n)
    afficher_entete_simple("Runge-Kutta Order 2 - Midpoint")
    for _ in range(n):
        y += h * f(x + h / 2, y + (h / 2) * f(x, y))
        x += h
        afficher_ligne_resultat_simple(x, y, f_exact(x))
    afficher_fin_simple()
    return y
