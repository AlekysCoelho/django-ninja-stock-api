from ninja import NinjaAPI

from app.accounts.api import auth_router

app_name = "ninja_stock"

api = NinjaAPI(version="1.0", urls_namespace="api-1.0", csrf=True)

api.add_router("/auth", auth_router)
