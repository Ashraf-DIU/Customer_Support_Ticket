from fastapi import APIRouter

from ..schemas import PredictIn, PredictionOut
from ..services.prediction import predictor

router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=PredictionOut)
def predict(body: PredictIn):
    return predictor.predict(body.subject, body.message)


@router.get("/model-info")
def model_info():
    return {"ready": predictor.ready, "version": predictor.version, "metrics": predictor.metrics}
