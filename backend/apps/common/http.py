from django.http import JsonResponse


def ok(data, message="success", status=200):
    return JsonResponse({"code": "ok", "message": message, "data": data}, status=status)


def fail(code, message, errors=None, status=400):
    payload = {"code": code, "message": message}
    if errors:
        payload["errors"] = errors
    return JsonResponse(payload, status=status)
