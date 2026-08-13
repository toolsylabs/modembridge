Ha. Endi vazifani bitta ZTE modem SDK emas, keyinchalik **ochiq universal cellular device SDK** bo‘ladigan qilib beramiz. Hozirgi ishlayotgan ZTE/Ucell modem — birinchi real driver.

Copilot’ga quyidagini to‘liq ber:

# TASK: Build `ModemBridge` — extensible Python SDK for cellular modems and SMS gateway devices

Mavjud repository/workspace ichida ishlayotgan `modem_sms_test` prototipi bor. U real ZTE/Ucell 5G modem orqali SMS yuborishni muvaffaqiyatli bajaryapti.

Mavjud ishlaydigan kodni DELETE, OVERWRITE yoki buzma.

Uning yonida mutlaqo yangi:

```text
modembridge/
```

project yarat.

Bu oddiy script emas.

Maqsad — keyinchalik GitHub va PyPI’da open-source package sifatida chiqarish mumkin bo‘lgan, vendor/model-independent, extensible **Python cellular modem SDK** yaratish.

Package/project nomi:

```text
ModemBridge
```

PyPI candidate:

```text
modembridge
```

Python import:

```python
import modembridge
```

Hozircha publish QILMA.

---

# 1. ASOSIY MAQSAD

SDK faqat ZTE yoki hozirgi modemga bog‘lanmasin.

Kelajakda quyidagi qurilmalarni qo‘shib borish mumkin bo‘lsin:

```text
USB GSM modems
USB LTE modems
USB 5G modems

Serial AT-command modems

ZTE WebUI/goform modems
Huawei HiLink modems

Quectel-based devices
SIMCom-based devices

Network/LAN cellular gateways

Wi-Fi cellular routers

professional SMS gateways

Android SMS gateway devices
```

Hozir HAMMASINI implement qilish shart emas.

Architecture shularni keyinchalik plugin/driver sifatida qo‘shishga tayyor bo‘lsin.

Birinchi REAL va TESTED driver mavjud ishlaydigan modem uchun yozilsin.

---

# 2. BIRINCHI REAL DEVICE

Hozir ishlayotgan modem:

```text
Vendor: ZTE
Gateway: 192.168.0.1
Firmware: BD_UCELLUZG5BV1.0.0B06
Hardware: G5BHWV1.0.0
Operator firmware: Ucell Uzbekistan
```

Private runtime information:

```text
SIM phone number
IMEI
IMSI
stok/session tokens
password
```

source code, tests, fixtures yoki documentation ichiga real qiymatlarda yozilmasin.

---

# 3. HOZIRGI ISHLAYDIGAN PROTOKOLNI SAQLA

Existing `modem_sms_test` implementation real hardware bilan ishlayapti.

Uni reference implementation sifatida ishlat.

Taxmin qilib ishlaydigan algoritmlarni almashtirma.

Current protocol:

```text
BASE URL:
http://192.168.0.1

POST:
 /goform/goform_set_cmd_process

GET:
 /goform/goform_get_cmd_process
```

Session:

```python
requests.Session()
```

Modem qaytargan `stok` cookie Session tomonidan boshqarilsin.

---

# 4. AUTHENTICATION

`LD`:

```text
cmd=LD
```

orqali olinadi.

Password:

```text
inner = SHA256(password)
password_hash = SHA256(inner + LD)
```

Login existing working implementation bilan aynan compatible bo‘lsin.

---

# 5. SMS AD GENERATION

SMS uchun `AD`:

```text
rd0 = wa_inner_version
rd1 = cr_version
RD  = modemdan cmd=RD

inner = SHA256(rd0 + rd1)
AD = SHA256(inner + RD)
```

Versions:

```text
cmd=Language,cr_version,wa_inner_version
multi_data=1
```

orqali olinadi.

Bu algoritm ZTE-specific driver ichida bo‘lsin.

Core ModemBridge `LD`, `RD`, `AD` haqida hech narsa bilmasin.

---

# 6. SMS SEND

Current ZTE driver:

