'''
Author: liguoqiang
Date: 2025-04-15 21:00:10
LastEditors: liguoqiang
LastEditTime: 2025-10-16 20:10:04
Description: 
'''
import re
import numpy as np
import pandas as pd
import os
import paddle
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes
import logging
from paddleocr import logger
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

fh = logging.FileHandler("/tmp/paddleocr.log")
logger.addHandler(fh)

paddle.device.set_device('cpu')
paddle.set_flags({'FLAGS_use_mkldnn': False})  # 关闭 MKLDNN
# 2. 初始化 OCR
ocr = PaddleOCR(
    use_angle_cls=True, 
    lang="ch")

def handle_upload_excel(event):
    # event.content 是文件的二进制内容
    import io
    file_content = io.BytesIO(event.content.read())
    df = pd.read_excel(file_content)
    print(df)

def extract_invoice_fields(texts: list, scores, boxes: list):
    """从 OCR 文本中提取发票关键字段"""
    result = {
        "购买方": '',
        "销售方": '',
        "规格": '',
        "数量": 0,
        "单价": 0,
        "税率": 0,
        "发票类型": 1,
        "发票号码": '',
        "开票日期": '',
        "红字发票": False,
        "蓝字发票号码": '',
        "金额": 0,
        "税额": 0,
        "含税额": 0,
        "发票内容": '',
        "备注": ''
    }

    money_x = 0
    tax_money_x = 0
    for idx, t in enumerate(texts):
        # 发票号码（8位数字）
        match = re.search(r"^发票号码[:：]?\s*([0-9]+)", t)
        if match:
            result["发票号码"] = match.group(1)

        #如何是红字发票，则搜索蓝字发票号码
        match = re.search(r"蓝字数电发票号码[:：]?\s*([0-9]+)", t)
        if match:
            result["蓝字发票号码"] = match.group(1)

        # 开票日期（YYYY年MM月DD日 或 YYYY-MM-DD）
        match = re.search(r"([0-9]{4}[年\-][0-9]{1,2}[月\-][0-9]{1,2}日?)", t)
        if match:
            result["开票日期"] = match.group(1)

        # 发票代码（10-12位数字）
        match = re.search(r"名称[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9\s\-_（）()]+)", t)
        if match:
            if boxes[idx][0][0] <= 100:  # x 坐标小于 100
                result["购买方"] = match.group(1)
            elif boxes[idx][0][0] >= 300:  # x 坐标大于 300
                result["销售方"] = match.group(1)

        match = re.search(r"项目名称", t)
        if match:
            x = 0
            y = boxes[idx][0][1] + 8 # 向下偏移 5
            name = ""
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] <= (x + 50) and b[0][1] >= y and b[0][1] <= (y + 40):
                    if name == "":
                        if len(texts[j]) > 12:
                            name = texts[j][:12]  # 只取前 12 个字符
                            result["规格"] = texts[j][12:]  # 其余部分作为规格
                        else:
                            name = texts[j]
                        y = b[0][1] + 15  # 继续向下偏移 15
                    else:
                        if len(texts[j]) > 12:
                            name = name + texts[j][:12]
                        else:
                            name = name + texts[j]
                        break
            result["发票内容"] = name
        match = re.search(r"规格", t)
        if match:
            x = boxes[idx][0][0] - 50  # 向左偏移 50
            y = boxes[idx][0][1] + 20 # 向下偏移 20
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] <= (x + 100) and b[0][1] >= y and b[0][1] <= (y + 30):
                    result["规格"] = texts[j]
                    break
        match = re.search(r"数量", t)
        if match:
            x = boxes[idx][0][0] - 50  # 向左偏移 50
            y = boxes[idx][0][1] + 10 # 向下偏移 10
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] <= (x + 100) and b[0][1] >= y and b[0][1] <= (y + 30):
                    value = texts[j].replace(',', '.')
                    number_list = value.split(' ')
                    number_str = '0'
                    if len(number_list) > 0:
                        number_str = number_list[0]
                    if len(number_list) > 1:
                        price_str = number_list[1]
                        result["单价"] = float(price_str)
                    result["数量"] = float(number_str)
                    break
        match = re.search(r"单价", t)
        if match:
            x = boxes[idx][0][0] - 50  # 向左偏移 50
            y = boxes[idx][0][1] + 10 # 向下偏移 10
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                    result["单价"] = float(texts[j].replace(' ', '').replace(',', '.'))
                    break

        match = re.search(r"金额", t)
        if match:
            money_x = boxes[idx][0][0] - 60  # 向左偏移 60
            y = boxes[idx][0][1] + 20 # 向下偏移 20
            for j, b in enumerate(boxes):
                if b[0][0] >= money_x and b[0][0] < (money_x + 100) and b[0][1] >= y and b[0][1] < (y + 40):
                    result["金额"] = float(texts[j].replace(' ', ''))
                    break

        match = re.search(r"红字发票", t)
        if match:
            result["红字发票"] = True

        match = re.search(r"(\d+?%)", t)
        if match:
            result["税率"] = match.group(1)
            # x = boxes[idx][0][0]
            # y = boxes[idx][0][1] + 40 # 向下偏移 50
            # for j, b in enumerate(boxes):
            #     if b[0][0] >= x and b[0][0] < (x + 300) and b[0][1] > y and b[0][1] < (y + 100):
            #         result["税率"] = texts[j]
            #         break
        match = re.search(r"税额", t)
        if match:
            tax_money_x = boxes[idx][0][0] - 50  # 向左偏移 150
            y = boxes[idx][0][1] + 20 # 向下偏移 50
            for j, b in enumerate(boxes):
                if b[0][0] >= tax_money_x and b[0][0] < (tax_money_x + 200) and b[0][1] >= y and b[0][1] < (y + 40):
                    result["税额"] = float(texts[j].replace(' ', ''))
                    break

        match = re.match(r"合|计|合计", t)
        if match:
            if money_x == 0:
                match = re.search(r"金额", t)
                if match:
                    money_x = boxes[idx][0][0] - 50  # 向左偏移 50
            x = money_x - 30  # 向左偏移 30
            y = boxes[idx][0][1] - 20
            if tax_money_x == 0:
                tax_money_x = 1500
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] < (y + 40):
                    money_txt = texts[j][1:]
                    money = float(money_txt.replace(',', '').replace(' ', ''))
                    if money != result["金额"]:
                        result["金额"] = money
                if b[0][0] >= tax_money_x and b[0][0] < (tax_money_x + 100) and b[0][1] >= y and b[0][1] < (y + 40):
                    money_txt = texts[j][1:]
                    money = float(money_txt.replace(',', '').replace(' ', ''))
                    if money != result["税额"]:
                        result["税额"] = money
                    break

        match = re.search(r"小写[)）]", t)
        if match:
            # amount_pattern = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?"
            amount_pattern = r".\d+(?:\.\d{1,2})?"
            match = re.search(r"小写[)）].\s*(" + amount_pattern + ")", t)
            if match:
                result["含税额"] = float(match.group(1))
            else:
                x = boxes[idx][0][0] + 30  # 向右偏移 100
                y = boxes[idx][0][1] - 10
                for j, b in enumerate(boxes):
                    if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                        result["含税额"] = float(texts[j][1:].replace(',', '').replace(' ', ''))
                        break

        match = re.search(r"备|注|备注", t)
        if match:
            x = boxes[idx][0][0] + 10  # 向右偏移 100
            y = boxes[idx][0][1] - 50
            remark = ""
            for j, b in enumerate(boxes):
                if b[0][0] > x and b[0][1] >= y and b[0][1] <= (y + 100):
                    if remark == "":
                        remark = texts[j]
                    else:
                        remark = remark + texts[j]
            if result["备注"] == '':
                result["备注"] = remark

    if isinstance(result["含税额"], (int, float)) and isinstance(result["金额"], (int, float)) and result["含税额"] > 0 and result["金额"] > 0:
        result["税额"] = round(float(result["含税额"] - result["金额"]), 2)
    # if result["备注"] == '':
    #     x = 10
    #     y = 840
    #     remark = ""
    #     for j, b in enumerate(boxes):
    #         if b[0][0] >= x and b[0][1] >= y and b[0][1] <= (y + 100):
    #             if remark == "":
    #                 remark = texts[j]
    #             else:
    #                 remark = remark + texts[j]
    #     result["备注"] = remark
    if not result["红字发票"] and result["金额"] < 0.0:
        result["红字发票"] = True
        
    return result

