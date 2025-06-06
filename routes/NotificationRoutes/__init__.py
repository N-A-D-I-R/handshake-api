from fastapi import APIRouter
from ..NotificationRoutes import get_notifications, mark_ad_read, delete_notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])
router.include_router(get_notifications.router)
router.include_router(mark_ad_read.router)
router.include_router(delete_notification.router)