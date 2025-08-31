from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
import numpy as np
import os
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantVectorDB:
    """
    Qdrant vector database manager for storing and searching image embeddings
    """
    
    def __init__(self, 
                 collection_name: str = "product_images",
                 vector_size: int = 512,
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 use_docker: bool = True,
                 timeout: int = 30,
                 api_key: Optional[str] = None,
                 url: Optional[str] = None):
        """
        Initialize Qdrant client and collection
        
        Args:
            collection_name (str): Name of the Qdrant collection
            vector_size (int): Dimension of the embedding vectors (CLIP default: 512)
            qdrant_host (str): Qdrant server host
            qdrant_port (int): Qdrant server port
            use_docker (bool): Whether to use Docker-based Qdrant
            timeout (int): Connection timeout in seconds
            api_key (str, optional): API key for Qdrant Cloud
            url (str, optional): Full URL for Qdrant Cloud
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.use_docker = use_docker
        self.timeout = timeout
        self.api_key = api_key
        self.url = url
        self._client = None
        
        # Test connection and create collection
        self._test_connection()
        self._create_collection()
    
    @property
    def client(self):
        """Lazy initialization of Qdrant client with connection management"""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self):
        """Create Qdrant client based on configuration"""
        try:
            # If URL is provided (Qdrant Cloud), use it with API key
            if self.url and self.api_key:
                client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    timeout=self.timeout,
                    prefer_grpc=False  # Cloud typically uses HTTP
                )
                logger.info(f"Qdrant Cloud client initialized with URL: {self.url}")
            elif self.use_docker:
                # Connect to Docker container or self-hosted instance
                client = QdrantClient(
                    host=self.qdrant_host,
                    port=self.qdrant_port,
                    timeout=self.timeout,
                    prefer_grpc=True  # Better performance for local connections
                )
                logger.info(f"Qdrant client initialized for Docker at {self.qdrant_host}:{self.qdrant_port}")
            else:
                # Use local file-based storage (fallback)
                qdrant_path = "./qdrant_data"
                os.makedirs(qdrant_path, exist_ok=True)
                client = QdrantClient(path=qdrant_path)
                logger.info(f"Qdrant client initialized with local path: {qdrant_path}")
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create Qdrant client: {e}")
            raise
    
    def close(self):
        """Close Qdrant client connection"""
        if self._client:
            try:
                self._client.close()
                self._client = None
                logger.info("Qdrant client connection closed")
            except Exception as e:
                logger.warning(f"Error closing Qdrant client: {e}")
    
    def _test_connection(self):
        """
        Test connection to Qdrant server
        """
        try:
            # Try to get collections to test connection
            collections = self.client.get_collections()
            logger.info("Successfully connected to Qdrant server")
        except Exception as e:
            if self.use_docker:
                logger.error(f"Failed to connect to Qdrant Docker container: {str(e)}")
                logger.error("Make sure to start Qdrant with: docker-compose up -d qdrant")
                raise ConnectionError(
                    "Could not connect to Qdrant Docker container. "
                    "Please ensure Docker is running and start Qdrant with: docker-compose up -d qdrant"
                )
            else:
                logger.error(f"Failed to initialize local Qdrant: {str(e)}")
                raise
    
    def _create_collection(self):
        """
        Create Qdrant collection with appropriate configuration
        """
        try:
            # Try to get collection info first
            try:
                collection_info = self.client.get_collection(self.collection_name)
                logger.info(f"Collection {self.collection_name} already exists")
                return
            except Exception:
                # Collection doesn't exist, create it
                pass
            
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, 
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
                
        except Exception as e:
            error_msg = str(e)
            if "File exists" in error_msg or "already exists" in error_msg.lower():
                logger.info(f"Collection {self.collection_name} already exists (caught during creation)")
                return
            logger.error(f"Error creating collection: {error_msg}")
            raise
    
    def recreate_collection(self):
        """
        Delete and recreate the collection (useful for fresh starts)
        """
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, 
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Recreated collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error recreating collection: {str(e)}")
            raise
    
    def add_product(self, 
                   product_id: str,
                   embedding: np.ndarray,
                   metadata: Dict) -> bool:
        """
        Add a single product to the vector database
        
        Args:
            product_id (str): Unique identifier for the product
            embedding (np.ndarray): Image embedding vector
            metadata (Dict): Product metadata (name, category, price, etc.)
            
        Returns:
            bool: Success status
        """
        try:
            # Convert string ID to integer for Qdrant
            if isinstance(product_id, str) and product_id.startswith('product_'):
                numeric_id = int(product_id.split('_')[1])
            else:
                numeric_id = hash(product_id) % (2**31)  # Fallback for other formats
            
            # Store original ID in metadata
            metadata['original_id'] = product_id
            
            # Create point structure
            point = PointStruct(
                id=numeric_id,
                vector=embedding.tolist(),
                payload=metadata
            )
            
            # Insert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Added product {product_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding product {product_id}: {str(e)}")
            return False
    
    def update_product_metadata(self, product_id: str, metadata: Dict) -> bool:
        """
        Update metadata for an existing product
        
        Args:
            product_id (str): Unique identifier for the product
            metadata (Dict): Updated product metadata
            
        Returns:
            bool: Success status
        """
        try:
            # Convert string ID to integer for Qdrant
            if isinstance(product_id, str) and product_id.startswith('product_'):
                numeric_id = int(product_id.split('_')[1])
            else:
                numeric_id = hash(product_id) % (2**31)
            
            # Store original ID in metadata
            metadata['original_id'] = product_id
            
            # Update metadata using set_payload
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=metadata,
                points=[numeric_id]
            )
            
            logger.info(f"Updated metadata for product {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metadata for product {product_id}: {str(e)}")
            return False
    
    def add_products_batch(self, 
                          products: List[Tuple[str, np.ndarray, Dict]],
                          batch_size: int = 100) -> int:
        """
        Add multiple products in batches
        
        Args:
            products (List[Tuple]): List of (product_id, embedding, metadata)
            batch_size (int): Batch size for insertion
            
        Returns:
            int: Number of successfully added products
        """
        try:
            total_added = 0
            
            for i in range(0, len(products), batch_size):
                batch = products[i:i + batch_size]
                points = []
                
                for product_id, embedding, metadata in batch:
                    # Convert string ID to integer for Qdrant
                    # Extract number from product_XXX format
                    if isinstance(product_id, str) and product_id.startswith('product_'):
                        numeric_id = int(product_id.split('_')[1])
                    else:
                        numeric_id = hash(product_id) % (2**31)  # Fallback for other formats
                    
                    # Store original ID in metadata
                    metadata['original_id'] = product_id
                    
                    point = PointStruct(
                        id=numeric_id,
                        vector=embedding.tolist(),
                        payload=metadata
                    )
                    points.append(point)
                
                # Insert batch
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                total_added += len(points)
                logger.info(f"Added batch {i//batch_size + 1}: {len(points)} products")
            
            logger.info(f"Successfully added {total_added} products to database")
            return total_added
            
        except Exception as e:
            logger.error(f"Error adding products batch: {str(e)}")
            return 0
    
    def search_similar(self, 
                      query_embedding: np.ndarray,
                      limit: int = 5,
                      score_threshold: float = 0.0,
                      category_filter: Optional[str] = None) -> List[Dict]:
        """
        Search for similar products using vector similarity
        
        Args:
            query_embedding (np.ndarray): Query image embedding
            limit (int): Maximum number of results to return
            score_threshold (float): Minimum similarity score threshold
            category_filter (str): Optional category filter
            
        Returns:
            List[Dict]: Search results with metadata and scores
        """
        try:
            # Prepare filter conditions
            filter_condition = None
            if category_filter:
                filter_condition = Filter(
                    must=[
                        FieldCondition(
                            key="category",
                            match=MatchValue(value=category_filter)
                        )
                    ]
                )
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_condition
            )
            
            # Format results
            results = []
            for result in search_results:
                result_dict = {
                    "id": result.payload.get('original_id', result.id),  # Use original ID if available
                    "score": result.score,
                    "metadata": result.payload
                }
                results.append(result_dict)
            
            logger.info(f"Found {len(results)} similar products")
            return results
            
        except Exception as e:
            logger.error(f"Error searching for similar products: {str(e)}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """
        Retrieve a product by its ID
        
        Args:
            product_id (str): Product identifier
            
        Returns:
            Dict: Product data or None if not found
        """
        try:
            # Convert string ID to numeric if needed
            if isinstance(product_id, str) and product_id.startswith('product_'):
                numeric_id = int(product_id.split('_')[1])
            else:
                numeric_id = hash(product_id) % (2**31)
            
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[numeric_id]
            )
            
            if result:
                return {
                    "id": result[0].payload.get('original_id', result[0].id),
                    "metadata": result[0].payload
                }
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
            return None
    
    def get_all_products(self, limit: int = 1000) -> List[Dict]:
        """
        Get all products from the database
        
        Args:
            limit (int): Maximum number of products to retrieve
            
        Returns:
            List[Dict]: All products with metadata
        """
        try:
            # Scroll through all points
            results = []
            offset = 0
            batch_size = min(limit, 100)
            
            while len(results) < limit:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                if not scroll_result[0]:  # No more results
                    break
                
                for point in scroll_result[0]:
                    results.append({
                        "id": point.payload.get('original_id', point.id),
                        "metadata": point.payload
                    })
                
                offset += batch_size
                
                if len(scroll_result[0]) < batch_size:  # Last batch
                    break
            
            logger.info(f"Retrieved {len(results)} products from database")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving all products: {str(e)}")
            return []
    
    def get_collection_info(self) -> Dict:
        """
        Get information about the collection
        
        Returns:
            Dict: Collection statistics
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.get("name", self.collection_name),
                "vector_size": info.config.params.vectors.size,
                "distance_metric": info.config.params.vectors.distance,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from the database
        
        Args:
            product_id (str): Product identifier
            
        Returns:
            bool: Success status
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[product_id]
            )
            logger.info(f"Deleted product {product_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """
        Clear all data from the collection
        
        Returns:
            bool: Success status
        """
        try:
            self.recreate_collection()
            logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
