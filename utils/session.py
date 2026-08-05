import base64
import json
import time


def _b64url_decode(segment: str) -> bytes:
    padded = segment + "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(padded)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def expire_refresh_token(driver, storage_key="etiya.refreshToken"):
    """sessionStorage'daki JWT refresh token'ın exp claim'ini geçmişe çekerek
    süresi dolmuş bir oturumu simüle eder (gerçek 8 saat beklemek yerine).

    Not: Token imzası (HS512) korunmuyor çünkü secret bilinmiyor - uygulama
    yalnızca payload'daki exp'i client tarafında kontrol ediyorsa bu yeterli;
    sunucu tarafı da doğrularsa geçersiz imza zaten reddedilmeyi tetikler.
    """
    token = driver.execute_script(f"return sessionStorage.getItem('{storage_key}');")
    header_b64, payload_b64, signature_b64 = token.split(".")

    payload = json.loads(_b64url_decode(payload_b64))
    payload["exp"] = int(time.time()) - 3600

    tampered_payload_b64 = _b64url_encode(json.dumps(payload).encode())
    tampered_token = f"{header_b64}.{tampered_payload_b64}.{signature_b64}"

    driver.execute_script(
        "sessionStorage.setItem(arguments[0], arguments[1]);", storage_key, tampered_token
    )
