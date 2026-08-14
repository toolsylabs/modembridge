# ZTE Goform Lab Report

This document preserves practical findings from the initial reverse-engineering and hardware validation phase for the ZTE Goform modem flow.

## Scope

- Vendor family: ZTE Goform HTTP WebUI
- Target gateway: `http://192.168.0.1`
- Goal: login, send SMS, read SMS history
- Source baseline: prototype implementation in `modem_sms_test`

## Protocol Endpoints

- POST: `/goform/goform_set_cmd_process`
- GET: `/goform/goform_get_cmd_process`

Session behavior:

- Use `requests.Session()`.
- Persist modem-issued `stok` cookie across requests.

## Authentication Flow (Verified)

1. Fetch `LD`:
   - `cmd=LD`
2. Compute login password hash:
   - `inner = SHA256(password)`
   - `password_hash = SHA256(inner + LD)`
3. Login request:
   - `goformId=LOGIN`
   - `password=<password_hash>`
   - `isTest=false`

Result:

- This flow is the known compatible approach for the tested device path.

## SMS AD Generation (ZTE-Specific)

1. Fetch `RD`:
   - `cmd=RD`
2. Fetch version fields:
   - `cmd=Language,cr_version,wa_inner_version`
   - `multi_data=1`
3. Extract:
   - `rd0 = wa_inner_version`
   - `rd1 = cr_version`
4. Compute AD:
   - `inner = SHA256(rd0 + rd1)`
   - `AD = SHA256(inner + RD)`

Important:

- `AD` is vendor/protocol specific and must stay inside the ZTE driver.

## SMS Send Payload (Verified Structure)

Required fields:

- `goformId=SEND_SMS`
- `notCallback=true`
- `Number=<phone>`
- `sms_time=<YY;MM;DD;HH;MM;SS;+timezone>`
- `MessageBody=<UTF-16BE HEX>`
- `ID=-1`
- `encode_type=GSM7_default`
- `AD=<generated>`
- `isTest=false`

Encoding note:

- Message body must be UTF-16BE hex.

## SMS History Read

GET parameters used:

- `cmd=sms_data_total`
- `page=0`
- `data_per_page=5`
- `mem_store=1`
- `tags=10`
- `order_by=order by id desc`
- `isTest=false`

Observed parsing semantics:

- `sms_class=4` => `sent`
- `sms_class=1` => `received`
- `tag=1` => `new`
- `tag=2` => `read`
- `tag=0` => `unread`

## Reliability Notes

- Read operations can be retried safely.
- SMS send should avoid blind retries to reduce duplicate delivery risk after uncertain responses.
- A successful `SEND_SMS` response means the modem accepted the request, not that the SMS is fully delivered.
- For final delivery confirmation, query `sms_cmd_status_info` with `sms_cmd=4` and read `sms_cmd_status_result`.

## Real-Modem Validation Notes

The live-device validation script was run against a real ZTE gateway using the local `.env` credentials.

Observed output:

- `probe()` returned `True`
- `get_sms_history()` returned real entries from the modem
- `send_sms()` returned `{"result":"success"}` and a queue status of `1` (`queued`)
- the newly sent message immediately appeared in history and was retrievable by modem `id`
- `get_sms_by_id()` and `get_sms_by_phone()` correctly found the message in the modem's history

This confirms the architecture works on real hardware and that status semantics must be interpreted as request acceptance, not final delivery.

## Security Notes

Never store these in source, tests, fixtures, or docs:

- real passwords
- session tokens (`stok`)
- IMEI/IMSI
- SIM phone numbers
- raw sensitive modem identifiers

## Migration Value for ModemBridge

This report defines the first production-like driver baseline:

- Driver: `zte_goform`
- Transport: HTTP
- Core remains vendor-neutral
- ZTE-specific logic isolated in driver module

## Future Device Onboarding Pattern

For each new modem/protocol:

1. Run isolated lab/prototype testing.
2. Extract only durable protocol facts.
3. Write one report in `docs/` with this structure.
4. Port logic into driver + tests.
5. Remove temporary prototype artifacts.
