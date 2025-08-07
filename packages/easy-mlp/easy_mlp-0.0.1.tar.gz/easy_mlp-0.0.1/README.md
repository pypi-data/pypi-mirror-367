# EasyMLP

A comprehensive Python library providing all the boilerplate code you need for building, training, and evaluating Multi-Layer Perceptron (MLP) models with PyTorch. EasyMLP eliminates the repetitive code and provides a clean, intuitive interface for both regression and classification tasks.

## Features

- **Flexible Model Architecture**: Build custom MLPs with configurable layers, activation functions, and dropout
- **Comprehensive Training Pipeline**: Built-in trainer with support for both regression and classification
- **Rich Metrics Tracking**: Automatic calculation and visualization of training/validation metrics
- **Multiple Loss Functions**: Support for various loss functions including custom RMSE
- **Optimizer Selection**: Easy integration with popular optimizers (Adam, SGD, RMSprop, L-BFGS)
- **Activation Functions**: Wide range of activation functions from ReLU to advanced options like GELU and Mish
- **Data Management**: Streamlined data loading and preprocessing utilities
- **Visualization**: Built-in plotting capabilities for training metrics

## Installation

```bash
pip install easy-mlp
```

Or install from source:

```bash
git clone https://github.com/bheki-maenetja/easy-mlp.git
cd easy-mlp
pip install -e .
```

## Quick Start

```python
import torch
from easy_mlp import MLP, MLPTrainer, get_tensors, get_data_loaders, get_optimiser, get_loss_fn

# Prepare your data
X_train, y_train, X_val, y_val = get_tensors(X_train, y_train, X_val, y_val)
train_loader, val_loader = get_data_loaders(X_train, y_train, X_val, y_val, batch_size=32)

# Define model architecture
layer_config = [
    (input_size, None, None),           # Input layer
    (64, "relu", 0.2),                 # Hidden layer 1: 64 neurons, ReLU, 20% dropout
    (32, "relu", 0.1),                 # Hidden layer 2: 32 neurons, ReLU, 10% dropout
    (1, None, None)                    # Output layer
]

# Create model
model = MLP(layer_config)
model.set_model_layers()

# Setup training
optimiser = get_optimiser("adam", model, l_rate=0.001)
loss_fn = get_loss_fn("mse")  # For regression
trainer = MLPTrainer(type="reg")

# Train the model
trainer.train(
    model=model,
    num_epochs=100,
    optimiser=optimiser,
    loss_fn=loss_fn,
    train_loader=train_loader,
    val_loader=val_loader
)
```

## Core Components

### 1. Data Management (`data.py`)

#### `EasyMLPData` Class

A PyTorch Dataset wrapper for easy data handling.

```python
from easy_mlp import EasyMLPData

# Create dataset
dataset = EasyMLPData(X_tensor, y_tensor)

# Access data
X_sample, y_sample = dataset[0]
print(f"Dataset size: {len(dataset)}")
```

**Parameters:**
- `X` (torch.Tensor): Input features
- `y` (torch.Tensor): Target labels

#### `get_tensors()` Function

Converts numpy arrays or lists to PyTorch tensors with proper formatting.

```python
from easy_mlp import get_tensors

# Convert training and validation data
X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor = get_tensors(
    X_train, y_train, X_val, y_val
)

# Convert only training data
X_train_tensor, y_train_tensor, None, None = get_tensors(X_train, y_train)
```

**Parameters:**
- `X_train` (array-like): Training input features
- `y_train` (array-like): Training target labels
- `X_val` (array-like, optional): Validation input features
- `y_val` (array-like, optional): Validation target labels

**Returns:**
- Tuple of PyTorch tensors: `(X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor)`

#### `get_data_loaders()` Function

Creates PyTorch DataLoader objects for batch processing.

```python
from easy_mlp import get_data_loaders

# Create data loaders
train_loader, val_loader = get_data_loaders(
    X_train_tensor, 
    y_train_tensor, 
    X_val_tensor, 
    y_val_tensor, 
    batch_size=32
)

# Training only
train_loader, None = get_data_loaders(X_train_tensor, y_train_tensor, batch_size=64)
```