```text
goformId=SEND_SMS
notCallback=true
Number=<phone>
sms_time=<YY;MM;DD;HH;MM;SS;+timezone>
MessageBody=<UTF-16BE HEX>
ID=-1
encode_type=GSM7_default
AD=<generated>
```

ishlatadi.

SMS history ham existing implementationdan olinib port qilinsin.

Current observed semantics:

```text
sms_class=4 -> sent
sms_class=1 -> received

tag=1 -> new
tag=2 -> read/old
tag=0 -> unread
```

Bular universal deb hisoblanmasin.

Faqat ZTE driver/parser semantics sifatida implement qilinsin.

---

# 7. ENG MUHIM ARCHITECTURE RULE

Core hech qachon:

```python
if vendor == "zte":
...
elif vendor == "huawei":
...
```

kabi architecturega aylanmasin.

Driver registry + discovery + probe mechanism ishlat.

Concept:

```text
Physical/Network Device
        ↓
    Discovery
        ↓
    Transport
        ↓
Driver Probe Registry
        ↓
Best matching Driver
        ↓
Unified Modem API
```

---

# 8. UNIVERSAL PUBLIC API

Oxirgi foydalanuvchi modemning ichki protokolini bilmasligi kerak.

Ideal usage:

```python
from modembridge import Modem

modem = Modem.connect(
    host="192.168.0.1",
    password="password",
)

print(modem.device)
print(modem.capabilities)

result = modem.send_sms(
    "+998991234567",
    "Hello from ModemBridge",
)

print(result)
```

Auto discovery ham:

```python
from modembridge import discover

devices = discover()

for device in devices:
    print(device)
```

Keyinchalik:

```python
from modembridge import ModemManager

manager = ModemManager()

manager.discover()

for modem in manager.modems:
    print(modem.id)
    print(modem.vendor)
    print(modem.model)
    print(modem.status)
```

ishlashi mumkin bo‘lsin.

Hozir network discovery'ni xavfsiz va minimal implement qilish mumkin.

USB/serial discovery platformga qarab optional bo‘lishi mumkin.

---

# 9. DRIVER INTERFACE

Abstract/base driver yarat.

Conceptual API:

```python
class ModemDriver:
    name: str

    def probe(self, target) -> ProbeResult:
        ...

    def connect(self):
        ...

    def disconnect(self):
        ...

    def health_check(self):
        ...

    def get_device_info(self):
        ...

    def get_capabilities(self):
        ...

    def send_sms(self, phone, message):
        ...

    def get_messages(self, limit=20):
        ...
```

Driver barcha funksiyani qo‘llashi majburiy emas.

Unsupported capability:

```python
UnsupportedFeatureError
```

qaytarsin.

---

# 10. PROBE / AUTO DETECTION

Driver o‘zining mosligini tekshirsin.

Masalan:

```python
ProbeResult(
    matched=True,
    confidence=95,
    vendor="ZTE",
    family="goform",
    model=None,
    evidence=[
        "goform endpoint detected",
        "wa_inner_version available",
    ],
)
```

Driver registry:

```python
registry.register(ZteGoformDriver)
registry.register(GenericAtDriver)
```

Keyinchalik:

```python
registry.register(HuaweiHilinkDriver)
registry.register(QuectelAtDriver)
```

qo‘shish mumkin bo‘lsin.

Detection:

```text
ZTE Goform      confidence 95
Generic HTTP    confidence 30
Generic AT      confidence 0
```

eng yaxshi compatible driver tanlansin.

---

# 11. MODEL ≠ DRIVER

Har bir modem modeli uchun yangi driver yozish kerak bo‘lmasin.

Masalan:

```text
ZTE Goform Driver
 ├── Generic ZTE Goform
 ├── G5B profile
 ├── MF286 profile
 ├── MF823 profile
 └── future profiles
```

Model-specific farqlar `profile/quirks` orqali hal qilinsin.

---

# 12. DEVICE PROFILES

Profiles declarative bo‘lishi kerak.

YAML yoki TOML ishlatish mumkin.

Masalan:

