import requests
import asyncio
import schedule
import time
from telegram import Bot


TELEGRAM_TOKEN = "7666815547:AAH1h9TEpJ8kSZrZur_IZeS8EqwULvseAtk"
CHAT_ID = "6252552504"


API_URL = "https://api.coingecko.com/api/v3/coins/markets"
API_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_asc",
    "per_page": 50,
    "page": 1,
    "sparkline": False,
}

MIN_MARKET_CAP = 10_000
MAX_MARKET_CAP = 10_000_000
MIN_VOLUME = 100_000
MAX_PRICE = 1.0

async def fetch_filtered_cryptos():
    """Busca criptomoedas e aplica filtros personalizados."""
    try:
        response = requests.get(API_URL, params=API_PARAMS)
        data = response.json()

        if response.status_code != 200:
            print("Erro na API CoinGecko: {}".format(response.status_code))
            return []

        
        filtered = [
            coin for coin in data
            if MIN_MARKET_CAP <= coin["market_cap"] <= MAX_MARKET_CAP
            and coin["total_volume"] >= MIN_VOLUME
            and coin["current_price"] <= MAX_PRICE
        ]
        return filtered
    except Exception as e:
        print("Erro ao buscar dados: {}".format(e))
        return []

async def send_filtered_crypto_updates():
    """Envia informações de criptomoedas filtradas para o Telegram."""
    try:
        cryptos = await fetch_filtered_cryptos()
        if not cryptos:
            await Bot(token=TELEGRAM_TOKEN).send_message(
                chat_id=CHAT_ID, text="Nenhuma moeda encontrada com os critérios especificados."
            )
            print("Nenhuma moeda encontrada com os critérios especificados.")
            return

        bot = Bot(token=TELEGRAM_TOKEN)

        for crypto in cryptos:
          
            message = (
                "🔹 *{}* ({})\n"
                "💰 Preço: ${:.2f}\n"
                "📈 Volume: ${:,}\n"
                "🌟 Market Cap: ${:,}\n"
                "🔗 [Mais detalhes](https://www.coingecko.com/en/coins/{})".format(
                    crypto["name"],
                    crypto["symbol"].upper(),
                    crypto["current_price"],
                    crypto["total_volume"],
                    crypto["market_cap"],
                    crypto["id"],
                )
            )

            
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            await asyncio.sleep(1)  
        print("Mensagens enviadas com sucesso!")
    except Exception as e:
        print("Erro ao enviar mensagens: {}".format(e))

def job():
    """Executa a tarefa do bot."""
    asyncio.run(send_filtered_crypto_updates())

if __name__ == "__main__":
    schedule.every(1).hour.do(job)
    print("Bot está rodando automaticamente... Pressione Ctrl+C para parar.")

    while True:
        schedule.run_pending()
        time.sleep(1)