def extract_certificate_fields(texts: list, scores, boxes: list) -> dict:
    """从 OCR 文本中提取关键字段"""
    result = {
        "No": '',
        "日期": '',
        "税务机关": '',
        "识别号": '',
        "名称": '',
        "原凭证号": [],
        "税种": [],
        "品目名称": [],
        "税款所属日期": [],
        "入库日期": [],
        "实缴金额": [],
        "总金额": 0,
        "备注": ''
    }

    total_money_y = 0
    for idx, t in enumerate(texts):
        # No号码
        match = re.search(r"^No\.\s*([0-9]+)", t)
        if match:
            result["No"] = match.group(1)

        match = re.search(r"填发日期", t)
        if match:
            x = boxes[idx][0][0] + 100
            y = boxes[idx][0][1] - 5
            year = None
            month = None
            day = None
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] < (y + 30):
                    text = texts[j].replace(' ', '').replace('\n', '')
                    match = re.search(r"([0-9]+)年", text)
                    if match:
                        year = match.group(1)
                    match = re.search(r"([0-9]+)月", text)
                    if match:
                        month = match.group(1).zfill(2)
                    match = re.search(r"([0-9]+)日", text)
                    if match:
                        day = match.group(1).zfill(2)
                    x = b[0][0] + 100
            if year and month and day:
                result["日期"] = f"{year}年{month}月{day}日"

        match = re.search(r"税务机关", t)
        if match:
            x = boxes[idx][0][0]
            y = boxes[idx][0][1] - 20
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] <= (y + 30):
                    if result["税务机关"] == '':
                        result["税务机关"] = texts[j].split('：')[-1]
                        y = b[0][1] + 10  # 继续向下偏移 10
                        if y > boxes[idx][0][1] + 10:
                            break
                    else:
                        result["税务机关"] = result["税务机关"] + texts[j].split('：')[-1]
                        break
        match = re.search(r"纳税人识别号", t)
        if match:
            x = boxes[idx][0][0] + 100
            y = boxes[idx][0][1] - 5
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] <= (y + 30):
                    result["识别号"] = texts[j]
                    break
        match = re.search(r"纳税人名称", t)
        if match:
            x = boxes[idx][0][0] + 100
            y = boxes[idx][0][1] - 5
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] <= (y + 30):
                    result["名称"] = texts[j]
                    break
        match = re.search(r"原凭证号", t)
        if match:
            x = boxes[idx][0][0] - 100
            y = boxes[idx][0][1] + 50
            original_voucher_numbers = []
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] <= (y + 100):
                    original_voucher_numbers.append(texts[j])
                    y = b[0][1] + 30  # 继续向下偏移 30
                    if y >= 1100:
                        break
            result["原凭证号"].extend(original_voucher_numbers)
        match = re.search(r"税种", t)
        if match:
            x = boxes[idx][0][0] - 100
            y = boxes[idx][0][1] + 50
            tax_types = []
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] <= (y + 100):
                    tax_types.append(texts[j])
                    y = b[0][1] + 30  # 继续向下偏移 30
                    if y >= 1100:
                        break
            result["税种"].extend(tax_types)
        match = re.search(r"品目名称", t)
        if match:
            x = boxes[idx][0][0] - 100
            y = boxes[idx][0][1] + 50
            item_names = []
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] <= (y + 100):
                    item_names.append(texts[j])
                    y = b[0][1] + 30  # 继续向下偏移 30
                    if y >= 1100:
                        break
            result["品目名称"].extend(item_names)
        match = re.search(r"税款所属时期", t)
        if match:
            x = boxes[idx][0][0] - 130
            y = boxes[idx][0][1] + 50
            name = ""
            tax_dates = []
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] <= (y + 100):
                    if name == "":
                        name = texts[j]
                    else:
                        name = name + texts[j]
                        tax_dates.append(name)
                        name = ""
                    y = b[0][1] + 30  # 继续向下偏移 30
                    if y >= 1100:
                        break
            result["税款所属日期"].extend(tax_dates)
        match = re.search(r"入[（(]退[)）]库日期", t)
        if match:
            x = boxes[idx][0][0] - 100
            y = boxes[idx][0][1] + 50
            inventory_dates = []
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] <= (y + 100):
                    inventory_dates.append(texts[j])
                    y = b[0][1] + 30  # 继续向下偏移 30
                    if y >= 1100:
                        break
            result["入库日期"].extend(inventory_dates)

        match = re.search(r"实缴[（(]退[)）]金额", t)
        if match:
            x = boxes[idx][0][0] - 100
            y = boxes[idx][0][1] + 50
            paid_amounts = []
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 300) and b[0][1] >= y and b[0][1] <= (y + 100):
                    paid_amounts.append(float(texts[j].replace(' ', '').replace(',', '').replace('￥', '').replace('¥', '')))
                    y = b[0][1] + 50  # 继续向下偏移 30
                    if y >= 1100:
                        break
            result["实缴金额"].extend(paid_amounts)
        match = re.search(r"金额合计", t)
        if match:
            total_money_y = boxes[idx][0][1] - 50
        match = re.search(r"[￥¥](\d+\s*\.\d{1,2})", t)
        if match:
            if total_money_y == 0:
                total_money_y = 1150
            if boxes[idx][0][1] >= total_money_y and boxes[idx][0][1] < (total_money_y + 100):
                result["总金额"] = float(match.group(1).replace(' ', '').replace(',', ''))
        match = re.search(r"备注[:：](.*)", t)
        if match:
            result["备注"] = match.group(1)
            start_x = boxes[idx][0][0] - 50
            start_y = boxes[idx][0][1] - 10
            remark_boxes = boxes[idx+1:]
            remart_texts = texts[idx+1:]
            x = start_x + 200
            y = start_y
            for j, b in enumerate(remark_boxes):
                if b[0][0] >= x and b[0][0] < (x + 500) and b[0][1] >= y and b[0][1] < (y + 50):
                    result["备注"] = result["备注"] + remart_texts[j]
                    x = x + 200
                else:
                    x = start_x
                    y = y + 30
                    if b[0][0] >= x and b[0][0] < (x + 500) and b[0][1] >= y and b[0][1] < (y + 50):
                        result["备注"] = result["备注"] + remart_texts[j]
                        x = x + 200
                if x > 1900:
                    x = start_x
                    y = y + 30  # 继续向下偏移 30
                if y >= 1400:
                    break
                
    return result
    
