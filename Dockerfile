ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}

USER root
SHELL ["/usr/bin/env", "bash", "-c"]

RUN apt-get update && apt-get upgrade -y
RUN apt-get install bash git -y

RUN git clone https://github.com/emscripten-core/emsdk /emsdk

COPY requirements.txt .

# Install emscripten version required by pyodide
RUN pip install --no-cache-dir -r requirements.txt && \
    cd /emsdk && \
    export PYODIDE_EMSCRIPTEN_VERSION=$(pyodide config get emscripten_version) && \
    ./emsdk install ${PYODIDE_EMSCRIPTEN_VERSION} && \
    ./emsdk activate ${PYODIDE_EMSCRIPTEN_VERSION}

# Build project
WORKDIR /app
COPY . .
RUN . /emsdk/emsdk_env.sh && pyodide build -o ./dist
