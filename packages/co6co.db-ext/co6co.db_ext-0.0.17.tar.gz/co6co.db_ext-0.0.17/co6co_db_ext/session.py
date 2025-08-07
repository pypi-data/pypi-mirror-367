from co6co.utils import log
from sqlalchemy.ext.asyncio import AsyncSession
from .db_session import db_service, connectSetting
from co6co.task.thread import ThreadEvent


class dbBll:
    def __init__(self, *,  db_settings: connectSetting = {}) -> None:
        self.t = ThreadEvent()
        if not db_settings:
            raise Exception("db_settings,参数不能为空")

        self.db_settings = db_settings
        self.session = None
        self.service = None
        self.t.runTask(self.create_db)
        self.closed = False

    async def create_db(self):
        # current_loop = asyncio.get_event_loop()
        # print(f"主函数中使用的事件循环: {current_loop} (ID: {id(current_loop)}),{id(self.t.loop)}")
        _service: db_service = db_service(self.db_settings)
        self.session: AsyncSession = _service.async_session_factory()
        self.service = _service

    def run(self, task, *args, **argkv):
        data = self.t.runTask(task, *args, **argkv)
        return data

    def close(self):
        self.closed = True
        self.t.runTask(self.session.close)
        self.t.runTask(self.service.engine.dispose)
        self.t.close()

    def __str__(self):
        return f'{self.__class__}'

    def __del__(self) -> None:
        try:
            if not self.closed:
                self.t.run(self.close)

        except Exception as e:
            log.warn("__del___ error", e)
            pass
