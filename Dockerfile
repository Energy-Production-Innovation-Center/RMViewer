# Target environment for Linux.
FROM rockylinux:9 AS target-linux
WORKDIR /repo

# Install required packages.
COPY --chmod=0755 scripts/target.sh .
RUN ./target.sh && rm target.sh

# Download continuous integration dependencies.
FROM target-linux AS ci
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=source=rmviewer,target=/repo/rmviewer,rw \
    python -m venv .venv \
    && source .venv/bin/activate \
    && python -m pip install --upgrade .[ci]

# Set project version
ARG APP_VERSION
RUN echo $APP_VERSION > .version

# Download CLI build dependencies.
FROM target-linux AS cd-linux-cli
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=source=rmviewer,target=/repo/rmviewer,rw \
    pip install --upgrade .[cd]

# Set project version
ARG APP_VERSION
RUN echo $APP_VERSION > .version

# Type checking.
FROM ci AS type-checker
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN --mount=source=rmviewer,target=/repo/rmviewer \
    mkdir -p /out/report \
    && source .venv/bin/activate \
    && python -m ty check --exit-zero rmviewer > /out/report/type_check.txt


# CLI executable generation.
FROM cd-linux-cli AS build-linux-cli
RUN --mount=source=rmviewer,target=/repo/rmviewer \
    pyinstaller \
    --onefile \
    --name RMViewer-$APP_VERSION \
    --add-data .version:. \
    --distpath /out/bin/linux \
    rmviewer/__main__.py

# Target environment for Windows.
FROM debian:bookworm-slim AS pack-env
ARG APP_VERSION
RUN echo $APP_VERSION > .version
RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    # NSIS windows packager
    nsis=3.08-3+deb12u1 \
    nsis-doc=3.08-3+deb12u1 \
    nsis-pluginapi=3.08-3+deb12u1 \
    # FPM linux packager
    ruby=1:3.1 \
    ruby-dev=1:3.1 \
    build-essential=12.9 \
    rpm=4.18.0+dfsg-1+deb12u1 \
    # Zip
    zip=3.0-13 \
    && rm -rf /var/lib/apt/lists/*
RUN gem install fpm:1.14.1

# Linux packaging.
FROM pack-env AS fpm
WORKDIR /installer
COPY --chmod=0755 scripts/package_linux.sh  .
COPY --from=build-linux-cli /out/bin/linux ./bin/
RUN ./package_linux.sh $APP_VERSION /out && rm -rf ./*

# Target environment for Windows.
FROM tobix/pywine:3.12 AS target-windows
WORKDIR /repo
# Update Wine version to one that is compatible to Numpy
RUN apt-get --purge remove -y wine-devel \
    && apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y winehq-devel git openssh-client \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
# Update pyinstaller from Wine prefix
RUN wine pip install --upgrade pyinstaller

# Download CLI build dependencies for Windows.
FROM target-windows AS cd-windows-cli
COPY pyproject.toml ./
RUN --mount=type=cache,target=/opt/wineprefix/drive_c/users/root/appdata/local/pip/cache \
    --mount=source=rmviewer,target=/repo/rmviewer,rw \
    # Install dependencies using pip
    wine pip install --upgrade .[cd]
# Set project version
ARG APP_VERSION
RUN echo $APP_VERSION > .version

# CLI executable generation for Windows.
FROM cd-windows-cli AS build-windows-cli
RUN --mount=source=rmviewer,target=/repo/rmviewer \
    wine pyinstaller \
    --onefile \
    --name RMViewer-$APP_VERSION \
    --add-data .version:. \
    --distpath /out/bin/windows \
    rmviewer/__main__.py

# Windows Packaging
FROM pack-env AS nsis
WORKDIR /installer
COPY --chmod=0755 scripts/package_windows.sh .
COPY installer.nsi ./
COPY --from=build-windows-cli /out/bin/windows ./bin/
RUN ./package_windows.sh $APP_VERSION /out && rm -rf ./*

# Type checking collection.
FROM scratch AS type
COPY --from=type-checker /out/* /

# CLI binary collection for Linux.
FROM scratch AS bin-linux-cli
COPY --from=build-linux-cli /out/* /

# CLI binary collection for Windows.
FROM scratch AS bin-windows-cli
COPY --from=build-windows-cli /out/* /

# Linux installer collection.
FROM scratch AS installer-linux
COPY --from=fpm /out/* /

# Windows installer collection.
FROM scratch AS installer-windows
COPY --from=nsis /out/* /