import tornado.ioloop
import tornado.web
import tornado.gen
import io
import sys
from main import run_hedge_fund
import json
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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





executor = ThreadPoolExecutor(max_workers=10)  # 增加线程池大小
tasks = {}

class HedgeFundHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        # 渲染表单页面
        self.render("form.html")

    def post(self):
        ticker = self.get_argument("name", "")
        start_date = self.get_argument('start_date', None)
        end_date = self.get_argument('end_date', None)
        show_reasoning = self.get_argument('show-reasoning', 'false').lower() == 'true'
        num_of_news = int(self.get_argument('news_count', 5))
        initial_capital = float(self.get_argument('initial-capital', 100000.0))
        initial_position = int(self.get_argument('initial-position', 0))
        task_id = str(uuid.uuid4())
        tasks[task_id] = {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "show_reasoning": show_reasoning,
            "num_of_news": num_of_news,
            "initial_capital": initial_capital,
            "initial_position": initial_position,
            "status": "running",
            "result": None
        }
        logger.info(f"Starting task {task_id}")
        tornado.ioloop.IOLoop.current().run_in_executor(executor, self.run_hedge_fund_async, task_id)
        self.redirect(f"/redirect?task_id={task_id}&ticker={ticker}")

    def run_hedge_fund_async(self, task_id):
        try:
            # 获取任务参数
            logger.info(f"Task ID: {task_id}")
            task = tasks.get(task_id)
            if task is None:
                logger.error(f"Task {task_id} not found")
                return

            portfolio = {
                "cash": task["initial_capital"],
                "stock": task["initial_position"]
            }
            result = run_hedge_fund(
                ticker=task["ticker"],
                start_date=task["start_date"],
                end_date=task["end_date"],
                portfolio=portfolio,
                show_reasoning=task["show_reasoning"],
                num_of_news=task["num_of_news"]
            )
            # 更新任务状态和结果
            task["status"] = "finished"
            task["result"] = json.loads(result)
            logger.info(f"Task {task_id} finished")
        except Exception as e:
            logger.error(f"Error in task {task_id}: {e}")
            task["status"] = "error"
            task["result"] = str(e)


class RedirectHandler(tornado.web.RequestHandler):
    def get(self):
        task_id = self.get_argument("task_id", "")
        ticker = self.get_argument("ticker", "")
        if task_id not in tasks:
            self.write(json.dumps({"status": "not_found"}))
            return
        # 返回任务 ID 到前端
        self.render("result_async.html", task_id=task_id, ticker=ticker)


class ResultHandler(tornado.web.RequestHandler):
    def get(self):
        task_id = self.get_argument("task_id", "")
        if task_id in tasks:
            task = tasks[task_id]
            self.write(json.dumps({
                "status": task["status"],
                "result": task["result"]
            }))
        else:
            self.write(json.dumps({"status": "not_found"}))

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", HedgeFundHandler),
        (r"/redirect", RedirectHandler),
        (r"/result", ResultHandler),
    ], template_path="templates")
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()