FROM ros:jazzy-ros-base
RUN apt-get update && apt-get install -y \
    ros-jazzy-turtlesim \
    ros-jazzy-rqt \
    ros-jazzy-rqt-common-plugins \
    ncal \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*