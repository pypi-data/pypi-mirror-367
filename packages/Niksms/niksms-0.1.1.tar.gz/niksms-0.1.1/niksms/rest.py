import requests
from typing import List, Optional, Dict, Any

class NiksmsRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()

    def _post(self, path: str, data: Dict[str, Any]) -> Any:
        url = f"{self.base_url}/api/v1/web-service/{path}"
        data = {**data, 'ApiKey': self.api_key}
        resp = self.session.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    def send_single(self, sender_number: str, phone: str, message: str, message_id: Optional[str]=None, send_date: Optional[str]=None, send_type: Optional[int]=None) -> Any:
        data = {
            'SenderNumber': sender_number,
            'Phone': phone,
            'Message': message,
        }
        if message_id: data['MessageId'] = message_id
        if send_date: data['SendDate'] = send_date
        if send_type: data['SendType'] = send_type
        return self._post('sms/send/single', data)

    def send_group(self, sender_number: str, message: str, recipients: List[Dict[str, str]], send_date: Optional[str]=None, send_type: Optional[int]=None) -> Any:
        data = {
            'SenderNumber': sender_number,
            'Message': message,
            'Recipients': recipients,
        }
        if send_date: data['SendDate'] = send_date
        if send_type: data['SendType'] = send_type
        return self._post('sms/send/group', data)

    def send_ptp(self, sender_number: str, recipients: List[Dict[str, str]], send_date: Optional[str]=None, send_type: Optional[int]=None) -> Any:
        data = {
            'SenderNumber': sender_number,
            'Recipients': recipients,
        }
        if send_date: data['SendDate'] = send_date
        if send_type: data['SendType'] = send_type
        return self._post('sms/send/ptp', data)

    def send_otp(self, sender_number: str, phone: str, message: str, message_id: Optional[str]=None, send_date: Optional[str]=None, send_type: Optional[int]=None) -> Any:
        data = {
            'SenderNumber': sender_number,
            'Phone': phone,
            'Message': message,
        }
        if message_id: data['MessageId'] = message_id
        if send_date: data['SendDate'] = send_date
        if send_type: data['SendType'] = send_type
        return self._post('sms/send/otp', data)

    def get_credit(self) -> Any:
        return self._post('panel/credit', {})

    def get_panel_expire_date(self) -> Any:
        return self._post('panel/expire-date', {})

    def get_sms_status(self, message_ids: List[str]) -> Any:
        data = {'MessageIds': message_ids}
        return self._post('sms/status/niksms', data)

    def get_sms_operator_status(self, message_ids: List[str]) -> Any:
        data = {'MessageIds': message_ids}
        return self._post('sms/status/operator', data) 