# The World in One Page — 19 November 2026

This entry is a one‑page newspaper front page summarising the eight stories that defined Thursday 19 November 2026, drawn entirely with Pillow. The entry program itself only validates and copies the finished image.

## The eight stories

1. **GTA VI launches worldwide at midnight after a 13‑year wait, with pre‑orders over $1.5 billion and a 99/100 critic score** -  
2. **Trump, Xi and Putin hold their first trilateral meeting in Shenzhen** -  
3. **Hakeem Jeffries is set to become the first Black Speaker of the U.S. House** -  
4. **The U.S. and Iran trade fire again as Iran widens its attacks to Kuwait and Bahrain** -  
5. **NASA's Voyager 1 probe reaches one light‑day from Earth after 49 years in space** -  
6. **Cyclone Akvan bears down on India's east coast between Machilipatnam and Puri** -  
7. **The EU proposes a 45 billion € loan for Ukraine, to be repaid from Russian reparations** -  
8. **Nvidia enters a new era after Jensen Huang quits, with its acting chief promising earlier pay rises** -  

## Layout

The page features a masthead “THE WORLD” with the date line, a large lead story on the GTA VI launch accompanied by a neon Vice City illustration, a second row containing the Shenzhen summit and the Jeffries speakership, a third row with the Gulf conflict, Voyager 1, and Cyclone Akvan, and an “ALSO TODAY” strip that highlights the EU loan and Nvidia story.

## How it is built

The draw script (run at build time only, not part of the graded run) creates `entry.png` (1024 × 1024 px, ≈ 123 KB) with Pillow using paper `#f7f3ea`, ink `#111111`, red `#b91c1c` and navy `#1e3a5f`. It is fully deterministic, so two executions produce byte‑identical output. The entry program `main.py` (standard library only) validates the image (PNG, ≤ 1 MiB, ≤ 1024 × 1024) and copies it to the output directory given by `MAKEFUN_OUTPUT_DIR` or `/output`.

## Run

```sh
# Regenerate the image at build time
python draw.py   # produces entry.png

# Run the graded program to copy the image to the output directory
python main.py
```
