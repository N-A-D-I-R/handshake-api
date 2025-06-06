from fastapi import APIRouter

from . import all_pending_offers, get_pending_offer, approve_post, reject_post
from . import all_profile_edit_requests, get_profile_edit_request, approve_profile_edit_request, reject_profile_edit_request

router = APIRouter(prefix="/moderation", tags=["Moderation"])

router.include_router(all_pending_offers.router)
router.include_router(get_pending_offer.router)
router.include_router(approve_post.router)
router.include_router(reject_post.router)

router.include_router(all_profile_edit_requests.router)
router.include_router(get_profile_edit_request.router)
router.include_router(approve_profile_edit_request.router)
router.include_router(reject_profile_edit_request.router)