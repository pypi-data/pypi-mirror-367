from utils.dispaly import afficher_entete_rk4, afficher_ligne_resultat_rk4, afficher_fin_rk4
def runge_kutta_4(f, x_end, x0, y0, h, n, f_exact):
    """
    Solve a differential equation using the 4th-order Runge-Kutta method.

    Parameters
    ----------
    f : Callable
        Function f(x, y).
    x_end : float
        Endpoint of integration.
    x0 : float
        Starting x value.
    y0 : float
        Initial y value.
    h : float
        Step size.
    n : int
        Number of steps.
    f_exact : Callable
        Exact solution for comparison.

    Returns
    -------
    float
        Final value of y at x_end.
    """
    y = y0
    x = x0
    n = int(n)
    afficher_entete_rk4()

    for _ in range(n):
        s1 = h * f(x, y)
        s2 = h * f(x + h / 2, y + s1 / 2)
        s3 = h * f(x + h / 2, y + s2 / 2)
        s4 = h * f(x + h, y + s3)
        y += (1 / 6) * (s1 + 2 * s2 + 2 * s3 + s4)
        x += h
        afficher_ligne_resultat_rk4(x, y, f_exact(x), s1, s2, s3, s4)

    afficher_fin_rk4()
    return y
