# Robotika

Megtanítunk robotot építeni, és programozni is, a folyamat elejétől a legvégéig. Bemutatjuk, hogyan lehet egy robotot megtervezni, összeszerelni, lesz szó irányítástechnikáról, mindenféle szenzorról és a környezetre való reagálásról, több robot összehangolásáról. A tábor során mindenki összerak egy saját robotot, amit utána meg is tarthat. Természetesen elérhető az egész tábor során a diákkör teljes robotikai arzenálja, beleértve számtalan MicroBit-et, és Rolandot a lánctalpas pokolgépet.

Örülünk, ha van előzetes tapasztalatod, de egyáltalán nem szükséges, minden tudnivalót el fogunk mondani. Mivel a teljes program eltér az eddigiekről, szívesen látjuk azokat is, akik tavaly is voltak robotika foglalkozáson.
Mivel a saját robotodat a tábor után hazaviszed, az alkatrészek ára miatt a foglalkozás kb. 15 000Ft extra költséggel jár a tábor alap ára mellé.

Bácskai Kristóf és Varga Benedek

## Szükséges szoftver

Kezdőknek [Thonny](https://thonny.org) ajánlott, haladóknak [VSCode](https://code.visualstudio.com).

## Type hints

Install python type hints (make sure to configure them in your editor):

```bash
pip install -U micropython-rp2-pico_w-stubs --no-user --target ./typings
```

To remove missing module source warnings in vscode put this into [.vscode/settings.json](./.vscode/settings.json):

```json
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingModuleSource": "none"
    }
}
```

## Running the code

Install [MicroPython remote](https://docs.micropython.org/en/latest/reference/mpremote.html) (with pip):

```bash
pip install --user mpremote --break-system-packages
```

Upload the code (press Ctrl+D to exit the repl and see program output):

```bash
mpremote a0 + fs cp code/* config.json :. + repl
```

## Color plotter

```bash
c ; mpremote a0 + fs cp code/* config.json :. + reset && sleep 1 && sudo cat /dev/ttyACM0 | awk '// { } /.+/ { print; fflush(); } /done/ { exit }' | tee testing/output.txt && py plot_data.py
```
