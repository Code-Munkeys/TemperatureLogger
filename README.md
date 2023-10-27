# Temperature Logger

Designed and Developed by Franz Ayestaran - http://franz.ayestaran.co.uk

Raspberry Pi Pico with external RTC

![SplashScreen](https://github.com/Code-Munkeys/TemperatureLogger/assets/1928315/a2cc1dbf-63b9-47ec-b51d-ba86650b9cf5)

(Splash Screen)

![CalibrationScreen](https://github.com/Code-Munkeys/TemperatureLogger/assets/1928315/dbb6d0c4-f885-4447-8070-91ca05a930c5)

(Calibration Screen)

![MainScreen](https://github.com/Code-Munkeys/TemperatureLogger/assets/1928315/b99f41a5-70cb-4808-b770-5c9e0655f9a0)

(Main Screen)

![TemperatureGraph](https://github.com/Code-Munkeys/TemperatureLogger/assets/1928315/96b69977-865b-4812-9188-341714147959)

(Example CSV Test Data)

Usage:

When the Splash screen has displayed for 5 seconds, the User will be presented with a Calibration screen. The User can press the GREEN Button to increase and the RED Button to decrease the required temperature adjustment amount, when finished the User simply presses the BLUE Button to continue.

When the Temperature screen is displayed the User can perform the following functions via the assigned inputs. RED Button: Toggle Logging On / Off, GREEN Button: Toggle °C / °F, BLUE Button: Toggle OLED display On / Off. When the OLED Display is in the off state, the Pico onboard LED is illuminated to show the temperature logger is on.

POTENTIOMETER: Interval time <Left 60s> <Center 30s> <Right 15s> (s = seconds)

When the logging CSV file is created and appended to, the filename suffix datetime stamp is set to the following format... [temperatureYYYY-MM-DD_HHMMSS.csv]. If no external RTC is installed then an additional random suffix number can be added to the filename... [temperatureYYYY-MM-DD_HHMMSS_01234567.csv]

Whenever the logging CSV file is being updated, the red LED will illuminate for half a second.
