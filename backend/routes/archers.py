from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select

from ..api_models import ArcherInput, PaginatedArcher, ArcherSearchInput
from ..models.models import Archer
from ..utils.sqlite import get_session

router = APIRouter()


@router.get("/archers/paginated", response_model=PaginatedArcher)
def get_archers_paginated(
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    offset = (page - 1) * limit

    total_stmt = select(func.count()).select_from(Archer)
    total = session.exec(total_stmt).one()

    archers_stmt = select(Archer).offset(offset).limit(limit).order_by(Archer.id.asc())
    archers = session.exec(archers_stmt).all()

    total_pages = (total + limit - 1) // limit

    return PaginatedArcher(
        count=len(archers),
        total=total,
        page=page,
        total_pages=total_pages,
        limit=limit,
        data=archers,
    )


@router.get("/archers", response_model=list[Archer])
def get_archers(session: Session = Depends(get_session)):
    archers = session.exec(select(Archer)).all()
    return archers


@router.post("/archers", response_model=Archer)
def post_archer(data: ArcherInput, session: Session = Depends(get_session)):
    archer = Archer(name=data.name, position=data.position)
    session.add(archer)
    session.commit()
    session.refresh(archer)
    return archer


@router.delete("/archers/{archer_id}")
def delete_archer(archer_id: int, session: Session = Depends(get_session)):
    archer = session.get(Archer, archer_id)
    if not archer:
        raise HTTPException(status_code=404, detail="Archer not found")

    session.delete(archer)
    session.commit()
    return {"message": "Archer deleted"}
