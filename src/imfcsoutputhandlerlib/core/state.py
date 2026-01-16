from .all_image import AllImage


def get_total_processed_files(list_all_image: AllImage) -> int:
    """Return total processed files"""

    total_processed_files = 0
    for i in range(len(list_all_image)):
        total_processed_files += int(
            list_all_image.get_image_info_from_list(i).is_ready()
        )

    return total_processed_files


def get_load_raw_progress_default_value(list_all_image: AllImage) -> int:
    """Return precentage of loaded files"""

    total_available_files = len(list_all_image)

    total_processed_files = 0
    for i in range(total_available_files):
        total_processed_files += int(
            list_all_image.get_image_info_from_list(i).is_ready()
        )

    return int((total_processed_files) / total_available_files * 100)