**Parameters:**
- `X_train` (torch.Tensor): Training input features
- `y_train` (torch.Tensor): Training target labels
- `X_val` (torch.Tensor, optional): Validation input features
- `y_val` (torch.Tensor, optional): Validation target labels
- `batch_size` (int): Batch size for training (default: 1)

**Returns:**
- Tuple of DataLoaders: `(train_loader, val_loader)`

### 2. Model Architecture (`models.py`)

#### `MLP` Class

A flexible Multi-Layer Perceptron implementation with configurable architecture.

```python
from easy_mlp import MLP

# Define layer configuration
layer_config = [
    (10, None, None),      # Input layer: 10 features
    (64, "relu", 0.2),     # Hidden layer 1: 64 neurons, ReLU, 20% dropout
    (32, "relu", 0.1),     # Hidden layer 2: 32 neurons, ReLU, 10% dropout
    (16, "tanh", None),    # Hidden layer 3: 16 neurons, Tanh, no dropout
    (1, None, None)        # Output layer: 1 output (regression)
]

# Create model
model = MLP(layer_config, model_name="MyRegressionModel")
model.set_model_layers()

# Forward pass
output = model(input_tensor)
```

**Layer Configuration Format:**
Each layer is defined as a tuple: `(neurons, activation, dropout)`
- `neurons` (int): Number of neurons in the layer
- `activation` (str or None): Activation function name (see available activations below)
- `dropout` (float or None): Dropout rate (0.0 to 1.0)

**Methods:**
- `set_layer_config(layer_config)`: Update the layer configuration
- `get_layer_config()`: Return current layer configuration
- `set_model_layers()`: Build the model architecture
- `forward(x)`: Perform forward pass

### 3. Helper Functions (`helpers.py`)

#### `get_activation()` Function

Returns PyTorch activation functions by name.

```python
from easy_mlp import get_activation

# Available activation functions
activations = {
    "relu": get_activation("relu"),      # ReLU
    "elu": get_activation("elu"),        # Exponential Linear Unit
    "selu": get_activation("selu"),      # Scaled Exponential Linear Unit
    "gelu": get_activation("gelu"),      # Gaussian Error Linear Unit
    "celu": get_activation("celu"),      # Continuously Differentiable ELU
    "sigmoid": get_activation("sigmoid"), # Sigmoid
    "tanh": get_activation("tanh"),      # Hyperbolic Tangent
    "mish": get_activation("mish"),      # Mish
    "swish": get_activation("swish"),    # Swish (Hardswish)
    "shrink": get_activation("shrink"),  # Hard Shrink
    "tanshrink": get_activation("tanshrink") # Tanh Shrink
}
```

#### `get_loss_fn()` Function

Returns loss functions for different tasks.

```python
from easy_mlp import get_loss_fn

# Available loss functions
loss_functions = {
    "binary": get_loss_fn("binary"),     # Binary Cross Entropy
    "multiclass": get_loss_fn("multiclass"), # Cross Entropy
    "mse": get_loss_fn("mse"),           # Mean Squared Error
    "rmse": get_loss_fn("rmse"),         # Root Mean Square Error (custom)
    "mae": get_loss_fn("mae"),           # Mean Absolute Error
    "smoothl1": get_loss_fn("smoothl1"), # Smooth L1 Loss
    "poisson": get_loss_fn("poisson"),   # Poisson NLL Loss
    "nll": get_loss_fn("nll")            # Negative Log Likelihood
}
```

#### `get_optimiser()` Function

Returns optimizers with specified parameters.

```python
from easy_mlp import get_optimiser

# Available optimizers
optimizers = {
    "adam": get_optimiser("adam", model, l_rate=0.001),
    "sgd": get_optimiser("sgd", model, l_rate=0.01, momentum=0.9),
    "rms": get_optimiser("rms", model, l_rate=0.001),
    "lbfgs": get_optimiser("lbfgs", model, l_rate=0.1)
}
```

#### `RMSELoss` Class

Custom Root Mean Square Error loss function.

```python
from easy_mlp import RMSELoss

rmse_loss = RMSELoss()
loss = rmse_loss(predictions, targets)
```

#### `print_row()` Function

Utility function for formatted table printing.

```python
from easy_mlp import print_row

# Print formatted row
row = print_row(["Epoch", "Loss", "Accuracy"], total_len=80, pad_char="-")
print(row)
```

### 4. Training (`trainers.py`)

