# Imports
## Local
## Standard
## Third-Party
import torch
from torch.utils.data import Dataset, DataLoader

# Functions and Classes
## Dataset Class
class EasyMLPData(Dataset):
    """
    Description:
    A basic dataset class for PyTorch that holds input features and target labels.
    This class inherits from torch.utils.data.Dataset and implements the necessary methods.

    Parameters:
    - X (torch.Tensor): Input features of the dataset.
    - y (torch.Tensor): Target labels of the dataset.

    Returns:
    - None: This class does not return anything; it is used to create a dataset object
    that can be used with DataLoader for training and evaluation.
    """
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

## Tensors and Dataloaders
def get_tensors(X_train, y_train, X_val=None, y_val=None):
    """
    Description:
    Converts input features and target labels into PyTorch tensors and prepares them for training.
    If validation data is provided, it also converts them into tensors.

    Parameters:
    - X_train (array-like): Training input features.
    - y_train (array-like): Training target labels.
    - X_val (array-like, optional): Validation input features. Default is None.
    - y_val (array-like, optional): Validation target labels. Default is None.

    Returns:
    - tuple: A tuple containing tensors for training and validation data.
        * If validation data is not provided, the validation tensors will be None.
    """
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)

    if X_val is not None:
        X_val = torch.tensor(X_val, dtype=torch.float32)
    
    if y_val is not None:
        y_val = torch.tensor(y_val, dtype=torch.float32).view(-1, 1)

    return X_train, y_train, X_val, y_val

def get_data_loaders(X_train, y_train, X_val=None, y_val=None, batch_size=1):
    """
    Description:
    Creates PyTorch DataLoader objects for training and validation datasets.

    Parameters:
    - X_train (torch.Tensor): Training input features.
    - y_train (torch.Tensor): Training target labels.
    - X_val (torch.Tensor, optional): Validation input features. Default is None.
    - y_val (torch.Tensor, optional): Validation target labels. Default is None.
    - batch_size (int): Batch size for the DataLoader. Default is 1.

    Returns:
    - tuple: A tuple containing the training DataLoader and validation DataLoader.
        * If validation data is not provided, the validation DataLoader will be None.
    """
    train_loader = DataLoader(
        EasyMLPData(X_train, y_train),
        batch_size=batch_size,
        shuffle=True,
    )

    if X_val is None or y_val is None:
        return train_loader, None
    
    val_loader = DataLoader(
        EasyMLPData(X_val, y_val),
        batch_size=batch_size,
        shuffle=False
    )

    return train_loader, val_loader