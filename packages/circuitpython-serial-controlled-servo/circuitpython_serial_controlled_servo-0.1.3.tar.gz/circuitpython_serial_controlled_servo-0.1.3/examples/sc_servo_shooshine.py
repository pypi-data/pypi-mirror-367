# SPDX-FileCopyrightText: Copyright (c) 2025 Jacques Supcik
#
# SPDX-License-Identifier: MIT

import math
import time

import board

from sc_servo import SerialControlledServo

STEPS = 128
SPEEDS = [int(math.sin(i * 2 * math.pi / STEPS) * 1000) for i in range(STEPS)]
DELAY_S = 0.2


def main() -> None:
    # Replace boards.IO02 and board.IO01 with the appropriate pins for your board
    servo = SerialControlledServo(tx_pin=board.IO02, rx_pin=board.IO01)
    index: int = 0
    while True:
        servo.set_motor_speed(servo_id=1, speed=SPEEDS[index])
        index = (index + 1) % len(SPEEDS)


main()
