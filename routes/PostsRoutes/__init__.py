from fastapi import APIRouter

from . import all_offers, get_offer, my_offers, offer_create, offer_edit, offer_delete

router = APIRouter(prefix="/offers")
router.include_router(all_offers.router)
router.include_router(get_offer.router)
router.include_router(my_offers.router)
router.include_router(offer_create.router)
router.include_router(offer_edit.router)
router.include_router(offer_delete.router)