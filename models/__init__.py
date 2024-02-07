"""initializer"""
import json


from models.engine.db_storage import DbStorage

with open ('moves.json', 'w') as f:
    json.dump({}, f)
storage = DbStorage()
storage.reload()