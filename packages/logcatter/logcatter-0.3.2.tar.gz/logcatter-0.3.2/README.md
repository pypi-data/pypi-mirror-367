# Logcatter 🐱

[See logcatter from PyPI](https://pypi.org/project/logcatter/)

**Brings the familiar convenience and readability of Android's Logcat to your Python projects.**

Tired of complex logger configurations? `Logcatter` lets you use intuitive methods like `Log.d()` and `Log.i()` right away. It automatically tags logs with the calling filename, dramatically speeding up your debugging workflow.

## ✨ Key Features

*   **☕ Android Logcat Style:** Get beautiful, easy-to-read logs formatted as `yyyy-MM-dd HH:mm:ss.SSS [D/tag] message`.
*   **🏷️ Automatic Tagging:** The name of the source file (`main.py`) that calls the log is automatically used as the tag, so you can instantly identify the origin of a log.
*   **🎨 Colored Output:** Log levels (Debug, Info, Warning, Error) are color-coded for enhanced visual recognition.
*   **🚀 Concise API:** Use intuitive methods nearly identical to the Android `Log` class: `Log.d()`, `Log.i()`, `Log.w()`, and `Log.e()`.
*   **🔧 Zero Configuration:** Works right out of the box after installation with no extra setup required.

## 📦 Installation

```shell
pip install logcatter
```

## 🚀 Quick Start

Just import the `Log` class into your project and call `Log.init()` first and `Log.dispose()` last of your code.

```python
from logcatter import Log

Log.init()

Log.d("This is log!!")
Log.set_level(Log.WARNING)  # Hide DEBUG, INFO level logs
Log.i("This is info!!")  # You cannot see this because you set the minimum level `WARNING`
Log.e("ERROR!!!", e=ValueError())  # You can log the caught exception/error with argument `e`
Log.f("FATAL ERROR", s=True)  # You can log the stacktrace with flag `s`

Log.dispose()
```

### Using with other's code

Some library or codes are using `print()`. And the format of `Log` is not applied basically to this. In this case, you can use `Log.redirect` as a context manager.

```python
import sys
from logcatter import Log
Log.init()

with Log.redirect(
    stdout=Log.VERBOSE,
    stderr=None,
):
    print("Some message")
    sys.stderr.write("stderr message\n")

Log.dispose()
```

Output:
```txt
1970-01-01 00:00:00 000 [V/<stdin>] Some message
stderr message
```

`stdout` outputs (include `print`) will be handled a VERBOSE level. You can change this by parameter `stdout`. If the value is `None`, `Log.redirect` does not redirect `stdout`.

Same as `stdout`, you can redirect `stderr` outputs by parameter `stderr`. But the default value is `None`.

If internal print codes use CR (carriage return) to rewrite last line such as [tqdm](https://github.com/tqdm/tqdm), the `Log` style will not be applied.

### Save logs

You can save the log messages using just a single line.

```python
from logcatter import Log
Log.init()

Log.i("This will not be saved")
Log.save("path of file")
Log.i("Message saved")

Log.dispose()
```

Saved log file:

```txt
Message saved
```

### Multiprocessing

You can use `Log` in the multiprocessing with calling `Log.init_worker()`. (Don't forget the brackets!)

```python
from logcatter import Log
import multiprocessing

Log.init()

with multiprocessing.Pool(processes=2, initializer=Log.init_worker()) as pool:
    Log.i("Some message")

Log.dispose()
```

## 💻 Output Example

**Visual Studio Code**

![visual-studio-code-output-example](/docs/images/vsc.png)

**PyCharm**

![pycharm-output-exmaple](/docs/images/pycharm.png)

**PowerShell 7 on Windows Terminal**

![pwsh7-wt-output-example](/docs/images/powershell.png)
