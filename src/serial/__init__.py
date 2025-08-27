import sys


if sys.platform != "emscripten":
    raise ImportError("Not running in WASM")
