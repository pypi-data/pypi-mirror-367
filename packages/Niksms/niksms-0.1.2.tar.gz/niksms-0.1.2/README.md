# niksms Python SDK

این پکیج برای اتصال آسان به وب‌سرویس پیامک Kendez.NikSms (نسخه REST و gRPC) در پایتون طراحی شده است.

This package provides an easy-to-use Python SDK for connecting to the Kendez.NikSms SMS web service (REST & gRPC).

## نصب / Installation

```bash
pip install niksms
```

## ویژگی‌ها / Features
- اتصال به REST API و gRPC
- قابل استفاده در پروژه‌های مختلف پایتون
- بدون وابستگی به آدرس ثابت (آدرس سرویس را خودتان وارد می‌کنید)

## استفاده سریع / Quick Usage

### REST Example
```python
from niksms import NiksmsRestClient

client = NiksmsRestClient(base_url="https://webservice.niksms.com", api_key="YOUR_API_KEY")

# ارسال پیامک تکی
result = client.send_single(sender_number="5000...", phone="0912...", message="کد تایید شما: 1234")
print(result)

# دریافت اعتبار
credit = client.get_credit()
print(credit)
```

### gRPC Example
```python
from niksms import NiksmsGrpcClient

client = NiksmsGrpcClient(grpc_url="grpc.niksms.com:443", api_key="YOUR_API_KEY")

# ارسال پیامک تکی
result = client.send_single(sender_number="5000...", phone="0912...", message="کد تایید شما: 1234")
print(result)

# دریافت اعتبار
credit = client.get_credit()
print(credit)
```
