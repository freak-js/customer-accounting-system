from .models import ECP, CashMachine, OFD, FN, TO


SERVICE_TYPE_DICT: dict = {'kkt': CashMachine, 'ecp': ECP, 'ofd': OFD, 'fn': FN, 'to': TO}


def get_service_class_instance(request):
    service_type = request.POST.get('service_type')
    service_class_instance = SERVICE_TYPE_DICT.get(service_type)
    return service_class_instance