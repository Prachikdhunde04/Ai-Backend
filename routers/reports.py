from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models, schemas
from routers.deps import get_current_active_admin, get_current_user
from typing import List

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/process-status", response_model=List[schemas.ProcessStatusResponse])
def get_all_process_statuses(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # Both active users and admins can view process status (like payment cheques) 
    return db.query(models.ProcessStatus).all()

@router.post("/admin/process-status", response_model=schemas.ProcessStatusResponse)
def create_or_update_process_status(
    status_data: schemas.ProcessStatusBase, 
    db: Session = Depends(get_db), 
    admin: models.User = Depends(get_current_active_admin)
):
    proc = db.query(models.ProcessStatus).filter(models.ProcessStatus.task_name == status_data.task_name).first()
    if proc:
        proc.status = status_data.status
        proc.notes = status_data.notes
    else:
        proc = models.ProcessStatus(**status_data.model_dump())
        db.add(proc)
    db.commit()
    db.refresh(proc)
    return proc

@router.get("/visuals/process-pie-chart")
def get_process_pie_chart_data(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # Aggregates statuses for a pie chart visualization
    results = db.query(
        models.ProcessStatus.status, 
        func.count(models.ProcessStatus.id)
    ).group_by(models.ProcessStatus.status).all()
    
    formatted_data = [{"status": r[0], "count": r[1]} for r in results]
    return formatted_data
