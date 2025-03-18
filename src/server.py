import tornado.ioloop
import tornado.web
import tornado.gen
import io
import sys
from main import run_hedge_fund

# Add this at the bottom of the file
# 重定向标准输出以捕获打印内容
class PrintCapture:
    def __init__(self):
        self.buffer = io.StringIO()
        self.original_stdout = sys.stdout

    def __enter__(self):
        sys.stdout = self.buffer
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout

    def get_output(self):
        return self.buffer.getvalue()

class HedgeFundHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        ticker = self.get_argument('ticker')
        start_date = self.get_argument('start-date', None)
        end_date = self.get_argument('end-date', None)
        show_reasoning = self.get_argument('show-reasoning', 'false').lower() == 'true'
        num_of_news = int(self.get_argument('num-of-news', 5))
        initial_capital = float(self.get_argument('initial-capital', 100000.0))
        initial_position = int(self.get_argument('initial-position', 0))

        portfolio = {
            "cash": initial_capital,
            "stock": initial_position
        }

        with PrintCapture() as capture:
            result = run_hedge_fund(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                portfolio=portfolio,
                show_reasoning=show_reasoning,
                num_of_news=num_of_news
            )

        output = capture.get_output()
        self.write(f'<pre>{output}</pre>')
        self.write(f'<pre>Final Result: {result}</pre>')

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/hedge_fund", HedgeFundHandler),
    ])
    app.listen(8888)
    print("Server is running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()