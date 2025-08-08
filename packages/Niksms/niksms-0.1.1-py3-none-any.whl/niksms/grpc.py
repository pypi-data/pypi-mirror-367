import grpc
from . import Service_pb2, Service_pb2_grpc
from typing import List, Optional

class NiksmsGrpcClient:
    def __init__(self, grpc_url: str, api_key: str):
        self.grpc_url = grpc_url
        self.api_key = api_key
        self.channel = grpc.insecure_channel(grpc_url)
        self.stub = Service_pb2_grpc.GrpcWebServiceStub(self.channel)

    def send_single(self, sender_number: str, phone: str, message: str, message_id: Optional[str]=None, send_date: Optional[str]=None, send_type: Optional[int]=None):
        req = Service_pb2.GrpcWebServiceSendSmsSingleRequest(
            ApiKey=self.api_key,
            SenderNumber=sender_number,
            Phone=phone,
            Message=message,
        )
        if message_id: req.MessageId = message_id
        if send_type: req.SendType = send_type
        # send_date: باید به google.protobuf.Timestamp تبدیل شود (در نسخه بعدی اضافه می‌شود)
        grpc_req = Service_pb2.GrpcWebService_SendSingleReq(Request=req)
        return self.stub.SendSingle(grpc_req)

    def send_group(self, sender_number: str, message: str, recipients: List[dict], send_date: Optional[str]=None, send_type: Optional[int]=None):
        recs = [Service_pb2.GrpcWebServiceGroupSmsRecipient(Phone=r['Phone'], MessageId=r['MessageId']) for r in recipients]
        req = Service_pb2.GrpcWebServiceSendSmsGroupRequest(
            ApiKey=self.api_key,
            SenderNumber=sender_number,
            Message=message,
            Recipients=recs,
        )
        if send_type: req.SendType = send_type
        grpc_req = Service_pb2.GrpcWebService_SendGroupReq(Request=req)
        return self.stub.SendGroup(grpc_req)

    def send_ptp(self, sender_number: str, recipients: List[dict], send_date: Optional[str]=None, send_type: Optional[int]=None):
        recs = [Service_pb2.GrpcWebServicePtpSmsRecipient(Message=r['Message'], Phone=r['Phone'], MessageId=r['MessageId']) for r in recipients]
        req = Service_pb2.GrpcWebServiceSendSmsPtpRequest(
            ApiKey=self.api_key,
            SenderNumber=sender_number,
            Recipients=recs,
        )
        if send_type: req.SendType = send_type
        grpc_req = Service_pb2.GrpcWebService_SendPtpReq(Request=req)
        return self.stub.SendPtp(grpc_req)

    def send_otp(self, sender_number: str, phone: str, message: str, message_id: Optional[str]=None, send_date: Optional[str]=None, send_type: Optional[int]=None):
        req = Service_pb2.GrpcWebServiceSendSmsOtpRequest(
            ApiKey=self.api_key,
            SenderNumber=sender_number,
            Phone=phone,
            Message=message,
        )
        if message_id: req.MessageId = message_id
        if send_type: req.SendType = send_type
        grpc_req = Service_pb2.GrpcWebService_SendOtpReq(Request=req)
        return self.stub.SendOtp(grpc_req)

    def get_credit(self):
        req = Service_pb2.GrpcWebServiceGetCreditRequest(ApiKey=self.api_key)
        grpc_req = Service_pb2.GrpcWebService_GetCreditReq(Request=req)
        return self.stub.GetCredit(grpc_req)

    def get_panel_expire_date(self):
        req = Service_pb2.GrpcWebServiceGetPanelExpireDateRequest(ApiKey=self.api_key)
        grpc_req = Service_pb2.GrpcWebService_GetPanelExpireDateReq(Request=req)
        return self.stub.GetPanelExpireDate(grpc_req)

    def get_sms_status(self, message_ids: List[str]):
        req = Service_pb2.GrpcWebServiceGetSmsStatusRequest(ApiKey=self.api_key, MessageIds=message_ids)
        grpc_req = Service_pb2.GrpcWebService_SmsStatusReq(Request=req)
        return self.stub.SmsStatus(grpc_req)

    def get_sms_operator_status(self, message_ids: List[str]):
        req = Service_pb2.GrpcWebServiceGetSmsOperatorStatusRequest(ApiKey=self.api_key, MessageIds=message_ids)
        grpc_req = Service_pb2.GrpcWebService_SmsOperatorStatusReq(Request=req)
        return self.stub.SmsOperatorStatus(grpc_req) 