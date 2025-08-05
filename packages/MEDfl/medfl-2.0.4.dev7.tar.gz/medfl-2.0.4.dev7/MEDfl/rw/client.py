# client.py
import argparse
import pandas as pd
import flwr as fl
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import accuracy_score, roc_auc_score
from model import Net  # your model definition in model.py
import socket
import platform 

# Differential Privacy configuration class
class DPConfig:
    """
    Configuration for differential privacy.

    Attributes:
        noise_multiplier (float): Noise multiplier for DP.
        max_grad_norm (float): Maximum gradient norm for clipping.
        batch_size (int): Batch size for training.
        secure_rng (bool): Whether to use secure random generator.
    """
    def __init__(
        self,
        noise_multiplier: float = 1.0,
        max_grad_norm: float = 1.0,
        batch_size: int = 32,
        secure_rng: bool = False,
    ):
        self.noise_multiplier = noise_multiplier
        self.max_grad_norm = max_grad_norm
        self.batch_size = batch_size
        self.secure_rng = secure_rng


class FlowerClient(fl.client.NumPyClient):
    def __init__(
        self,
        server_address: str,
        data_path: str = "data/data.csv",
        dp_config: DPConfig = None,
    ):
        self.server_address = server_address

        # 1. Load data from CSV
        df = pd.read_csv(data_path)
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values

        # Convert to tensors and store for metrics
        self.X_tensor = torch.tensor(X, dtype=torch.float32)
        self.y_tensor = torch.tensor(y, dtype=torch.float32)

        # Create DataLoader
        batch_size = dp_config.batch_size if dp_config else 32
        dataset = TensorDataset(self.X_tensor, self.y_tensor)
        self.train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # 2. Initialize model, loss, optimizer
        input_dim = X.shape[1]
        self.model = Net(input_dim)
        
        self.criterion = nn.BCEWithLogitsLoss()
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.01)

        # 3. Set up differential privacy if requested
        self.privacy_engine = None
        if dp_config is not None:
            try:
                from opacus import PrivacyEngine

                # Instantiate engine without secure_rng argument
                self.privacy_engine = PrivacyEngine()
                # Attach privacy engine with secure_rng flag
                self.model, self.optimizer, self.train_loader = self.privacy_engine.make_private(
                    module=self.model,
                    optimizer=self.optimizer,
                    data_loader=self.train_loader,
                    noise_multiplier=dp_config.noise_multiplier,
                    max_grad_norm=dp_config.max_grad_norm,
                    secure_rng=dp_config.secure_rng,
                )
            except ImportError:
                print("Opacus not installed, running without DP.")

    def get_parameters(self, config):
        return [val.cpu().numpy() for val in self.model.state_dict().values()]

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        # Update model parameters
        self.set_parameters(parameters)
        self.model.train()

        total_loss = 0.0
        for X_batch, y_batch in self.train_loader:
            self.optimizer.zero_grad()
            outputs = self.model(X_batch)
            loss = self.criterion(outputs.squeeze(), y_batch)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item() * X_batch.size(0)

        avg_loss = total_loss / len(self.train_loader.dataset)
        # Compute training metrics (accuracy, AUC) on full dataset
        with torch.no_grad():
            logits = self.model(self.X_tensor).squeeze()
            probs = torch.sigmoid(logits).cpu().numpy()
            y_true = self.y_tensor.cpu().numpy()
        binary_preds = (probs >= 0.5).astype(int)
        acc = accuracy_score(y_true, binary_preds)
        auc = roc_auc_score(y_true, probs)
        
        hostname = socket.gethostname()
        os_type = platform.system()

        metrics = {"hostname": hostname, "train_loss": avg_loss, "train_accuracy": acc, "train_auc": auc , "os_type": os_type}
        return self.get_parameters(config), len(self.train_loader.dataset), metrics

    def evaluate(self, parameters, config):
        # Update model parameters
        self.set_parameters(parameters)
        self.model.eval()

        total_loss = 0.0
        all_probs = []
        all_true = []
        with torch.no_grad():
            for X_batch, y_batch in self.train_loader:
                outputs = self.model(X_batch)
                loss = self.criterion(outputs.squeeze(), y_batch)
                total_loss += loss.item() * X_batch.size(0)
                probs = torch.sigmoid(outputs.squeeze()).cpu().numpy()
                all_probs.extend(probs.tolist())
                all_true.extend(y_batch.cpu().numpy().tolist())

        avg_loss = total_loss / len(self.train_loader.dataset)
        binary_preds = [1 if p >= 0.5 else 0 for p in all_probs]
        acc = accuracy_score(all_true, binary_preds)
        auc = roc_auc_score(all_true, all_probs)

        metrics = {"eval_loss": avg_loss, "eval_accuracy": acc, "eval_auc": auc}
        print(f"Evaluation metrics: {metrics}")
        return float(avg_loss), len(self.train_loader.dataset), metrics
        
# client.py - Update the get_properties method
    def get_properties(self, config):
        """
        Return dataset statistics before training starts.

        NOTE: Only scalar values (int, float, str, bool, bytes) are allowed.
        Lists will cause the “not a 1:1 mapping” TypeError.
        """
        num_samples = len(self.X_tensor)
        num_features = self.X_tensor.shape[1]
        # Convert list to comma‑separated string
        column_names = [f"feature_{i}" for i in range(num_features)]
        columns_str = ",".join(column_names)

        hostname = socket.gethostname()
        os_type = platform.system()

        return {
            "hostname": hostname,
            "os_type": os_type,
            "num_samples": num_samples,
            "num_features": num_features,
            "columns": columns_str,  # now a single str, not a list
        }


    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flower client with DP support and metrics")
    parser.add_argument(
        "--server_address",
        type=str,
        required=True,
        help="Address of the Flower server (e.g., 127.0.0.1:8080)",
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="data/data.csv",
        help="Path to your CSV training data",
    )
    parser.add_argument(
        "--dp",
        action="store_true",
        help="Enable differential privacy",
    )
    parser.add_argument(
        "--noise_multiplier",
        type=float,
        default=1.0,
        help="Noise multiplier for DP",
    )
    parser.add_argument(
        "--max_grad_norm",
        type=float,
        default=1.0,
        help="Clip norm for DP",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=32,
        help="Batch size for training",
    )
    args = parser.parse_args()

    dp_config = None
    if args.dp:
        dp_config = DPConfig(
            noise_multiplier=args.noise_multiplier,
            max_grad_norm=args.max_grad_norm,
            batch_size=args.batch_size,
        )

    client = FlowerClient(
        server_address=args.server_address,
        data_path=args.data_path,
        dp_config=dp_config,
    )
    fl.client.start_numpy_client(server_address=client.server_address, client=client)