# Encoder

## Hall sensors


## [Pulse counting algorithm](https://www.motioncontroltips.com/how-are-encoders-used-for-speed-measurement/)

Pulse counting uses a sampling period (t) and the number of pulses (n) that are counted over the sampling period 
to determine the average time for one pulse (t/n). Knowing the number of pulses per revolution (N) for the encoder,
the speed can be calculated:

$w = 2pi*n/Nt$

Where:

- w = angular speed (rad/s)

- n = number of pulses

- t = sampling period (s)

- N = pulses per rotation


At low speeds, the resolution of pulse counting is poor, so this method is best applied in high speed applications.

## [Pulse timing algorithm](https://www.motioncontroltips.com/how-are-encoders-used-for-speed-measurement/)

With the pulse timing method, a high-frequency clock signal is counted during one encoder period 
(the pitch, or interval between two adjacent lines or windows). The number of cycles of the clock signal (m), 
divided by the clock frequency (f), gives the time for the encoder period (the time for the encoder to rotate through one pitch). 
If the encoder PPR is denoted by N, the angular speed of the encoder is given by:

w = 2pi*f/Nm

Where:

- w = angular speed (rad/s)

- f = clock frequency (Hz)

- m = number of clock cycles

- N = pulses per rotation

## Calculating linear velocity

If we know the angular velocity of a wheel and its radius, we can easily calculate the linear velocity:

v = r * w

Where:

- r = radius (m)

1. Sorte sub
2. Esse eadem pectore ante
3. Oris seges victus in turis remotis
4. Una polluit deorum iterum obstantes Cepheus nec
5. Illum lux mentem in nunc supplex

Iove alis? Aure init umbrosa damnarat tenebras [error illis
nulla](http://www.ore-pavefactaque.net/iners-noxque), tandem.
