import notiondbrs
from typing import List, Tuple, Dict

class NotionClient:
    
    def __init__(self, token: str):
        """
        initialize the notion client
        """
        
        self.client = notiondbrs.NotionClient(token)
    
    def get_all_databases(self) -> List[Tuple[str, str]]:
        """
        get all databases accessible by the given token
        """
        return self.client.get_all_databases()
    
    def get_data_from_database(self, db_id: str) -> List[dict]:
        """
        get data from a specific database
        """
        return self.client.get_data(db_id)
    
    def merge_data(self, data: Dict[str, List[str]], db_id: str) -> None:
        """
        merge data into the database
        """
        self.client.merge_data(data, db_id)
    
    def insert_data(self, data: Dict[str, List[str]], db_id: str, new_db:bool = False) -> None:
        self.client.insert_data(data, db_id, new_db)