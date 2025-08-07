def maxM(M, k, n):
    max_val = 0
    max_i, max_j = k, k
    for i in range(k, n):
        for j in range(k, n):
            if abs(M[i][j]) > abs(max_val):
                max_val = M[i][j]
                max_i, max_j = i, j
    return max_val, max_i, max_j