#### `MLPTrainer` Class

Comprehensive training pipeline for MLP models.

```python
from easy_mlp import MLPTrainer

# For regression
reg_trainer = MLPTrainer(type="reg")

# For binary classification
cls_trainer = MLPTrainer(type="cls", is_multiclass=False)

# For multiclass classification
multiclass_trainer = MLPTrainer(type="cls", is_multiclass=True)

# Train the model
trainer.train(
    model=model,
    num_epochs=100,
    optimiser=optimiser,
    loss_fn=loss_fn,
    train_loader=train_loader,
    val_loader=val_loader,
    pred_threshold=0.5,  # For binary classification
    device="cpu"         # or "cuda" for GPU
)
```

**Parameters:**
- `type` (str): Task type - "reg" for regression, "cls" for classification
- `is_multiclass` (bool): Whether to handle multiclass classification

**Training Parameters:**
- `model`: PyTorch model to train
- `num_epochs`: Number of training epochs
- `optimiser`: PyTorch optimizer
- `loss_fn`: Loss function
- `train_loader`: Training data loader
- `val_loader`: Validation data loader (optional)
- `pred_threshold`: Classification threshold (default: 0.5)
- `device`: Device to use ("cpu" or "cuda")

### 5. Metrics (`metrics.py`)

#### `MetricsManager` Class

Comprehensive metrics tracking and visualization.

```python
from easy_mlp import MetricsManager

# Initialize metrics manager
mm = MetricsManager(type="reg")  # or type="cls" for classification

# Calculate metrics
loss, rmse, mse, mae, r2 = mm.calculate(
    loss=0.5, 
    preds=predictions, 
    labels=targets, 
    append_list="train",
    return_metrics=True
)

# Print formatted metrics
result_row = mm.print_metrics(epoch=10)

# Generate visualization
chart = mm.get_metric_chart("loss")
chart.show()

# Generate multiple charts
charts = mm.get_metric_chart_collection(["loss", "rmse", "r2"])
charts.show()

# Reset metrics
mm.reset()
```

**Available Metrics:**

**Regression Metrics:**
- Loss: Training/validation loss
- RMSE: Root Mean Square Error
- MSE: Mean Squared Error
- MAE: Mean Absolute Error
- R²: R-squared score

**Classification Metrics:**
- Loss: Training/validation loss
- Accuracy: Classification accuracy
- Precision: Precision score
- Recall: Recall score
- F1: F1 score

**Methods:**
- `calculate()`: Calculate and optionally store metrics
- `print_metrics()`: Print formatted metrics row
- `reset()`: Clear all stored metrics
- `get_metric_name()`: Get full metric name from shorthand
- `get_metric_chart()`: Generate single metric plot
- `get_metric_chart_collection()`: Generate multiple metric plots

## Complete Examples

### Regression Example

```python
import torch
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from easy_mlp import *

# Generate sample data
X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Prepare data
X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor = get_tensors(
    X_train, y_train, X_val, y_val
)
train_loader, val_loader = get_data_loaders(
    X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor, batch_size=32
)

# Define model
layer_config = [
    (10, None, None),      # Input layer
    (64, "relu", 0.2),     # Hidden layer 1
    (32, "relu", 0.1),     # Hidden layer 2
    (16, "relu", None),    # Hidden layer 3
    (1, None, None)        # Output layer
]

model = MLP(layer_config, model_name="RegressionModel")
model.set_model_layers()

# Setup training
optimiser = get_optimiser("adam", model, l_rate=0.001)
loss_fn = get_loss_fn("mse")
trainer = MLPTrainer(type="reg")

# Train
trainer.train(
    model=model,
    num_epochs=50,
    optimiser=optimiser,
    loss_fn=loss_fn,
    train_loader=train_loader,
    val_loader=val_loader
)

# Visualize results
mm = trainer.mm
charts = mm.get_metric_chart_collection(["loss", "rmse", "r2"])
charts.show()
```

### Binary Classification Example

