import psutil
import subprocess
import time

try:
    import win32pdh
except ImportError:
    win32pdh = None

_gpu_usage_cache = None
_gpu_usage_cache_time = 0.0
_gpu_name_cache = None


def _clamp(value):
    return max(0.0, min(100.0, float(value)))


def _get_gpu_usage_pdh():
    if win32pdh is None:
        return None

    try:
        _, instances = win32pdh.EnumObjectItems(
            None, None, "GPU Engine", win32pdh.PERF_DETAIL_WIZARD
        )

        if not instances:
            return None

        query = win32pdh.OpenQuery()
        counters = []

        try:
            for index, instance in enumerate(instances):
                if "engtype_3d" not in instance.lower():
                    continue

                path = win32pdh.MakeCounterPath(
                    (None, "GPU Engine", instance, None, index, "Utilization Percentage")
                )

                try:
                    counters.append(win32pdh.AddCounter(query, path))
                except Exception:
                    pass

            if not counters:
                return None

            win32pdh.CollectQueryData(query)
            time.sleep(0.05)
            win32pdh.CollectQueryData(query)

            values = []

            for counter in counters:
                try:
                    _, value = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_DOUBLE
                    )
                    values.append(float(value))
                except Exception:
                    pass

            if not values:
                return None

            return _clamp(sum(values))
        finally:
            win32pdh.CloseQuery(query)

    except Exception:
        return None


def _get_gpu_usage_powershell():
    """Fallback for systems where the pywin32 PDH query is unavailable."""
    command = (
        "$samples = (Get-Counter "
        "'\\GPU Engine(*)\\Utilization Percentage' "
        "-ErrorAction Stop).CounterSamples | "
        "Where-Object { $_.InstanceName -like '*engtype_3D*' }; "
        "($samples | Measure-Object -Property CookedValue -Sum).Sum"
    )

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ],
            capture_output=True,
            text=True,
            timeout=2.0
        )

        if result.returncode != 0:
            return None

        raw = result.stdout.strip().replace(",", ".")
        if not raw or raw.lower() == "nan":
            return None

        return _clamp(float(raw))
    except Exception:
        return None


def get_gpu_usage():
    global _gpu_usage_cache, _gpu_usage_cache_time

    value = _get_gpu_usage_pdh()

    if value is not None:
        _gpu_usage_cache = value
        _gpu_usage_cache_time = time.time()
        return value

    # Avoid launching PowerShell on every UI refresh.
    now = time.time()
    if now - _gpu_usage_cache_time < 2.0:
        return _gpu_usage_cache

    value = _get_gpu_usage_powershell()
    _gpu_usage_cache = value
    _gpu_usage_cache_time = now
    return value


def get_gpu_name():
    """Return the primary Windows display adapter name when available."""
    global _gpu_name_cache

    if _gpu_name_cache:
        return _gpu_name_cache

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_VideoController | "
                "Where-Object { $_.Name } | "
                "Select-Object -ExpandProperty Name) -join ' | '"
            ],
            capture_output=True,
            text=True,
            timeout=2.0
        )

        if result.returncode == 0:
            name = result.stdout.strip()
            if name:
                _gpu_name_cache = name
                return _gpu_name_cache
    except Exception:
        pass

    return _gpu_name_cache


def get_system_snapshot():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "ram_used": psutil.virtual_memory().used,
        "ram_total": psutil.virtual_memory().total,
        "gpu": get_gpu_usage(),
        "gpu_name": get_gpu_name()
    }
