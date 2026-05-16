import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SubjectModel
from ..schemas import SubjectCreate, Subject

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("", response_model=list[Subject])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(SubjectModel).all()

@router.post("", response_model=list[Subject])
def add_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    new_sub = SubjectModel(name=subject.name, totalHours=subject.totalHours)
    db.add(new_sub)
    db.commit()
    return db.query(SubjectModel).all()

@router.post("/skip/{subject_id}", response_model=list[Subject])
def skip_class(subject_id: int, db: Session = Depends(get_db)):
    sub = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    sub.skipped += 1
    sub.last_skipped = int(time.time())
    db.commit()
    return db.query(SubjectModel).all()

@router.post("/undo/{subject_id}", response_model=list[Subject])
def undo_skip(subject_id: int, db: Session = Depends(get_db)):
    sub = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    if sub.skipped > 0:
        sub.skipped -= 1
        sub.last_skipped = None
        db.commit()
    return db.query(SubjectModel).all()

@router.delete("/{subject_id}", response_model=list[Subject])
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    sub = db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
    if sub:
        db.delete(sub)
        db.commit()
    return db.query(SubjectModel).all()
