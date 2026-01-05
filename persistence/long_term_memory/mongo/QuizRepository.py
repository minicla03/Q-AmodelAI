import logging
from typing import Optional, Dict, List, Union, Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from persistence.IxRepository.IRepos import IQuizRepository

logger = logging.getLogger(__name__)


class MongoQuizRepository(IQuizRepository):
    COLLECTION_NAME = "quizzes"

    def __init__(self, db):
        super().__init__(db)
        self.collection = self.db[self.COLLECTION_NAME]

    def create_quiz(self, quiz: Any) -> str:
        try:
            if hasattr(quiz, "to_dict"):
                data = quiz.to_dict()
            elif isinstance(quiz, dict):
                data = quiz
            else:
                raise ValueError("Il dato passato non è né un oggetto Quiz né un dizionario valido.")

            if "notebook_id" in data and isinstance(data["notebook_id"], str):
                try:
                    data["notebook_id"] = ObjectId(data["notebook_id"])
                except InvalidId:
                    logger.warning(f"Notebook ID non valido ricevuto durante la creazione quiz: {data['notebook_id']}")

            if "_id" in data and not data["_id"]:
                del data["_id"]

            result = self.collection.insert_one(data)
            new_id = str(result.inserted_id)

            logger.info(f"Quiz creato con successo. ID: {new_id}")
            return new_id

        except PyMongoError as e:
            logger.error(f"Errore DB durante creazione quiz: {e}")
            raise RuntimeError(f"Impossibile salvare il quiz: {e}")

    def delete_quiz(self, quiz_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(quiz_id)})

            if result.deleted_count > 0:
                logger.info(f"Quiz {quiz_id} eliminato.")
                return True
            else:
                logger.warning(f"Nessun quiz trovato con ID {quiz_id} da eliminare.")
                return False

        except InvalidId:
            logger.error(f"ID Quiz non valido per eliminazione: {quiz_id}")
            return False
        except PyMongoError as e:
            logger.error(f"Errore DB eliminando quiz {quiz_id}: {e}")
            return False

    def get_quiz_by_user(self, user_id: str) -> List[Dict]:
        try:
            cursor = self.collection.find({"user_id": user_id})

            quizzes = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                if "notebook_id" in doc:
                    doc["notebook_id"] = str(doc["notebook_id"])
                quizzes.append(doc)

            return quizzes

        except PyMongoError as e:
            logger.error(f"Errore recupero quiz per user {user_id}: {e}")
            return []

    def get_quiz_by_notebook(self, notebook_id: str) -> List[Dict]:
        try:
            query = {"notebook_id": ObjectId(notebook_id)}
            cursor = self.collection.find(query)

            quizzes = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["notebook_id"] = str(doc["notebook_id"])
                quizzes.append(doc)

            return quizzes

        except InvalidId:
            logger.error(f"Notebook ID non valido per ricerca quiz: {notebook_id}")
            return []
        except PyMongoError as e:
            logger.error(f"Errore recupero quiz per notebook {notebook_id}: {e}")
            return []