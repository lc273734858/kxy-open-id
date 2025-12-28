# DES 加密使用说明

本项目已集成 DES 加密算法（CBC 模式 + PKCS5 填充），用于密码等敏感信息的加解密。

## 功能特性

- **加密算法**: DES (Data Encryption Standard)
- **工作模式**: CBC (Cipher Block Chaining)
- **填充方式**: PKCS5
- **输出格式**: 十六进制字符串
- **字符编码**: UTF-8（支持中文等多语言字符）

## 快速开始

### 1. 使用全局函数（推荐）

```python
from app.utils.auth_utils import encrypt_password, decrypt_password

# 加密密码
original = "myPassword123"
encrypted = encrypt_password(original)
print(f"加密结果: {encrypted}")
# 输出: 加密结果: efaf2f5c9088e4c51298ed9cd17eb04b

# 解密密码
decrypted = decrypt_password(encrypted)
print(f"解密结果: {decrypted}")
# 输出: 解密结果: myPassword123
```

### 2. 使用类实例（自定义密钥）

```python
from app.utils.auth_utils import DesEncryption

# 使用默认密钥
crypto = DesEncryption()
encrypted = crypto.encrypt("Hello World")
decrypted = crypto.decrypt(encrypted)

# 使用自定义密钥（必须是 8 字节）
crypto_custom = DesEncryption(key="12345678")
encrypted = crypto_custom.encrypt("Secret Message")
decrypted = crypto_custom.decrypt(encrypted)
```

## 配置说明

### 环境变量

在 `.env` 文件中配置加密密钥：

```bash
# DES 加密密钥（8 字节）
DES_KEY=f87e43f9
```

如果不配置，将使用默认密钥 `f87e43f9`。

### 配置文件

密钥配置在 `app/config.py` 中：

```python
DES_KEY = os.getenv("DES_KEY", "f87e43f9")
```

## API 参考

### encrypt_password(password: str) -> str

加密密码字符串。

**参数:**
- `password` (str): 明文密码

**返回:**
- `str`: 十六进制编码的加密字符串

**示例:**
```python
encrypted = encrypt_password("admin@123")
# 返回: "fd5c5e66c2906e70..."
```

### decrypt_password(encrypted_text: str) -> str

解密已加密的字符串。

**参数:**
- `encrypted_text` (str): 十六进制编码的加密字符串

**返回:**
- `str`: 解密后的明文字符串

**示例:**
```python
decrypted = decrypt_password("fd5c5e66c2906e70")
# 返回: "admin@123"
```

### DesEncryption 类

#### `__init__(key: str = None)`

初始化加密实例。

**参数:**
- `key` (str, 可选): 8 字节加密密钥。如果不提供，使用配置中的 DES_KEY

**异常:**
- `ValueError`: 当密钥长度不是 8 字节时抛出

#### `encrypt(password: str) -> str`

加密字符串。

#### `decrypt(text: str) -> str`

解密字符串。

## 注意事项

1. **密钥长度**: DES 密钥必须是 **8 字节**（8 个字符）
2. **生产环境**: 务必在生产环境中修改默认密钥
3. **安全性**: DES 算法已被认为不够安全，仅适用于兼容性需求。对于新项目，建议使用 AES 等更安全的算法
4. **字符编码**: 支持 UTF-8 编码，可以加密中文等多语言字符
5. **输出格式**: 加密结果为十六进制字符串，便于存储和传输

## 测试

运行测试脚本验证加密功能：

```bash
python test_des_encryption.py
```

## 与原有认证系统的关系

项目中同时保留了两种密码处理方式：

1. **bcrypt 哈希**（`hash_password` / `verify_password`）
   - 用于不可逆的密码存储
   - 适用于用户认证场景

2. **DES 加密**（`encrypt_password` / `decrypt_password`）
   - 用于可逆的密码加密
   - 适用于需要解密的场景（如第三方系统对接）

根据实际业务需求选择合适的方式。

## 示例代码

更多使用示例请参考 `test_des_encryption.py` 文件。
