"""Convert lat/lon to MRMS x/y grid coordinates.

        Args:
            lat (float): Latitude (WGS84/NAD83)
            lon (float): Longitude

        Returns:
            tuple[int, int]: (x, y) grid indices
        """
import os
import gc
import time
import logging
import shutil
import numpy as np
import psutil
import requests
from typing import Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob
from osgeo import gdal
import plotly.graph_objects as go

class MRMSLocator:
    """Converts latitude/longitude (WGS84/NAD83) to MRMS x/y grid coordinates."""

    _geotransform = (
        -129.99999999985712,   # Top-left longitude
        0.009999999714244895,  # Pixel width
        0.0,
        54.9999999998571,      # Top-left latitude
        0.0,
        -0.009999999714204058  # Pixel height
    )

    @classmethod
    def latlon_to_grid(cls, lat: float, lon: float) -> tuple[int, int]:
        """Convert lat/lon to MRMS x/y grid coordinates.

        Args:
            lat (float): Latitude (WGS84/NAD83)
            lon (float): Longitude

        Returns:
            tuple[int, int]: (x, y) grid indices
        """
        origin_x, pixel_width, _, origin_y, _, pixel_height = cls._geotransform
        x = round((lon - origin_x) / pixel_width)
        y = round((lat - origin_y) / pixel_height)
        return x, y

