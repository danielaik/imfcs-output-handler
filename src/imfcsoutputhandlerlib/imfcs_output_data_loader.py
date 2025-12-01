import concurrent.futures
import os
import threading
import time

import ipywidgets as widgets
import pandas as pd

from .all_image import AllImage
from .image_info import ImageInfo


class OutputDataLoaderSingleThread:

    list_all_image_object: AllImage
    total_iterations: int  # number of .xlxs files to be loaded
    current_progress: int = 0  # keep track of sucessfully loaded files

    # Control flag for stopping the loop
    stop_flag = threading.Event()
    thread: threading.Thread

    # ipywidget
    progress: widgets.IntProgress
    progress_label: widgets.Label
    output: widgets.Output

    input_folder: str

    # ANSI escape codes for colors

    GREEN = "\033[32m"
    RESET = "\033[0m"  # Reset to default color

    def __init__(
        self,
        list_all_image_object: AllImage,
        progress: widgets.IntProgress,
        progress_label: widgets.Label,
        output: widgets.Output,
        input_folder: str,
    ):
        self.list_all_image_object = list_all_image_object
        self.total_iterations = len(self.list_all_image_object)
        self.progress = progress
        self.progress_label = progress_label
        self.output = output
        self.thread = None
        self.input_folder = input_folder

    def _log(self, msg: str):
        # works well from threads
        self.output.append_stdout(msg + "\n")

    def long_process(self):
        """
        A long-running process that loops and updates the progress bar.
        """

        self._log(f"{self.GREEN}Loading dataset...{self.RESET}")

        self.stop_flag.clear()  # Reset stop flag

        start_time = time.time()  # Start timer

        while (
            self.current_progress < self.total_iterations
            and not self.stop_flag.is_set()
        ):

            # Calculate percentage of completion
            percentage = int((self.current_progress + 1) / self.total_iterations * 100)

            # work start
            time.sleep(0.1)

            im_info = self.list_all_image_object.get_image_info_from_list(
                index=self.current_progress
            )

            im_info.read_excel_df_and_avr_int(input_folder=self.input_folder)

            # work end

            self.current_progress += 1  # Increment progress
            self.progress.value = percentage
            self.progress_label.value = f"{percentage}%"

            self._log(
                f"{self.GREEN}Processed step {self.current_progress} / {self.total_iterations}{self.RESET}"
            )

        if self.stop_flag.is_set():
            print(f"{self.GREEN}Process stopped.{self.RESET}")
        elif self.current_progress >= self.total_iterations:
            end_time = time.time()  # End timer
            elapsed_time = end_time - start_time
            print(
                f"{self.GREEN}Process completed in {elapsed_time:.2f} seconds.{self.RESET}"
            )

    def start_process(self):
        """
        Start the long process in a separate thread.
        """
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.long_process)
            self.thread.start()

    def on_start_clicked(self, b):
        """
        Start button callback.
        If progress has reached 100% or Stop has been pressed, restart progress.
        """

        if self.current_progress >= self.total_iterations:  # If completed
            self.output.clear_output()
            self._log("completed previously")
            return

        if self.stop_flag.is_set() and self.current_progress > 0:  # If stopped
            self.output.clear_output()
            self._logprint("stopped previously")
            threading.Thread(target=self.long_process).start()
            return

        if not self.stop_flag.is_set():  # Avoid starting multiple threads
            self.output.clear_output()
            self._log("start")
            self.start_process()
            return

    def on_stop_clicked(self, b):
        """
        Stop button callback.
        """
        self.stop_flag.set()  # Signal the process to stop
        with self.output:
            self.output.clear_output()
            print("Stopping process...")


class OutputDataLoaderMultiThread:

    list_all_image_object: AllImage
    total_iterations: int  # number of .xlxs files to be loaded

    # Control flag for stopping the loop
    stop_flag = threading.Event()
    thread: threading.Thread

    # ipywidget
    progress: widgets.IntProgress
    progress_label: widgets.Label
    output: widgets.Output

    input_folder: str

    GREEN = "\033[32m"
    RESET = "\033[0m"  # Reset to default color

    def __init__(
        self,
        list_all_image_object: AllImage,
        progress: widgets.IntProgress,
        progress_label: widgets.Label,
        output: widgets.Output,
        input_folder: str,
    ):
        self.list_all_image_object = list_all_image_object
        # num_entries = 1000
        # my_dict = {f"key_{i}": [f"value_{i}"] for i in range(num_entries)}
        # self.list_all_image_object = AllImage(experiment_name="exp1", group_files=my_dict)
        self.total_iterations = len(self.list_all_image_object)

        self.progress = progress
        self.progress_label = progress_label
        self.output = output
        self.input_folder = input_folder
        self.progress_checklist = [False for _ in range(self.total_iterations)]
        self.thread = None
        self.stop_flag = threading.Event()  # Use threading.Event for stop_flag
        self.stop_flag.clear()

    def process_data(self, im_info: ImageInfo):
        # time.sleep(0.1)
        im_info.read_excel_df_and_avr_int(input_folder=self.input_folder)

        return im_info

    def long_process(self):
        """
        Run the long process in a thread, respecting the stop_flag.
        """
        print(f"{self.GREEN}Loading dataset...{self.RESET}")
        self.stop_flag.clear()  # Reset the stop flag

        start_time = time.time()  # Start timer

        # with self.output:
        # consider ProcessPoolExecutor() for CPU heavy performance instead of ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.process_data, image): image
                for image, include in zip(
                    self.list_all_image_object.get_list_of_image(),
                    self.progress_checklist,
                )
                if not include
            }

            for future in concurrent.futures.as_completed(futures):

                if self.stop_flag.is_set():
                    print(f"{self.GREEN}Process stopped.{self.RESET}")
                    break

                result = future.result()

                # get the index of image to be processed with respect to list_image
                assert isinstance(
                    result, type(self.list_all_image_object.get_list_of_image()[0])
                ), "different type error RawDataLoaderMultiThread class"
                index = self.list_all_image_object.get_list_of_image().index(result)
                self.progress_checklist[index] = True

                # Update progress bar
                percentage = int(
                    sum(self.progress_checklist) / self.total_iterations * 100
                )
                self.progress.value = percentage
                self.progress_label.value = f"{percentage}%"
                print(
                    f"{self.GREEN}Processed step {sum(self.progress_checklist)} / {self.total_iterations}{self.RESET}: {result.key}"
                )

        if not self.stop_flag.is_set():
            end_time = time.time()  # End timer
            elapsed_time = end_time - start_time
            print(
                f"{self.GREEN}Process completed in {elapsed_time:.2f} seconds.{self.RESET}"
            )

    def start_process(self):
        """
        Start the long process in a separate thread.
        """
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.long_process)
            self.thread.start()

    def on_start_clicked(self, b):
        """
        Start button callback.
        """

        if sum(self.progress_checklist) >= self.total_iterations:  # If completed
            # print("completed previously")
            return

        if self.stop_flag.is_set() and sum(self.progress_checklist) > 0:  # If stopped
            # print("stopped previously")
            threading.Thread(target=self.long_process).start()
            return

        if not self.stop_flag.is_set():  # Avoid starting multiple threads
            # print("start")
            self.start_process()
            return

    def on_stop_clicked(self, b):
        """
        Stop button callback.
        """

        self.stop_flag.set()  # Signal the process to stop

        with self.output:
            print("Stopping process...")
