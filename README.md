# Temperature Logger

Designed and Developed by Franz Ayestaran - http://franz.ayestaran.co.uk

Raspberry Pi Pico with external RTC

![SplashScreen](https://github.com/Code-Munkeys/TemperatureLogger/assets/1928315/f6138f1d-16f4-49f7-910c-7f0d40304b91)

![MainScreen](https://github.com/Code-Munkeys/TemperatureLogger/assets/1928315/b99f41a5-70cb-4808-b770-5c9e0655f9a0)

Usage:

RED Button: Toggle Logging On / Off, GREEN Button: Toggle °C / °F, BLUE Button: Toggle OLED display On / Off. When the OLED Display is in the off state, the Pico onboard LED is illuminated to show the temperature logger is on.

POTENTIOMETER: Interval time <Left 60s> <Center 30s> <Right 15s> (s = seconds)

When the logging CSV file is created and appended to, the filename suffix datetime stamp is set to the following format... [temperatureYYYY-MM-DD_HHMMSS.csv]. If no external RTC is installed then an additional random suffix number can be added to the filename... [temperatureYYYY-MM-DD_HHMMSS_01234567.csv]

Whenever the logging CSV file is being updated, the red LED will illuminate for half a second.
