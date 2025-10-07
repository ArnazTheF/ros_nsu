import sys
import rclpy
from rclpy.node import Node
from full_name_interfaces.srv import SummFullName

class FullNameClient(Node):
    def __init__(self):
        super().__init__('full_name_client')
        self.cli = self.create_client(SummFullName, 'SummFullName')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

    def send_request(self, surname, name, patronymic):
        req = SummFullName.Request()
        req.surname = surname
        req.name = name
        req.patronymic = patronymic
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

def main(args=None):
    if len(sys.argv) != 4:
        print('Usage: client_name surname name patronymic')
        return
    rclpy.init(args=args)
    client = FullNameClient()
    response = client.send_request(sys.argv[1], sys.argv[2], sys.argv[3])
    client.get_logger().info(f'Result: {sys.argv[1]} {sys.argv[2]} {sys.argv[3]} -> {response.full_name}')
    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()