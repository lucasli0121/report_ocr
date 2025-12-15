from datetime import datetime
from typing import Any
from dao.company_dao import CompanyDao
from dao.service_record_dao import ServiceRecordDao
from db.mydb import MyDb
from mq.mq_impl import MqImpl
mq_impl = MqImpl()
my_db = MyDb()

def create_mq() -> bool:
    if mq_impl.connect() is False:
        return False
    mq_impl.loop_for_thread()
    return True

def subscribe_online_topic(mac: str, handle_online_func) -> bool:
    return mq_impl.subscribe(f'hjy-dev/device/heart_beat/{mac.lower()}', handle_online_func)
def unsubscribe_online_topic(mac: str) -> bool:
    return mq_impl.unsubscribe(f'hjy-dev/device/heart_beat/{mac.lower()}')
def subscribe_event_topic(mac: str, handle_event_func) -> bool:
    return mq_impl.subscribe(f'server-h03/study/event/{mac.lower()}', handle_event_func)
def subscribe_attr_topic(mac: str, handle_attr_func) -> bool:
    return mq_impl.subscribe(f'server-t1/study/attr/{mac.lower()}', handle_attr_func)
def unsubscribe_event_topic(mac: str):
    mq_impl.unsubscribe(f'server-h03/study/event/{mac.lower()}')
def unsubscribe_attr_topic(mac: str):
    mq_impl.unsubscribe(f'server-t1/study/attr/{mac.lower()}')


def query_company_name_company() -> tuple[bool, dict[str, CompanyDao]]:
    result, list_values = my_db.query_all_company('','','','')
    if result is False:
        return False, {}
    company_info = {}
    if result and list_values is not None:
        for item in list_values:
            company = CompanyDao()
            company.from_db(item)
            company_info[company.brief_name] = company
    return True, company_info

#
# 查询服务记录的合同名称字典
# 返回的字典以合同名称为键，ServiceRecordDao对象为值
# from_company_id: 发起方公司ID
# to_company_id: 接收方公司ID
# 返回: (查询成功与否, {合同名称: ServiceRecordDao对象})
#
def query_service_name_dict(from_company_id: str, to_company_id: str) -> tuple[bool, dict[str, ServiceRecordDao]]:
    result, value_list = my_db.query_all_service_record(from_company_id, to_company_id, 0, '', '')
    if result is False or value_list is None:
        return False, {}
    service_name_dict = {}
    for item in value_list:
        dao = ServiceRecordDao()
        dao.from_db(item)
        service_name_dict[dao.contract_name] = dao
    return True, service_name_dict

#
# 更新合同的开票金额
# contract_id: 合同ID
# invoice_money: 要增加的开票金额
# 返回: 成功返回True，否则返回False
#
def update_contract_invoice_money(contract_id: str, invoice_money: float) -> bool:
    result, service_dao = my_db.query_service_record_by_id(contract_id)
    if not result or service_dao is None:
        return False
    service_dao.invoice_money += invoice_money
    if service_dao.invoice_money > service_dao.payment_money:
        service_dao.status = 2 # 更新状态为待付款
    if service_dao.invoice_money < service_dao.payment_money:
        service_dao.status = 3 # 更新状态为待开票
    if service_dao.invoice_money == service_dao.contract_money and service_dao.payment_money == service_dao.contract_money:
        service_dao.status = 4 # 更新状态为完成
    service_dao.latest_invoice_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return my_db.update_service_record(service_dao.to_db(), {})

#
# 更新合同的付款金额
# contract_id: 合同ID
# invoice_money: 要增加的开票金额
# 返回: 成功返回True，否则返回False
#
def update_contract_payment_money(contract_id: str, payment_money: float) -> bool:
    result, service_dao = my_db.query_service_record_by_id(contract_id)
    if not result or service_dao is None:
        return False
    service_dao.payment_money += payment_money
    if service_dao.payment_money > service_dao.invoice_money:
        service_dao.status = 3 # 更新状态为待付款
    if service_dao.payment_money < service_dao.invoice_money:
        service_dao.status = 2 # 更新状态为待开票
    if service_dao.payment_money == service_dao.contract_money and service_dao.invoice_money == service_dao.contract_money:
        service_dao.status = 4 # 更新状态为完成
    service_dao.latest_payment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return my_db.update_service_record(service_dao.to_db(), {})