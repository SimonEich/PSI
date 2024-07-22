from __future__ import annotations
import socket
from typing import Literal, List, Tuple

class FanucError(Exception):
    pass

class Robot:
    def __init__(
            self,
            robot_model: str,
            host: str,
            port: int = 18375,
            ee_DO_type: str | None = None,
            ee_DO_num: int | None = None,
            socket_timeout: int = 60,
    ):
        self.robot_model = robot_model
        self.host = host
        self.port = port
        self.ee_DO_type = ee_DO_type
        self.ee_DO_num = ee_DO_num
        self.sock_buff_sz = 1024
        self.socket_timeout = socket_timeout
        self.comm_sock: socket.socket
        self.SUCCESS_CODE = 0
        self.ERROR_CODE = 1

    def handle_response(
            self, resp: str, continue_on_error: bool = False
    ) -> tuple[Literal[0, 1], str]:
        code_, msg = resp.split(":")
        code = int(code_)

        if code == self.ERROR_CODE and not continue_on_error:
            raise FanucError(msg)
        if code not in (self.SUCCESS_CODE, self.ERROR_CODE):
            raise FanucError(f"Unknown response code: {code} and message: {msg}")

        return code, msg  # type: ignore[return-value]

    def connect(self) -> tuple[Literal[0, 1], str]:
        self.comm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_sock.settimeout(self.socket_timeout)
        self.comm_sock.connect((self.host, self.port))
        resp = self.comm_sock.recv(self.sock_buff_sz).decode()
        return self.handle_response(resp)

    def disconnect(self) -> None:
        self.comm_sock.close()

    def send_cmd(
            self, cmd: str, continue_on_error: bool = False
    ) -> tuple[Literal[0, 1], str]:
        cmd = cmd.strip() + "\n"
        self.comm_sock.sendall(cmd.encode())
        resp = self.comm_sock.recv(self.sock_buff_sz).decode()
        return self.handle_response(resp=resp, continue_on_error=continue_on_error)

    def setregister(self, cmd: str, continue_on_error: bool = False) -> tuple[Literal[0, 1], str]:
        return self.send_cmd(cmd, continue_on_error=continue_on_error)

    def send_vision_data(self, vision_data: List[Tuple[float, float, float]], continue_on_error: bool = False) -> List[tuple[Literal[0, 1], str]]:
        # Calculate max points per message (5 characters per value plus delimiters)
        max_points_per_msg = 12  # Ensuring the total length is within 254 characters
        responses = []

        # Format each value to 5 characters
        formatted_vision_data = [(f"{x_pos:05.1f}", f"{y_pos:05.1f}", f"{w_orient:05.1f}") for x_pos, y_pos, w_orient in vision_data]

        # Anzahl von erkannten Chips
        n_chips_vision = len(formatted_vision_data)
        n_chips_vision_ = f"{n_chips_vision:02}"

        # Send data in chunks
        for i in range(0, len(formatted_vision_data), max_points_per_msg):
            chunk = formatted_vision_data[i:i + max_points_per_msg]
            cmd_parts = ["vision", str(i // max_points_per_msg + 1), n_chips_vision_]
            for data in chunk:
                cmd_parts.extend(data)
            cmd = ":".join(cmd_parts)
            responses.append(self.send_cmd(cmd, continue_on_error=continue_on_error))

        return responses

if __name__ == "__main__":
    robot = Robot(
        robot_model="Fanuc",
        host="127.0.0.1",
        port=18735,
        ee_DO_type="RDO",
        ee_DO_num=7,
    )
    robot.connect()

    # Set register example
    #robot.setregister(cmd="setregister:9:9:9:9:9:9:9:9:9:9:9:9")

    # Vision data example (36 points)
    vision_data = [
        (1.0, 2.0, 30.0), (1.1, 2.1, 30.1), (1.2, 2.2, 30.2), (1.3, 2.3, 30.3),
        (1.4, 2.4, 30.4), (1.5, 2.5, 30.5), (1.6, 2.6, 30.6), (1.7, 2.7, 30.7),
        (1.8, 2.8, 30.8), (1.9, 2.9, 30.9), (2.0, 3.0, 31.0), (2.1, 3.1, 31.1),
        (2.2, 3.2, 31.2), (2.3, 3.3, 31.3), (2.4, 3.4, 31.4), (2.5, 3.5, 31.5),
        (2.6, 3.6, 31.6), (2.7, 3.7, 31.7), (2.8, 3.8, 31.8), (2.9, 3.9, 31.9),
        (3.0, 4.0, 32.0), (3.1, 4.1, 32.1), (3.2, 4.2, 32.2), (3.3, 4.3, 32.3),
        (3.4, 4.4, 32.4), (3.5, 4.5, 32.5), (3.6, 4.6, 32.6), (3.7, 4.7, 32.7),
        (3.8, 4.8, 32.8), (3.9, 4.9, 32.9), (4.0, 5.0, 33.0), (4.1, 5.1, 33.1),
        (4.2, 5.2, 33.2), (4.3, 5.3, 33.3), (4.4, 5.4, 33.4), (4.5, 5.5, 33.5)
    ]  # 36 tuples of (x, y, w)
    robot.send_vision_data(vision_data)

    robot.disconnect()
