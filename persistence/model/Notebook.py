import datetime

class Notebook:

    def __init__(self, id_user, notebook_name):
        self.id_notebook = None
        self.id_user = id_user
        self.chat_id = None
        self.notebook_name = notebook_name
        self.documents= []
        self.created_at = datetime.datetime.now()

    def to_dict(self):
        return {
            'id_notebook': self.id_notebook,
            'id_user': self.id_user,
            'notebook_name': self.notebook_name,
            'created_at': self.created_at,
            'documents': self.documents
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Notebook":
        notebook = cls(
            id_user=data["id_user"],
            notebook_name=data["notebook_name"]
        )
        notebook.id_notebook = data.get("id_notebook") or str(data.get("_id"))
        notebook.documents = data.get("documents", [])
        notebook.created_at = data.get("created_at", datetime.datetime.now())
        return notebook


