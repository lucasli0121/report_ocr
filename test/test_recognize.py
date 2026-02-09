import logging
import os
import logging.config
import yaml
from nicegui import ui,app,events
from recognize.invoice_recognize import parse_invoice_recognize_result_to_dao
from recognize.recognize_tools import recognize_invoice_pdf

def init_logger():
    cfg_path = 'cfg/log.yaml'
    if not os.path.exists("log"):
        os.makedirs("log")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            config = yaml.load(f, yaml.FullLoader)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s-%(name)s-%(lineno)s-%(levelname)s-%(message)s",
            filename="log/report_ocr.log",
            filemode="w",
        )
async def handle_upload_ocr(event: events.UploadEventArguments):
    # event.content 是文件的二进制内容
    file_content = await event.file.read()
    result_list = recognize_invoice_pdf(file_content)
    parse_response = parse_invoice_recognize_result_to_dao(result_list)
    print(parse_response)

with ui.dialog().props('persistent') as dialog:
    with ui.card().classes('w-1/3 h-1/3') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('size-full mt-5 place-content-between'):
            uploader = ui.upload(label="请选择批量上传设备文件", on_upload=handle_upload_ocr) \
                .props('flat accept=".pdf"') \
                .classes('size-full')

dialog.open()

ui.run(language='zh-CN',
    reconnect_timeout=120)
