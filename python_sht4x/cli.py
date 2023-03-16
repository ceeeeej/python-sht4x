import time
import statistics
import collections
import logging
import time


import click
from python_sht4x import SHT4xSensor


@click.command()
@click.version_option()
@click.option(
    "--busnum",
    default=1,
    help='I2C Bus Number, from "ls /dev/i2c*" with the number as an integer.',
)
@click.option(
    "--addr",
    default=0x44,
    help="Device Address in hex, see datasheet for specific device (typ: 0x44 or 0x45 for SHT4x).",
)
@click.option(
    "--mode",
    default=1,
    type=click.Choice(range(0, 10)),
    help="Operating mode: 1 thru 9, numbers defined by this library",
)
@click.option(
    "--degrees_unit",
    default="C",
    type=click.Choice(["C", "F", "K"]),
    help="Unit for temperature measurements.",
)
@click.option(
    "--bus_delay",
    default=0.05,
    type=float,
    help="Device Address in hex, see datasheet for specific device (typ: 0x44 or 0x45 for SHT4x).",
)
@click.option(
    "--readings",
    default=1,
    type=int,
    help="Number of readings to take and average.",
)
@click.option(
    "--readings_delay",
    default=1.0,
    type=float,
    help="Delay between readings.",
)
@click.option(
    "--readings_return",
    default="average",
    type=click.Choice(["average", "list"]),
    help="Return average of measured values or list of data",
)
def main(
    busnum,
    addr,
    mode,
    degrees_unit,
    bus_delay,
    readings,
    readings_delay,
    readings_return,
) -> None:
    """python-sht4x"""
    sensor = SHT4xSensor(
        busnum=busnum,
        addr=addr,
        mode=mode,
        degrees_unit=degrees_unit,
        bus_delay=bus_delay,
    )
    temps = []
    humidities = []
    for i in range(readings + 1):
        sensor.get_data()
        temps.append(sensor.t_deg)
        humidities.append(sensor.rh_pRH)
        if readings > 1:
            time.sleep(readings_delay)
    if readings_return == "average":
        print(
            f"Temperature: {statistics.mean(temps):.2f}°{sensor.degrees_unit}, Humidity: {statistics.mean(humidities):.2f}%"
        )
    elif readings_return == "list":
        print(
            f"Temperature: {temps}°{sensor.degrees_unit}\nHumidity: {humidities:.2f}%"
        )


if __name__ == "__main__":
    main(prog_name="python-sht4x")  # pragma: no cover
