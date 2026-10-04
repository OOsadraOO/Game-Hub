import psutil

try:
    import win32pdh
except ImportError:
    win32pdh = None


def get_gpu_usage():
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
                if "engtype_3D" not in instance.lower():
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

            import time
            time.sleep(0.05)

            win32pdh.CollectQueryData(query)

            total = 0.0
            for counter in counters:
                try:
                    _, value = win32pdh.GetFormattedCounterValue(
                        counter, win32pdh.PDH_FMT_DOUBLE
                    )
                    total += float(value)
                except Exception:
                    pass

            return max(0.0, min(100.0, total))
        finally:
            win32pdh.CloseQuery(query)

    except Exception:
        return None


def get_system_snapshot():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "ram_used": psutil.virtual_memory().used,
        "ram_total": psutil.virtual_memory().total,
        "gpu": get_gpu_usage()
    }
