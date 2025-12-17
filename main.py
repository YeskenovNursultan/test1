from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# --- Хранилище состояния ---
system_state = {
    "temperature": 0.0,
    "relay_on": False
}

class EspData(BaseModel):
    temperature: float

# --- УЛУЧШЕННЫЙ ИНТЕРФЕЙС (HTML/CSS/JS) ---
html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Умный Дом</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-color: #ffffff;
            --accent-off: #3a3a3a;
            --accent-on: #4CAF50; /* Зеленый */
            --accent-on-glow: rgba(76, 175, 80, 0.4);
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            /* Запрет выделения текста для ощущения "приложения" */
            -webkit-user-select: none;
            user-select: none; 
        }

        .container {
            background-color: var(--card-bg);
            width: 90%;
            max-width: 400px;
            padding: 40px 20px;
            border-radius: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        h1 {
            font-weight: 300;
            font-size: 1.2rem;
            opacity: 0.7;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* Блок температуры */
        .temp-box {
            position: relative;
        }
        
        .temp-val {
            font-size: 5rem;
            font-weight: 600;
            line-height: 1;
        }
        
        .temp-unit {
            font-size: 1.5rem;
            vertical-align: super;
            opacity: 0.6;
        }

        /* Кнопка-переключатель */
        .power-btn {
            background-color: var(--accent-off);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 25px;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            -webkit-tap-highlight-color: transparent; /* Убирает синий квадрат при тапе на Android */
        }

        /* Состояние: нажатая кнопка (эффект нажатия) */
        .power-btn:active {
            transform: scale(0.96);
        }

        /* Состояние: ВКЛЮЧЕНО */
        .power-btn.active {
            background-color: var(--accent-on);
            box-shadow: 0 0 20px var(--accent-on-glow);
        }

        .icon {
            font-size: 1.5rem;
        }

        /* Индикатор связи */
        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #555;
            border-radius: 50%;
            margin: 0 auto;
            transition: background 0.3s;
        }
        .status-dot.online { background-color: #4CAF50; }

    </style>
</head>
<body>

    <div class="container">
        <h1>Температура</h1>
        
        <div class="temp-box">
            <span id="temp_val" class="temp-val">--</span>
            <span class="temp-unit">°C</span>
        </div>

        <button id="relay_btn" class="power-btn" onclick="toggleRelay()">
            <span id="btn_icon" class="icon">🔌</span>
            <span id="btn_text">Включить</span>
        </button>
        
        <div id="connection_status" class="status-dot" title="Статус соединения"></div>
    </div>

    <script>
        // Функция вибрации (работает на Android)
        function vibratePhone() {
            if (navigator.vibrate) {
                navigator.vibrate(50); // Вибрация 50мс
            }
        }

        async function updateData() {
            try {
                let response = await fetch('/api/status');
                if (!response.ok) throw new Error("Нет связи");
                
                let data = await response.json();
                
                // Обновляем температуру
                document.getElementById('temp_val').innerText = data.temperature.toFixed(1);
                
                // Обновляем кнопку
                let btn = document.getElementById('relay_btn');
                let btnText = document.getElementById('btn_text');
                let btnIcon = document.getElementById('btn_icon');

                if (data.relay_on) {
                    btn.classList.add("active");
                    btnText.innerText = "Включено";
                    btnIcon.innerText = "⚡";
                } else {
                    btn.classList.remove("active");
                    btnText.innerText = "Выключено";
                    btnIcon.innerText = "🔌";
                }
                
                // Индикатор "онлайн"
                document.getElementById('connection_status').classList.add('online');
                
            } catch (e) {
                document.getElementById('connection_status').classList.remove('online');
            }
        }

        async function toggleRelay() {
            vibratePhone(); // Тактильный отклик
            await fetch('/api/toggle', { method: 'POST' });
            updateData();
        }

        setInterval(updateData, 2000);
        updateData();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return html_content

@app.get("/api/status")
async def get_status():
    return system_state

@app.post("/api/toggle")
async def toggle_relay():
    system_state["relay_on"] = not system_state["relay_on"]
    return {"status": "ok", "new_state": system_state["relay_on"]}

@app.post("/api/esp-update")
async def esp_update(data: EspData):
    system_state["temperature"] = data.temperature
    return {"relay_target": system_state["relay_on"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)