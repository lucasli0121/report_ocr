from datetime import datetime
import logging
import os
import logging.config
import threading
import unittest
import yaml
from nicegui import ui,app,events
from nicegui.elements.upload_files import FileUpload
from dao.recognize_info_dao import RecognizeInfoDao, RecognizeResult, RecognizeType
import utils.global_vars as g

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
"""
# @function: handle_common_upload_file
# @description: 处理通用文件上传

"""
async def handle_common_upload_file(files: list[FileUpload], type: int) -> bool:
    for file in files:
        # event.content 是文件的二进制内容
        file_content = await file.read()
        save_dir = './static/uploads/'
        os.makedirs(save_dir, exist_ok=True)  # 创建目录（若不存在）
        file_name = file.name
        save_path = os.path.join(save_dir, file_name)
        with open(save_path, 'wb') as f:
            f.write(file_content)
        # 通过 gRPC 进行发票识别
        recognize_dao = RecognizeInfoDao()
        recognize_dao.file_name = file_name
        recognize_dao.type = type
        recognize_dao.result = RecognizeResult.Waiting.value
        recognize_dao.retry_count = 0
        recognize_dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dt = recognize_dao.to_db()
        res, value = g.my_db.add_recognize_info(dt)
        if res is False:
            return False
    return True

'''
    打开发票 OCR 对话框
'''
def open_ocr_invoice_dialog():
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2 h-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full h-[60%] mt-5 place-content-between'):
            async def handle_upload_invoice_ocr(e: events.MultiUploadEventArguments):
                res = await handle_common_upload_file(e.files, RecognizeType.InvoiceType.value)
                if not res:
                    ui.notify("保存到数据库失败", color='negative')
                dialog.close()
            ui.upload(label="请选择批量上传文件", multiple=True) \
                .props('flat batch accept=".pdf"') \
                .classes('size-full') \
                .on_multi_upload(handle_upload_invoice_ocr)
        with ui.row().classes('w-full place-content-center') as loading_row:
            ui.icon('autorenew').classes('animate-spin text-4xl text-blue-500')
            ui.label("识别仅支持 CPU 识别，识别速度较慢，请耐心等待...")
            loading_row.visible = False
        with ui.row().classes('w-full h-[30%] place-content-center'):
            ui.button('关闭', on_click=lambda: dialog.close()).classes('w-1/3')

    dialog.open()

'''
    打开完税凭证 OCR 对话框
'''
def open_ocr_certificate_dialog():
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2 h-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full h-[60%] mt-5 place-content-between'):
            async def handle_upload_ocr(e: events.MultiUploadEventArguments):
                res = await handle_common_upload_file(e.files, RecognizeType.TaxProofType.value)
                if not res:
                    ui.notify("保存到数据库失败", color='negative')
                dialog.close()
            ui.upload(label="请选择批量上传文件", multiple=True) \
                .props('flat batch accept=".pdf"') \
                .classes('size-full') \
                .on_multi_upload(handle_upload_ocr)
        with ui.row().classes('w-full place-content-center') as loading_row:
            ui.icon('autorenew').classes('animate-spin text-4xl text-blue-500')
            ui.label("识别仅支持 CPU 识别，识别速度较慢，请耐心等待...")
            loading_row.visible = False
        with ui.row().classes('w-full place-content-center'):
            ui.button('关闭', on_click=lambda: dialog.close()).classes('w-1/3')

    dialog.open()

def start_ocr_scheduler_thread():
    g.ocr_mgr.start()

if __name__ in {"__main__", "__mp_main__"}:
    init_logger()
    thread = threading.Thread(target=start_ocr_scheduler_thread,daemon=True)
    thread.start()
    open_ocr_invoice_dialog()
    ui.run(language='zh-CN',
        host='0.0.0.0',
        port=8084,
        reconnect_timeout=120)
    # g.ocr_mgr.stop()
    # thread.join()