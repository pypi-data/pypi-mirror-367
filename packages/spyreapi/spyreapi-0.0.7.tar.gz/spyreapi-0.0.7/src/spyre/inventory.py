from .Models.inventory_models import InventoryItem, UnitOfMeasure, UPC
from .client import SpireClient, APIResource
from urllib.parse import urlparse 
from .Exceptions import CreateRequestError
from typing import Any, Optional, Dict, List
from typing import TYPE_CHECKING

class InventoryClient():
    
    def __init__(self, client : SpireClient):
        self.client = client
        self.endpoint = 'inventory'
        self.items = ItemsClient(client=client)
        self.upcs = UpcClient(client=client)
    
    def __getattr__(self, name):
       
        if hasattr(self.items, name):
            return getattr(self.items, name)
       
        if hasattr(self.upcs, name):
            return getattr(self.upcs, name)
        raise AttributeError(f"'InventoryClient' object has no attribute '{name}'")

class ItemsClient():

    def __init__(self, client : SpireClient):
        self.client = client
        self.endpoint = 'inventory/items'

    def get_item(self, id: int = None, part_no: str = None, warehouse: str = None) -> "item":
        """
        Retrieve an inventory item by ID or (part_no + warehouse).

        Sends a GET request to the Spire API to fetch inventory item data for the
        specified ID, or uses a filtered query with part number and warehouse.
        Wraps the result in an `item` instance, which retains a reference to the
        client for further actions.

        Args:
            id (int, optional): The ID of the inventory item to retrieve.
            part_no (str, optional): The part number of the item to retrieve.
            warehouse (str, optional): The warehouse code where the item is located.

        Returns:
            item: An `item` wrapper instance containing the retrieved data.

        Raises:
            ValueError: If neither ID nor (part_no and warehouse) are provided,
                        or if no matching item is found.
        """
        if id is not None:
            response = self.client._get(f"/{self.endpoint}/{str(id)}")
            return item.from_json(response, self.client)

        elif part_no and warehouse:
            items = self.query_inventory_items(filter={"partNo": part_no, "whse": warehouse})
            for itm in items:
                if getattr(itm, "partNo", None) == part_no and getattr(itm, "whse", None) == warehouse:
                    return itm
            raise ValueError(f"No item found with part_no='{part_no}' and warehouse='{warehouse}'.")

        else:
            raise ValueError("You must provide either 'id' or both 'part_no' and 'warehouse'.")
    
    def create_item(self, item : 'InventoryItem') -> 'item':
        """
        Create a new Inventory Item in Spire.

        Sends a POST request to the Inventory/Items endpoint .

        Args:
            item (dict): A InventoryItem instace containing the sales order details.

        Returns:
            item: The created InventoryItem instance.

        Raises:
            CreateRequestError: If the creation fails or response is invalid.
        """

        response =  self.client._post(f"/{self.endpoint}", json=item.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            id = path_segments[-1]
            return self.get_item(id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)

    
    def update_item(self, id: int, inventory_item : 'InventoryItem') -> "item":
        """
        Update an existing Inventory Item by ID.

        Sends a PUT request to the Inventory/Items endpoint with the provided data
        to update the existing record. Returns a wrapped `item` object containing
        the updated information.

        Args:
            id (int): The ID of the item to update.
            inventory_item (InventoryItem): A InventoryItem instance with the sales order details.

        Returns:
            item: An instance of the item wrapper class initialized with 
                        the updated data and client session.
        """
        response = self.client._put(f"/{self.endpoint}/{str(id)}", json=inventory_item.model_dump(exclude_none=True, exclude_unset=True))
        return item.from_json(response, self.client)
    
    def delete_item(self, id: int) -> bool:
        """
        Delete a inventory_item by its ID.

        Sends a DELETE request to the endpoint to remove the specified
        inventory item from the system.

        Args:
            id (int): The ID of the inventory item to delete.

        Returns:
            bool (bool): True if the item was successfully deleted, False otherwise.
        """
        return self.client._delete(f"/{self.endpoint}/{str(id)}")
    

    def query_inventory_items(
        self,
        *,
        query: Optional[str] = None,
        sort: Optional[Dict[str, str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        all: bool = False,
        limit: int = 1000,
        start: int = 0,
        **extra_params
    ) -> List["item"]:
        """
        Query inventory items with optional full-text search, filtering, multi-field sorting, and pagination.

        Args:
            query (str, optional): Full-text search string.
            sort (dict, optional): Dictionary of sorting rules (e.g., {"orderDate": "desc", "orderNo": "asc"}).
            filter (dict, optional): Dictionary of filters to apply (will be JSON-encoded and URL-safe).
            all (bool, optional): If True, retrieves all pages of results.
            limit (int, optional): Number of results per page (max 1000).
            start (int, optional): Starting offset for pagination.
            **extra_params (Any): Any additional parameters to include in the query.

        Returns:
            List[item]: List of wrapped sales order resources.
        """
        return self.client._query(
            endpoint=self.endpoint,
            resource_cls=item,
            query=query,
            sort=sort,
            filter=filter,
            all=all,
            limit=limit,
            start=start,
            **extra_params
        )
    
    def get_item_uoms(self, id : int) -> List["uom"]:
        """
        Retrieve all Unit of Measure (UOM) entries for a specific inventory item.

        This method sends a GET request to the Spire API to retrieve the unit of measure
        records associated with the specified inventory item ID. Each returned record is 
        wrapped into a `uom` object, which includes the model and the client reference.

        Args:
            id (int): The unique identifier of the inventory item.

        Returns:
            List[uom]: A list of `uom` objects representing the UOM records for the item.
        """
        uoms = []
        response = self.client._get(f"{self.endpoint}/{str(id)}/uoms")
        items = response.get('records')
        for item in items:
            uoms.append(uom.from_json(json_data=item, client = self.client, item_id = id))
        return uoms

    def get_uom(self, item_id :int , uom_id : int) -> "uom":
        """
        Retrieve a specific Unit of Measure (UOM) for a given inventory item.

        This method sends a GET request to the Spire API to fetch a single UOM record
        associated with a specific inventory item and UOM ID. The response is wrapped
        into a `uom` object that maintains a reference to the API client.

        Args:
            item_id (int): The unique ID of the inventory item.
            uom_id (int): The unique ID of the UOM to retrieve.

        Returns:
            uom: A `uom` object representing the retrieved unit of measure.

        """
        response = self.client._get(f"/{self.endpoint}/{str(item_id)}/uoms/{str(uom_id)}")
        return uom.from_json(response, self.client , item_id = item_id)
    

    def create_item_uom(self, id: int, uom : UnitOfMeasure) -> "uom":
        """
        Create a new Unit of Measure (UOM) for a specific inventory item.

        Sends a POST request to the Spire API to create a new UOM for the inventory item
        with the specified ID. If successful, the method retrieves and returns the newly
        created UOM object. If the creation fails, an exception is raised.

        Args:
            id (int): The ID of the inventory item for which to create the UOM.
            uom (UnitOfMeasure): A Pydantic model instance representing the UOM to create.

        Returns:
            List[uom]: A list containing the created `uom` object.

        Raises:
            CreateRequestError: If the API response status is not 201 (Created).
        """
        response =  self.client._post(f"/{self.endpoint}/{str(id)}/uoms", json=uom.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            new_uom_id = path_segments[-1]
            return self.get_uom(item_id=id, uom_id=new_uom_id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)

    def delete_uom(self, item_id : int, uom_id :int) -> bool:
        """
        Delete a Unit of Measure (UOM) from a specific inventory item.

        Sends a DELETE request to the Spire API to remove a UOM associated with the
        given item and UOM ID.

        Args:
            item_id (int): The ID of the inventory item.
            uom_id (int): The ID of the Unit of Measure to delete.

        Returns:
            bool: True if the deletion was successful, otherwise raises an error.
        """
        return self.client._delete(f"/{self.endpoint}/{str(item_id)}/uoms/{str(uom_id)}")
    
    def update_item_uom(self, item_id: int, uom_id : int, uom_record :'uom') -> 'uom':
        """
        Update an existing Unit of Measure (UOM) for a given inventory item.

        Sends a PUT request to the Spire API to update the UOM record with the specified
        item and UOM ID using the provided `uom` data.

        Args:
            item_id (int): The ID of the inventory item.
            uom_id (int): The ID of the UOM to update.
            uom (uom): A `uom` instance with updated field values.

        Returns:
            uom: The updated `uom` instance returned from the API.
        """
        response = self.client._put(f"/{self.endpoint}/{str(item_id)}/uoms/{str(uom_id)}", json=uom_record.model_dump(exclude_none=True, exclude_unset=True))
        return uom.from_json(response, self.client, item_id = item_id)
    

    def get_item_upcs(self, id : int) -> List["upc"]:
        """
        Retrieve all UPC records associated with a specific inventory item.

        Sends a GET request to the Spire API to fetch UPCs for the specified item ID,
        then constructs and returns a list of `upc` objects.

        Args:
            id (int): The ID of the inventory item.

        Returns:
            List[upc]: A list of `upc` objects representing the item's UPC codes.
        """
        upcs = []
        response = self.client._get(f"{self.endpoint}/{str(id)}/upcs")
        items = response.get('records')
        for item in items:
            upcs.append(upc.from_json(json_data=item, client = self.client, item_id = id))

        return upcs
    
    def get_upc(self, item_id :int , upc_id : int) -> "upc":
        """
        Retrieve a specific UPC (upc) for a given inventory item.

        This method sends a GET request to the Spire API to fetch a single upc record
        associated with a specific inventory item and upc ID. The response is wrapped
        into a `upc` object that maintains a reference to the API client.

        Args:
            item_id (int): The unique ID of the inventory item.
            upc_id (int): The unique ID of the upc to retrieve.

        Returns:
            upc: A `upc` object representing the retrieved unit of measure.

        """
        response = self.client._get(f"/{self.endpoint}/{str(item_id)}/upcs/{str(upc_id)}")
        return upc.from_json(response, self.client , item_id = item_id)
    
    def create_item_upc(self, id: int, upc : UPC) -> "upc":
        """
        Create a new UPC (upc) for a specific inventory item.

        Sends a POST request to the Spire API to create a new upc for the inventory item
        with the specified ID. If successful, the method retrieves and returns the newly
        created upc object. If the creation fails, an exception is raised.

        Args:
            id (int): The ID of the inventory item for which to create the upc.
            upc (UPC): A Pydantic model instance representing the upc to create.

        Returns:
            List[upc]: A list containing the created `upc` object.

        Raises:
            CreateRequestError: If the API response status is not 201 (Created).
        """
        response =  self.client._post(f"/{self.endpoint}/{str(id)}/upcs", json=upc.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            new_upc_id = path_segments[-1]
            return self.get_upc(item_id=id, upc_id = new_upc_id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)

    def delete_upc(self, item_id : int, upc_id :int) -> bool:
        """
        Delete a UPC (upc) from a specific inventory item.

        Sends a DELETE request to the Spire API to remove a upc associated with the
        given item and upc ID.

        Args:
            item_id (int): The ID of the inventory item.
            upc_id (int): The ID of the Unit of Measure to delete.

        Returns:
            bool: True if the deletion was successful, otherwise raises an error.
        """
        return self.client._delete(f"/{self.endpoint}/{str(item_id)}/upcs/{str(upc_id)}")
    
    def update_item_upc(self, item_id: int, upc_id : int, upc_record :'upc') -> 'upc':
        """
        Update an existing UPC (upc) for a given inventory item.

        Sends a PUT request to the Spire API to update the upc record with the specified
        item and upc ID using the provided `upc` data.

        Args:
            item_id (int): The ID of the inventory item.
            upc_id (int): The ID of the upc to update.
            upc (upc): A `upc` instance with updated field values.

        Returns:
            upc: The updated `upc` instance returned from the API.
        """
        response = self.client._put(f"/{self.endpoint}/{str(item_id)}/upcs/{str(upc_id)}", json=upc_record.model_dump(exclude_none=True, exclude_unset=True))
        return upc.from_json(response, self.client, item_id = item_id)
    

class item(APIResource[InventoryItem]):
    
    endpoint =  'inventory/items'
    Model = InventoryItem

    def delete(self) -> bool:
        """
        Cancels or deletes the item.

        Sends a DELETE request to the API to remove the inventory item with the current ID.

        Returns:
            bool: True if the order was successfully deleted (HTTP 204 or 200), False otherwise.
        """
        
        return self._client._delete(f"/{self.endpoint}/{str(self.id)}")
    
    def update(self, inventory_item: "item" = None) -> 'item':
        """
        Update the inventory item.

        If no item object is provided, updates the current instance on the server.
        If an item object is provided, updates the item using the given data.

        Args:
            inventory_item (item, optional): An optional item instance to use for the update.

        Returns:
            item: The updated item object reflecting the new status.
        """
        data = inventory_item.model_dump(exclude_unset=True, exclude_none=True) if inventory_item else self.model_dump(exclude_unset=True, exclude_none=True)
        response = self._client._put(f"/{self.endpoint}/{str(self.id)}", json=data)
        return item.from_json(response, self._client)    
    
    def get_uoms(self) -> List["uom"]:
        """
        Retrieve all Unit of Measure (UOM) records for the current inventory item.

        This method sends a GET request to the Spire API and returns all UOMs
        associated with this item's ID.

        Returns:
            List[uom]: A list of `uom` instances representing the available units of measure.
        """       
        uoms = []
        response = self._client._get(f"{self.endpoint}/{self.id}/uoms")
        items = response.get('records')
        for item in items:
            uoms.append(uom.from_json(json_data=item, client = self._client, item_id = self.id))

        return uoms
    
    def get_upcs(self) -> List["upc"]:
        """
        Retrieve all UPC records for the current inventory item.

        This method sends a GET request to the Spire API and returns all UPCs
        associated with this item's ID.

        Returns:
            List[upc]: A list of `upc` instances representing the available units of measure.
        """     
        upcs = []
        response = self._client._get(f"{self.endpoint}/{self.id}/upcs")
        items = response.get('records')
        for item in items:
            upcs.append(upc.from_json(json_data=item, client = self._client, item_id = id))

        return upcs

    def add_uom(self, uom_record : UnitOfMeasure) -> "uom":
        """
        Add a new Unit of Measure (UOM) to the current inventory item.

        Sends a POST request to the Spire API to create a new UOM record using the provided
        `UnitOfMeasure` model. If the creation is successful (HTTP 201), it retrieves
        and returns the created UOM.

        Args:
            uom (UnitOfMeasure): The UnitOfMeasure Pydantic model to be created.

        Returns:
            uom (uom): The newly created Unit of measure as a `uom` instance.

        Raises:
            CreateRequestError: If the API returns a non-201 status code during creation.
        """
        response =  self._client._post(f"/{self.endpoint}/{str(self.id)}/uoms", json=uom_record.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            id = path_segments[-1]
            return InventoryClient(self._client).items.get_uom(id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)
        
    def add_upc(self, upc_record : UPC) -> "upc":
        """
        Add a new UPC to the current inventory item.

        Sends a POST request to the Spire API to create a new UPC record using the provided
        UPC model. If the creation is successful (HTTP 201), it retrieves
        and returns the created UPC.

        Args:
            uom_record (UPC): The UPC Pydantic model to be created.

        Returns:
            upc (upc): The newly created UPC as a `upc` instance.

        Raises:
            CreateRequestError: If the API returns a non-201 status code during creation.
        """
        response =  self._client._post(f"/{self.endpoint}/{str(self.id)}/upcs", json=upc_record.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            id = path_segments[-1]
            return InventoryClient(self._client).items.get_upc(id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)
    
class uom(APIResource[UnitOfMeasure]):
    Model = UnitOfMeasure
    _endpoint = ''  # Will be dynamically set in __init__


    def __init__(self, model, client, item_id=None):
        if item_id is None:
            raise ValueError("item_id must be provided")
        super().__init__(model, client)
        uom_id = model.id
        self._endpoint = f'inventory/items/{item_id}/uoms/{str(uom_id)}'
        self._item_id = item_id

    def delete(self) -> bool:
        """
        Cancels or deletes the uom.

        Sends a DELETE request to the API to remove the uom with the current ID.

        Returns:
            bool: True if the uom was successfully deleted (HTTP 204 or 200), False otherwise.
        """
        
        return self._client._delete(f"/{self._endpoint}")
    
    def update(self, _uom: "uom" = None) -> 'uom':
        """
        Update the uom.

        If no uom object is provided, updates the current instance on the server.
        If an uom object is provided, updates the item using the given data.

        Args:
            _uom (uom, optional): An optional uom instance to use for the update.

        Returns:
            uom: The updated uom object reflecting the new status.
        """
        data = _uom.model_dump(exclude_unset=True, exclude_none=True) if _uom else self.model_dump(exclude_unset=True, exclude_none=True)
        response = self._client._put(f"/{self._endpoint}", json=data)
        return uom.from_json(response, self._client, item_id = self._item_id)    

class UpcClient():

    def __init__(self, client : SpireClient):
        self.endpoint = 'inventory/upcs'
        self.client = client

    def get_upc(self, upc_id : int) -> "upc":
        """
        Retrieve a specific UPC (upc) for given id.

        This method sends a GET request to the Spire API to fetch a single upc record
        associated with the upc ID. The response is wrapped
        into a `upc` object that maintains a reference to the API client.

        Args:
            upc_id (int): The unique ID of the upc to retrieve.

        Returns:
            upc: A `upc` object representing the retrieved unit of measure.

        """
        response = self.client._get(f"/{self.endpoint}/{str(upc_id)}")
        return upc.from_json(response, self.client)
    
    def create_item_upc(self, upc : UPC) -> "upc":
        """
        Create a new UPC (upc) for a given id.

        Sends a POST request to the Spire API to create a new upc.
        If successful, the method retrieves and returns the newly
        created upc object. If the creation fails, an exception is raised.
        For a successful creation, either the whse and the partNo or the inventory
        field has to be filled in

        Args:
            upc (UPC): A Pydantic model instance representing the upc to create.

        Returns:
            upc (upc): A list containing the created `upc` object.

        Raises:
            CreateRequestError: If the API response status is not 201 (Created).
        """
        response =  self.client._post(f"/{self.endpoint}/{str(id)}", json=upc.model_dump(exclude_unset=True, exclude_none=True))
        if response.get('status_code') == 201:
            location = response.get('headers').get('location')
            parsed_url = urlparse(location)
            path_segments = parsed_url.path.rstrip("/").split("/")
            new_upc_id = path_segments[-1]
            return self.get_upc(upc_id = new_upc_id)
        else:
            error_message = response.get('content')
            raise CreateRequestError(self.endpoint, status_code=response.get('status_code'), error_message=error_message)

    def delete_upc(self, upc_id :int) -> bool:
        """
        Delete a UPC.

        Sends a DELETE request to the Spire API to remove a upc associated with the
        given upc ID.

        Args:
            upc_id (int): The ID of the Unit of Measure to delete.

        Returns:
            bool: True if the deletion was successful, otherwise raises an error.
        """
        return self.client._delete(f"/{self.endpoint}/{str(upc_id)}")
    
    def update_item_upc(self, upc_id : int, upc_record :'upc') -> 'upc':
        """
        Update an existing UPC.

        Sends a PUT request to the Spire API to update the upc record with the specified
        upc ID using the provided `upc` data.

        Args:
            upc_id (int): The ID of the upc to update.
            upc (upc): A `upc` instance with updated field values.

        Returns:
            upc: The updated `upc` instance returned from the API.
        """
        response = self.client._put(f"/{self.endpoint}/{str(upc_id)}", json=upc_record.model_dump(exclude_none=True, exclude_unset=True))
        return upc.from_json(response, self.client)

class upc(APIResource[UPC]):
    _endpoint = ''         
    Model = UPC

    def __init__(self, model, client, item_id=None):

        super().__init__(model, client)
        upc_id = model.id
        if item_id is None:
            self._endpoint = f'inventory/upcs/{str(upc_id)}'
        else:
            self._endpoint = f'inventory/items/{item_id}/upcs/{str(upc_id)}'
        self._item_id = item_id

    def delete(self) -> bool:
        """
        Cancels or deletes the upc.

        Sends a DELETE request to the API to remove the upc with the current ID.

        Returns:
            bool: True if the upc was successfully deleted (HTTP 204 or 200), False otherwise.
        """
        
        return self._client._delete(f"/{self._endpoint}")
    
    def update(self, _upc: "upc" = None) -> 'upc':
        """
        Update the upc.

        If no upc object is provided, updates the current instance on the server.
        If an upc object is provided, updates the item using the given data.

        Args:
            _upc (upc, optional): An optional upc instance to use for the update.

        Returns:
            upc: The updated upc object reflecting the new status.
        """
        data = _upc.model_dump(exclude_unset=True, exclude_none=True) if _upc else self.model_dump(exclude_unset=True, exclude_none=True)
        response = self._client._put(f"/{self._endpoint}", json=data)
        return upc.from_json(response, self._client, item_id = self._item_id)    