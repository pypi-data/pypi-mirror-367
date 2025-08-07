from tabulate import tabulate

def print_iterations(iterations, headers):
    print(tabulate(iterations,headers=headers,tablefmt="fancy_grid"))
    
def afficher(A,B,n):
    for i in range(n):
        print("[",end="")
        for j in range(n):
            print(f"{A[i][j]}  ",end="")
            if j==n-1:
                print(f"] [{B[i]}]")
        print()
        
def afficheNormale(M):
    
    for i in range(len(M)):
        print()
        for j in range(len(M[i])):
            print(M[i][j], end=" ") 

    print()
    
def afficher_entete_simple(method_name):
    print(f"\nMéthode {method_name.upper()} - Résultats numériques vs exacts")
    print(f"{'x':>8} | {'yk (num)':>15} | {'y (exact)':>15} | {'Erreur |y - yk|':>18}")
    print("-" * 62)

def afficher_ligne_resultat_simple(x, yk, yexact):
    erreur = abs(yexact - yk)
    print(f"{x:8.3f} | {yk:15.8f} | {yexact:15.8f} | {erreur:18.8f}")

def afficher_fin_simple():
    print("-" * 62)