# Imports
## Standard
## Local
from .helpers import print_row

## Third-Party
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.metrics import root_mean_squared_error, mean_squared_error, mean_absolute_error, r2_score
import pretty_plotly.plot as pp

# Functions and Classes
class MetricsManager:
    """
    Description:
    A class to manage and calculate various metrics for regression and classification tasks.
    This class supports both regression and classification metrics, allowing for flexible metric management.

    Parameters:
    - type (str): Type of metrics to manage, either "reg" for regression or "cls" for classification.
    - is_multiclass (bool): If True, uses 'weighted' average for classification metrics; otherwise, uses 'binary'.

    Returns:
    - None: This class does not return anything; it is used to manage and calculate metrics
    during training and evaluation.
    """
    def __init__(self, type="reg", is_multiclass=False):
        assert type in ["reg", "cls"], "Metric type must be 'reg' or 'cls'."
        self.type = type
        self.avg = "binary" if not is_multiclass else "weighted"

        self.metrics = {
            "train": {
                "loss": [],
                "acc": [],
                "prec": [],
                "rec": [],
                "f1": [],
                "rmse": [],
                "mse": [],
                "mae": [],
                "r2": [],
            },
            "val": {
                "loss": [],
                "acc": [],
                "prec": [],
                "rec": [],
                "f1": [],
                "rmse": [],
                "mse": [],
                "mae": [],
                "r2": [],
            }
        }

        if type == "reg":
            self.active_metrics = ["loss", "rmse", "mse", "mae", "r2"]
        elif type == "cls":
            self.active_metrics = ["loss", "acc", "prec", "rec", "f1"]
    
    def calculate(self, loss, preds, labels, append_list="", return_metrics=False):
        """
        Description:
        Calculates and appends metrics based on the type of task (regression or classification).

        Parameters:
        - loss (float): The loss value for the current batch.
        - preds (array-like): Predicted values from the model.
        - labels (array-like): True labels for the current batch.
        - append_list (str): If provided, appends metrics to the specified list ("train" or "val").
        - return_metrics (bool): If True, returns the calculated metrics; otherwise, appends them to the lists.

        Returns:
        - tuple: If return_metrics is True, returns a tuple of calculated metrics.
            * For regression: (loss, rmse, mse, mae, r2)
            * For classification: (loss, acc, prec, rec, f1)
        """
        assert append_list in ["", "train", "val"], "append_list must be '', 'train', or 'val'."
        if self.type == "reg":
            # Calculate RMSE, MSE, MAE, and R2 score
            rmse = root_mean_squared_error(labels, preds)
            mse = mean_squared_error(labels, preds)
            mae = mean_absolute_error(labels, preds)
            r2 = r2_score(labels, preds)

            # Append metrics to lists if necessary
            if append_list:
                self.metrics[append_list]["loss"].append(loss)
                self.metrics[append_list]["rmse"].append(rmse)
                self.metrics[append_list]["mse"].append(mse)
                self.metrics[append_list]["mae"].append(mae)
                self.metrics[append_list]["r2"].append(r2)

            if return_metrics: return loss, rmse, mse, mae, r2
        elif self.type == "cls":
            # Calculate accuracy, precision, recall, and F1 score
            acc = accuracy_score(labels, preds)
            prec = precision_score(labels, preds, average=self.avg) 
            rec = recall_score(labels, preds, average=self.avg)
            f1 = f1_score(labels, preds, average=self.avg)

            # Append metrics to lists if necessary
            if append_list:
                self.metrics[append_list]["loss"].append(loss)
                self.metrics[append_list]["acc"].append(acc)
                self.metrics[append_list]["prec"].append(prec)
                self.metrics[append_list]["rec"].append(rec)
                self.metrics[append_list]["f1"].append(f1)
            
            if return_metrics: return loss, acc, prec, rec, f1
    
    def print_metrics(self, epoch=0, row_len=120):
        """
        Description:
        Prints the metrics for the current epoch in a formatted row.

        Parameters:
        - epoch (int): The current epoch number. Default is 0.

        Returns:
        - str: A formatted string representing the metrics for the current epoch.
        """
        result_row = [
            f"{self.metrics['train'][m][-1]:.2e}"
            if self.metrics['train'][m] != []
            else f"{np.nan:.2e}"
            for m in self.active_metrics
        ] + [
            f"{self.metrics['val'][m][-1]:.2e}"
            if self.metrics['val'][m] != []
            else f"{np.nan:.2e}"
            for m in self.active_metrics
        ]

        result_row_str = print_row(result_row, total_len=row_len)
        return f"{epoch+1}".zfill(3) + " " + result_row_str
    
    def reset(self):
        """
        Description:
        Resets the metrics for both training and validation sets.

        Parameters:
        - None: This method does not take any parameters.
        """
        self.metrics = {
            k: {m: [] for m in self.metrics[k]}
            for k in self.metrics
        }

    def get_metric_name(self, short_hand):
        """
        Description:
        Returns the full name of a metric based on its shorthand notation.

        Parameters:
        - short_hand (str): The shorthand notation of the metric. Examples include:
            * "loss", "acc", "prec", "rec", "f1" for classification metrics
            * "rmse", "mse", "mae", "r2" for regression metrics.
        
        Returns:
        - str: The full name of the metric.
        """
        # Make sure shorthand is lowercased
        short_hand = short_hand.lower()

        return {
            "loss": "Loss",
            "losses": "Loss",
            "acc": "Accuracy",
            "accs": "Accuracy",
            "accuracy": "Accuracy",
            "prec": "Precision",
            "precs": "Precision",
            "precision": "Precision",
            "rec": "Recall",
            "recs": "Recall",
            "recall": "Recall",
            "f1": "F1 Score",
            "f1s": "F1 Score",
            "rmse": "RMSE",
            "rmses": "RMSE",
            "mse": "MSE",
            "mses": "MSE",
            "mae": "MAE",
            "maes": "MAE",
            "r2": "R2 Score",
            "r2s": "R2 Score",
        }[short_hand]

    def get_metric_chart(self, metric_name):
        """
        Description:
        Generates a chart for a specific metric over epochs.

        Parameters:
        - metric_name (str): The name of the metric to plot. Should be one of the active metrics.
            * Examples include "loss", "acc", "prec", "rec", "f1", "rmse", "mse", "mae", "r2".
        
        Returns:
        - pp.Figure: A Plotly figure containing the chart for the specified metric.
        """
        # Get relevant logs
        train_logs = self.metrics["train"][metric_name]
        val_logs = self.metrics["val"][metric_name]

        if val_logs == []:
            val_logs = [np.nan] * len(train_logs)

        # Get relevant chart title
        title = self.get_metric_name(metric_name)

        # Create chart traces
        x = np.arange(1, len(train_logs)+1)
        train_trace = pp.create_trace(
            x, 
            train_logs, 
            name=f"Training {title}", 
            mode="lines+markers",
        )
        val_trace = pp.create_trace(
            x,
            val_logs, 
            name=f"Validation {title}", 
            mode="lines+markers",
        )

        # Creating chart
        chart = pp.plot_data(
            title=title,
            train_data=train_trace,
            val_data=val_trace,
            x_label="Epochs",
            y_label=title,
        )

        return chart
    
    def get_metric_chart_collection(self, metric_names):
        """
        Description:
        Generates a collection of charts for multiple metrics over epochs.

        Parameters:
        - metric_names (list): A list of metric names to plot. Each name should be one of the active metrics.
            * Examples include "loss", "acc", "prec", "rec", "f1", "rmse", "mse", "mae", "r2".
        
        Returns:
        - pp.Figure: A Plotly figure containing a collection of charts for the specified metrics
        """
        # Get charts
        charts = [self.get_metric_chart(n) for n in metric_names]

        # Get subplot titles
        subplot_titles = [self.get_metric_name(n) for n in metric_names]

        # Get multiplot title
        title = ", ".join(subplot_titles[:-1]) + " and " + subplot_titles[-1]

        # Positioning charts and labels
        x_labels = {}
        y_labels = {}
        plots = {}

        if len(metric_names) % 2 == 0 and len(metric_names) > 2:
            cols = 2
            rows = len(metric_names) // 2

            for i, name in enumerate(zip(metric_names[::2], metric_names[1::2])):
                for j in range(2):
                    key = (i+1, j+1)
                    index = int(f"{i}{j}", 2)
                    x_labels[key] = "Epochs"
                    y_labels[key] = subplot_titles[index]
                    plots[key] = charts[index]
        else:
            cols = 1
            rows = len(metric_names)

            for i, _ in enumerate(metric_names):
                key = (i+1, 1)
                x_labels[key] = "Epochs"
                y_labels[key] = subplot_titles[i]
                plots[key] = charts[i]

        # Creating plot collection
        all_plots = pp.plot_collection(
            plots,
            title=title,
            cols=cols,
            rows=rows,
            subplot_titles=subplot_titles,
            x_labels=x_labels,
            y_labels=y_labels,
        )

        return all_plots