class DownloadManager:
    """Convert lat/lon to MRMS x/y grid coordinates.

        Args:
            lat (float): Latitude (WGS84/NAD83)
            lon (float): Longitude

        Returns:
            tuple[int, int]: (x, y) grid indices
        """
    def __init__(self, product: str, x: int, y: int, start_date: datetime, end_date: datetime,
                 interval: int, output_prefix: str, output_dir: str,
                 template_file: str, max_workers: int = 4, subfolder: Optional[str] = None):
        self.product = product
        self.subfolder = subfolder
        self.x = x
        self.y = y
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.output_prefix = output_prefix
        self.output_dir = output_dir
        self.template_file = template_file
        self.max_workers = max_workers

    def _check_disk_space(self, path: str, threshold: int = 10) -> None:
        usage = shutil.disk_usage(path)
        free_percent = (usage.free / usage.total) * 100
        if free_percent < threshold:
            raise RuntimeError(f"Insufficient disk space: {free_percent:.2f}% free.")

    def _log_memory(self, tag: str) -> None:
        mem = psutil.virtual_memory()
        logging.info(f"[MEMORY] {tag}: Used={mem.used / 1e9:.2f} GB, Avail={mem.available / 1e9:.2f} GB")

    def _generate_url(self, date: datetime) -> str:
        path = date.strftime("%Y/%m/%d")
        fname = f"{self.product}_00.00_{date.strftime('%Y%m%d-%H%M')}00.grib2.gz"

        if self.subfolder:
            url = f"https://mtarchive.geol.iastate.edu/{path}/mrms/ncep/{self.subfolder}/{self.product}/{fname}"
        else:
            url = f"https://mtarchive.geol.iastate.edu/{path}/mrms/ncep/{self.product}/{fname}"

        return url

    def _download_file(self, url: str, out: str) -> Optional[str]:
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(out, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
            return out
        except Exception as e:
            logging.warning(f"Download failed: {e}")
            return None

    def _extract_value(self, file: str, date: datetime) -> Optional[np.ndarray]:
        ds = gdal.Open(f"/vsigzip/{file}")
        if ds is None:
            return None
        try:
            band = ds.GetRasterBand(1)
            value = band.ReadAsArray(self.x, self.y, 1, 1)[0, 0]
            return np.array([[date, value]])
        except Exception as e:
            logging.warning(f"Extract failed: {e}")
            return None
        finally:
            band, ds = None, None
            gc.collect()

    def _process_date(self, date: datetime) -> None:
        gz = f"temp_{date.strftime('%Y%m%d%H%M')}.grib2.gz"
        url = self._generate_url(date)
        if not self._download_file(url, gz):
            return
        arr = self._extract_value(gz, date)
        if arr is not None:
            name = f"{self.output_prefix}_{date.strftime('%Y%m%d_%H%M')}.npy"
            np.save(os.path.join(self.output_dir, name), arr)
        if os.path.exists(gz):
            os.remove(gz)

    def download_all(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        self._check_disk_space(self.output_dir)
        self._log_memory("Start")

        timestamps = []
        current = self.start_date
        while current <= self.end_date:
            timestamps.append(np.datetime64(current))
            current += timedelta(minutes=self.interval)

        np.save(self.template_file, np.array(timestamps))

        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = [ex.submit(self._process_date, dt.astype(datetime)) for dt in timestamps]
            for f in as_completed(futures):
                f.result()

        self._log_memory("End")


class TimeSeriesConsolidator:
    """Convert lat/lon to MRMS x/y grid coordinates.

        Args:
            lat (float): Latitude (WGS84/NAD83)
            lon (float): Longitude

        Returns:
            tuple[int, int]: (x, y) grid indices
        """
    def __init__(self, input_dir: str, output_file: str, template_file: str):
        self.input_dir = input_dir
        self.output_file = output_file
        self.template_file = template_file

    def consolidate(self) -> None:
        timestamps = np.load(self.template_file)
        pattern = os.path.join(self.input_dir, "*.npy")
        files = sorted(glob(pattern))
        index_map = {ts: i for i, ts in enumerate(timestamps)}
        data = np.zeros(len(timestamps), dtype="float32")

        for file in files:
            try:
                arr = np.load(file, allow_pickle=True)
                dt, val = arr[0]
                idx = index_map.get(np.datetime64(dt))
                if idx is not None:
                    data[idx] = float(val)
            except Exception:
                continue

        np.save(self.output_file, data)


class TimeSeriesPlotter:
    """Convert lat/lon to MRMS x/y grid coordinates.

        Args:
            lat (float): Latitude (WGS84/NAD83)
            lon (float): Longitude

        Returns:
            tuple[int, int]: (x, y) grid indices
        """
    def __init__(self, timestamps_file: str, data_file: str, site_id: str, product: str):
        self.timestamps = np.load(timestamps_file)
        self.data = np.load(data_file)
        self.site_id = site_id
        self.product = product

    def plot(self) -> None:
        print(f"[DEBUG] Product (raw): {self.product}")  # <- nuevo
        product_upper = self.product.upper()
        print(f"[DEBUG] Product (upper): {product_upper}")  # <- nuevo
        if product_upper in ("SAC_MAXSTREAMFLOW", "CREST_MAXSTREAMFLOW", "HP_MAXSTREAMFLOW"):
            y_title = "Streamflow (cms)"
        elif product_upper == "RadarOnly_QPE_01H":
            y_title = "Precipitation Rate (mm/h)"
        else:
            y_title = "Value"

        # Imprime para depuración
        print(f"[DEBUG] Product: {self.product}")
        print(f"[DEBUG] y-axis title: {y_title}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.timestamps, y=self.data,
            mode='lines+markers',
            name=self.site_id,
            marker=dict(size=3)
        ))

        fig.update_layout(
            title=f"Time Series for Site {self.site_id}",
            xaxis_title="Date",
            yaxis_title=y_title,
            template="plotly_white",
            height=600,
            width=1000
        )
        fig.show()




class Processor:
    """Convert lat/lon to MRMS x/y grid coordinates.

        Args:
            lat (float): Latitude (WGS84/NAD83)
            lon (float): Longitude

        Returns:
            tuple[int, int]: (x, y) grid indices
        """
    def __init__(self, product: str, x: int, y: int,
                 start_date: datetime, end_date: datetime,
                 interval_minutes: int, site_id: str,
                 output_dir: str, max_workers: int = 4):
        self.product = product
        self.x = x
        self.y = y
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval_minutes
        self.site_id = site_id
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.template_path = os.path.join(output_dir, f"{site_id}_timestamps.npy")
        self.output_file = os.path.join(output_dir, f"{site_id}_time_series.npy")

    def run(self, plot: bool = False) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(f"{self.site_id}.log", mode="w")]
        )
        logging.info("🚀 FlashProcessor started")
        
        if self.product in ("SAC_MAXSTREAMFLOW", "CREST_MAXSTREAMFLOW", "HP_MAXSTREAMFLOW"):
            subfolder = "FLASH"
        elif self.product == "RadarOnly_QPE_01H":
            subfolder = None
        else:
            raise ValueError(f"Product not supported: {self.product}")

        downloader = DownloadManager(
            product=self.product,
            x=self.x,
            y=self.y,
            start_date=self.start_date,
            end_date=self.end_date,
            interval=self.interval,
            output_prefix=self.site_id,
            output_dir=self.output_dir,
            template_file=self.template_path,
            max_workers=self.max_workers,
            subfolder=subfolder
        )
        downloader.download_all()

        consolidator = TimeSeriesConsolidator(
            input_dir=self.output_dir,
            output_file=self.output_file,
            template_file=self.template_path
        )
        consolidator.consolidate()

        if plot:
            plotter = TimeSeriesPlotter(
                timestamps_file=self.template_path,
                data_file=self.output_file,
                site_id=self.site_id,
                product=self.product
            )
            plotter.plot()