```yaml
id: zte_g5b_ucell

match:
  vendor: ZTE
  hardware_prefix: G5BHW
  firmware_prefix: BD_UCELLUZG5B

driver: zte_goform

capabilities:
  sms_send: true
  sms_receive: true
  device_info: true
  network_info: true

quirks:
  sms_encoding: utf16be
  auth_scheme: ld_sha256
  sms_ad_scheme: rd_sha256
```

Lekin config orqali executable Python yoki xavfli dynamic code ishlatma.

Profiles faqat declarative data bo‘lsin.

---

# 13. GENERIC FALLBACK

Agar aniq model registry’da bo‘lmasa, lekin ZTE Goform driver probe muvaffaqiyatli bo‘lsa:

```text
Generic ZTE Goform Device
```

sifatida ishlasin.

Ya'ni:

```text
unknown model != unsupported device
```

Agar protocol compatible bo‘lsa ishlashni davom ettir.

Bu ModemBridge'ning asosiy design principles'dan biri bo‘lsin.

---

# 14. CAPABILITY SYSTEM

Universal enum/model yarat:

```text
SMS_SEND
SMS_RECEIVE
SMS_DELETE

USSD

SIGNAL_INFO
NETWORK_INFO
OPERATOR_INFO

SIM_INFO
DEVICE_INFO

REBOOT
```

Masalan:

```python
if modem.supports("sms_send"):
    modem.send_sms(...)
```

yoki typed enum:

```python
if modem.supports(Capability.SMS_SEND):
    ...
```

Ikkinchi variant afzal.

---

# 15. TRANSPORT LAYER

Driver va transportni ajrat.

Structure:

```text
Transport
├── HTTPTransport
├── SerialTransport
└── future transports
```

HTTP transport:

```text
requests.Session
timeout
retry
cookies
headers
JSON handling
```

bilan shug‘ullansin.

ZTE-specific:

```text
goform
LD
RD
AD
SEND_SMS
```

transport layer ichida bo‘lmasin.

---

# 16. SERIAL / AT ARCHITECTURE

Hozir to‘liq Generic AT implementation shart emas.

Lekin architecture tayyor bo‘lsin:

```text
SerialTransport
      ↓
GenericAtDriver
      ↓
AT
AT+CPIN?
AT+CSQ
AT+COPS?
AT+CMGF
AT+CMGS
```

`pyserial` optional dependency sifatida tashkil qil.

Masalan:

```bash
pip install modembridge[serial]
```

Hozir stub emas, imkon bo‘lsa minimal:

```text
AT ping
device detection
```

implement qil.

Lekin asosiy real tested driver ZTE Goform bo‘lib qolsin.

---

# 17. FUTURE ANDROID SUPPORT

Android'ni hozir implement qilma.

Lekin architecture documentation’da Android Gateway:

```text
Cloud/Local API
      ↓
Android Agent
      ↓
Android SmsManager
```

ModemBridge ecosystem'ga adapter sifatida qanday kirishi mumkinligini yoz.

Core cellular modem SDK bilan remote messaging device abstraction'ni keraksiz aralashtirma.

---

# 18. MULTI-MODEM

Architecture boshidan bir nechta modem bilan ishlashga tayyor bo‘lsin.

Masalan:

```python
manager = ModemManager()

manager.add(modem1)
manager.add(modem2)

for modem in manager.modems:
    print(modem.status)
```

Keyinchalik:

```text
USB modem #1
USB modem #2
HTTP modem #1
HTTP modem #2
```

bir process ichida ishlashi mumkin bo‘lsin.

Global `requests.Session` yoki global mutable device state ishlatma.

Har modemning session/state'i mustaqil bo‘lsin.

---

# 19. DEVICE IDENTITY

Device runtime identity uchun imkon bo‘lsa:

```text
vendor
model
hardware_version
firmware_version
IMEI
serial number
transport address
```

ishlat.

Lekin sensitive identifiers loglarda mask qilinsin.

Device ID generation deterministic bo‘lishi mumkin, lekin raw IMEI public ID sifatida expose qilinmasin.

Masalan hash/fingerprint ishlatish mumkin.

---

# 20. PROJECT STRUCTURE

Professional `src` layout ishlat:

