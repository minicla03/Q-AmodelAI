import datetime
from typing import Optional, Dict, List

from bson import ObjectId
from pymongo.errors import PyMongoError
from persistence.IxRepository import IRepos
from persistence.model.Notebook import Notebook


class MongoNotebookRepository(IRepos.INotebookRepository):

    USERS_COLLECTION = "users"
    NOTEBOOKS_COLLECTION = "notebooks"
    CHATS_METADATA_COLLECTION = "chats_metadata"

    def __init__(self, db):
        super().__init__(db)

    def create_notebook(self, notebook: Notebook) -> str:
        try:
            notebook_dict = notebook.to_dict()
            result = self.db[MongoNotebookRepository.NOTEBOOKS_COLLECTION].insert_one(notebook_dict)
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RuntimeError(f"Errore creando notebook: {e}")

    def update_chat_metadata(self, notebook_id: str, chat_id: str, summary: Optional[str] = None,docs: Optional[List[str]] = None) -> None:
        try:
            self.db[MongoNotebookRepository.CHATS_METADATA_COLLECTION].update_one(
                {"notebook_id": ObjectId(notebook_id)},
                {"$set": {
                    "chat_id": chat_id,
                    "last_summary": summary,
                    "updated_at": datetime.datetime.now(),
                    "docs": docs
                }},
                upsert=True
            )
        except PyMongoError as e:
            raise RuntimeError(f"Errore aggiornando metadata del notebook {notebook_id}: {e}")

    def get_notebook_by_id(self, notebook_id: str) -> Optional[Dict]:
        try:
            notebook = self.db[MongoNotebookRepository.NOTEBOOKS_COLLECTION].find_one({"notebook_id": ObjectId(notebook_id)})
            return notebook
        except PyMongoError as e:
            raise RuntimeError(f"Errore recuperando notebook {notebook_id}: {e}")

    def get_notebook_by_user(self, user_id: str) -> List[Dict]:
        try:
            notebooks = list(self.db[MongoNotebookRepository.NOTEBOOKS_COLLECTION].find({"id_user": user_id}))
            return notebooks
        except PyMongoError as e:
            raise RuntimeError(f"Errore recuperando notebook per utente {user_id}: {e}")

    def delete_notebook(self, notebook_id: str) -> bool:
        try:
            result = self.db[MongoNotebookRepository.NOTEBOOKS_COLLECTION].delete_one({"notebook_id": notebook_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Errore cancellando notebook {notebook_id}: {e}")

    def get_list_docs(self, notebook_id: str) -> List[str]:
        try:
            metadata = self.db[self.CHATS_METADATA_COLLECTION].find_one({"notebook_id": ObjectId(notebook_id)})
            if metadata and "docs" in metadata:
                return metadata["docs"]
            return []
        except PyMongoError as e:
            raise RuntimeError(f"Errore recuperando documenti per notebook {notebook_id}: {e}")

    def update_last_summary(self, chat_id: str, summary: str) -> None:
        try:
            self.db[self.CHATS_METADATA_COLLECTION].update_one(
                {"last_chat_id": chat_id},
                {"$set": {"last_summary": summary, "updated_at": datetime.datetime.utcnow()}},
                upsert=True,
            )
        except PyMongoError as e:
            raise RuntimeError(f"Errore aggiornando ultimo sommario per chat {chat_id}: {e}")

    def get_last_summary(self, chat_id: str) -> Optional[str]:
        try:
            metadata = self.db[self.CHATS_METADATA_COLLECTION].find_one({"last_chat_id": chat_id})
            return metadata.get("last_summary") if metadata else None
        except PyMongoError as e:
            raise RuntimeError(f"Errore recuperando ultimo sommario per chat {chat_id}: {e}")

    def delete_last_summary(self, chat_id: str) -> bool:
        try:
            result = self.db[self.CHATS_METADATA_COLLECTION].update_one(
                {"last_chat_id": chat_id},
                {"$unset": {"last_summary": ""}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            raise RuntimeError(f"Errore cancellando ultimo sommario per chat {chat_id}: {e}")


