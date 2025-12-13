"""
File Handler Utility
Xử lý đọc/ghi file cho các thuật toán mã hóa
"""

import base64


def read_text_file(filepath, encoding='utf-8'):
    """
    Đọc file text
    Returns: str
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")


def write_text_file(filepath, content, encoding='utf-8'):
    """Ghi file text"""
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Error writing file: {str(e)}")


def read_binary_file(filepath):
    """
    Đọc file binary
    Returns: bytes
    """
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading binary file: {str(e)}")


def write_binary_file(filepath, data):
    """Ghi file binary"""
    try:
        with open(filepath, 'wb') as f:
            f.write(data)
    except Exception as e:
        raise Exception(f"Error writing binary file: {str(e)}")


def hex_to_bytes(hex_string):
    """
    Chuyển hex string thành bytes
    hex_string: '48656c6c6f' -> b'Hello'
    """
    try:
        # Remove spaces and make lowercase
        hex_string = hex_string.replace(' ', '').replace('\n', '').lower()
        return bytes.fromhex(hex_string)
    except Exception as e:
        raise ValueError(f"Invalid hex string: {str(e)}")


def bytes_to_hex(data):
    """
    Chuyển bytes thành hex string
    b'Hello' -> '48656c6c6f'
    """
    return data.hex()


def base64_to_bytes(b64_string):
    """Chuyển base64 string thành bytes"""
    try:
        return base64.b64decode(b64_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {str(e)}")


def bytes_to_base64(data):
    """Chuyển bytes thành base64 string"""
    return base64.b64encode(data).decode('utf-8')


def format_hex_output(hex_string, line_length=64):
    """
    Format hex string để dễ đọc
    Chia thành các dòng
    """
    lines = []
    for i in range(0, len(hex_string), line_length):
        lines.append(hex_string[i:i + line_length])
    return '\n'.join(lines)


# Specific handlers for DES/AES

def read_des_key_from_hex(hex_string):
    """
    Đọc DES key từ hex string
    Returns: 8 bytes
    """
    key = hex_to_bytes(hex_string)
    if len(key) != 8:
        raise ValueError(f"DES key must be 8 bytes (16 hex chars), got {len(key)}")
    return key


def read_des_iv_from_hex(hex_string):
    """
    Đọc DES IV từ hex string
    Returns: 8 bytes
    """
    iv = hex_to_bytes(hex_string)
    if len(iv) != 8:
        raise ValueError(f"DES IV must be 8 bytes (16 hex chars), got {len(iv)}")
    return iv


def read_aes_key_from_hex(hex_string, key_size=128):
    """
    Đọc AES key từ hex string
    key_size: 128, 192, or 256 bits
    Returns: bytes
    """
    key = hex_to_bytes(hex_string)
    expected_length = key_size // 8
    
    if len(key) != expected_length:
        raise ValueError(f"AES-{key_size} key must be {expected_length} bytes "
                        f"({expected_length * 2} hex chars), got {len(key)}")
    return key


def read_aes_iv_from_hex(hex_string):
    """
    Đọc AES IV từ hex string
    Returns: 16 bytes
    """
    iv = hex_to_bytes(hex_string)
    if len(iv) != 16:
        raise ValueError(f"AES IV must be 16 bytes (32 hex chars), got {len(iv)}")
    return iv


def save_encrypted_output(filepath, ciphertext_hex, iv_hex=None, mode='ECB'):
    """
    Lưu output mã hóa theo format chuẩn
    Format:
    Mode: ECB/CBC
    IV: <hex> (nếu có)
    Ciphertext:
    <hex data>
    """
    lines = []
    lines.append(f"Mode: {mode}")
    
    if iv_hex:
        lines.append(f"IV: {iv_hex}")
    
    lines.append("Ciphertext:")
    lines.append(format_hex_output(ciphertext_hex))
    
    content = '\n'.join(lines)
    write_text_file(filepath, content)


def parse_encrypted_input(filepath):
    """
    Parse file mã hóa
    Returns: dict with 'mode', 'iv', 'ciphertext'
    """
    content = read_text_file(filepath)
    lines = content.strip().split('\n')
    
    result = {
        'mode': 'ECB',
        'iv': None,
        'ciphertext': ''
    }
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('Mode:'):
            result['mode'] = line.split(':', 1)[1].strip()
        
        elif line.startswith('IV:'):
            result['iv'] = line.split(':', 1)[1].strip()
        
        elif line.startswith('Ciphertext:'):
            # Đọc tất cả các dòng sau đó
            ciphertext_lines = []
            i += 1
            while i < len(lines):
                ciphertext_lines.append(lines[i].strip())
                i += 1
            result['ciphertext'] = ''.join(ciphertext_lines)
            break
        
        i += 1
    
    return result


if __name__ == "__main__":
    # Test
    print("Testing file_handler utilities...")
    
    # Test hex conversion
    test_bytes = b"Hello World"
    hex_str = bytes_to_hex(test_bytes)
    print(f"Bytes to hex: {hex_str}")
    
    back_to_bytes = hex_to_bytes(hex_str)
    print(f"Hex to bytes: {back_to_bytes}")
    
    assert test_bytes == back_to_bytes, "Conversion failed!"
    print("✓ Hex conversion test passed!")