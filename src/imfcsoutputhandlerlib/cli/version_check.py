from importlib.metadata import metadata, version


def main() -> None:
    lib_name = "imfcsoutputhandlerlib"
    print(f"Running {metadata(lib_name)['Name']} v{version(lib_name)}")


if __name__ == "__main__":
    main()