```text
modembridge/
│
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── concepts.md
│   ├── discovery.md
│   ├── drivers.md
│   ├── transports.md
│   ├── device-profiles.md
│   ├── adding-a-driver.md
│   ├── adding-a-device-profile.md
│   ├── supported-devices.md
│   ├── zte-goform.md
│   ├── sms.md
│   └── security.md
│
├── examples/
│   ├── discover.py
│   ├── diagnose.py
│   ├── device_info.py
│   ├── send_sms.py
│   ├── read_sms.py
│   └── multi_modem.py
│
├── src/
│   └── modembridge/
│       │
│       ├── __init__.py
│       ├── modem.py
│       ├── manager.py
│       ├── exceptions.py
│       ├── models.py
│       ├── capabilities.py
│       │
│       ├── core/
│       │   ├── registry.py
│       │   ├── discovery.py
│       │   ├── probe.py
│       │   ├── device.py
│       │   └── profiles.py
│       │
│       ├── transports/
│       │   ├── base.py
│       │   ├── http.py
│       │   └── serial.py
│       │
│       ├── drivers/
│       │   ├── base.py
│       │   │
│       │   ├── zte_goform/
│       │   │   ├── driver.py
│       │   │   ├── auth.py
│       │   │   ├── sms.py
│       │   │   ├── parser.py
│       │   │   └── constants.py
│       │   │
│       │   └── generic_at/
│       │       ├── driver.py
│       │       └── commands.py
│       │
│       ├── profiles/
│       │   ├── loader.py
│       │   └── builtin/
│       │       └── zte_g5b_ucell.yaml
│       │
│       ├── sms/
│       │   ├── models.py
│       │   ├── encoding.py
│       │   └── phone.py
│       │
│       ├── diagnostics/
│       │   └── health.py
│       │
│       └── utils/
│           ├── crypto.py
│           ├── masking.py
│           └── time.py
│
└── tests/
    ├── unit/
    ├── fixtures/
    └── hardware/
```

Agar strukturani soddalashtirish kerak deb hisoblasang, soddalashtir.

Lekin boundaries:

```text
core
transport
driver
profile
domain models
```

aniq saqlansin.

---

# 21. CONNECTION DIAGNOSTICS

Professional diagnostic system yarat.

Example:

```python
report = modem.health_check()
print(report)
```

ZTE HTTP modem uchun:

```text
Gateway reachable ........ OK
HTTP transport ........... OK
WebUI .................... OK
Goform API ............... OK
Driver ................... zte_goform
Profile .................. zte_g5b_ucell
Authentication ........... OK
SIM ...................... READY
Network .................. REGISTERED
Operator ................. Ucell
Signal ................... AVAILABLE
SMS send ................. AVAILABLE
SMS receive .............. AVAILABLE
```

Structured result ham qaytsin.

---

# 22. LOGGING

Standard Python `logging`.

Root package logger:

```text
modembridge
```

Child loggers:

```text
modembridge.discovery
modembridge.transport.http
modembridge.transport.serial

modembridge.driver.zte_goform
modembridge.driver.generic_at

modembridge.sms
```

Default package import qilinganda log spam qilmasin.

DEBUG yoqilsa diagnostika uchun yetarli ma'lumot bersin.

HECH QACHON quyidagilarni to‘liq log qilma:

```text
password
password hash
stok
session secrets
IMSI
IMEI
SIM phone number
SMS body
```

Sensitive values mask qil.

---

# 23. EXCEPTIONS

Unified exception hierarchy:

```text
ModemBridgeError

DiscoveryError

TransportError
ConnectionError
TimeoutError

DriverError
DriverNotFoundError
UnsupportedDeviceError
UnsupportedFeatureError

AuthenticationError
SessionExpiredError

SimError
SimNotReadyError

NetworkError
NetworkNotRegisteredError

SmsError
SmsSendError
SmsDecodeError

ProtocolError
```

Raw `requests` yoki `serial` exceptionlarini public API'dan tashqariga chiqarma.

---

# 24. SMS DOMAIN MODELS

Universal models:

```python
SmsMessage
SmsSendResult
```

Masalan:

