from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "fruits360_mobilenetv2_finetuned_alternative.h5"
)

SERIAL_PORT = "COM9"
BAUD_RATE = 9600
CAMERA_INDEX = 0