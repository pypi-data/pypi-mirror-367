# Imports
## Standard
## Local
from .helpers import get_activation

## Third-Party
import torch.nn as nn

# Functions and Classes
## Model Class
class MLP(nn.Module):
    """
    Description:
    A simple Multi-Layer Perceptron (MLP) model class for PyTorch.
    This class inherits from nn.Module and allows for flexible layer configurations.

    Parameters:
    - layer_config (list): A list of tuples where each tuple contains:
        * Number of neurons in the layer (int)
        * Activation function (str or None)
        * Dropout rate (float or None)
    - model_name (str): Optional name for the model.
    """
    def __init__(self, layer_config, model_name=""):
        # Initialise the superclass
        super(MLP, self).__init__()

        # Set layer configuration and model name
        self.layer_config = layer_config
        self.model = None
        self.model_name = model_name

    def set_layer_config(self, layer_config):
        """
        Description:
        Sets the layer configuration for the model.

        Parameters:
        - layer_config (list): A list of tuples where each tuple contains:
            * Number of neurons in the layer (int)
            * Activation function (str or None)
            * Dropout rate (float or None)

        Returns:
        - None: This method does not return anything; it updates the layer configuration.
        """
        self.layer_config = layer_config

    def get_layer_config(self):
        """
        Description:
        Returns the current layer configuration of the model.

        Returns:
        - list: The current layer configuration; a list of tuples containing:
            * Number of neurons in the layer (int)
            * Activation function (str or None)
            * Dropout rate (float or None)
        """
        return self.layer_config

    def set_model_layers(self):
        """
        Description:
        Constructs the model layers based on the current layer configuration.
        This method creates a list of layers including linear layers, activation functions, and dropout layers.
        It updates the model attribute with a ModuleList containing these layers.

        Returns:
        - None: This method does not return anything; it updates the model attribute.
        """
        layer_list = []

        for i, l in enumerate(self.layer_config[1:]):
            # Create linear layer
            layer_list.append(
                nn.Linear(self.layer_config[i][0], l[0])
            )

            # Add activation
            if l[1]:
                layer_list.append(get_activation(l[1]))

            # Add Dropout
            if l[2]:
                layer_list.append(nn.Dropout(l[2]))

        # Create model using new layer configuration
        self.model = nn.ModuleList(layer_list)

    def forward(self, x):
        """
        Description:
        Forward pass of the model. It applies the layers defined in the model attribute to the input tensor.

        Parameters:
        - x (torch.Tensor): Input tensor to the model.

        Returns:
        - torch.Tensor: Output tensor after passing through the model layers.
        """
        # Forward pass
        for layer in self.model:
            x = layer(x)

        return x