```python
SmsMessage(
    id="72",
    phone="+998...",
    content="Hello",
    direction=SmsDirection.SENT,
    status=SmsStatus.READ,
    timestamp=...,
)
```

Enums:

```text
SmsDirection
UNKNOWN
SENT
RECEIVED

SmsStatus
UNKNOWN
NEW
UNREAD
READ
SENT
FAILED
```

Driver-specific raw values universal modelga mapper orqali o‘tkazilsin.

---

# 25. RETRY VA DUPLICATE SMS

Bu juda muhim.

GET/read operations uchun retry mumkin.

Lekin:

```text
SEND_SMS
```

blind retry qilinmasin.

Sabab:

```text
SMS modemga ketgan
↓
HTTP response yo‘qolgan
↓
SDK retry qiladi
↓
recipient 2 ta SMS oladi
```

SMS yuborish natijasini:

```text
SUCCESS
FAILED
UNKNOWN
```

kabi holatlar bilan modellashtirish haqida o‘yla.

Agar modem history orqali tekshirish imkonini bersa, uncertain requestdan keyin history bilan reconcile qilish mumkin.

Documentation’da bu muammoni tushuntir.

---

# 26. SECURITY

Credentials:

```text
source code
git
README
fixtures
tests
```

ichida bo‘lmasin.

Examples:

```text
MODEMBRIDGE_HOST=192.168.0.1
MODEMBRIDGE_PASSWORD=
```

environment variable yoki secure prompt ishlatsin.

Real IMEI/IMSI/SIM raqamlarini hech qayerga ko‘chirma.

---

# 27. TESTING

Unit tests real modem talab qilmasin.

Mock/fixture ishlat.

Test:

```text
SHA256 helpers
ZTE LD password calculation
ZTE AD calculation
UTF-16BE encoding
UTF-16BE decoding
phone normalization
SMS history parsing
capability mapping
profile matching
driver probe ranking
sensitive data masking
```

Hardware tests:

```python
@pytest.mark.hardware
```

bilan alohida bo‘lsin.

Default:

```bash
pytest
```

real modemga request yubormasin.

---

# 28. CLI

Debug/diagnostic uchun optional CLI yarat:

```bash
modembridge discover

modembridge diagnose \
  --host 192.168.0.1

modembridge info \
  --host 192.168.0.1

modembridge sms send \
  --host 192.168.0.1 \
  +998991234567 \
  "Test"

modembridge sms list \
  --host 192.168.0.1
```

Password CLI argument sifatida berilmasin, chunki shell history'da qoladi.

Environment variable yoki interactive `getpass()` ishlat.

---

# 29. README

Professional GitHub/PyPI README yarat.

README structure:

```text
# ModemBridge

Universal Python SDK for cellular modems and messaging devices.

Why ModemBridge

Features

Architecture

Supported transports

Supported drivers

Supported devices

Installation

Quick Start

Auto Discovery

Send SMS

Receive SMS

Diagnostics

Multiple Modems

Adding New Modems

Device Profiles

Driver Development

Security

Roadmap

Contributing

Disclaimer

License
```

Projectning asosiy falsafasini yoz:

```text
One API. Multiple modem vendors and transports.
```

Lekin marketing copy'ni haddan tashqari ko‘paytirma.

---

# 30. SUPPORTED DEVICES

`docs/supported-devices.md` yarat.

Categories:

```text
Tested
Compatible
Experimental
Planned
```

Current hardware:

```text
Vendor: ZTE
Hardware identifier: G5BHWV1.0.0
Firmware: BD_UCELLUZG5BV1.0.0B06
Transport: HTTP
Driver: zte_goform
SMS Send: Tested
SMS Read: Tested
```

Marketing model nomi aniq tasdiqlanmagan bo‘lsa uni o‘ylab topma.

---

# 31. ADDING NEW DEVICE

Maqsad:

Agar yangi modem mavjud driver bilan compatible bo‘lsa, developer faqat:

```text
profile YAML
fixtures
tests
documentation
```

qo‘shib support bera olsin.

Yangi Python driver FAQAT protocol fundamentally boshqacha bo‘lsa kerak bo‘lsin.

Example:

```text
New ZTE Goform modem
        ↓
existing zte_goform driver
        ↓
new YAML profile
```

