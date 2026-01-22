from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from .database import User, BugReport, Metric, Description

class AdminUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def findAll(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def getUserCount(self) -> int:
        """Get total user count"""
        return self.db.query(User).count()

    def updateUser(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields (role, is_active, etc.)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def deleteUser(self, user_id: int) -> bool:
        """Delete a user and their data"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Delete related data
            self.db.query(Description).filter(Description.user_id == user_id).delete()
            self.db.query(BugReport).filter(BugReport.user_id == user_id).delete()
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def getUserActivity(self, user_id: int) -> Dict:
        """Get user activity statistics"""
        desc_count = self.db.query(Description).filter(Description.user_id == user_id).count()
        last_activity = self.db.query(Description).filter(
            Description.user_id == user_id
        ).order_by(desc(Description.created_at)).first()

        return {
            "description_count": desc_count,
            "last_activity": last_activity.created_at if last_activity else None
        }

class BugReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: str, description: str) -> BugReport:
        """Create a new bug report"""
        report = BugReport(user_id=user_id, title=title, description=description)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def findAll(self, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[BugReport]:
        """Get bug reports with optional status filter"""
        query = self.db.query(BugReport)
        if status:
            query = query.filter(BugReport.status == status)
        return query.order_by(desc(BugReport.created_at)).offset(skip).limit(limit).all()

    def updateStatus(self, report_id: int, status: str, priority: Optional[str] = None) -> Optional[BugReport]:
        """Update report status and optionally priority"""
        report = self.db.query(BugReport).filter(BugReport.id == report_id).first()
        if report:
            report.status = status
            if priority:
                report.priority = priority
            report.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(report)
        return report

class MetricRepository:
    def __init__(self, db: Session):
        self.db = db

    def getHistoricalMetrics(self, hours: int = 24) -> List[Metric]:
        """Get metrics from the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(Metric).filter(
            Metric.timestamp >= cutoff
        ).order_by(Metric.timestamp).all()

    def getAggregatedStats(self) -> Dict:
        """Get aggregated statistics"""
        total_requests = self.db.query(func.sum(Metric.request_count)).scalar() or 0
        total_errors = self.db.query(func.sum(Metric.error_count)).scalar() or 0
        avg_response_time = self.db.query(func.avg(Metric.response_time_avg)).scalar() or 0

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "avg_response_time": avg_response_time,
            "overall_success_rate": (total_requests - total_errors) / max(total_requests, 1)
        }