def recognize_invoice_pdf(pdf_content):
    # 1. PDF 转图片
    pages = convert_from_bytes(pdf_content, dpi=300)

    all_fields = []

    # 3. 逐页识别
    for i, page in enumerate(pages):
        print(f"\n===== 第 {i+1} 页 =====")
        # img_path = f"page_{i+1}.jpg"
        # page.save(img_path, "JPEG")

        page = page.resize((2*page.width // 3, 2*page.height // 3))
        img = np.array(page)

        results = ocr.predict(img)
        texts  = results[0]['rec_texts']
        scores = results[0]['rec_scores']
        boxes  = results[0]['dt_polys']

        print("OCR 结果：")
        for text, score, box in zip(texts, scores, boxes):
            print(f"文字: {text}, 置信度: {score:.3f}, 坐标: {box}")

        fields = extract_invoice_fields(texts, scores, boxes)
        print("\n提取字段：", fields)

        all_fields.append(fields)

    return all_fields

def recognize_certificate_pdf(pdf_content):
    # 1. PDF 转图片
    pages = convert_from_bytes(pdf_content, dpi=300)

    all_fields = []

    # 3. 逐页识别
    for i, page in enumerate(pages):
        print(f"\n===== 第 {i+1} 页 =====")
        # img_path = f"page_{i+1}.jpg"
        # page.save(img_path, "JPEG")

        page = page.resize((2*page.width // 3, 2*page.height // 3))
        img = np.array(page)

        results = ocr.predict(img)
        texts  = results[0]['rec_texts']
        scores = results[0]['rec_scores']
        boxes  = results[0]['dt_polys']

        print("OCR 结果：")
        for text, score, box in zip(texts, scores, boxes):
            print(f"文字: {text}, 置信度: {score:.3f}, 坐标: {box}")

        fields = extract_certificate_fields(texts, scores, boxes)
        print("\n提取字段：", fields)

        all_fields.append(fields)

    return all_fields

def handle_upload_ocr(event):
    # event.content 是文件的二进制内容
    import io
    file_content = io.BytesIO(event.content.read())
    results = recognize_invoice_pdf(file_content.read())
    print(results)

def handle_muliple_upload(event):
    # event.content 是文件的二进制内容
    pass
