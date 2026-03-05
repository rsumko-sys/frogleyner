import { Telegraf } from "telegraf"
import fs from "fs"
import fetch from "node-fetch"
import dotenv from "dotenv"

dotenv.config()

const bot = new Telegraf(process.env.BOT_TOKEN)

const STATE_FILE = "./frog_states.json"

function loadStates() {
  if (!fs.existsSync(STATE_FILE)) {
    const defaultStates = [
      "жаба пьет пиво",
      "жаба пишет код",
      "жаба злится на баг",
      "жаба расследует преступление",
      "жаба командует армией",
      "жаба смотрит апокалипсис",
      "жаба философствует",
      "жаба спит в болоте",
      "жаба танцует рейв",
      "жаба в режиме хаоса"
    ]
    fs.writeFileSync(STATE_FILE, JSON.stringify(defaultStates, null, 2))
    return defaultStates
  }
  return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"))
}

function saveStates(states) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(states, null, 2))
}

let frogStates = loadStates()

function randomState() {
  return frogStates[Math.floor(Math.random() * frogStates.length)]
}

bot.start((ctx) => {
  ctx.reply("🐸 Жаба проснулась. Болото онлайн.")
})

bot.command("frog", (ctx) => {
  ctx.reply("🐸 Состояние: " + randomState())
})

bot.command("states", (ctx) => {
  ctx.reply("Список состояний:\n\n" + frogStates.join("\n"))
})

bot.command("frog_add", (ctx) => {
  const text = ctx.message.text.replace("/frog_add ", "").trim()
  if (!text) {
    ctx.reply("Напиши состояние после команды.")
    return
  }

  frogStates.push(text)
  saveStates(frogStates)

  ctx.reply("Новое состояние добавлено.")
})

bot.command("frog_random", (ctx) => {
  ctx.reply("🎲 " + randomState())
})

bot.command("frog_generate", (ctx) => {
  const generated = [
    "жаба пишет стартап",
    "жаба спорит с искусственным интеллектом",
    "жаба читает древние манускрипты",
    "жаба запускает ракеты",
    "жаба контролирует болото"
  ]

  frogStates.push(...generated)
  saveStates(frogStates)

  ctx.reply("Жаба придумала новые состояния.")
})

bot.command("frog_clear", (ctx) => {
  frogStates = []
  saveStates(frogStates)
  ctx.reply("Болото очищено.")
})

bot.command("ping", (ctx) => {
  ctx.reply("pong 🐸")
})

bot.command("status", (ctx) => {
  ctx.reply("система работает\nжаба жива")
})

bot.command("weather", async (ctx) => {
  const city = (ctx.message.text.replace("/weather", "").trim() || "Kyiv").replace(/^\s+/, "") || "Kyiv"
  const apiKey = process.env.OPENWEATHER_API_KEY || process.env.WEATHER_API_KEY

  if (!apiKey) {
    ctx.reply("Не задан OPENWEATHER_API_KEY в .env")
    return
  }

  const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${apiKey}&units=metric`

  try {
    const res = await fetch(url)
    const data = await res.json()

    if (data.cod !== 200) {
      ctx.reply("Город не найден или ошибка API.")
      return
    }

    const temp = data.main.temp
    const desc = data.weather[0].description
    ctx.reply(`Погода в ${data.name}\n${temp}°C\n${desc}`)
  } catch {
    ctx.reply("не получилось получить погоду")
  }
})

bot.command("fortune", (ctx) => {
  const fortunes = [
    "болото принесет удачу",
    "сегодня день хаоса",
    "жаба видит новые возможности",
    "в болоте зреют великие планы",
    "всё пойдет странно но правильно"
  ]

  const f = fortunes[Math.floor(Math.random() * fortunes.length)]
  ctx.reply("🔮 " + f)
})

bot.command("joke", (ctx) => {
  const jokes = [
    "жаба написала код без багов. никто не поверил.",
    "жаба оптимизировала код. теперь он не работает.",
    "жаба нашла баг. это был не баг а фича."
  ]

  const j = jokes[Math.floor(Math.random() * jokes.length)]
  ctx.reply(j)
})

bot.command("map", (ctx) => {
  ctx.reply("📍 отправь координаты: /coords 50.45 30.52")
})

bot.command("coords", (ctx) => {
  const parts = ctx.message.text.split(/\s+/)

  if (parts.length < 3) {
    ctx.reply("пример: /coords 50.45 30.52")
    return
  }

  const lat = parts[1]
  const lon = parts[2]
  const link = `https://www.google.com/maps?q=${lat},${lon}`

  ctx.reply("карта:\n" + link)
})

bot.command("secret", (ctx) => {
  ctx.reply("🕳 секрет болота активирован")
})

bot.launch()

process.once("SIGINT", () => bot.stop("SIGINT"))
process.once("SIGTERM", () => bot.stop("SIGTERM"))
