import os


def init_directories():
    dirs = [
        "src/results",
        "src/prediction_models/lstm/models"
    ]

    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Utworzono katalog: {dir_path}")


if __name__ == "__main__":
    init_directories()