"""
Service Contract logic (Phase C).
"""
from typing import Any, List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service_contract import ServiceContract
from app.services import audit_service


def list_contracts_for_asset(db: Session, asset_id: int) -> List[ServiceContract]:
    return list(db.scalars(
        select(ServiceContract)
        .where(ServiceContract.asset_id == asset_id)
        .order_by(ServiceContract.end_date.desc())
    ))


def create_contract(
    db: Session, asset_id: int, data: dict[str, Any], actor_user_id: int
) -> ServiceContract:
    contract = ServiceContract(asset_id=asset_id, **data)
    db.add(contract)
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="SERVICE_CONTRACT_CREATED",
        entity_type="ServiceContract",
        entity_id=contract.id,
        new_value={"asset_id": asset_id, "vendor_id": data.get("vendor_id"), "contract_number": data.get("contract_number")},
    )
    return contract


def update_contract(
    db: Session, contract: ServiceContract, data: dict[str, Any], actor_user_id: int
) -> ServiceContract:
    old_value = {k: getattr(contract, k) for k in data.keys()}
    for key, value in data.items():
        setattr(contract, key, value)
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="SERVICE_CONTRACT_UPDATED",
        entity_type="ServiceContract",
        entity_id=contract.id,
        old_value={k: str(v) for k, v in old_value.items()},
        new_value={k: str(v) for k, v in data.items()},
    )
    return contract
