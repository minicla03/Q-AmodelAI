from persistence.IxRepository import IRepos
from rag_logic.memory.ChatManager import logger


class FlashcardManager:
    def __init__(self, repository: IRepos.IFlashcardRepository, notebook_id: str, user_id: str):
        self.repository = repository
        self.notebook_id = notebook_id
        self.user_id = user_id
        self._buffer = []

    def add_to_buffer(self, flashcards: list):
        """Aggiunge nuove flashcard generate al buffer in memoria."""
        self._buffer.extend(flashcards)

    def persist_buffer(self):
        """Salva il contenuto del buffer nel database."""
        if not self._buffer:
            return 0

        count = 0
        try:
            for fc in self._buffer:
                data = fc.to_dict() if hasattr(fc, 'to_dict') else fc
                data['notebook_id'] = self.notebook_id
                data['user_id'] = self.user_id
                self.repository.create_flashcard(data)
                count += 1
            self._buffer.clear()
            return count
        except Exception as e:
            logger.error(f"Errore salvataggio flashcards: {e}")
            return 0

    def get_all(self) -> list:
        """Recupera flashcard da DB e RAM."""
        try:
            db_cards = self.repository.get_flashcard_by_notebook(str(self.notebook_id))
        except Exception:
            db_cards = []

        ram_cards = []
        for idx, fc in enumerate(self._buffer):
            data = fc.to_dict() if hasattr(fc, 'to_dict') else fc.copy()
            data['_id'] = f"ram_{idx}"
            data['is_unsaved'] = True
            ram_cards.append(data)

        return db_cards + ram_cards

    def delete(self, card_id: str) -> bool:
        """Elimina da RAM o DB in base all'ID."""
        if card_id.startswith("ram_"):
            try:
                idx = int(card_id.split("_")[1])
                if 0 <= idx < len(self._buffer):
                    self._buffer.pop(idx)
                    return True
            except (ValueError, IndexError):
                return False
            return False

        return self.repository.delete_flashcard(card_id)