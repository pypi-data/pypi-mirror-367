# Fars TTS 🇮🇷
Use pertian tts so easy.
## Requirements
- edge-tts
- asyncio

## How to install❓
```shell script
$ pip install fars_tts
```

## How to use it❓
```shell script
$ pip install edge-tts
$ pip install asyncio
```

### Male voice:
```python
import asynico
import fars_tts

asynico.run(fars_tts.male_tts(text="سلام. این یک آزمایش است."), output="output.mp3")
```
### Female voice:
```python
import asynico
import fars_tts

asynico.run(fars_tts.female_tts(text="سلام. این یک آزمایش است."), output="output.mp3")
```

### All rights reserved.
&copy; Amirali Mahdavi