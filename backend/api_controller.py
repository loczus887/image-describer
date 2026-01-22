from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from .data.database import get_db, init_db, User
from .auth.jwt_bearer import get_current_user
from .models.auth_models import UserRegister, UserLogin, Token, UserResponse
from .data.admin_repositories import BugReportRepository

load_dotenv()
# Lazy import all services to avoid loading heavy dependencies at startup
# from .services.description_service import DescriptionService
# from .services.monitoring_service import MonitoringService
# from .services.validation_service import ValidationService

app = FastAPI(title="Image Describer API")

# CORS middleware - DISABLED TEMPORARILY (causes issues with Python 3.14)
# Will add CORS headers manually in endpoints if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# CORS headers - add manually in each endpoint if needed
# Temporarily disabled middleware to avoid blocking issues

# Services - lazy initialization
monitoring_service = None
validation_service = None

def get_monitoring_service():
    global monitoring_service
    if monitoring_service is None:
        from .services.monitoring_service import MonitoringService
        monitoring_service = MonitoringService()
    return monitoring_service

def get_validation_service():
    global validation_service
    if validation_service is None:
        from .services.validation_service import ValidationService
        validation_service = ValidationService()
    return validation_service

# Database initialization flag
_db_initialized = False

def ensure_db_initialized():
    """Initialize database on first request if not already done"""
    global _db_initialized
    if not _db_initialized:
        try:
            print("[DB] Initializing database on first request...")
            init_db()
            _db_initialized = True
            print("[DB] Database initialized")
        except Exception as e:
            print(f"[DB] Error initializing database: {e}")
            import traceback
            traceback.print_exc()

class DescriptionResponse(BaseModel):
    success: bool
    description: Optional[str] = None
    error: Optional[str] = None

class HistoryItem(BaseModel):
    id: int
    image_hash: str
    description: str
    created_at: str

    class Config:
        from_attributes = True

class MetricsResponse(BaseModel):
    uptime_seconds: float
    request_count: int
    error_count: int
    success_rate: float

@app.post("/describe", response_model=DescriptionResponse)
async def handleDescribeRequest(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle image description request"""
    ensure_db_initialized()
    get_monitoring_service().incrementRequestCount()

    try:
        print(f"[API] Received request from user {current_user.id} for file: {file.filename}, content_type: {file.content_type}")

        # Read file data
        file_data = await file.read()
        print(f"[API] Read {len(file_data)} bytes from file")

        # Validate file
        valid, error = get_validation_service().validateImageFile(
            len(file_data),
            file.content_type or ""
        )
        if not valid:
            print(f"[API] Validation failed: {error}")
            get_monitoring_service().incrementErrorCount()
            raise HTTPException(status_code=400, detail=error)

        # Process image
        print("[API] Creating DescriptionService...")
        from .services.description_service import DescriptionService
        description_service = DescriptionService(db)
        print("[API] Processing image...")
        success, description, error_msg = description_service.processImage(file_data, user_id=current_user.id)
        
        if not success:
            print(f"[API] Processing failed: {error_msg}")
            get_monitoring_service().incrementErrorCount()
            raise HTTPException(status_code=500, detail=error_msg or "Failed to process image")
        
        print(f"[API] Success! Description: {description[:50]}...")
        return DescriptionResponse(
            success=True,
            description=description,
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[API] Unexpected error: {str(e)}")
        print(f"[API] Traceback: {error_trace}")
        monitoring_service.incrementErrorCount()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history")
async def getHistory(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get description history"""
    ensure_db_initialized()
    from .services.description_service import DescriptionService
    description_service = DescriptionService(db)
    history = description_service.getHistory(user_id=current_user.id, limit=limit)

    return [
        HistoryItem(
            id=item.id,
            image_hash=item.image_hash,
            description=item.description,
            created_at=item.created_at.isoformat()
        )
        for item in history
    ]

@app.delete("/history")
async def clearHistory(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all description history for current user"""
    ensure_db_initialized()
    from .data.database import Description

    try:
        deleted_count = db.query(Description).filter(
            Description.user_id == current_user.id
        ).delete()
        db.commit()

        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} history items"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

@app.get("/metrics", response_model=MetricsResponse)
async def getMetrics():
    """Get monitoring metrics"""
    metrics = get_monitoring_service().getMetrics()
    return MetricsResponse(**metrics)

@app.get("/health")
async def healthCheck():
    """Health check endpoint - simple, no database"""
    # Don't initialize DB on health check - it might block
    return {"status": "healthy", "message": "Backend is running"}

@app.get("/model-status")
async def modelStatus():
    """Check if AI model is loaded"""
    try:
        from .services.ai_model_integration import AIModelIntegration
        model = AIModelIntegration()
        return {
            "loaded": model.isModelLoaded(),
            "model_name": model.model_name
        }
    except Exception as e:
        return {
            "loaded": False,
            "error": str(e)
        }

# Authentication Endpoints

@app.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    ensure_db_initialized()

    from .services.auth_service import AuthService
    auth_service = AuthService(db)

    success, user, error = auth_service.register_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    if not success:
        raise HTTPException(status_code=400, detail=error)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        created_at=user.created_at.isoformat()
    )

@app.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and receive JWT token"""
    ensure_db_initialized()

    from .services.auth_service import AuthService
    auth_service = AuthService(db)

    user = auth_service.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    return Token(access_token=access_token, token_type="bearer")

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at.isoformat()
    )

@app.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (token invalidation handled client-side)"""
    return {"message": "Successfully logged out"}

# Bug Report Endpoint

class BugReportRequest(BaseModel):
    title: str
    description: str

@app.post("/report-bug")
async def submitBugReport(
    report: BugReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a bug report"""
    ensure_db_initialized()
    report_repo = BugReportRepository(db)

    bug_report = report_repo.create(
        user_id=current_user.id,
        title=report.title,
        description=report.description
    )

    return {"success": True, "report_id": bug_report.id}

# Include admin router
from .admin_controller import router as admin_router
app.include_router(admin_router)

