# """Command-line interface."""
import collections
import logging
import time
from crc import Configuration, Calculator
from smbus2 import SMBus, i2c_msg


class SHT4xSensor:
    def __init__(
        self,
        addr=0x44,
        busnum=1,
        degrees_unit="C",
        mode=1,
        bus_delay=0.05,
    ):
        """Create an SHT4x Sensor object
        Parameters:
            busnum (int): I2C Bus Number (default: 1)
            addr (int): I2C Address (default: 0x44)
            degrees_unit (str): Units for Degrees Measurements, options: 'C', 'F', 'K', (default: "C")
            mode (int): Mode for measurements (1-9)
        Calculations and other information per https://sensirion.com/media/documents/33FD6951/624C4357/Datasheet_SHT4x.pdf
        """

        # Initialize device settings
        self.busnum = int(busnum)
        self.addr = int(addr)
        self.degrees_unit = degrees_unit.upper()
        self.bus_delay = float(bus_delay)
        self.get_sn()
        # Set mode defaults, at the end self.mode will call the property setter to validate the mode and set the mode parameters
        self.mode_description = None
        self.mode_command_byte_length = None
        self.mode_command_time = None
        self.mode_command = None
        self.mode = int(mode)

        # Initialize variables and return data
        self.rx_bytes = []
        self.t_ticks = 0
        self.checksum_t = 0
        self.rh_ticks = 0
        self.checksum_rh = 0

    @property
    def degrees_unit(self):
        return self._degrees_unit

    @degrees_unit.setter
    def degrees_unit(self, value):
        assert value in ("C", "F", "K")
        self._degrees_unit = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        Mode = collections.namedtuple(
            "Mode", ["mode", "command", "command_length", "command_time", "description"]
        )
        modes = [
            Mode(
                1,
                0xFD,
                6,
                self.bus_delay,
                "Measure T and RH with high precision (high repeatability)",
            ),
            Mode(
                2,
                0xF6,
                6,
                self.bus_delay,
                "Measure T and RH with medium precision (medium repeatability)",
            ),
            Mode(
                3,
                0xE0,
                6,
                self.bus_delay,
                "Measure T and RH with lowest precision (low repeatability)",
            ),
            Mode(
                4,
                0x39,
                6,
                self.bus_delay + 1,
                "activate heater with 200mW for 1s, including a high precision measurement just before deactivation",
            ),
            Mode(
                5,
                0x32,
                6,
                self.bus_delay + 0.1,
                "activate heater with 200mW for 0.1s including a high precision measurement just before deactivation",
            ),
            Mode(
                6,
                0x2F,
                6,
                self.bus_delay + 1,
                "activate heater with 110mW for 1s including a high precision measurement just before deactivation",
            ),
            Mode(
                7,
                0x24,
                6,
                self.bus_delay + 0.1,
                "activate heater with 110mW for 0.1s including a high precision measurement just before deactivation",
            ),
            Mode(
                8,
                0x1E,
                6,
                self.bus_delay + 1,
                "activate heater with 20mW for 1s including a high precision measurement just before deactivation",
            ),
            Mode(
                9,
                0x15,
                6,
                self.bus_delay + 0.1,
                "activate heater with 20mW for 0.1s including a high precision measurement just before deactivation",
            ),
        ]
        assert value in tuple(range(1, len(modes)))
        selected_mode = modes[value - 1]
        self._mode = value
        self.mode_command = selected_mode.command
        self.mode_command_time = selected_mode.command_time
        self.mode_command_byte_length = selected_mode.command_length
        self.mode_description = selected_mode.description

    def get_sn(self):
        """
        Get sensor serial number
        :return: serialnumber
        """
        with SMBus(self.busnum) as bus:
            time.sleep(self.bus_delay)
            msg = i2c_msg.write(self.addr, [int(0x89)])
            bus.i2c_rdwr(msg)
            time.sleep(self.bus_delay)
            msg = i2c_msg.read(self.addr, 6)
            bus.i2c_rdwr(msg)
        rx_bytes = list(msg)
        self.serialnumber = (
            f"0x{(rx_bytes[0] + rx_bytes[1]):x}{(rx_bytes[3] + rx_bytes[4]):x}"
        )

    def set_mode(self, mode=1):
        # Check mode
        Mode = collections.namedtuple(
            "Mode", ["mode", "command", "command_length", "command_time", "description"]
        )
        modes = [
            Mode(
                1,
                0xFD,
                6,
                self.bus_delay,
                "Measure T and RH with high precision (high repeatability)",
            ),
            Mode(
                2,
                0xF6,
                6,
                self.bus_delay,
                "Measure T and RH with medium precision (medium repeatability)",
            ),
            Mode(
                3,
                0xE0,
                6,
                self.bus_delay,
                "Measure T and RH with lowest precision (low repeatability)",
            ),
            Mode(
                4,
                0x39,
                6,
                self.bus_delay + 1,
                "activate heater with 200mW for 1s, including a high precision measurement just before deactivation",
            ),
            Mode(
                5,
                0x32,
                6,
                self.bus_delay + 0.1,
                "activate heater with 200mW for 0.1s including a high precision measurement just before deactivation",
            ),
            Mode(
                6,
                0x2F,
                6,
                self.bus_delay + 1,
                "activate heater with 110mW for 1s including a high precision measurement just before deactivation",
            ),
            Mode(
                7,
                0x24,
                6,
                self.bus_delay + 0.1,
                "activate heater with 110mW for 0.1s including a high precision measurement just before deactivation",
            ),
            Mode(
                8,
                0x1E,
                6,
                self.bus_delay + 1,
                "activate heater with 20mW for 1s including a high precision measurement just before deactivation",
            ),
            Mode(
                9,
                0x15,
                6,
                self.bus_delay + 0.1,
                "activate heater with 20mW for 0.1s including a high precision measurement just before deactivation",
            ),
        ]
        selected_mode = modes[mode - 1]
        self.mode_command = selected_mode.command
        self.mode_command_time = selected_mode.command_time
        self.mode_command_byte_length = selected_mode.command_length
        self.mode_description = selected_mode.description

    def soft_reset(self):
        with SMBus(self.busnum) as bus:
            time.sleep(self.bus_delay)
            msg = i2c_msg.write(self.addr, [int(0x94)])
            bus.i2c_rdwr(msg)

    def get_raw_data(self):
        """
        Get raw data from sensor
        :return: list of bytes
        """
        with SMBus(self.busnum) as bus:
            time.sleep(self.mode_command_time)
            msg = i2c_msg.write(self.addr, [int(self.mode_command)])
            bus.i2c_rdwr(msg)
            time.sleep(self.mode_command_time)
            msg = i2c_msg.read(self.addr, int(self.mode_command_byte_length))
            bus.i2c_rdwr(msg)
        self.rx_bytes = list(msg)
        self.t_ticks = self.rx_bytes[0] * 256 + self.rx_bytes[1]
        self.checksum_t = self.rx_bytes[2]
        self.rh_ticks = self.rx_bytes[3] * 256 + self.rx_bytes[4]
        self.checksum_rh = self.rx_bytes[5]
        return self.rx_bytes

    def get_data(self):
        """
        Get data (calculation made from raw)
        :return: nothing, data is stored in self.t_deg and self.rh_pRH
        """
        self.compute_data()

    def compute_data(self):
        rx_bytes = self.get_raw_data()

        t_ticks = rx_bytes[0] * 256 + rx_bytes[1]
        checksum_t = rx_bytes[2]
        self.crc_check([rx_bytes[0], rx_bytes[1]], checksum_t)
        rh_ticks = rx_bytes[3] * 256 + rx_bytes[4]
        checksum_rh = rx_bytes[5]
        self.crc_check([rx_bytes[3], rx_bytes[4]], checksum_rh)

        # Calculations per https://sensirion.com/media/documents/33FD6951/624C4357/Datasheet_SHT4x.pdf
        if self.degrees_unit == "C":
            t_deg = -45 + 175 * t_ticks / 65535
        elif self.degrees_unit == "K":
            t_deg = -45 + 175 * t_ticks / 65535 + 273.15
        elif self.degrees_unit == "F":
            t_deg = -49 + 315 * t_ticks / 65535
        else:
            raise ValueError(
                f"Invalid degrees calculation with unit {self.degrees_unit}."
            )

        rh_pRH = -6 + 125 * rh_ticks / 65535
        if rh_pRH > 100:
            rh_pRH = 100
        elif rh_pRH < 0:
            rh_pRH = 0

        self.t_deg = t_deg
        self.rh_pRH = rh_pRH

    def crc_check(self, mydata, checksum):
        width = 8
        poly = 0x31
        init_value = 0xFF
        final_xor_value = 0x00
        reverse_input = False
        reverse_output = False
        configuration = Configuration(
            width, poly, init_value, final_xor_value, reverse_input, reverse_output
        )
        use_table = True
        mydata = bytes(mydata)
        expected_checksum = checksum
        crc_calculator = Calculator(configuration)#, use_table)
        checksum = crc_calculator.checksum(mydata)
        assert checksum == expected_checksum
        # assert crc_calculator.checksum(mydata, expected_checksum)
