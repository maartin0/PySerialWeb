ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}

USER root

RUN apt-get update && apt-get upgrade -y
RUN apt-get install bash git -y

RUN git clone https://github.com/emscripten-core/emsdk /emsdk

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install emscripten version required by pyodide
RUN cd /emsdk && \
    export PYODIDE_EMSCRIPTEN_VERSION=$(pyodide config get emscripten_version) && \
    ./emsdk install ${PYODIDE_EMSCRIPTEN_VERSION} && \
    ./emsdk activate ${PYODIDE_EMSCRIPTEN_VERSION} && \
    mkdir -p /app && cd /app && \
    . /emsdk/emsdk_env.sh && pyodide xbuildenv install --download

RUN echo '#!/bin/bash\nsource /emsdk/emsdk_env.sh > /dev/null\nexec "$@"' > /usr/local/bin/emsdk_shell && \
    chmod +x /usr/local/bin/emsdk_shell
SHELL ["/usr/local/bin/emsdk_shell", "/bin/bash", "-c"]

# Verify install was successful
RUN which emcc

# Build project
WORKDIR /app
COPY . .
RUN pyodide build -o ./dist
