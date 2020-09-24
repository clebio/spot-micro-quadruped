#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 14:51:58 2020

@author: miguel-asd

Updates on September, 2020
@author: clebio
"""

import numpy as np
import time
import logging
from sys import exit
from os import environ

from src.joystick import Joystick, setup_joystick
from src.arduino import get_ACM


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    joystick = setup_joystick()

    ARDUINO = False if environ.get("NO_ARDUINO") else True
    if ARDUINO:
        arduino = get_ACM()
    else:
        logging.info("Skipping Arduino setup!")

    angles = [90 for i in np.zeros(12)]

    lastTime = 0.0
    interval = 0.02

    while True:
        now = time.time()
        if now - lastTime < interval:
            continue
        lastTime = now
        logger.debug(f"Loop at {lastTime} ms")

        oh_joy = joystick.read()
        if isinstance(oh_joy[0], str) and oh_joy[0] == "Shutdown!":
            logger.info("Shutting down")
            if ARDUINO:
                arduino.send("<QUIT>")
                line = arduino.arduino.readline().decode("utf-8").rstrip()
                logger.info(f"Shutdown response: {line}")
            logger.info("Done with calibration")
            exit(0)

        commandPose, commandOrn, V, angle, Wrot, T, compliantMode = oh_joy
        logger.debug("{}, {}".format(commandPose.tolist(), commandOrn.tolist()))

        if ARDUINO:
            (
                arduinoLoopTime,
                battery,
                Xacc,
                Yacc,
                realRoll,
                realPitch,
            ) = arduino.receive()

        pos = np.sin(now)
        pulses = [pos for _ in range(12)]

        command = [90 + np.rad2deg(a) for a in pulses]

        message = "<SERVO#{}>\n".format(
            "#".join(f"{i}~{str(c)}" for i, round(c, 3) in enumerate(command))
        )

        log_message = " ".join(str(round(c, 2)) for c in limited_angles)
        logger.info(f"Commands: {log_message}")
        if ARDUINO:
            arduino.send(message)
            # line = arduino.arduino.readline().decode("utf-8").rstrip()
            # logger.info(line)
