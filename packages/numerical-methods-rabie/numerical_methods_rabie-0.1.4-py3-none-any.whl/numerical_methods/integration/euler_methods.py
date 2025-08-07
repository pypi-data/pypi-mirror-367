from utils.dispaly import *

def euler_method(f, x_end, x0, y0, h, n, f_exact):
    """
    Solve a differential equation using the Euler method.

    Parameters
    ----------
    f : Callable
        The function f(x, y) representing dy/dx.
    x_end : float
        The endpoint of the interval.
    x0 : float
        The initial x value.
    y0 : float
        The initial y value.
    h : float
        Step size (will be recomputed from x0 to x_end and n).
    n : int
        Number of steps.
    f_exact : Callable
        The exact solution function for comparison.

    Returns
    -------
    None
    """
    h = (x_end - x0) / n
    y = y0
    x = x0
    afficher_entete_simple("Euler Method")
    afficher_ligne_resultat_simple(x, y, f_exact(x))
    for _ in range(n):
        y += h * f(x, y)
        x += h
        afficher_ligne_resultat_simple(x, y, f_exact(x))
    afficher_fin_simple()

def modified_euler(f, x_end, x0, y0, h, n, f_exact):
    """
    Solve a differential equation using Modified Euler (RK2) method.

    Parameters
    ----------
    f : Callable
        Function f(x, y).
    x_end : float
        End x value.
    x0 : float
        Initial x.
    y0 : float
        Initial y.
    h : float
        Step size.
    n : int
        Number of steps.
    f_exact : Callable
        Exact solution.

    Returns
    -------
    float
        Final y value.
    """
    y = y0
    x = x0
    n = int(n)
    afficher_entete_simple("Runge-Kutta Order 2 - Modified Euler")
    for _ in range(n):
        y += (h / 2) * (f(x, y) + f(x + h, y + h * f(x, y)))
        x += h
        afficher_ligne_resultat_simple(x, y, f_exact(x))
    afficher_fin_simple()
    return y
