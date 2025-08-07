##  Thư viện Admin SDK dành cho các module.


### Cài đặt:
```bash
 $ pip3 install mobio-admin-sdk
 ```

### Chức năng:
* Verify token 


### Sử dụng:

##### 1. Verify token:
   ```python
    from mobio.sdks.admin import MobioAdminSDK

    MobioAdminSDK().config(
        admin_host="",	# admin host
        redis_uri="",	# redis uri
        module_use="",	# liên hệ admin để khai báo tên của module
        module_encrypt="",	# liên hệ admin để lấy mã
        api_admin_version="api/v2.1",   # danh sách api có thể sử dụng ["v1.0", "api/v2.0", "api/v2.1"]
    )
    auth = MobioAdminSDK().create_mobio_verify_token()
    
    @service_mod.route(url_path, methods=["get"])
    @auth.verify_token
    @try_catch_error
    def get_config(merchant_id):
        return build_response_message(Config(merchant_id).get_data())
   ```

##### 2. Merchant config:
   ```python
    from mobio.sdks.admin import MobioAdminSDK

    MobioAdminSDK().request_get_merchant_config_host(
            merchant_id,
            key=None,       # key muốn lấy giá trị
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
        )
    MobioAdminSDK().request_get_merchant_config_other(
            merchant_id,
            list_key=None,       # danh sách key muốn lấy giá trị
            admin_version=None, # api version admin muốn gọi trong trường hợp chỉ có version đó hỗ trợ
        )
    
    MobioAdminSDK().request_get_partner_info(
            partner_key=None,
            decrypt_data=False,
    )   # result: { "code": 200, "data": ""}, {"code": 400, "message": "key not found"}, {"code": 412, "message": "key not active"}, {"code": 413, "message": "key expire"}
        
    MobioAdminSDK().request_get_config_time_and_currency(merchant_id="")   
    # result: { 
    #      "config_time": {
    #             "timezone": 7,
    #             "text": "(UTC+07:00) Bangkok, Hanoi, Jakarta",
    #             "location": "Asia/Saigon",
    #         },
    #         "currency_code": "vnd"
    # }
    
    MobioAdminSDK().convert_datetime_to_format(merchant_id: str, from_date: datetime.datetime,
                                   format_type: int, tz=None, lang=None)
    """
    :param merchant_id: 
    :param from_date: datetime
    :param format_type: FORMAT_ddmm = 1 FORMAT_ddmmYYYY = 2 FORMAT_ddmmYYYYHHMM = 3
    :param tz: number hour
    :param lang: vi en
    :return: string format date 
    """
    
    MobioAdminSDK().gen_jwt_anonymous_user(merchant_id: str, data_jwt: dict, session_time=None)
    """
    :param merchant_id: 
    :param data_jwt: dict, là dữ liệu sẽ được đóng gói vào trong jwt, sau này từ request của client có thể đọc thông tin này.
    :param session_time: int, giây, thời gian hợp lệ của jwt 
    :return: string jwt 
    """
    



```

#### Log - 1.0.1
    - release sdk
#### Log - 1.0.2
    - Kiểm tra license server còn hạn sử dụng hay không 
#### Log - 1.0.3
    - Fix lỗi đọc file license 
#### Log - 1.0.4
    - Authen app key data out 
#### Log - 1.0.5
    - update lib kafka v2
#### Log - 1.0.6
    - encrypt, decrypt field by config
#### Log - 1.0.7
    - kiểm tra thông tin field trước khi encrypt, decrypt 
#### Log - 1.0.8
    - sdk tự lấy thông tin REDIS_URI  
#### Log - 1.0.9
    - bỏ encoding trong json.loads  
#### Log - 1.0.10
    - thêm hàm lấy cấu hình múi giờ và tiền tệ
    - cập nhật kết nối redis theo loại
#### Log - 1.0.11
    - thêm hàm định dạng thời gian từ date thành string theo chuẩn
#### Log - 1.0.12
    - thêm hàm gen token jwt anonymous   

#### Log - 1.0.18
    - cập nhật logic mã hóa field   
#### Log - 1.0.19
    - thêm mã hóa kiểu dữ liệu bất kỳ

