from fastapi import FastAPI

from mercedes.api.endpoints.urls import router
from mercedes.utils.conf import settings

app = FastAPI(title=settings.APP)
app.include_router(router)
