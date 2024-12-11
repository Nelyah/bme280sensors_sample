import smbus2
import bme280
import argparse
import time
import influxdb_client
import logging
from dotenv import dotenv_values
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Config(BaseModel):
    INFLUXDB_ORG: str
    INFLUXDB_API_TOKEN: str
    INFLUXDB_URL: str
    INFLUXDB_BUCKET: str
    INFLUXDB_POINT_NAME: str
    LOCATION_TAG: str


def main(args: argparse.Namespace) -> None:
    # BME280 sensor address (default address)
    address = 0x76

    # Initialize I2C bus
    bus = smbus2.SMBus(1)

    calibration_params = bme280.load_calibration_params(bus, address)
    config = Config.model_validate(dotenv_values(args.env_file))

    client = influxdb_client.InfluxDBClient(
        url=config.INFLUXDB_URL,
        token=config.INFLUXDB_API_TOKEN,
        org=config.INFLUXDB_ORG,
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while True:
        time.sleep(args.poll_seconds)

        # Read sensor data
        # Temperature is in Celcius
        data = bme280.sample(bus, address, calibration_params)

        p = (
            influxdb_client.Point(config.INFLUXDB_POINT_NAME)
            .tag("location", config.LOCATION_TAG)
            .field("temperature", data.temperature)
            .field("humidity", data.humidity)
            .field("pressure", data.pressure)
        )

        write_api.write(
            bucket=config.INFLUXDB_BUCKET, org=config.INFLUXDB_ORG, record=p
        )

        logger.info(
            "Temp={0:0.1f}ºC, Humidity={1:0.1f}%, Pressure={2:0.2f}hPa".format(
                data.temperature, data.humidity, data.pressure
            )
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-file", required=False, type=str, help="Path to the .env file to use"
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=60,
        help="Number of seconds in between each sample. [default: 60]",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
