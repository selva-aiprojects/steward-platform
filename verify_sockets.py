import socketio
import asyncio

async def test_socket_updates():
    sio = socketio.AsyncClient()

    @sio.on('connect')
    def on_connect():
        print('✅ Connected to backend socket.')
        sio.emit('join_stream', {'role': 'USER'})

    @sio.on('market_update')
    def on_market_update(data):
        print(f'📈 Received Market Update: {data["symbol"]} - {data["price"]} ({data["change"]})')
        print(f'   AI Projection: {data.get("projection")}')

    @sio.on('steward_prediction')
    def on_steward_prediction(data):
        print(f'🧠 Received Steward Intelligence: {data["prediction"]}')

    print("🔗 Connecting to http://localhost:8000 ...")
    connected = False
    for i in range(5):
        try:
            await sio.connect('http://localhost:8000')
            connected = True
            break
        except Exception as e:
            print(f"⏳ Attempt {i+1} failed, retrying in 2s...")
            await asyncio.sleep(2)
            
    if not connected:
        print("❌ Socket Error: Could not connect after 5 attempts.")
        return

    try:
        print("⏳ Waiting 15 seconds for live events...")
        await asyncio.sleep(15)
    finally:
        await sio.disconnect()

if __name__ == '__main__':
    asyncio.run(test_socket_updates())
