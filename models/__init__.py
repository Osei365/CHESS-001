"""initializer"""


from models.engine.db_storage import DbStorage

storage = DbStorage()
storage.reload()