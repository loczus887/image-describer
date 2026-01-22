from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .data.database import get_db, User, BugReport
from .data.admin_repositories import AdminUserRepository, BugReportRepository, MetricRepository
from .auth.jwt_bearer import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# Pydantic models
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    description_count: int
    last_activity: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None

class BugReportResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BugReportUpdateRequest(BaseModel):
    status: str
    priority: Optional[str] = None

@router.get("/metrics")
async def getAdminMetrics(
    hours: int = Query(24, ge=1, le=168),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed system metrics with historical data"""
    from .services.monitoring_service import MonitoringService
    monitoring = MonitoringService(db)
    metric_repo = MetricRepository(db)

    current = monitoring.getDetailedMetrics()
    historical = metric_repo.getHistoricalMetrics(hours)
    aggregated = metric_repo.getAggregatedStats()

    return {
        "current": current,
        "historical": [
            {
                "timestamp": m.timestamp.isoformat(),
                "request_count": m.request_count,
                "error_count": m.error_count,
                "success_rate": m.success_rate,
                "cache_size": m.cache_size,
                "response_time_avg": m.response_time_avg
            } for m in historical
        ],
        "aggregated": aggregated
    }

@router.get("/users", response_model=List[UserResponse])
async def getUsers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users with activity information"""
    user_repo = AdminUserRepository(db)
    users = user_repo.findAll(skip, limit)

    result = []
    for user in users:
        activity = user_repo.getUserActivity(user.id)
        result.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            description_count=activity["description_count"],
            last_activity=activity["last_activity"]
        ))

    return result

@router.put("/users/{user_id}")
async def updateUser(
    user_id: int,
    update_data: UserUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user (block/unblock, change role)"""
    user_repo = AdminUserRepository(db)

    update_dict = update_data.dict(exclude_unset=True)
    user = user_repo.updateUser(user_id, **update_dict)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "user_id": user_id}

@router.delete("/users/{user_id}")
async def deleteUser(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete user and all their data"""
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user_repo = AdminUserRepository(db)
    success = user_repo.deleteUser(user_id)

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"success": True, "message": "User deleted"}

@router.get("/reports", response_model=List[BugReportResponse])
async def getBugReports(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get bug reports with optional status filter"""
    report_repo = BugReportRepository(db)
    reports = report_repo.findAll(status, skip, limit)
    return reports

@router.put("/reports/{report_id}")
async def updateBugReport(
    report_id: int,
    update_data: BugReportUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update bug report status"""
    report_repo = BugReportRepository(db)
    report = report_repo.updateStatus(
        report_id,
        update_data.status,
        update_data.priority
    )

    if not report:
        raise HTTPException(status_code=404, detail="Bug report not found")

    return {"success": True, "report_id": report_id}
