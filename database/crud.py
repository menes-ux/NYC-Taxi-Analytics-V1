# db/crud_base.py
from sqlalchemy.orm import Session

class CRUDBase:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_in: dict):
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: Session, obj_id):
        return db.query(self.model).get(obj_id)

    def update(self, db: Session, obj_id, update_data: dict):
        obj = db.query(self.model).get(obj_id)
        if obj:
            for key, value in update_data.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
        return obj

    def delete(self, db: Session, obj_id):
        obj = db.query(self.model).get(obj_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
