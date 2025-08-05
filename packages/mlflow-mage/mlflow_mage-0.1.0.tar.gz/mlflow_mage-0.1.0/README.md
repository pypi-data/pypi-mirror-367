# mlflow-mage

MLFlow mage is a wrapper for MLFlow to allow for better logging capabilites inside Mage AI.

## MlflowSaver

The `MlflowSaver` class simplifies MLflow logging within Mage AI pipelines. It provides a context manager for automatically starting and ending MLflow runs, along with methods for logging parameters, metrics, artifacts, and models.

### Usage Example

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.datasets import load_iris
from mlflow_mage.mlflow_saver import MlflowSaver
from dotenv import load_dotenv

load_dotenv(".env")

iris = load_iris()
X, y = iris.data, iris.target

with MlflowSaver(run_name="end_to_end_pipeline") as logger:
    params = {
        "dataset": "iris",
        "test_size": 0.2,
        "random_state": 42
    }
    logger.log_params(params)

    with logger.create_child_run("preprocessing") as preproc_logger: # Create child runs inside the parent run, which can be usefull as in this example, and also for epoch based training.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=params["test_size"],
            random_state=params["random_state"]
        )

        preproc_logger.log_metrics({
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }, step=0) # Log the metrics once

        preproc_logger.log_metrics({
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }, step=1) # Log them again with the same name, but at another step

    with logger.create_child_run("model_training") as train_logger:
        # Model training
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=params["random_state"]
        )
        model.fit(X_train, y_train)

        # Log hyperparameters
        train_logger.log_params(model.get_params())

        # Log training performance
        y_pred = model.predict(X_test)
        train_logger.log_metrics({
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
