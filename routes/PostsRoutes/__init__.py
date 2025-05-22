from fastapi import APIRouter

from . import all_offers, my_offers, offer_create, offer_delete, offer_edit, get_offer

router = APIRouter(prefix="/offers")
router.include_router(all_offers.router)
router.include_router(my_offers.router)
router.include_router(offer_create.router)
router.include_router(offer_delete.router)
router.include_router(offer_edit.router)
router.include_router(get_offer.router)