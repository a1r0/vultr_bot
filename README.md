# vultr_bot

![GitHub last commit](https://img.shields.io/github/last-commit/a1r0/vultr_bot)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/a1r0/vultr_bot/Deploy)

This bot manages a specific VPS and supports basic operations like showing bandwidth data usage , server CPU and RAM usage , shutdown and startup operations. 

## Installation procedure on Linux and Windows

1. Setup python language on youre machine first.
2. Install a few dependencies _(will automate this in the future)_
    ```bash
    pip install -m requirements.txt
    ```
3. Create config.py file and fill it with the following lines:
    ```pyhton
    vultr_key = 'your vultr api key'
    telegram_api_key = 'yours telegram api key'
    instance_id = ''
    ```
    Example and detail are shared in the **vps_config_example.py** file
4. Copy this repository whatever you want and run the **bot.py** file. 

Telegram bot which works with VULTR API
Someday I'll fix everything here.
