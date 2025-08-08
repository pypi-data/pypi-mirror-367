from utils.dispaly import afficher_entete_simple, afficher_ligne_resultat_simple, afficher_fin_simple
def taylor_method(f, x_end, x0, y0, h, n, df_dx, df_dy, f_exact):
    """
    Solve a differential equation using Taylor method (2nd order).

    Parameters
    ----------
    f : Callable
        Function f(x, y).
    x_end : float
        Endpoint of the integration interval.
    x0 : float
        Initial x.
    y0 : float
        Initial y.
    h : float
        Step size (recalculated from interval).
    n : int
        Number of steps.
    df_dx : Callable
        Partial derivative of f with respect to x.
    df_dy : Callable
        Partial derivative of f with respect to y.
    f_exact : Callable
        Exact solution for comparison.

    Returns
    -------
    None
    """
    h = (x_end - x0) / n
    y = y0
    x = x0
    afficher_entete_simple("Taylor Method")
    afficher_ligne_resultat_simple(x, y0, f_exact(x))
    for _ in range(n):
        f_val = f(x, y)
        y += h * f_val + (h**2 / 2) * (df_dx(x) + df_dy(x) * f_val)
        x += h
        afficher_ligne_resultat_simple(x, y, f_exact(x))
    afficher_fin_simple()
