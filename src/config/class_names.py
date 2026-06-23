"""
IMPORTANTE

El orden de estas clases coincide exactamente con
el orden utilizado durante el entrenamiento del modelo
fruits360_mobilenetv2_finetuned_alternative.h5.

NO modificar el orden.

Dataset de referencia:
Fruit and Vegetable Image Recognition (Kaggle)
"""

EXPECTED_CLASSES = 36

CLASS_NAMES = [
    "apple",
    "banana",
    "beetroot",
    "bell pepper",
    "cabbage",
    "capsicum",
    "carrot",
    "cauliflower",
    "chilli pepper",
    "corn",
    "cucumber",
    "eggplant",
    "garlic",
    "ginger",
    "grapes",
    "jalepeno",
    "kiwi",
    "lemon",
    "lettuce",
    "mango",
    "onion",
    "orange",
    "paprika",
    "pear",
    "peas",
    "pineapple",
    "pomegranate",
    "potato",
    "radish",
    "soy beans",
    "spinach",
    "sweetcorn",
    "sweetpotato",
    "tomato",
    "turnip",
    "watermelon"
]

if len(CLASS_NAMES) != EXPECTED_CLASSES:
    raise ValueError(
        f"CLASS_NAMES debe contener exactamente "
        f"{EXPECTED_CLASSES} clases."
    )