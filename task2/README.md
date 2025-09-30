##1 часть
```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "source ~/ros2_ws/install/local_setup.bash" >> ~/.bashrc
source ~/.bashrc
```
###Создание воркспейса:
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
source install/local_setup.bash
printenv | grep ROS > ex01.txt
mkdir ex01
cp ex01.txt ~/.bashrc ex01/
```
##2 часть
```bash
# Переходим в рабочую директорию (если нужно)
cd ~/ros2_ws
# Создаем папку ex02 если она еще не существует
mkdir -p ex02
# 1. Находим путь к пакету ros2topic и сохраняем в файл
ros2 pkg prefix ros2topic > ex02/package_path_rostopic.txt
# 2. Находим исполняемые файлы в пакете action_tutorials_py и сохраняем в файл
ros2 pkg executables action_tutorials_py > ex02/list_exec_action_tutorials.txt
# Проверяем содержимое файлов
cat ex02/package_path_rostopic.txt
cat ex02/list_exec_action_tutorials.txt
```
##3 часть
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python semar_package --dependencies std_msgs rclpy
cd ~/ros2_ws
colcon build --packages-select semar_package
ros2 pkg list | grep semar
```
##4 Часть
```bash
colcon build --packages-select semar_package &> file.txt
```

##5 Часть
```bash
ros2 run turtlesim turtlesim_node --ros-args --remap __node:=semar_turtle
mkdir -p ex05
ros2 node list > ex05/rosnode_list.txt
ros2 node info /semar_turtle > ex05/rosnode_info.txt

```

##6 Часть
```bash
ros2 run rqt_graph rqt_graph # запуск графа
ros2 run turtlesim turtlesim_node --ros-args --remap __node:=semar_turtle
mkdir -p ex06
ros2 topic echo /turtle1/cmd_vel > ex06/cmd_vel.txt & 
ECHO_PID=$!
# Начинаем рисовать восьмерку
# Первая половина восьмерки (верхний круг)
ros2 topic pub -1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"
sleep 6
# Вторая половина восьмерки (нижний круг)
ros2 topic pub -1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -0.5}}"
sleep 6
# Завершаем и останавливаем черепаху
ros2 topic pub -1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
# Установите ImageMagick если нет
sudo apt update && sudo apt install -y imagemagick
# Сделайте скриншот окна turtlesim
import -window "TurtleSim" ex06/eight.png
```
##7 Часть
```bash
ros2 run turtlesim turtlesim_node
# Леонардо
ros2 service call /spawn turtlesim/srv/Spawn "{x: 5.0, y: 5.0, theta: 0.0, name: 'Leonardo'}"
# Рафаэль
ros2 service call /spawn turtlesim/srv/Spawn "{x: 8.0, y: 8.0, theta: 1.57, name: 'Raphael'}"
# Донателло
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 8.0, theta: 3.14, name: 'Donatello'}"
# Микеланджело
ros2 service call /spawn turtlesim/srv/Spawn "{x: 8.0, y: 2.0, theta: -1.57, name: 'Michelangelo'}"
ros2 param set /turtlesim background_g 124
mkdir -p ex07
import -window "TurtleSim" ex07/turtles.png
ros2 service list > rosservice_list.txt
ros2 param dump /turtlesim > parameter_server.txt
mv rosservice_list.txt ex07/
mv parameter_server.txt ex07/
```
##8 Часть
```bash
ros2 run rqt_console rqt_console
mkdir -p ~/ros2_ws/src/launch
cd ~/ros2_ws/src/launch
touch three_turtles_launch.py
chmod +x three_turtles_launch.py 
ros2 run turtlesim turtle_teleop_key --ros-args --remap turtle1/cmd_vel:=/turtlesim1/turtle1/cmd_vel
```
##9 Часть
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake full_name_interfaces
cd full_name_interfaces
mkdir msg srv
```
```cmake
# Найти необходимые зависимости
find_package(rosidl_default_generators REQUIRED)

# Сгенерировать интерфейсы
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/FullNameMessage.msg"
  "srv/FullNameSumService.srv"
)
```
```xml
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```
```bash
cd ~/ros2_ws
colcon build --packages-select full_name_interfaces
source install/setup.bash
ros2 interface show full_name_interfaces/msg/FullNameMessage
ros2 interface show full_name_interfaces/srv/FullNameSumService
mkdir -p ~/ros2_ws/ex09
cp -r ~/ros2_ws/src/full_name_interfaces/* ~/ros2_ws/ex09/
```
##10 Часть
```bash
# Терминал 1: Запускаем turtlesim
ros2 run turtlesim turtlesim_node

# Терминал 2: Запускаем наш узел
ros2 run text_to_cmd_vel text_to_cmd_vel

# Терминал 3: Тестируем команды
ros2 topic pub /cmd_text std_msgs/msg/String "{data: 'move_forward'}"
```