import httpx
import os

class Result:
    def __init__(self, response):
        self.trace_id = None
        self.meta = None
        try:
            self.response = response.json()
            self.data = self.response.get('data')
            self.error = self.response.get("error")
            self.trace_id = self.response.get("traceId")
            self.meta = self.response.get("meta")
            if self.error:
                self.data = None
                self.success = False
            else:
                self.success = True
        except:
            self.data = None
            self.error = response.text
            self.success = False

    def __getitem__(self, key):
        return self.data.get(key)

    def __str__(self) -> str:
        return f"CarthooksResult(success={self.success}, data={self.data}, error={self.error})"

class Client:
    def __init__(self, timeout=None, max_connections=None, max_keepalive_connections=None, http2=None):
        """
        Initialize Carthooks client with HTTP/2 support and connection pooling

        Args:
            timeout: Request timeout in seconds (default: 30.0, env: CARTHOOKS_TIMEOUT)
            max_connections: Maximum number of connections in the pool (default: 100, env: CARTHOOKS_MAX_CONNECTIONS)
            max_keepalive_connections: Maximum number of keep-alive connections (default: 20, env: CARTHOOKS_MAX_KEEPALIVE_CONNECTIONS)
            http2: Enable HTTP/2 support (default: True, env: CARTHOOKS_HTTP2_DISABLED to disable)
        """
        self.base_url = os.getenv('CARTHOOKS_API_URL')
        if self.base_url == None:
            self.base_url = "https://api.carthooks.com"
        self.headers = {
            'Content-Type': 'application/json',
        }

        # Get configuration from environment variables with fallbacks
        if timeout is None:
            timeout = float(os.getenv('CARTHOOKS_TIMEOUT', '30.0'))

        if max_connections is None:
            max_connections = int(os.getenv('CARTHOOKS_MAX_CONNECTIONS', '100'))

        if max_keepalive_connections is None:
            max_keepalive_connections = int(os.getenv('CARTHOOKS_MAX_KEEPALIVE_CONNECTIONS', '20'))

        if http2 is None:
            http2_disabled = os.getenv('CARTHOOKS_HTTP2_DISABLED', 'false').lower()
            http2 = not (http2_disabled in ('true', '1', 'yes', 'on'))

        # Configure connection pool limits
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections
        )

        # Create HTTP client with HTTP/2 support and connection pooling
        self.client = httpx.Client(
            timeout=timeout,
            limits=limits,
            http2=http2
        )

    def setAccessToken(self, access_token):
        """Set the access token for API authentication"""
        self.headers['Authorization'] = f'Bearer {access_token}'
        # Update client headers
        self.client.headers.update(self.headers)

    def getItems(self, app_id, collection_id, limit=20, start=0, **options):
        """Get items from a collection with pagination"""
        options['pagination[start]'] = start
        options['pagination[limit]'] = limit
        url = f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items'
        response = self.client.get(url, headers=self.headers, params=options)
        return Result(response)

    def getItemById(self, app_id, collection_id, item_id, fields=None):
        """Get a specific item by ID"""
        params = {}
        if fields:
            params['fields'] = fields
        response = self.client.get(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}',
            headers=self.headers,
            params=params if params else None
        )
        return Result(response)
    

# POST    /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/     OpenAPI.CreateSubItem
# PUT     /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/items/:sub_row_id/:sub_row_id     OpenAPI.UpdateSubItem
# DELETE  /open/api/v1/apps/:app_id/collections/:entity_id/items/:row_id/subform/:field_id/items/:sub_row_id/:sub_row_id     OpenAPI.DeleteSubItem
    def createSubItem(self, app_id, collection_id, item_id, field_id, data):
        """Create a sub-item in a subform field"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)

    def updateSubItem(self, app_id, collection_id, item_id, field_id, sub_item_id, data):
        """Update a sub-item in a subform field"""
        print("data", data)
        response = self.client.put(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}/items/{sub_item_id}',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)

    def deleteSubItem(self, app_id, collection_id, item_id, field_id, sub_item_id):
        """Delete a sub-item from a subform field"""
        response = self.client.delete(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/subform/{field_id}/items/{sub_item_id}',
            headers=self.headers
        )
        return Result(response)
    
    def getSubmissionToken(self, app_id, collection_id, options):
        """Get a submission token for creating items"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/submission-token',
            headers=self.headers,
            json=options
        )
        return Result(response)

    def updateSubmissionToken(self, app_id, collection_id, item_id, options):
        """Update a submission token for an existing item"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/update-token',
            headers=self.headers,
            json=options
        )
        return Result(response)

    def createItem(self, app_id, collection_id, data):
        """Create a new item in a collection"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)

    def updateItem(self, app_id, collection_id, item_id, data):
        """Update an existing item"""
        response = self.client.put(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}',
            headers=self.headers,
            json={'data': data}
        )
        return Result(response)
    
    def lockItem(self, app_id, collection_id, item_id, lock_timeout=600, lock_id=None, subject=None):
        """Lock an item to prevent concurrent modifications"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/lock',
            headers=self.headers,
            json={'lockTimeout': lock_timeout, 'lockId': lock_id, 'lockSubject': subject}
        )
        return Result(response)

    def unlockItem(self, app_id, collection_id, item_id, lock_id=None):
        """Unlock a previously locked item"""
        response = self.client.post(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}/unlock',
            headers=self.headers,
            json={'lockId': lock_id}
        )
        return Result(response)

    def deleteItem(self, app_id, collection_id, item_id):
        """Delete an item from a collection"""
        response = self.client.delete(
            f'{self.base_url}/v1/apps/{app_id}/collections/{collection_id}/items/{item_id}',
            headers=self.headers
        )
        return Result(response)

    def getUploadToken(self):
        """Get a token for file uploads"""
        response = self.client.post(
            f'{self.base_url}/v1/uploads/token',
            headers=self.headers
        )
        return Result(response)

    def getUser(self, user_id):
        """Get user information by user ID"""
        response = self.client.get(
            f'{self.base_url}/v1/users/{user_id}',
            headers=self.headers
        )
        return Result(response)

    def getUserByToken(self, token):
        """Get user information by token"""
        response = self.client.get(
            f'{self.base_url}/v1/user-token/{token}',
            headers=self.headers
        )
        return Result(response)

    def close(self):
        """Close the client and release connection pool resources"""
        if hasattr(self, 'client'):
            self.client.close()
    
