import json
from typing import Any, Dict, List, Union
from .operators import ElectrusLogicalOperators
from ...exception.base import ElectrusException
from .result import DatabaseActionResult

class DeleteData:
    @staticmethod
    def delete(collection_path: str, filter_query: Dict[str, Any], multi: bool = False) -> DatabaseActionResult:
        try:
            collection_data = DeleteData._read_collection_data(collection_path)
            deleted_items = [item for item in collection_data if ElectrusLogicalOperators().evaluate(item, filter_query)]

            if not deleted_items:
                return DatabaseActionResult(success=False)

            if not multi:
                deleted_items = deleted_items[:1] 

            updated_collection = [item for item in collection_data if item not in deleted_items]

            DeleteData._write_collection_data(collection_path, updated_collection)
            
            deleted_ids = [item.get('_id') for item in deleted_items]
            deleted_ids = DeleteData._format_deleted_ids(deleted_ids)
            
            return DatabaseActionResult(success=True, deleted_count=len(deleted_items), inserted_ids=deleted_ids)

        except FileNotFoundError:
            raise ElectrusException("Collection file not found.")
        except json.JSONDecodeError:
            raise ElectrusException("Error decoding collection data. Invalid JSON format.")
        except Exception as e:
            raise ElectrusException(f"Error deleting documents: {e}")

    @staticmethod
    def _read_collection_data(collection_path: str) -> List[Dict[str, Any]]:
        try:
            with open(collection_path, 'r') as file:
                return json.loads(file.read())
        except FileNotFoundError:
            raise ElectrusException("Collection file not found.")
        except json.JSONDecodeError:
            raise ElectrusException("Error decoding collection data. Invalid JSON format.")
        except Exception as e:
            raise ElectrusException(f"Error reading collection data: {e}")

    @staticmethod
    def _write_collection_data(collection_path: str, collection_data: List[Dict[str, Any]]) -> None:
        try:
            with open(collection_path, 'w') as file:
                file.write(json.dumps(collection_data, indent=4))
        except FileNotFoundError:
            raise ElectrusException("Collection file not found.")
        except Exception as e:
            raise ElectrusException(f"Error writing collection data: {e}")
        
    @staticmethod
    def _format_deleted_ids(deleted_ids: List[str]) -> Union[str, List[str]]:
        if len(deleted_ids) == 1:
            return deleted_ids[0]
        return deleted_ids
