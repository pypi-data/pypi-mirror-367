
import os
import platform

import signal
import subprocess

import threading
import time
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

import qrcode
from flet.utils import (

    get_local_ip,

    open_in_browser,

)

from watchdog.events import FileSystemEventHandler



def patch_flet_cli():
    try:
        import sys
        from flet_cli.commands import run as run_module

        class Handler(FileSystemEventHandler):
            def __init__(
                    self,
                    args,
                    watch_directory,
                    script_path,
                    port,
                    host,
                    page_name,
                    uds_path,
                    web,
                    ios,
                    android,
                    hidden,
                    assets_dir,
                    ignore_dirs,
                    flet_app_data_dir,
                    flet_app_temp_dir,
            ) -> None:
                super().__init__()
                self.args = args
                self.watch_directory = watch_directory
                self.script_path = script_path
                self.port = port
                self.host = host
                self.page_name = page_name
                self.uds_path = uds_path
                self.web = web
                self.ios = ios
                self.android = android
                self.hidden = hidden
                self.assets_dir = assets_dir
                self.ignore_dirs = ignore_dirs
                self.last_time = time.time()
                self.is_running = False
                self.fvp = None
                self.pid_file = None
                self.page_url_prefix = f"PAGE_URL_{time.time()}"
                self.page_url = None
                self.flet_app_data_dir = flet_app_data_dir
                self.flet_app_temp_dir = flet_app_temp_dir
                self.terminate = threading.Event()
                self.start_process()

            def start_process(self):
                p_env = {**os.environ}
                if self.web or self.ios or self.android:
                    p_env["FLET_FORCE_WEB_SERVER"] = "true"

                    # force page name for ios
                    if self.ios or self.android:
                        p_env["FLET_WEB_APP_PATH"] = "/".join(Path(self.script_path).parts[-2:])
                if self.port is not None:
                    p_env["FLET_SERVER_PORT"] = str(self.port)
                if self.host is not None:
                    p_env["FLET_SERVER_IP"] = str(self.host)
                if self.page_name:
                    p_env["FLET_WEB_APP_PATH"] = self.page_name
                if self.uds_path is not None:
                    p_env["FLET_SERVER_UDS_PATH"] = self.uds_path
                if self.assets_dir is not None:
                    p_env["FLET_ASSETS_DIR"] = self.assets_dir
                p_env["FLET_DISPLAY_URL_PREFIX"] = self.page_url_prefix

                p_env["FLET_APP_STORAGE_DATA"] = self.flet_app_data_dir
                p_env["FLET_APP_STORAGE_TEMP"] = self.flet_app_temp_dir

                p_env["PYTHONIOENCODING"] = "utf-8"
                p_env["PYTHONWARNINGS"] = "default::DeprecationWarning"

                self.p = subprocess.Popen(
                    self.args, env=p_env, stdout=subprocess.PIPE, encoding="utf-8"
                )

                self.is_running = True
                th = threading.Thread(target=self.print_output, args=[self.p], daemon=True)
                th.start()

            def on_any_event(self, event):
                for directory in self.ignore_dirs:
                    child = os.path.abspath(event.src_path)
                    # check if the file which triggered the reload is in the (ignored) directory
                    if os.path.commonpath([directory]) == os.path.commonpath(
                            [directory, child]
                    ):
                        return

                if (
                        self.watch_directory or event.src_path == self.script_path or event.src_path.endswith(".ft")
                ) and event.event_type in ["modified", "deleted", "created", "moved"]:
                    current_time = time.time()
                    if (current_time - self.last_time) > 0.5 and self.is_running:
                        self.last_time = current_time
                        th = threading.Thread(target=self.restart_program, args=(), daemon=True)
                        th.start()

            def print_output(self, p):
                while True:
                    line = p.stdout.readline()
                    if not line:
                        break
                    line = line.rstrip("\r\n")
                    if line.startswith(self.page_url_prefix):
                        if not self.page_url:
                            self.page_url = line[len(self.page_url_prefix) + 1:]
                            if (
                                    self.page_url.startswith("http")
                                    and not self.ios
                                    and not self.android
                            ):
                                print(self.page_url)
                            if self.ios or self.android:
                                self.print_qr_code(self.page_url, self.android)
                            elif self.web:
                                open_in_browser(self.page_url)
                            else:
                                th = threading.Thread(
                                    target=self.open_flet_view_and_wait, args=(), daemon=True
                                )
                                th.start()
                    else:
                        print(line)

            def open_flet_view_and_wait(self):
                from flet_desktop import open_flet_view

                self.fvp, self.pid_file = open_flet_view(
                    self.page_url, self.assets_dir, self.hidden
                )
                self.fvp.wait()
                self.p.send_signal(signal.SIGTERM)
                try:
                    self.p.wait(2)
                except subprocess.TimeoutExpired:
                    self.p.kill()
                self.terminate.set()

            def restart_program(self):
                self.is_running = False
                self.p.send_signal(signal.SIGTERM)
                self.p.wait()
                self.start_process()

            def print_qr_code(self, orig_url: str, android: bool):
                u = urlparse(orig_url)
                ip_addr = get_local_ip()
                lan_url = urlunparse(
                    (u.scheme, f"{ip_addr}:{u.port}", u.path, None, None, None)
                )
                # self.clear_console()
                print("App is running on:", lan_url)
                print("")
                qr_url = (
                    urlunparse(
                        (
                            "https",
                            "android.flet.dev",
                            quote(f"{ip_addr}:{u.port}{u.path}", safe="/"),
                            None,
                            None,
                            None,
                        )
                    )
                    if android
                    else urlunparse(
                        ("flet", "flet-host", quote(lan_url, safe=""), None, None, None)
                    )
                )
                # print(qr_url)
                qr = qrcode.QRCode()
                qr.add_data(qr_url)
                qr.print_ascii(invert=True)
                # qr.print_tty()
                print("")
                print("Scan QR code above with Camera app.")

            def clear_console(self):
                if platform.system() == "Windows":
                    if platform.release() in {"10", "11"}:
                        subprocess.run(
                            "", shell=True
                        )  # Needed to fix a bug regarding Windows 10; not sure about Windows 11
                        print("\033c", end="")
                    else:
                        subprocess.run(["cls"])
                else:  # Linux and Mac
                    print("\033c", end="")

        # wstawiamy naszą klasę do modułu run
        run_module.Handler = Handler
        sys.modules["flet_cli.commands.run"].Handler = Handler

        print("✅ flet_cli.commands.run.Handler has been replaced with custom version")

    except Exception as e:
        print(f"❌ Failed to patch flet_cli Handler: {e}")
