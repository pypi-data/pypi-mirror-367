# Imports
## Local
## Standard
## Third-Party
import torch
import torch.nn as nn
import torch.optim as optim

# Functions and Classes
## Printing Rows
def print_row(cols, total_len=100, pad_char=" ", side_bound="|", return_str=True):
    """
    Description:
    Prints a row of columns with specified total length, padding character, and side boundaries.

    Parameters:
    - cols (list): List of column strings to be printed.
    - total_len (int): Total length of the row to be printed.
    - pad_char (str): Character used for padding between columns.
    - side_bound (str): Character used for the side boundaries of the row.
    - return_str (bool): If True, returns the row as a string; otherwise, prints it.

    Returns:
    - str: The formatted row string if return_str is True.
    - None: If return_str is False, the row is printed directly.
    """
    # Get width for each column
    col_width = total_len // len(cols)

    # Get strings representing each column
    col_strings = []
    for c in cols:
        c_len = len(c)
        pad_len = (col_width - c_len) // 2 - 1
        pad_mod = (col_width - c_len) % 2
        c_str = f"{side_bound}{pad_len*pad_char}{c}{(pad_len + pad_mod)*pad_char}{side_bound}"
        col_strings.append(c_str)

    if return_str: return "".join(col_strings)
    print("".join(col_strings))

## Losses
class RMSELoss(nn.Module):
    """
    Description:
    Root Mean Square Error (RMSE) loss function.
    This class inherits from nn.Module and implements the forward method to compute RMSE.
    """
    def __init__(self):
        super().__init__()
    
    def forward(self, yhat, y):
        mse = torch.mean((yhat - y) ** 2, axis=0)
        return torch.sqrt(mse)

def get_loss_fn(fn_name="binary"):
    """
    Description:
    Returns a loss function based on the provided name.

    Parameters:
    - fn_name (str): Name of the loss function to retrieve. Options include:
        - "binary": Binary Cross Entropy Loss
        - "multiclass": Cross Entropy Loss for multi-class classification
        - "mse": Mean Squared Error Loss
        - "rmse": Root Mean Square Error Loss
        - "mae": Mean Absolute Error Loss
        - "smoothl1": Smooth L1 Loss
        - "poisson": Poisson Negative Log Likelihood Loss
        - "nll": Negative Log Likelihood Loss
    
    Returns:
    - nn.Module: The corresponding loss function as a PyTorch module.
    """
    if fn_name == "binary":
        return nn.BCELoss()
    elif fn_name == "multiclass":
        return nn.CrossEntropyLoss()
    elif fn_name == "mse":
        return nn.MSELoss()
    elif fn_name == "rmse":
        return RMSELoss()
    elif fn_name == "mae":
        return nn.L1Loss()
    elif fn_name == "smoothl1":
        return nn.SmoothL1Loss()
    elif fn_name == "poisson":
        return nn.PoissonNLLLoss()
    elif fn_name == "nll":
        return nn.NLLLoss()
    else:
        raise ValueError(f"Unknown loss function: {fn_name}")

## Optimisers and Initialisation
def get_optimiser(opt_name, model, l_rate, **kwargs):
    """
    Description:
    Returns an optimiser based on the provided name and model parameters.

    Parameters:
    - opt_name (str): Name of the optimiser to retrieve. Options include:
        - "adam": Adam optimiser
        - "sgd": Stochastic Gradient Descent optimiser
        - "rms": RMSprop optimizer
        - "lbfgs": L-BFGS optimiser
    - model (nn.Module): The model whose parameters will be optimised.
    - l_rate (float): Learning rate for the optimiser.
    - **kwargs: Additional keyword arguments to pass to the optimiser.
    """
    if opt_name == "adam":
        return optim.Adam(model.parameters(), lr=l_rate, **kwargs)
    elif opt_name == "sgd":
        return optim.SGD(model.parameters(), lr=l_rate, **kwargs)
    elif opt_name == "rms":
        return optim.RMSprop(model.parameters(), lr=l_rate, **kwargs)
    elif opt_name == "lbfgs":
        return optim.LBFGS(model.parameters(), lr=l_rate, **kwargs)

def param_init(m, init_name):
    if init_name == "zeroes":
        if type(m) == nn.Linear:
            nn.init.zeros_(m.weight)
    elif init_name == "ones":
        if type(m) == nn.Linear:
            nn.init.ones_(m.weight)
    elif init_name == "uniform":
        if type(m) == nn.Linear:
            nn.init.uniform_(m.weight)
    elif init_name == "normal":
        if type(m) == nn.Linear:
            nn.init.normal_(m.weight)
    elif init_name == "xavier":
        if type(m) == nn.Linear:
            nn.init.xavier_normal_(m.weight)
    elif init_name == "kaiming":
        if type(m) == nn.Linear:
            nn.init.kaiming_normal_(m.weight)

## Activations
def get_activation(act_name):
    """
    Description:
    Returns a PyTorch activation function based on the provided name.

    Parameters:
    - act_name (str): Name of the activation function to retrieve. Options include:
        - "relu": ReLU activation
        - "elu": Exponential Linear Unit activation
        - "selu": Scaled Exponential Linear Unit activation
        - "gelu": Gaussian Error Linear Unit activation
        - "celu": Continuously Differentiable Exponential Linear Unit activation
        - "sigmoid": Sigmoid activation
        - "tanh": Hyperbolic Tangent activation
        - "mish": Mish activation
        - "swish": Swish activation
        - "shrink": Hard Shrink activation
        - "tanshrink": Tanh Shrink activation
    
    Returns:
    - nn.Module: The corresponding activation function as a PyTorch module.
    """
    if act_name == "relu":
        return nn.ReLU()
    elif act_name == "elu":
        return nn.ELU()
    elif act_name == "selu":
        return nn.SELU()
    elif act_name == "gelu":
        return nn.GELU()
    elif act_name == "celu":
        return nn.CELU()
    elif act_name == "sigmoid":
        return nn.Sigmoid()
    elif act_name == "tanh":
        return nn.Tanh()
    elif act_name == "mish":
        return nn.Mish()
    elif act_name == "swish":
        return nn.Hardswish()
    elif act_name == "shrink":
        return nn.Hardshrink()
    elif act_name == "tanshrink":
        return nn.Tanhshrink()