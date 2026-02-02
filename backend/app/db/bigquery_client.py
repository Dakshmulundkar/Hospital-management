"""BigQuery client for data storage and retrieval"""
from google.cloud import bigquery
from typing import List, Optional
from datetime import datetime
from ..config import settings


class BigQueryClient:
    """Client for interacting with BigQuery"""
    
    def __init__(self):
        self.client = None
        self.dataset_id = settings.bigquery_dataset
        self.available = False
        
        # Only initialize if project ID is available
        if settings.bigquery_project_id:
            try:
                self.client = bigquery.Client(project=settings.bigquery_project_id)
                self.available = True
            except Exception as e:
                print(f"BigQuery initialization failed: {e}")
                self.available = False
    
    def get_table_ref(self, table_name: str) -> str:
        """Get fully qualified table reference"""
        return f"{settings.bigquery_project_id}.{self.dataset_id}.{table_name}"
    
    async def check_connection(self) -> bool:
        """Check if BigQuery connection is healthy"""
        if not self.available or not self.client:
            return False
            
        try:
            # Try to list tables in the dataset
            tables = list(self.client.list_tables(self.dataset_id, max_results=1))
            return True
        except Exception as e:
            print(f"BigQuery connection check failed: {e}")
            return False
    
    def insert_rows(self, table_name: str, rows: List[dict]) -> bool:
        """Insert rows into a BigQuery table"""
        if not self.available or not self.client:
            print("BigQuery not available, cannot insert rows")
            return False
            
        table_ref = self.get_table_ref(table_name)
        errors = self.client.insert_rows_json(table_ref, rows)
        
        if errors:
            print(f"Errors inserting rows: {errors}")
            return False
        return True
    
    def query(self, sql: str) -> List[dict]:
        """Execute a SQL query and return results"""
        if not self.available or not self.client:
            print("BigQuery not available, returning empty results")
            return []
            
        query_job = self.client.query(sql)
        results = query_job.result()
        return [dict(row) for row in results]


# Singleton instance
bigquery_client = BigQueryClient()
