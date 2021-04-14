# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Healthy Home Sensor IAQ (TBHV110) binary payload converter
# Author: Gary A. Stafford
# Date: 2021-04-09

# | Bytes | Description                       |
# |-------|-----------------------------------|
# |     0 | Status                            |
# |     1 | Battery (Volts)                   |
# |     2 | Board temperature (Celsius)       |
# |     3 | Relative humidity (%)             |
# |     4 | CO2 equivalent estimate (eCO2)    |
# |     5 | CO2 equivalent estimate (eCO2)    |
# |     6 | VOC                               |
# |     7 | VOC                               |
# |     8 | Indoor-air-quality (IAQ)          |
# |     9 | Indoor-air-quality (IAQ)          |
# |    10 | Environment temperature (Celsius) |

import base64
import json

DEBUG_OUTPUT = False


def dict_from_payload(base64_input: str, fport: int = None):
    """ Decodes a base64-encoded binary payload into JSON.
            Parameters
            ----------
            base64_input : str
                Base64-encoded binary payload
            fport: int
                FPort as provided in the metadata. Please note the fport is optional and can have value "None", if not provided by the LNS or invoking function.

                If  fport is None and binary decoder can not proceed because of that, it should should raise an exception.

            Returns
            -------
            JSON object with key/value pairs of decoded attributes

        """
    decoded = base64.b64decode(base64_input)

    if DEBUG_OUTPUT:
        print(f"Input: {decoded.hex().upper()}")

    # Byte 1, bit 0
    status = decoded[0] & 0b00000001  # (1 << 1) - 1

    # Byte 2, bits 3:0
    battery = decoded[1] & 0b00001111  # (1 << 4) - 1
    battery = (25 + battery) / 10

    # Byte 3, bits 6:0
    board_temp = decoded[2] & 0b01111111  # (1 << 7) - 1
    board_temp = board_temp - 32

    # Byte 4, bits 6:0
    rh = decoded[3] & 0b01111111  # (1 << 7) - 1

    # Byte 5-6, bits 15:0
    eco2 = decoded[5] << 8 | decoded[4]
    eco2 = helpers.bin16dec(eco2)

    # Byte 7-8, bits 15:0
    voc = decoded[7] << 8 | decoded[6]
    voc = helpers.bin16dec(voc)

    # Byte 9-10, bits 15:0
    iaq = decoded[9] << 8 | decoded[8]
    iaq = helpers.bin16dec(iaq)

    # Byte 11, bits 6:0
    env_temp = decoded[10] & 0b1111111  # (1 << 7) - 1
    env_temp = env_temp - 32

    result = {
        'Status': status,
        'Battery': battery,
        'BoardTemp': board_temp,
        'RH': rh,
        'ECO2': eco2,
        'VOC': voc,
        'IAQ': iaq,
        'EnvTemp': env_temp,
    }

    if DEBUG_OUTPUT:
        print(f"Output: {json.dumps(result,indent=2)}")

    return result
