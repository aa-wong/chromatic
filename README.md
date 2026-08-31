# Chromatic

*An experimental piece that translates an original composition into light.* (August 2023)

Chromatic plays on the word's two meanings — the twelve-tone musical scale, and colour. An
original composition is written to MIDI, each of the twelve pitch classes is mapped to a
distinct hue, and note events are resolved to RGB values. The colour sequence is played back
through a moving light source and captured in a single long-exposure photograph, so the whole
piece lands as one light painting: time becomes extent, and a sequence you had to wait through
becomes a shape you take in all at once.

**Techniques:** light painting, long-exposure photography, MIDI, music visualization, colour
theory, creative coding, LEDs.

**Credits:** Composition, MIDI-to-colour mapping & software — Aaron Wong-Ellis. Collaborating
artist — Kevin Meric (industrial designer, artist, photographer).

More: <https://aaronwongellis.com/projects/chromatic>

## What's in this repo

| File | Purpose |
| --- | --- |
| `midi2rgb.py` | Core conversion: `convert_midi_to_rgb(file)` and `convert_midi_to_rgb2(file)` return a list of `(r, g, b)` tuples from a MIDI file. |
| `midi2rgb.ipynb` | Notebook the module was exported from. |
| `Example.ipynb` | Worked example / colour sequence previews. |
| `song.mid`, `song2.mid` | Source compositions. |

Quick check on any machine:

```bash
python3 -c "from midi2rgb import convert_midi_to_rgb; print(convert_midi_to_rgb('song.mid')[:8])"
```

## Running on a Raspberry Pi

Tested shape: Pi 4 / Pi 5 or Zero 2 W, Raspberry Pi OS (Bookworm, 64-bit), driving a WS2812B
("NeoPixel") strip on **GPIO18**.

### 1. System packages

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git libopenblas-dev
```

### 2. Get the code and create a virtualenv

```bash
git clone <this-repo> chromatic && cd chromatic
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install mido python-rtmidi
```

`mido` is all `midi2rgb.py` needs. `python-rtmidi` is only required if you want to read from a
live MIDI device rather than a `.mid` file.

### 3. LED driver

```bash
pip install rpi_ws281x adafruit-circuitpython-neopixel
```

WS2812 timing on the Pi uses the PWM peripheral, which needs root — run playback with `sudo`,
and note it conflicts with the onboard analog audio. If you need audio and LEDs at once, drive
the strip over SPI (`adafruit-circuitpython-neopixel-spi` on GPIO10/MOSI) and enable SPI with
`sudo raspi-config` → Interface Options → SPI.

### 4. Play the sequence

Save as `play.py`:

```python
import time
import board, neopixel
from midi2rgb import convert_midi_to_rgb

NUM_PIXELS = 60
HOLD = 0.12  # seconds per note event — this sets the length of the light trail

pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, auto_write=False, brightness=0.5)

for r, g, b in convert_midi_to_rgb("song.mid"):
    pixels.fill((r, g, b))
    pixels.show()
    time.sleep(HOLD)

pixels.fill((0, 0, 0))
pixels.show()
```

```bash
sudo .venv/bin/python play.py
```

Open the camera shutter (bulb mode, low ISO, small aperture) in a dark room, start `play.py`,
move the strip through the frame for the length of the piece, then close the shutter. `HOLD`
times the total run: `len(colors) * HOLD` seconds — match it to your exposure.

## Running on an NVIDIA Jetson

Tested shape: Jetson Nano / Orin Nano, JetPack (Ubuntu), 40-pin header.

### 1. System packages and code

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
git clone <this-repo> chromatic && cd chromatic
python3 -m venv .venv && source .venv/bin/activate
pip install mido python-rtmidi
```

The conversion step is pure Python and runs unchanged.

### 2. LED output — read this before wiring

The Jetson has **no equivalent of the Pi's PWM/DMA WS2812 driver**; `rpi_ws281x` will not work.
Bit-banging from Linux userspace does not hold WS2812's ~800 kHz timing reliably. Pick one:

- **SPI (recommended).** Use `Jetson.GPIO` + Adafruit Blinka and drive the strip from the SPI
  MOSI pin (pin 19 on the 40-pin header):

  ```bash
  sudo pip3 install Jetson.GPIO
  sudo usermod -aG gpio $USER   # log out and back in
  pip install Adafruit-Blinka adafruit-circuitpython-neopixel-spi
  ```

  ```python
  import board, neopixel_spi
  pixels = neopixel_spi.NeoPixel_SPI(board.SPI(), 60, brightness=0.5, auto_write=False)
  ```

  On Nano-class boards SPI may need enabling first: `sudo /opt/nvidia/jetson-io/jetson-io.py`.

- **Offload to a microcontroller.** Send RGB frames over USB serial to a Pico/Arduino that owns
  the strip. Most robust option, and it keeps LED timing off a preemptible Linux box.

- **Use APA102/SK9822 strips instead.** They carry their own clock line, so ordinary SPI drives
  them with no timing constraints (`adafruit-circuitpython-dotstar`).

Otherwise the playback loop is identical to the Pi version above — swap the `pixels` object for
the one your chosen path creates, and drop the `sudo` if your user is in the `gpio` group.

## Wiring notes (both boards)

- Power the strip from a separate 5 V supply sized for the strip, not the board's 5 V rail.
- Tie the strip's ground to the board's ground.
- Both boards output 3.3 V logic; WS2812 wants 5 V data. A level shifter (74AHCT125) makes long
  runs reliable.
- Add a ~1000 µF capacitor across the strip's 5 V/GND and a 330–470 Ω resistor in series with
  the data line.
