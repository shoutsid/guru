import numpy as np


def sigmoid_activation(x):
    """
    Sigmoid activation function.
    """
    return 1 / (1 + np.exp(-x))


def relu_activation(x):
    """
    ReLU activation function.
    """
    return np.maximum(0, x)


def tanh_activation(x):
    """
    Tanh activation function.
    """
    return np.tanh(x)


def softmax_activation(x):
    """
    Softmax activation function.
    """
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=1, keepdims=True)


def CMM(I, W_in):
    """
    Compute matrix multiplication followed by calculation of N.
    """
    D = W_in.shape[0]  # Assuming W_in is a square matrix
    L, N = [np.zeros_like(I)], np.zeros_like(I)

    for d in range(1, D+1):
        L_d = I if d == 1 else L[d-1] @ W_in[d-1]
        N_d = L_d > 0
        L.append(L_d)
        N = N + (2 ** (d-1)) * N_d.astype(int)

    return L, N


def FFF(I, W_in, W_out, activation_func):
    """
    Perform the FFF inference forward pass with the specified activation function.
    """
    L, N = CMM(I, W_in)
    O = activation_func(L[1])

    for d in range(1, len(W_out)+1):
        O_d = O @ W_out[d-1]
        O = O + O_d

    return O

# Example usage:
# Define input matrix I, weight matrices W_in and W_out
# I = np.array([[...]])  # Example input matrix
# W_in = np.array([[..., ...], [..., ...]])  # Example W_in matrix
# W_out = np.array([[..., ...], [..., ...]])  # Example W_out matrix
# Choose an activation function from the ones provided
# activation_func = relu_activation  # or sigmoid_activation, tanh_activation, softmax_activation
# Uncomment the following lines and replace the ellipses with actual numbers to use the function
# output_matrix = FFF(I, W_in, W_out, activation_func)
# print(output_matrix)
