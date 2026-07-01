import json

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.common.http import fail, ok

from .services import OrderValidationError, create_order, preview_order


@method_decorator(csrf_exempt, name="dispatch")
class OrderPreviewView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            return ok(preview_order(payload))
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", exc.errors, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class OrderCreateView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            order, preview = create_order(payload)
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", exc.errors, status=400)
        return ok({"order_no": order.order_no, **preview}, status=201)
