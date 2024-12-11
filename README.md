# Log BME280 sensor readings to InfluxDB

The goal of this project is to get reads from a BME280 sensor for temperature (Celcius), humidity (%) and pressure (hPa).

## How to

1. Clone this repo on the device that will be doing the readings
2. Install the virtual environment
3. Potentially adjust the systemd unit file to have the right path
4. Setup an .env file with your values
5. Install the systemd unit file

```
git clone git@github.com:Nelyah/bme280sensors_sample
cd bme280sensors_sample
python -m venv .venv
source .venv/bin/activate
cp env.template .venv

# Edit .env file

# Potentially edit the systemd unit file

sudo cp bme280_sample.service /etc/systemd/system/
sudo systemctl start bme280_sample.service
sudo systemctl enable bme280_sample.service
```

You can follow the system logs with:

```
journalctl -u bme280_sample -f
```
