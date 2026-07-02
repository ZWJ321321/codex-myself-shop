import json

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.common.http import fail, ok

from .services import OrderPriceChangedError, OrderValidationError, create_order, preview_order


def _parse_request_payload(request):
    try:
        payload = json.loads(request.body or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise OrderValidationError({"payload": ["提交数据不合法"]}) from exc

    if not isinstance(payload, dict):
        raise OrderValidationError({"payload": ["提交数据不合法"]})

    return payload


@method_decorator(csrf_exempt, name="dispatch")
class OrderPreviewView(View):
    def post(self, request):
        try:
            payload = _parse_request_payload(request)
            return ok(preview_order(payload))
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", errors=exc.errors, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class OrderCreateView(View):
    def post(self, request):
        try:
            payload = _parse_request_payload(request)
            order, summary = create_order(payload)
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", errors=exc.errors, status=400)
        except OrderPriceChangedError as exc:
            return fail("price_changed", "订单金额已变化，请重新确认", data=exc.summary, status=409)
        return ok({"order_no": order.order_no, **summary}, status=201)