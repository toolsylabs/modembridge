from __future__ import annotations

import hashlib
import datetime as dt
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

from ...core.models import ModemProfile, SmsHistoryEntry, SmsSendResult
from ...core.exceptions import ModemAuthenticationError


class ZteGoformDriver:
    def __init__(self, profile: ModemProfile) -> None:
        self.profile = profile
        self.base_url = profile.host.rstrip("/")
        self._cookie_domain = urlparse(self.base_url).hostname or ""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-Requested-With": "XMLHttpRequest",
                "Origin": self.base_url,
                "Referer": f"{self.base_url}/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0",
            }
        )
        if profile.extra.get("stok"):
            self.session.cookies.set(
                "stok",
                str(profile.extra["stok"]),
                domain=self._cookie_domain,
                path="/",
            )
        self._stok = None

    def probe(self) -> bool:
        try:
            response = self._get(
                "/goform/goform_get_cmd_process",
                {"isTest": "false", "cmd": "Language", "multi_data": "1"},
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _post(self, endpoint: str, data: dict[str, Any] | None = None) -> requests.Response:
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return self.session.post(url, data=data, timeout=10)

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> requests.Response:
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return self.session.get(url, params=params, timeout=10)

    def _sha256_upper(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()

    def _build_login_password(self, password: str, ld: str) -> str:
        return self._sha256_upper(self._sha256_upper(password) + ld)

    def _build_ad_value(self, rd0: str, rd1: str, rd: str) -> str:
        return self._sha256_upper(self._sha256_upper(rd0 + rd1) + rd)

    def _update_session_from_response(self, response: requests.Response) -> None:
        if not response.headers.get("Set-Cookie"):
            return
        for cookie_part in response.headers.get("Set-Cookie", "").split(","):
            if "stok=" in cookie_part:
                self._stok = cookie_part.split("stok=", 1)[1].split(";", 1)[0].strip('"')
                if self._cookie_domain:
                    self.session.cookies.set("stok", self._stok, domain=self._cookie_domain, path="/")
                break

    def _fetch_modem_params(self) -> dict[str, str]:
        ld_response = self._get("/goform/goform_get_cmd_process", {"isTest": "false", "cmd": "LD"})
        self._update_session_from_response(ld_response)
        ld_response.raise_for_status()

        rd_response = self._get("/goform/goform_get_cmd_process", {"isTest": "false", "cmd": "RD"})
        self._update_session_from_response(rd_response)
        rd_response.raise_for_status()

        language_response = self._get(
            "/goform/goform_get_cmd_process",
            {"isTest": "false", "cmd": "Language,cr_version,wa_inner_version", "multi_data": "1"},
        )
        self._update_session_from_response(language_response)
        language_response.raise_for_status()

        ld_data = ld_response.json()
        rd_data = rd_response.json()
        language_data = language_response.json()

        return {
            "LD": str(ld_data.get("LD", "")),
            "RD": str(rd_data.get("RD", "")),
            "rd0": str(language_data.get("wa_inner_version", "")),
            "rd1": str(language_data.get("cr_version", "")),
        }

    def login(self) -> None:
        auth_params = self._fetch_modem_params()
        password_hash = self._build_login_password(self.profile.password or self.profile.extra.get("password", ""), auth_params["LD"])
        payload = {
            "isTest": "false",
            "goformId": "LOGIN",
            "password": password_hash,
        }
        response = self._post("/goform/goform_set_cmd_process", payload)
        self._update_session_from_response(response)
        if response.text and '"result":"0"' in response.text:
            return
        raise ModemAuthenticationError(f"Login failed: {response.text}")

    def send_sms(self, phone: str, text: str, retries: int = 3) -> SmsSendResult:
        self.login()
        for attempt in range(retries):
            try:
                params = self._fetch_modem_params()
                ad_value = self._build_ad_value(params["rd0"], params["rd1"], params["RD"])
                payload = {
                    "isTest": "false",
                    "goformId": "SEND_SMS",
                    "notCallback": "true",
                    "Number": phone,
                    "sms_time": self._format_sms_time(),
                    "MessageBody": text.encode("utf-16-be").hex(),
                    "ID": "-1",
                    "encode_type": "GSM7_default",
                    "AD": ad_value,
                }
                response = self._post("/goform/goform_set_cmd_process", payload)
                self._update_session_from_response(response)
                if response.text and '"result":"success"' in response.text.lower():
                    status = self._read_sms_send_status()
                    details = {
                        "attempt": attempt + 1,
                        "response": response.text,
                        "sms_cmd_status_result": status.get("sms_cmd_status_result"),
                        "send_status": self._describe_sms_send_status(str(status.get("sms_cmd_status_result", "")).strip()),
                    }
                    return SmsSendResult(
                        ok=True,
                        message="SMS send request accepted by modem; final delivery status must be checked separately",
                        details=details,
                    )
                if response.text and '"result":"success"' not in response.text.lower():
                    if attempt < retries - 1:
                        continue
                    return SmsSendResult(ok=False, message="SMS send failed", details={"attempt": attempt + 1, "response": response.text})
            except Exception as exc:  # pragma: no cover - network errors
                if attempt < retries - 1:
                    continue
                return SmsSendResult(ok=False, message=str(exc), details={"attempt": attempt + 1})
        return SmsSendResult(ok=False, message="SMS send failed", details={})

    def _read_sms_send_status(self) -> dict[str, Any]:
        response = self._get(
            "/goform/goform_get_cmd_process",
            {"isTest": "false", "cmd": "sms_cmd_status_info", "sms_cmd": "4"},
        )
        self._update_session_from_response(response)
        response.raise_for_status()
        if not response.text:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}

    def _describe_sms_send_status(self, value: str) -> str:
        normalized = str(value).strip()
        mapping = {
            "0": "unknown",
            "1": "queued",
            "2": "sending",
            "3": "delivered",
            "4": "failed",
        }
        return mapping.get(normalized, "unknown")

    def get_sms_history(self) -> list[SmsHistoryEntry]:
        self.login()
        params = {
            "isTest": "false",
            "cmd": "sms_data_total",
            "page": "0",
            "data_per_page": "5",
            "mem_store": "1",
            "tags": "10",
            "order_by": "order by id desc",
        }
        response = self._get("/goform/goform_get_cmd_process", params)
        self._update_session_from_response(response)
        response.raise_for_status()

        data = response.json() if response.text else {}
        entries = []
        history = data.get("messages") or []
        for item in history:
            if not isinstance(item, dict):
                continue
            entries.append(
                SmsHistoryEntry(
                    id=str(item.get("id") or item.get("Index") or ""),
                    sender=self._decode_utf16_hex(str(item.get("number") or item.get("sender") or "")),
                    receiver=self._decode_utf16_hex(str(item.get("receiver") or item.get("number") or "")),
                    body=self._decode_utf16_hex(str(item.get("content") or item.get("body") or "")),
                    status=self._normalize_sms_status(item),
                    direction=self._infer_sms_direction(item),
                    raw=item,
                )
            )
        return entries

    def close(self) -> None:
        self.session.close()

    def _decode_utf16_hex(self, value: str) -> str:
        if not value:
            return ""
        try:
            return bytes.fromhex(value).decode("utf-16-be")
        except (ValueError, UnicodeDecodeError):
            return value

    def _normalize_sms_status(self, item: dict[str, Any]) -> str:
        tag = str(item.get("tag", "")).strip()
        if tag == "1":
            return "new"
        if tag == "2":
            return "read"
        if tag == "0":
            return "unread"
        return "unknown"

    def _infer_sms_direction(self, item: dict[str, Any]) -> str:
        direction = str(item.get("direction", "")).strip().lower()
        if direction in {"sent", "send", "outgoing", "out"}:
            return "sent"
        if direction in {"received", "receive", "incoming", "in"}:
            return "received"

        sms_class = str(item.get("sms_class", "")).strip().lower()
        if sms_class in {"4", "sent", "outgoing", "out"}:
            return "sent"
        if sms_class in {"1", "received", "incoming", "in"}:
            return "received"

        return "unknown"

    def _format_sms_time(self) -> str:
        now = dt.datetime.now()
        return f"{now.strftime('%y')};{now.strftime('%m')};{now.strftime('%d')};{now.strftime('%H')};{now.strftime('%M')};{now.strftime('%S')};+5"
