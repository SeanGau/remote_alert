![image](https://github.com/user-attachments/assets/58139a50-a4a1-4b1f-b598-641be7e9b740)

# About
這是一個透過 websocket 方式可以遠端遙控的倒數計時器，也提供簡易的文字訊息提醒功能。

This is a countdown timer that can be remotely controlled via WebSocket and also provides a simple text reminder feature.

# 如何使用
1. 造訪 https://ra.seangau.xyz
2. 自動轉址至隨機字串
3. 在其他裝置打開 Viewer 網址
4. 在 Sender 開始倒數！

# How to Use
1. Visit https://ra.seangau.xyz
2. You will be automatically redirected to a random string URL.
3. Open the Viewer link on another device.
4. Start the timer on the Sender!

# Self Host
1. setup enviroment with pipenv (`pipenv sync`)
2. add `app/config.py`
3. `pipenv run fastapi run app`