```python
import torch
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from easy_mlp import *

# Generate sample data
X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Prepare data
X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor = get_tensors(
    X_train, y_train, X_val, y_val
)
train_loader, val_loader = get_data_loaders(
    X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor, batch_size=32
)

# Define model
layer_config = [
    (10, None, None),      # Input layer
    (64, "relu", 0.2),     # Hidden layer 1
    (32, "relu", 0.1),     # Hidden layer 2
    (1, "sigmoid", None)   # Output layer with sigmoid
]

model = MLP(layer_config, model_name="BinaryClassifier")
model.set_model_layers()

# Setup training
optimiser = get_optimiser("adam", model, l_rate=0.001)
loss_fn = get_loss_fn("binary")
trainer = MLPTrainer(type="cls", is_multiclass=False)

# Train
trainer.train(
    model=model,
    num_epochs=50,
    optimiser=optimiser,
    loss_fn=loss_fn,
    train_loader=train_loader,
    val_loader=val_loader,
    pred_threshold=0.5
)

# Visualize results
mm = trainer.mm
charts = mm.get_metric_chart_collection(["loss", "acc", "f1"])
charts.show()
```

### Multiclass Classification Example

```python
import torch
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from easy_mlp import *

# Generate sample data
X, y = make_classification(n_samples=1000, n_features=10, n_classes=3, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Prepare data
X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor = get_tensors(
    X_train, y_train, X_val, y_val
)
train_loader, val_loader = get_data_loaders(
    X_train_tensor, y_train_tensor, X_val_tensor, y_val_tensor, batch_size=32
)

# Define model
layer_config = [
    (10, None, None),      # Input layer
    (64, "relu", 0.2),     # Hidden layer 1
    (32, "relu", 0.1),     # Hidden layer 2
    (3, None, None)        # Output layer (3 classes)
]

model = MLP(layer_config, model_name="MulticlassClassifier")
model.set_model_layers()

# Setup training
optimiser = get_optimiser("adam", model, l_rate=0.001)
loss_fn = get_loss_fn("multiclass")
trainer = MLPTrainer(type="cls", is_multiclass=True)

# Train
trainer.train(
    model=model,
    num_epochs=50,
    optimiser=optimiser,
    loss_fn=loss_fn,
    train_loader=train_loader,
    val_loader=val_loader
)

# Visualize results
mm = trainer.mm
charts = mm.get_metric_chart_collection(["loss", "acc", "f1"])
charts.show()
```

## Advanced Usage

### Custom Layer Configuration

```python
# Complex architecture with different activation functions
layer_config = [
    (20, None, None),           # Input: 20 features
    (128, "relu", 0.3),         # Hidden 1: 128 neurons, ReLU, 30% dropout
    (64, "gelu", 0.2),          # Hidden 2: 64 neurons, GELU, 20% dropout
    (32, "mish", 0.1),          # Hidden 3: 32 neurons, Mish, 10% dropout
    (16, "tanh", None),         # Hidden 4: 16 neurons, Tanh, no dropout
    (1, "sigmoid", None)        # Output: 1 neuron, Sigmoid
]

model = MLP(layer_config)
model.set_model_layers()
```

### Custom Training Loop

```python
# Manual training with custom logic
model.train()
for epoch in range(num_epochs):
    for batch_X, batch_y in train_loader:
        optimiser.zero_grad()
        predictions = model(batch_X)
        loss = loss_fn(predictions, batch_y)
        loss.backward()
        optimiser.step()
    
    # Custom validation
    model.eval()
    with torch.no_grad():
        val_predictions = model(val_X)
        val_loss = loss_fn(val_predictions, val_y)
        print(f"Epoch {epoch}: Val Loss = {val_loss.item():.4f}")
```

### GPU Training

```python
# Move model and data to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Update data loaders to use GPU
train_loader, val_loader = get_data_loaders(
    X_train_tensor.to(device), 
    y_train_tensor.to(device), 
    X_val_tensor.to(device), 
    y_val_tensor.to(device), 
    batch_size=32
)

# Train on GPU
trainer.train(
    model=model,
    num_epochs=100,
    optimiser=optimiser,
    loss_fn=loss_fn,
    train_loader=train_loader,
    val_loader=val_loader,
    device=device
)
```

## Dependencies

- PyTorch >= 1.9.0
- NumPy >= 1.21.0
- scikit-learn >= 1.0.0
- pretty-plotly >= 0.1.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with PyTorch for deep learning capabilities
- Inspired by the need for simplified MLP implementations
- Thanks to the open-source community for various activation functions and loss implementations
