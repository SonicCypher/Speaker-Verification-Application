import joblib
import logging
import numpy as np
import torch
import json
from ASV_System.verification import register_user, run_verification_from_db
from CM_System.spoofing_score import evaluate_utterance
import importlib.resources

MODEL_CM_PATH = importlib.resources.files("Weights").joinpath("AASIST.pth")
MODEL_FUSION_PATH = importlib.resources.files("Weights").joinpath("fusion_model.pkl")
MODEL_FUSION_SCALER_PATH = importlib.resources.files("Weights").joinpath("scaler.pkl" )

def load_fusion_model_and_scaler(model_path="fusion_model.pkl", scaler_path="scaler.pkl"):
    logging.info(f"Loading model from {model_path} and scaler from {scaler_path}")
    fusion_model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return fusion_model, scaler

def predict_verification(username, test_file, device="cpu", threshold=0.1994701042959457):
    asv_score = run_verification_from_db(username, test_file)
    print(f"[ASV Score] {asv_score:.4f}")

    cm_score = evaluate_utterance(MODEL_CM_PATH, test_file, device)
    print(f"[CM Score] {cm_score:.4f}")

    fusion_model, scaler = load_fusion_model_and_scaler(MODEL_FUSION_PATH, MODEL_FUSION_SCALER_PATH)
    X = np.array([[asv_score, cm_score]])
    X_scaled = scaler.transform(X)
    print(f"Scaled features: {X_scaled}")
    prob = fusion_model.predict_proba(X_scaled)[:, 1][0]  # Probability of 'target'
    print(f"[Fusion Probability] {prob:}")
    verified = prob >= threshold
    # Print verification result with score
    print(f"[Fusion Score] {prob:.4f} - {'✅ Verified (same speaker)' if verified else '❌ Not Verified (different speaker)'}")
    return verified, prob