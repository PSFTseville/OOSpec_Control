# OOSpec_Control
Control scripts for OceanOptics spectrometers. If connected through OceanView it does not work!!!

For manual measurement just type:

```php
python main.py %shot_filename %number_of_measurements %integration_time
```
The following command sets the computer to listening mode, and waits for a TCPIP package to tell them to prepare, trigger and save the file:

```php
python main.py %shot_filename %number_of_measurements %integration_time
```

These are the commands:

Prepares the spectrometer to measure and, if a number is added, sets the integration time: 
```php
PREP #integrationtime(us)
```
Triggers the spectrometer and sets the number of captures (10 if not provided):
```php
TRIG #numberofcaptures
```
Saves the data to a json file to a certain file:
```php
SAVE #filename
```

