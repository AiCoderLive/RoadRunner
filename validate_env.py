def validate_environment():
    """Validate that all required packages are installed correctly."""
    import sys

    packages = [
        "tensorflow",
        "numpy",
        "scipy",
        # Add other critical packages here
    ]

    failed = []
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package} successfully imported")
        except ImportError:
            failed.append(package)
            print(f"✗ {package} import failed")

    if failed:
        print(f"\nEnvironment validation failed for: {', '.join(failed)}")
        return False
    else:
        print("\nEnvironment validation successful!")
        return True


if __name__ == "__main__":
    validate_environment()