from fastapi import APIRouter
from routes.PostsRoutes import post_create, post_delete, post_edit, post_search

router = APIRouter(prefix="/post")
router.include_router(post_create.router)
router.include_router(post_delete.router)
router.include_router(post_edit.router)
router.include_router(post_search.router)