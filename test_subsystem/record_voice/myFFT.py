import math
import numpy as np

def batched_butterfly_operation(p, q, r, W, f):
    if int(len(f)) == 1:
        return f
    else:
        tmp1 = []
        tmp2 = []
        for i in range(int(len(f)/2)):
            tmp1.append(f[i] + (W**(r*(2**(q-p))))*f[i + int(len(f)/2)])
            tmp2.append(f[i] - (W**(r*(2**(q-p))))*f[i + int(len(f)/2)])
        return (batched_butterfly_operation(p+1, q, r, W, tmp1)
                + batched_butterfly_operation(p+1, q, r+2**(p-1), W, tmp2))

#define FFT(f): # f is a list of complex numbers
def FFT(f, is_inverse=False):
    N = len(f)
    if is_inverse:
        W = math.e ** (2j*math.pi/N)
    else:
        W = math.e ** (-2j*math.pi/N)
    q = int(math.log(N, 2))
    r = -int(N/2)
    if is_inverse != True:
        r = -int(N/2)
    F = batched_butterfly_operation(1, q, r, W, f)

    #rearrange the output
    for i in range(q):
        tmp = []
        for j in range(int(N/(2**(i+1)))):
            if i == 0:
                tmp.append([F[j], F[j+int(N/2)]])
            else:
                tmp.append(F[j] + F[j+int(N/(2**(i+1)))])
        F = tmp

    F = np.array(F[0])
    if is_inverse != True:
        F = F / N
    return F