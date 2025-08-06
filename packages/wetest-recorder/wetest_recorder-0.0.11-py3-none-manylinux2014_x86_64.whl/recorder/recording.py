import os
import time
import platform
import subprocess
import sys
import threading
from typing import Tuple, List, Optional, IO

from recorder._exceptions import InstanceError


class Recorder:

    def __init__(
        self,
        udid: str,
        device_type: str = "iOS",
        duration: int = 5,
        output: str = "output.mp4",
        launch: bool = True,
        audio: bool = True,
        bitrate: int = 6000000,
        fix_pts: bool = True,
        fps: int = 25,
        height: int = 1024,
        ios_video_port: int = 21344,
        socket_name: str = "sa3-scrcpy",
        ver: bool = False,
        debug: bool = False,
        re_encode: bool = True,
    ) -> None:
        """
        Initialize recorder.

        Args:
            udid (str): device udid for iOS or serial number for Android.
            device_type (str): iOS or Android.
            duration (int): duration in second.
            output (str): out file path.
            launch (bool): launch scrcpy on device.
            audio (bool): record video with audio.
            bitrate (int): bitrate.
            fix_pts (bool): fix device pts.
            fps (int): frame per second.
            height (int): height of video.
            ios_video_port (int): ios video port, scrcpy is 21344, replaykit is 21345.
            socket_name (str): Android unix-domain-socket name.
            ver (bool): version of recorder.
            debug (bool): dump raw data to file.
            re_encode (bool): re-encode video and audio.

        Returns:
            None.
        """
        system_type = platform.system().lower()
        base_path = os.path.join(os.path.dirname(__file__), "bin")
        if system_type == "windows":
            base_path = os.path.join(base_path, "win")
            recorder_path = os.path.join(base_path, "recorder.exe")
        elif system_type == "linux":
            arch = arch = platform.machine().lower()
            base_path = os.path.join(base_path, "linux", arch)
            recorder_path = os.path.join(base_path, "recorder")
        elif system_type == "darwin":
            base_path = os.path.join(base_path, "macosx")
            recorder_path = os.path.join(base_path, "recorder")
        else:
            raise Exception(f"Unsupported platform: {system_type}")
        self.command: List[str] = [
            recorder_path,
            "-workDir",
            base_path,
        ]
        self.recorder_command = self.command.copy()
        if launch:
            self.recorder_command.append("-launch")

        if audio:
            self.recorder_command.append("-a")

        command = [
            "-u",
            udid,
            "-t",
            device_type,
            "-d",
            str(duration),
            "-o",
            output,
            "-bitrate",
            str(bitrate),
            "-fps",
            str(fps),
            "-height",
            str(height),
            "-ios_video_port",
            str(ios_video_port),
            "-socket_name",
            socket_name,
            f"-fix_pts={fix_pts}",
            f"-re_encode={re_encode}",
        ]
        self.recorder_command.extend(command)
        if ver:
            self.recorder_command.append("-v")
        if debug:
            self.recorder_command.append("-debug")

        self.process: Optional[subprocess.Popen] = None
        self.stdout_thread: threading.Thread = None
        self.stderr_thread: threading.Thread = None
        self.stdout: List[str] = []
        self.stderr: List[str] = []

        self.started: bool = False
        self.stopped: bool = False

        self.output_file = output
        # output in terminal(True) or not
        self.debug: bool = debug

    def __enter__(self) -> None:
        """
        Context management for “with” statement
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Context management for “with” statement
        """
        self.stop()

    def start(self) -> None:
        """
        Start recorder.

        Args:
            None.

        Returns:
            None.
        """
        if self.stopped:
            raise InstanceError("This instance has been stopped and can't be restarted. Please create a new instance.")
        if self.started:
            # print("This instance has been started.")
            return
        self.started = True

        if not self.debug:
            self.process = subprocess.Popen(
                self.recorder_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        else:
            self.process = subprocess.Popen(
                self.recorder_command,
                text=True,
            )

        self.stdout_thread = threading.Thread(target=self._get_buf, args=(self.process.stdout, self.stdout))
        self.stderr_thread = threading.Thread(target=self._get_buf, args=(self.process.stderr, self.stderr))
        self.stdout_thread.start()
        self.stderr_thread.start()

        while self.is_alive() and not os.path.exists(f"{self.output_file}.tmp"):
            time.sleep(0.1)

    def _get_buf(self, pipe: Optional[IO[str]], output: List[str]) -> None:
        """
        Read stdout and stderr from PIPE to avoid to Popen.wait->deadlock/ Popen.communicate->lag.

        Args:
            pipe (Optional[IO[str]]): stdout or stderr pipe.
            output (List[str]): output string.

        Returns:
            None.
        """
        while True:
            line = pipe.readline()
            if line:
                output.append(line)
            else:
                break

    def wait(self) -> None:
        """
        Wait until the thread terminates.

        Args:
            None.

        Returns:
            None.
        """
        # 对于录制完上传的场景，阻塞执行 不要轮询
        if not self.started:
            raise InstanceError("Cannot wait instance before it is started.")

        self.process.wait()

    def _terminate(self, timeout: float = 5) -> None:
        """
        Terminate subprocess, do not invoke it directly.

        Args:
            timeout (float): timeout in second.

        Returns:
            None.
        """
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()

    def is_alive(self) -> bool:
        """
        Check if the recorder is alive.

        Args:
            None.

        Returns:
            bool: recorder's status.
        """
        if not self.process or self.process.poll() is not None:
            return False
        return True

    def stop(self) -> None:
        """
        Interrupt recorder by sending signal terminate, and save record file.

        Args:
            None.

        Returns:
            None.
        """

        if not self.started:
            raise InstanceError("Cannot stop instance before it is started.")
        if self.stopped:
            print("This instance has been stopped.")
            return

        if self.is_alive():
            self.process.terminate()
            # self.process.send_signal(signal.SIGTERM)
        self.stopped = True

    def get_output(self) -> Tuple[str, str]:
        """
        Get recorder's stdout and stderr.

        Args:
            None.

        Returns:
            Tuple[str, str]: recorder's stdout and stderr.
        """
        self.stdout_thread.join()
        self.stderr_thread.join()
        return "".join(self.stdout), "".join(self.stderr)

    @classmethod
    def _cmdline(cls) -> None:
        """
        Screen recording by cmd.

        Args:
            None.

        Returns:
            None.
        """
        recorder = cls(None)
        recorder_command = recorder.command.copy()
        recorder_command.extend(sys.argv[1:])
        subprocess.run(recorder_command)
