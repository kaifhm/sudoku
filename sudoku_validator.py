def transpose(matrix):
    result = []
    for i in range(len(matrix)):
        interim = []
        for j in range(len(matrix[0])):
            interim.append(matrix[j][i])
        result.append(interim)
    return result


def split(li, n):
    k, m = divmod(len(li), n)
    return (li[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def valid_solution(board):
    validator = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
    for i in board:
        if not set(i) == validator:
            solution = False
            break

    for j in transpose(board):
        if not set(j) == validator:
            solution = False
            break

    blocks = [list(split(i, 3)) for i in board]

    for line in blocks:
        for n in range(0, 9, 3):
            for m in range(3):
                if set(blocks[n][m]+blocks[n+1][m]+blocks[n+2][m]) != validator:
                    return False

    return True


#PAS2020127069
