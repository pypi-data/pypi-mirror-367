from .client import SpireClient
from .sales import OrdersClient, InvoiceClient
from .customers import CustomerClient
from .inventory import InventoryClient

class Spire:
    """
    High-level interface to interact with the Spire API.

    This class wraps the lower-level API clients (Orders, Invoices, Customers, Inventory) into a unified interface,
    initializing them using shared authentication via `SpireClient`.

    Attributes:
        client (SpireClient): Authenticated Spire API client.
        orders (OrdersClient): Client for accessing sales orders.
        invoices (InvoiceClient): Client for accessing invoices.
        customers (CustomerClient): Client for accessing customer records.
        inventory (InventoryClient): Client for accessing inventory items.
    """
    def __init__(self, host : str, company : str, username : str, password : str):
        """
        Creates a Spire session.

        Args:
            host (str): Spire Server host (e.g., black-disk-5630.spirelan.com:10880).
            company (str): Spire company.
            username (str): Spire user username.
            password (str): Spire user password.
        """
        self.client = SpireClient(host, company, username, password)
        self.orders = OrdersClient(self.client)
        self.invoices = InvoiceClient(self.client)
        self.customers = CustomerClient(self.client)
        self.inventory = InventoryClient(self.client)


