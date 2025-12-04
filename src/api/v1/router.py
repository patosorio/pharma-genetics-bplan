from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.db import get_db
from src.services.google_sheets import sync_data
from src.core.shared.exceptions import InternalServerError

router = APIRouter(prefix='/api', tags=['sync'])

@router.post('/sync')
async def trigger_sync(db: Session = Depends(get_db)):
    try:
        result = sync_data(db)
        return result
    except Exception as e:
        raise InternalServerError(detail=str(e))