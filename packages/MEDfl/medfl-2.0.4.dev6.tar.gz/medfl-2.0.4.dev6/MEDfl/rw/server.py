import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.server.server import ServerConfig
from typing import Optional, Any
from MEDfl.rw.strategy import Strategy
import asyncio
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.common import GetPropertiesIns
from flwr.common import GetPropertiesIns


class FederatedServer:
    """
    FederatedServer wraps the launch and configuration of a Flower federated learning server.

    Attributes:
        server_address (str): Server host and port in the format "host:port".
        server_config (ServerConfig): Configuration for the Flower server.
        strategy_wrapper (Strategy): Wrapper around the actual Flower strategy.
        strategy (flwr.server.Strategy): Actual Flower strategy instance.
        certificates (Any): Optional TLS certificates.
        connected_clients (list): List of connected client IDs.

    Methods:
        start():
            Launch the Flower server with the specified strategy and log client connections.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        num_rounds: int = 3,
        strategy: Optional[Strategy] = None,
        certificates: Optional[Any] = None,
    ):
        """
        Initialize the FederatedServer.

        Args:
            host (str): Hostname or IP to bind the server to.
            port (int): Port to listen on.
            num_rounds (int): Number of federated learning rounds to execute.
            strategy (Optional[Strategy]): Optional custom strategy wrapper.
            certificates (Optional[Any]): Optional TLS certificates.
        """
        # Server address and configuration
        self.server_address = f"{host}:{port}"
        self.server_config = ServerConfig(num_rounds=num_rounds)

        # Use custom or default strategy
        self.strategy_wrapper = strategy or Strategy()
        self.strategy_wrapper.create_strategy()
        if self.strategy_wrapper.strategy_object is None:
            raise ValueError("Strategy object not initialized. Call create_strategy() first.")
        self.strategy = self.strategy_wrapper.strategy_object

        self.certificates = certificates
        self.connected_clients = []  # Track connected client IDs


    def start(self) -> None:
        """
        Start the Flower server with the configured strategy and track client connections.
        """
        print(f"Using strategy: {self.strategy_wrapper.name}")
        print(f"Starting Flower server on {self.server_address} with strategy {self.strategy_wrapper.name}")

        # Use a custom client manager that logs client connections
        client_manager = TrackingClientManager(self)

        # Launch the Flower server
        fl.server.start_server(
            server_address=self.server_address,
            config=self.server_config,
            strategy=self.strategy,
            certificates=self.certificates,
            client_manager=client_manager,
        )


class TrackingClientManager(fl.server.client_manager.SimpleClientManager):
    """
    TrackingClientManager extends the default SimpleClientManager to log client connections.

    Attributes:
        server (FederatedServer): The FederatedServer instance this manager belongs to.
        client_properties (dict): Placeholder for storing client-specific properties.
    """

    def __init__(self, server: FederatedServer):
        """
        Initialize the TrackingClientManager.

        Args:
            server (FederatedServer): Reference to the FederatedServer.
        """
        super().__init__()
        self.server = server
        self.client_properties = {}

    def register(self, client: ClientProxy) -> bool:
        """
        Register a client, log its connection, and patch its 'fit' method
        to log real-time training completion.
        """
        success = super().register(client)

        if success:
            # 1. Log client hostname (your original logic)
            if client.cid not in self.server.connected_clients:
                asyncio.run(self._fetch_and_log_hostname(client))

            # 2. Monkey-patch the 'fit' method to log training completion
            original_fit = client.fit

            async def timed_fit(ins, timeout):
                import time
                start_time = time.time()
                fit_result = await original_fit(ins, timeout)
                duration = time.time() - start_time

                print(f"🟢 [Real-time] Client {client.cid} finished training in {duration:.2f} seconds")
                # Optional: notify your frontend here
                return fit_result

            client.fit = timed_fit  # Patch the method

        return success


    async def _fetch_and_log_hostname(self, client: ClientProxy):
        """
        Asynchronously fetch and log the client's hostname or CID.

        Args:
            client (ClientProxy): The client proxy.
        """
        # Optional: uncomment to fetch hostname from client properties
        # try:
        #     ins = GetPropertiesIns(config={})
        #     props = await client.get_properties(ins=ins, timeout=10.0, group_id=0)
        #     hostname = props.properties.get("hostname", "unknown")
        # except Exception as e:
        #     hostname = f"Error: {e}"

        print(f"✅ Client connected - CID: {client.cid}")
        self.server.connected_clients.append(client.cid)
