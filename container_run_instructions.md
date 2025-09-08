```bash
docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -e XAUTHORITY=/tmp/xauth \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --name ros_jazzy_container \
    ros-jazzy-desktop
```
Затем в контейнере:
```bash
source /opt/ros/jazzy/setup.bash
```