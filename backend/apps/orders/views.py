import json

from django.views import View

from apps.common.http import fail, ok

from .services import OrderValidationError, create_order, preview_order


class OrderPreviewView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            return ok(preview_order(payload))
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", exc.errors, status=400)


class OrderCreateView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            order, preview = create_order(payload)
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", exc.errors, status=400)
        return ok({"order_no": order.order_no, **preview}, status=201)
