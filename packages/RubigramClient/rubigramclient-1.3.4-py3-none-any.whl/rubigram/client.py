from rubigram.types import Update, InlineMessage
from rubigram.method import Method
from aiohttp import web

class Client(Method):
    def __init__(self, token: str):
        self.messages_handler = []
        super().__init__(token)
        
    def on_message(self, *filters):
        def decorator(func):
            async def wrapped(client, update):
                if all(f(update) for f in filters):
                    await func(client, update)
            self.messages_handler.append(wrapped)
            return func
        return decorator
    
    async def update(self, data: dict):
        event = Update.read(data["update"]) if data.get("update") else InlineMessage.read(data["inline_message"])
        for handler in self.messages_handler:
            await handler(self, event)
    
    def run(self):
        routes = web.RouteTableDef()
        @routes.post("/receiveUpdate")
        @routes.post("/receiveInlineMessage")
        async def webhook(request):
            data = await request.json()
            await self.update(data)
            return web.json_response({"status": "ok"})
        app = web.Application()
        app.add_routes(routes)
        web.run_app(app, host="0.0.0.0", port=5000)