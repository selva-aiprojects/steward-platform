import socketio
import asyncio

async def test_socket_enrichment():
    sio = socketio.AsyncClient()
    
    @sio.on('market_update')
    def on_market_update(data):
        print(f"\n[RECEIVED TICKER UPDATE] {data.get('exchange', '???')}:{data.get('symbol', '???')}")
        print(f"Price: {data.get('price')} | Change: {data.get('change')}%")
        if 'exchange' in data:
            print("✅ Exchange data present.")
        else:
            print("❌ Missing exchange data.")

    @sio.on('steward_prediction')
    def on_steward_prediction(data):
        print("\n[RECEIVED STEWARD PREDICTION]")
        expected = ['prediction', 'decision', 'confidence', 'signal_mix', 'risk_radar']
        missing = [f for f in expected if f not in data]
        if missing:
            print(f"❌ Missing fields: {missing}")
        else:
            print("✅ All high-fidelity metrics present.")
        
    try:
        print("Connecting to http://127.0.0.1:8000...")
        await sio.connect('http://127.0.0.1:8000')
        print("Waiting for broadcast (up to 30s)...")
        await asyncio.sleep(30)
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await sio.disconnect()

if __name__ == '__main__':
    asyncio.run(test_socket_enrichment())
