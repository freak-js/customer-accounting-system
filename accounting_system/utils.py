from .models import ECP, CashMachine, OFD, FN, TO, Service, Client
from typing import Union
import datetime
from dateutil.relativedelta import relativedelta


SERVICE_TYPE_DICT: dict = {'kkt': CashMachine, 'ecp': ECP, 'ofd': OFD, 'fn': FN, 'to': TO}


def get_service_class_instance(request) -> Union[CashMachine, ECP, OFD, FN, TO]:
    service_type: str = request.POST.get('service_type')
    service_class_instance: Union[CashMachine, ECP, OFD, FN, TO] = SERVICE_TYPE_DICT.get(service_type)
    return service_class_instance


def create_service_for_client(request) -> None:
    p = request.POST
    client_pk = p.get('client_pk')
    client = Client.objects.get(pk=client_pk)

    cash_machine_pk = p.get('cash_machine_pk')
    factory_number = p.get('factory_number')
    cash_machine = CashMachine.objects.get(pk=cash_machine_pk) if cash_machine_pk else None

    ecp_pk = p.get('ecp_pk')
    ecp = ECP.objects.get(pk=ecp_pk) if ecp_pk else None
    ecp_add_date = p.get('add_ecp_date') if p.get('add_ecp_date') else None
    ecp_expiration_date = get_expiration_date(ecp_pk, 'ecp', ecp_add_date) if ecp_add_date else None

    ofd_pk = p.get('ofd_pk')
    ofd = OFD.objects.get(pk=ofd_pk) if ofd_pk else None
    ofd_add_date = p.get('add_ofd_date') if p.get('add_ofd_date') else None
    ofd_expiration_date = get_expiration_date(ofd_pk, 'ofd', ofd_add_date) if ofd_add_date else None

    fn_pk = p.get('fn_pk')
    fn = FN.objects.get(pk=fn_pk) if fn_pk else None
    fn_add_date = p.get('add_fn_date') if p.get('add_fn_date') else None
    fn_expiration_date = get_expiration_date(fn_pk, 'fn', fn_add_date) if fn_add_date else None

    to_pk = p.get('to_pk')
    to = TO.objects.get(pk=to_pk) if to_pk else None
    to_add_date = p.get('add_to_date') if p.get('add_to_date') else None
    to_expiration_date = get_expiration_date(to_pk, 'to', to_add_date) if to_add_date else None

    service = Service(client=client, cash_machine=cash_machine, factory_number=factory_number,
                      ecp=ecp, ecp_add_date=ecp_add_date, ecp_expiration_date=ecp_expiration_date,
                      ofd=ofd, ofd_add_date=ofd_add_date, ofd_expiration_date=ofd_expiration_date,
                      fn=fn, fn_add_date=fn_add_date, fn_expiration_date=fn_expiration_date,
                      to=to, to_add_date=to_add_date, to_expiration_date=to_expiration_date)
    service.save()


def get_expiration_date(service_pk: str, service_type: str, add_date: str) -> datetime:
    service: Union[ECP, OFD, FN, TO] = SERVICE_TYPE_DICT[service_type].objects.get(pk=service_pk)
    validity: int = service.validity
    day: int = int(add_date[8:10])
    month: int = int(add_date[5:7])
    year: int = int(add_date[0:4])
    datetime_add_date = datetime.date(year, month, day)
    return datetime_add_date + relativedelta(months=validity)