versus:

```text
Huawei HiLink modem
        ↓
new huawei_hilink driver
```

---

# 32. EXTERNAL DRIVER PLUGINS

Architecture kelajakda third-party drivers'ni package core'iga qo‘shmasdan install qilishga tayyor bo‘lsin.

Kelajakdagi conceptual example:

```bash
pip install modembridge-huawei
pip install modembridge-quectel
```

va ModemBridge ularni Python entry points orqali discover qila olishi mumkin.

Hozir to‘liq ecosystem qilish shart emas.

Lekin registry architecture bunga to‘sqinlik qilmasin.

Agar oson bo‘lsa `importlib.metadata.entry_points()` asosida plugin discovery implement qil.

Plugin group masalan:

```text
modembridge.drivers
```

bo‘lsin.

---

# 33. DEPENDENCIES

Minimal dependencies.

Core:

```text
requests
```

Serial optional:

```text
pyserial
```

Development:

```text
pytest
pytest-mock
ruff
```

Python:

```text
>=3.11
```

Modern `pyproject.toml`.

Package:

```bash
pip install -e .
```

bilan development mode'da ishlasin.

Optional:

```bash
pip install -e ".[serial,dev]"
```

ishlashi mumkin.

---

# 34. CODE QUALITY

Use:

```text
type hints
dataclasses where appropriate
Enums
ABC/Protocol where useful
docstrings for public API
small focused modules
dependency inversion
composition over inheritance where appropriate
```

Avoid:

```text
god classes
giant 1000-line files
vendor checks throughout core
hardcoded device model logic
global sessions
global modem state
unnecessary async
FastAPI
Redis
database
Docker dependency
```

Bu SDK.

Cloud platform emas.

---

# 35. DON'T OVERENGINEER

Architecture extensible bo‘lsin, lekin ishlamaydigan abstractionlar yaratib tashlama.

Hozirgi priority:

```text
1. current ZTE modem STILL WORKS
2. clean public API
3. driver abstraction
4. transport abstraction
5. profile system
6. diagnostics
7. tests
8. documentation
```

Future features uchun interface/extension point yetarli.

---

# 36. MIGRATION FROM EXISTING PROTOTYPE

Existing:

```text
modem_sms_test/
```

kodini avval o‘rgan.

Ishlayotgan:

```text
authentication
AD generation
SMS send
SMS history
retry behavior
encoding
```

qismlarini aniqlab ol.

Keyin ularni yangi architecture ichiga ehtiyotkorlik bilan port qil.

Existing projectni reference sifatida saqla.

Regression bo‘lmasligi kerak.

---

# 37. REAL HARDWARE VALIDATION

Unit tests tugagandan keyin current modem uchun hardware test script yarat.

Masalan:

```bash
MODEMBRIDGE_HOST=192.168.0.1 \
python examples/diagnose.py
```

va:

```bash
python examples/send_sms.py
```

SMS example foydalanuvchidan:

```text
Phone:
Message:
```

deb so‘rasin.

Test recipient hardcode qilinmasin.

---

# 38. FINAL VALIDATION

Projectni yaratib bo‘lgach:

```bash
python -m compileall src
pytest
ruff check .
```

run qil.

Package importni tekshir:

```bash
python -c "import modembridge; print(modembridge.__version__)"
```

Keyin project tree chiqar.

---

# 39. FINAL REPORT

Ish tugaganda menga qisqa, lekin aniq report ber:

```text
Created:
Implemented:
Tests:
Current real driver:
Profiles:
Auto detection:
Diagnostics:
Known limitations:
Hardware validation commands:
Next recommended driver:
```

Qaysi feature:

```text
TESTED ON REAL HARDWARE
UNIT TESTED
EXPERIMENTAL
NOT IMPLEMENTED
```

ekanligini aniq ajrat.

Hech qachon real hardware’da tekshirilmagan narsani "working" deb yozma.

---

# 40. ARCHITECTURAL TARGET

ModemBridge oxir-oqibat quyidagi modelga yetishi kerak:

```text
                    ModemBridge
                         │
              ┌──────────┴──────────┐
              │                     │
          Discovery              Manager
              │                     │
         Driver Registry            │
              │                     │
     ┌────────┼─────────┐           │
     ▼        ▼         ▼           │
 ZTE Goform Generic AT Huawei...    │
     │        │         │           │
 HTTP      Serial      HTTP         │
     │        │         │           │
     └────────┴─────────┴───────────┘
                         │
                    Unified API
                         │
             SMS / Device / Network
```

User modemni ulaydi.

ModemBridge imkon qadar:

```text
discover
→ probe
→ identify
→ select driver
→ select profile
→ expose capabilities
→ connect
```

jarayonini avtomatik bajaradi.

Maqsad har bir yangi modem uchun ModemBridge core'ni o‘zgartirish emas.

Yangi modem:

* mavjud protocolga mos bo‘lsa → profile;
* yangi protocol bo‘lsa → driver;
* yangi connection method bo‘lsa → transport.

Shu separation'ni butun project davomida qat'iy saqla.

Endi mavjud `modem_sms_test` kodini tahlil qil va `modembridge/` projectini yaratishni boshlagin.

Shu prompt bilan biz hozirgi ZTE kodini shunchaki “chiroyli package” qilmaymiz. **ModemBridge’ning birinchi driveri** qilib qo‘yamiz.

Keyinchalik rivojlanish juda tabiiy bo‘ladi:

```text
v0.1  ZTE HTTP/Goform
v0.2  Generic AT / USB
v0.3  Huawei HiLink
v0.4  multi-modem discovery
v0.5  Windows/Linux Local Agent
v1.0  stable SDK
```

---

# 41. SERIAL/AT ROADMAP (PHASED)

Serial/AT yo‘nalishi bosqichma-bosqich qo‘shiladi, lekin core API o‘zgarmasdan qoladi.

## Phase A (minimal foundation)

- `SerialTransport` bilan port ochish/yopish
- `AT` ping (`AT -> OK`) va basic timeout handling
- Device evidence yig‘ish (`ATI`, `AT+GMM`, `AT+CGMI` mavjud bo‘lsa)
- `GenericAtDriver.probe()` confidence qaytarishi

Natija:

- Discovery va probe zanjirida serial qurilma "aniqlanishi" mumkin bo‘ladi.

## Phase B (basic SMS path)

- Text mode uchun minimal SMS capability (`AT+CMGF`, `AT+CMGS`)
- Xatoliklarni unified exceptionlarga map qilish
- `supports(Capability.SMS_SEND)` ni transport/driver holatiga qarab belgilash

Natija:

- Mos AT modemlarda basic SMS send ishlashi mumkin, lekin model-specific farqlar cheklangan bo‘ladi.

## Phase C (profile-driven compatibility)

- Vendor oilalari uchun profile/quirks kengaytmasi (Quectel, SIMCom va boshqalar)
- AT buyruq farqlarini profile orqali boshqarish
- Parser va status mappingni fixture+test bilan mustahkamlash

Natija:

- Har bir yangi model uchun yangi driver yozmasdan, ko‘p holatda profile qo‘shish kifoya bo‘ladi.

## Phase D (production hardening)

- Port lock/reconnect strategiyasi
- Duplicate-send xavfini kamaytirish bo‘yicha reconcile mexanizmlari
- Hardware matrix testlari (Windows/Linux + bir nechta USB modem)

Natija:

- Serial yo‘nalishi real deploy uchun barqaror darajaga chiqadi.

## Boundary rule

- Yangi serial modem qo‘shishda ustuvor tartib:
    1. Avval profile/quirks
    2. Zarurat bo‘lsa generic AT parser kengaytmasi
    3. Faqat protokol tubdan boshqacha bo‘lsa yangi driver

Bu tartib core ichida vendor bo‘yicha `if/elif` tarqalib ketishini oldini oladi.

Undan keyin biz qurayotgan xalqaro messaging platforma `ModemBridge`ni dependency sifatida ishlatadi. Ya’ni **ModemBridge alohida open-source loyiha**, SaaS platformamiz esa uning ustidagi tijoriy mahsulot bo‘ladi.
