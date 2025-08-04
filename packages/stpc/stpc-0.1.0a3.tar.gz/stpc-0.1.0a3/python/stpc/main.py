import struct
from typing import Tuple, Iterator, Optional, Set
import stpc
from dataclasses import dataclass, field
from .time_sync import Time
import re
import base64
import ipaddress
import hashlib
import datetime
from datetime import datetime
from .micro_logger import Micro_Logger
import socket

class CRLRevokedError(Exception):
    pass

# Initialize time instance
time_get = Time()
_ = time_get.get_time()  # Предварительная инициализация NTP-клиента

class Utils:
    @staticmethod
    def pack_blocks(*blocks: Tuple[int, bytes]) -> bytes:
        packed_data = bytearray()
        for tag, data in blocks:
            if not 0x00 <= tag <= 0xFFFFFFFFFFFFFFFF:
                raise ValueError("Tag must be 0x00..0xFFFFFFFFFFFFFFFF")
            packed_data.extend(struct.pack('>BH', tag, len(data)) + data)

        size_header = struct.pack('>Q', len(packed_data))
        return size_header + packed_data

    @staticmethod
    def unpack_blocks_safe(
        data: bytes,
        max_total_length: int = 16 * 1024 * 1024,
        max_block_length: int = 1024 * 1024,
        allowed_tags: Optional[Set[int]] = None
    ) -> Iterator[Tuple[int, bytes]]:
        try:
            if len(data) < 8:
                raise ValueError()
            total_length = struct.unpack('>Q', data[:8])[0]
            if total_length > max_total_length:
                raise ValueError()
            if len(data) - 8 < total_length:
                raise ValueError()
            payload = data[8:8+total_length]
            offset = 0
            while offset < len(payload):
                if offset + 3 > len(payload):
                    raise ValueError()
                tag, length = struct.unpack_from('>BH', payload, offset)
                offset += 3
                if not 0x00 <= tag <= 0xFFFFFFFFFFFFFFFF:
                    raise ValueError()
                if allowed_tags is not None and tag not in allowed_tags:
                    raise ValueError()
                if length > max_block_length:
                    raise ValueError()
                if offset + length > len(payload):
                    raise ValueError()
                yield tag, payload[offset:offset+length]
                offset += length
        except Exception:
            raise ValueError("Invalid packet format")


@dataclass
class SignatureAlgorithms:
    algorithms: list[tuple] = field(default_factory=lambda: [
        (0x01, "RSA", stpc.stpc.Rsa),
        (0x02, "Ed25519", stpc.stpc.Ed25519),
        (0x03, "Falcon512", stpc.stpc.Falcon512),
        (0x04, "Falcon1024", stpc.stpc.Falcon1024),
    ])

    def get_by_id(self, alg_id: int) -> tuple[str, type]:
        for _id, name, cls in self.algorithms:
            if _id == alg_id:
                if name == "RSA":
                    print("WARNING! RSA signer is deprecated because it is vulnerable to Kocher's Timing Attack.")
                return name, cls
        raise ValueError(f"Unknown algorithm ID: {alg_id}")


class Certificates:
    @staticmethod
    def _validate_utf8(field: bytes, name: str, max_len=256):
        try:
            text = field.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError(f"{name} must be valid UTF-8")
        if len(text) > max_len:
            raise ValueError(f"{name} too long (max {max_len} chars)")
        if not re.match(r'^[\w\s\-\.]*$', text):
            raise ValueError(f"{name} contains invalid characters")

    @staticmethod
    def _validate_region(region_id: bytes):
        if len(region_id) != 2 or not region_id.decode().isalpha():
            raise ValueError("region_id must be 2-letter country code")

    @staticmethod
    def _validate_ip(ip: bytes):
        try:
            ip_str = ip.decode()
            if ip_str.lower() == "localhost":
                return
            ipaddress.ip_address(ip_str)
        except Exception:
            raise ValueError("Invalid IP address format (expected IPv4, IPv6 or 'localhost')")

    @staticmethod
    def generate_cert(
        alg_id: int,
        issuer: bytes,
        IP: bytes,
        First_Name: bytes,
        Last_name: bytes,
        Organization_unit: bytes,
        Organization_name: bytes,
        city: bytes,
        region_id: bytes,
        public_key: bytes,
        time_expire: int,
        signing_key: bytes
    ) -> bytes:
        Certificates._validate_ip(IP)
        Certificates._validate_utf8(First_Name, "First_Name")
        Certificates._validate_utf8(Last_name, "Last_name")
        Certificates._validate_utf8(Organization_unit, "Organization_unit")
        Certificates._validate_utf8(Organization_name, "Organization_name")
        Certificates._validate_utf8(city, "city")
        Certificates._validate_region(region_id)
        
        not_before_time = int(time_get.get_time()).to_bytes(8, byteorder="big")
        not_after_time = int(time_get.get_time() + time_expire).to_bytes(8, byteorder="big")
        
        version = stpc.stpc.__version__.encode()
        serial_number = hashlib.sha3_256(public_key).hexdigest().encode()
        
        subject = Utils.pack_blocks(
            (0x01, IP),
            (0x02, First_Name),
            (0x03, Last_name),
            (0x04, Organization_unit),
            (0x05, Organization_name),
            (0x06, city),
            (0x07, region_id),
            (0x08, serial_number),
            (0x09, not_before_time),
            (0xA, not_after_time),
            (0xB, public_key)
        )

        _, alg_class = SignatureAlgorithms().get_by_id(alg_id)
        alg_id_bytes = alg_id.to_bytes(8, byteorder="big")

        signature = alg_class.sign(subject, signing_key)

        cert = Utils.pack_blocks(
            (0x01, version),
            (0x02, alg_id_bytes),
            (0x03, issuer),
            (0x04, subject),
            (0x05, signature)
        )
        return cert

    @staticmethod
    def serialize_cert(cert: bytes) -> str:
        b64 = base64.b64encode(cert).decode('ascii')
        blocks = [b64[i:i + 70] + "\r\n" for i in range(0, len(b64), 70)]
        return (
            "--------------------------BEGIN-STPC-CERT----------------------------\r\n"
            + "".join(blocks) +
            "---------------------------END-STPC-CERT-----------------------------\r\n"
        )

    @staticmethod
    def deserialize_cert(pem: str) -> bytes:
        lines = pem.strip().splitlines()
        begin = "--------------------------BEGIN-STPC-CERT----------------------------"
        end = "---------------------------END-STPC-CERT-----------------------------"
        if lines[0] != begin or lines[-1] != end:
            raise ValueError("Invalid certificate format")
        b64_data = "".join(lines[1:-1]).replace("\r", "")
        return base64.b64decode(b64_data)

    @staticmethod
    def parse_cert(cert_bytes: bytes, trusted_key: Optional[bytes] = None, CRL_list: Optional[bytes] = None) -> dict:
        fields = {
            0x01: "version",
            0x02: "alg_id",
            0x03: "issuer",
            0x04: "subject",
            0x05: "signature"
        }
        parsed = {v: None for v in fields.values()}
        for tag, val in Utils.unpack_blocks_safe(cert_bytes):
            key = fields.get(tag)
            if key:
                parsed[key] = val

        alg_id = int.from_bytes(parsed["alg_id"], byteorder="big")
        _, alg_class = SignatureAlgorithms().get_by_id(alg_id)

        # Извлекаем public_key из subject
        subject_parsed = {}
        public_key = None
        subject_tags = {
            0x01: "IP",
            0x02: "First_Name",
            0x03: "Last_name",
            0x04: "Organization_unit",
            0x05: "Organization_name",
            0x06: "City",
            0x07: "Region_ID",
            0x08: "Serial_Number",
            0x09: "not_before_time",
            0xA: "not_after_time",
            0xB: "public_key"
        }
        
        for tag, val in Utils.unpack_blocks_safe(parsed["subject"]):
                key = subject_tags.get(tag, f"UNKNOWN_{tag:02X}")
                if tag in (0x09, 0xA):  # Временные метки
                    subject_parsed[key] = int.from_bytes(val, byteorder="big")
                elif tag == 0xB:  # public_key
                    public_key = val
                    subject_parsed[key] = base64.b64encode(val).decode('ascii')
                else:
                    # Декодируем строковые поля из байтов
                    try:
                        subject_parsed[key] = val.decode('utf-8')
                    except UnicodeDecodeError:
                        subject_parsed[key] = val.hex()
                        
                        
        if not public_key:
            raise ValueError("Certificate missing public_key in subject")

        if trusted_key and not alg_class.verify(parsed["subject"], parsed["signature"], trusted_key):
            raise ValueError("Invalid signature")

        now = int(time_get.get_time())
        
        if now < subject_parsed["not_before_time"]:
            raise ValueError("Certificate not yet valid")
        if now > subject_parsed["not_after_time"]:
            raise ValueError("Certificate expired")

        if CRL_list:
            dat = CRL.check_SN(CRL_list, subject_parsed["Serial_Number"].encode(), trusted_key)
            if dat["revoked"]:
                raise CRLRevokedError(f"Certificate revoked by CRL. Reason: {dat['reason']}. Time revoked: {datetime.fromtimestamp(dat['timeset']).strftime('%Y-%m-%d %H:%M:%S')}")

        return {
            "version": parsed["version"].decode(),
            "issuer": parsed["issuer"].decode(),
            "algorithm": alg_class.__name__,
            "subject": subject_parsed,
        }


class RootCertificates:
    @staticmethod
    def _validate_utf8(field: bytes, name: str, max_len=256):
        try:
            text = field.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError(f"{name} must be valid UTF-8")
        if len(text) > max_len:
            raise ValueError(f"{name} too long (max {max_len} chars)")
        if not re.match(r'^[\w\s\-\.]*$', text):
            raise ValueError(f"{name} contains invalid characters")

    @staticmethod
    def _validate_region(region_id: bytes):
        if len(region_id) != 2 or not region_id.decode().isalpha():
            raise ValueError("region_id must be 2-letter country code")

    @staticmethod
    def generate_cert(
        alg_id: int,
        issuer: bytes,
        First_Name: bytes,
        Last_name: bytes,
        Organization_unit: bytes,
        Organization_name: bytes,
        city: bytes,
        region_id: bytes,
        public_key: bytes,
        time_expire: int,
        signing_key: bytes
    ) -> bytes:
        RootCertificates._validate_utf8(First_Name, "First_Name")
        RootCertificates._validate_utf8(Last_name, "Last_name")
        RootCertificates._validate_utf8(Organization_unit, "Organization_unit")
        RootCertificates._validate_utf8(Organization_name, "Organization_name")
        RootCertificates._validate_utf8(city, "city")
        RootCertificates._validate_region(region_id)
        
        not_before_time = int(time_get.get_time()).to_bytes(8, byteorder="big")
        not_after_time = int(time_get.get_time() + time_expire).to_bytes(8, byteorder="big")
        
        version = stpc.stpc.__version__.encode()
        
        subject = Utils.pack_blocks(
            (0x01, First_Name),
            (0x02, Last_name),
            (0x03, Organization_unit),
            (0x04, Organization_name),
            (0x05, city),
            (0x06, region_id),
            (0x07, not_before_time),
            (0x08, not_after_time),
            (0x09, b"ROOT_CA"),
            (0xA, public_key)
        )

        _, alg_class = SignatureAlgorithms().get_by_id(alg_id)
        alg_id_bytes = alg_id.to_bytes(8, byteorder="big")

        signature = alg_class.sign(subject, signing_key)

        cert = Utils.pack_blocks(
            (0x01, version),
            (0x02, alg_id_bytes),
            (0x03, issuer),
            (0x04, subject),
            (0x05, b"ROOT_CA"),
            (0x06, signature)
        )
        return cert

    @staticmethod
    def serialize_cert(cert: bytes) -> str:
        b64 = base64.b64encode(cert).decode('ascii')
        blocks = [b64[i:i + 70] + "\r\n" for i in range(0, len(b64), 70)]
        return (
            "-------------------------BEGIN-STPC-ROOT-CERT------------------------\r\n"
            + "".join(blocks) +
            "--------------------------END-STPC-ROOT-CERT-------------------------\r\n"
        )

    @staticmethod
    def deserialize_cert(pem: str) -> bytes:
        lines = pem.strip().splitlines()
        begin = "-------------------------BEGIN-STPC-ROOT-CERT------------------------"
        end = "--------------------------END-STPC-ROOT-CERT-------------------------"
        if lines[0] != begin or lines[-1] != end:
            raise ValueError("Invalid certificate format")
        b64_data = "".join(lines[1:-1]).replace("\r", "")
        return base64.b64decode(b64_data)

    @staticmethod
    def parse_cert(cert_bytes: bytes) -> dict:
        fields = {
            0x01: "version",
            0x02: "alg_id",
            0x03: "issuer",
            0x04: "subject",
            0x05: "ROOT_CA",
            0x06: "signature"
        }
        parsed = {v: None for v in fields.values()}
        for tag, val in Utils.unpack_blocks_safe(cert_bytes):
            key = fields.get(tag)
            if key:
                parsed[key] = val

        alg_id = int.from_bytes(parsed["alg_id"], byteorder="big")
        _, alg_class = SignatureAlgorithms().get_by_id(alg_id)

        # Извлекаем public_key из subject
        subject_parsed = {}
        public_key = None
        subject_tags = {
            0x01: "First_Name",
            0x02: "Last_name",
            0x03: "Organization_unit",
            0x04: "Organization_name",
            0x05: "City",
            0x06: "Region_ID",
            0x07: "not_before_time",
            0x08: "not_after_time",
            0x09: "ROOT_CA",
            0xA: "public_key"
        }
        
        for tag, val in Utils.unpack_blocks_safe(parsed["subject"]):
                key = subject_tags.get(tag, f"UNKNOWN_{tag:02X}")
                if tag in (0x07, 0x08):  # Временные метки
                    subject_parsed[key] = int.from_bytes(val, byteorder="big")
                elif tag == 0xA:  # public_key
                    public_key = val
                    subject_parsed[key] = base64.b64encode(val).decode('ascii')
                else:
                    # Декодируем строковые поля из байтов
                    try:
                        subject_parsed[key] = val.decode('utf-8')
                    except UnicodeDecodeError:
                        subject_parsed[key] = val.hex()
        

        if not public_key:
            raise ValueError("RootCA certificate missing public_key in subject")

        # Проверяем подпись своим же публичным ключом
        if not alg_class.verify(parsed["subject"], parsed["signature"], public_key):
            raise ValueError("Invalid RootCA signature (self-signed check failed)")

        now = int(time_get.get_time())          
        
        if now < subject_parsed["not_before_time"]:
            raise ValueError("Certificate not yet valid")
        if now > subject_parsed["not_after_time"]:
            raise ValueError("Certificate expired")

        return {
            "version": parsed["version"].decode(),
            "issuer": parsed["issuer"].decode(),
            "algorithm": alg_class.__name__,
            "subject": subject_parsed,
        }


class CRL:
    @staticmethod
    def generate_CRL(
        revoked_certificates: list[tuple[bytes, bytes, bytes]],
        issuer: bytes,
        signing_key: bytes,
        alg_id: int
    ) -> bytes:
        now = int(time_get.get_time()).to_bytes(8, "big")
        version = stpc.stpc.__version__.encode()

        # Собираем блоки отозванных сертификатов
        revoked_blocks = []
        for i, (serial, timestamp, reason) in enumerate(revoked_certificates, 1):
            # Каждый отозванный сертификат - это блок (index, serial, timestamp, reason)
            cert_block = Utils.pack_blocks(
                (0x10, serial),
                (0x11, timestamp),
                (0x12, reason)
            )
            revoked_blocks.append((i, cert_block))

        revoked_data = Utils.pack_blocks(*revoked_blocks)

        tbs = Utils.pack_blocks(
            (0x01, version),
            (0x02, issuer),
            (0x03, now),
            (0x04, revoked_data)
        )

        _, alg_class = SignatureAlgorithms().get_by_id(alg_id)
        signature = alg_class.sign(tbs, signing_key)

        crl = Utils.pack_blocks(
            (0x01, version),
            (0x02, issuer),
            (0x03, alg_id.to_bytes(8, "big")),
            (0x04, now),
            (0x05, revoked_data),
            (0x06, signature)
        )
        return crl

    @staticmethod
    def serialize_CRL(crl: bytes) -> str:
        b64 = base64.b64encode(crl).decode('ascii')
        blocks = [b64[i:i + 70] + "\r\n" for i in range(0, len(b64), 70)]
        return (
            "--------------------------BEGIN-STPC-CRL-----------------------------\r\n"
            + "".join(blocks) +
            "---------------------------END-STPC-CRL------------------------------\r\n"
        )

    @staticmethod
    def deserialize_CRL(pem: str) -> bytes:
        lines = pem.strip().splitlines()
        begin = "--------------------------BEGIN-STPC-CRL-----------------------------"
        end = "---------------------------END-STPC-CRL------------------------------"
        if lines[0] != begin or lines[-1] != end:
            raise ValueError("Invalid CRL format")
        b64_data = "".join(lines[1:-1]).replace("\r", "")
        return base64.b64decode(b64_data)

    @staticmethod
    def check_SN(crl: bytes, serial_number: bytes, public_key: bytes) -> dict:
        if isinstance(serial_number, str):
            serial_number = serial_number.encode()
        
        # Проверка формата серийного номера
        try:
            serial_str = serial_number.decode()
            if not re.match(r'^[a-fA-F0-9]+$', serial_str):
                raise ValueError("Invalid serial number format")
        except UnicodeDecodeError:
            pass  # Если не декодируется как UTF-8, пропускаем проверку

        fields = {
            0x01: "version",
            0x02: "issuer",
            0x03: "alg_id",
            0x04: "thisUpdate",
            0x05: "revoked",
            0x06: "signature"
        }
        parsed = {v: None for v in fields.values()}
        
        # Парсим CRL
        for tag, val in Utils.unpack_blocks_safe(crl):
            key = fields.get(tag)
            if key:
                parsed[key] = val
        
        # Валидация issuer
        if parsed["issuer"]:
            Certificates._validate_utf8(parsed["issuer"], "issuer")
        
        alg_id = int.from_bytes(parsed["alg_id"], "big")

        # Восстанавливаем TBS часть
        tbs = Utils.pack_blocks(
            (0x01, parsed["version"]),
            (0x02, parsed["issuer"]),
            (0x03, parsed["thisUpdate"]),
            (0x04, parsed["revoked"])
        )

        # Проверяем подпись
        _, alg_class = SignatureAlgorithms().get_by_id(alg_id)
        if not alg_class.verify(tbs, parsed["signature"], public_key):
            raise ValueError("Invalid CRL signature")

        # Ищем серийный номер
        revoked_data = parsed["revoked"]
        for _, cert_block in Utils.unpack_blocks_safe(revoked_data):
            cert_info = {}
            for tag, val in Utils.unpack_blocks_safe(cert_block):
                if tag == 0x10:
                    cert_info['serial'] = val
                elif tag == 0x11:
                    cert_info['timestamp'] = int.from_bytes(val, "big")
                elif tag == 0x12:
                    cert_info['reason'] = val
            
            if cert_info.get('serial') == serial_number:
                return {
                    "revoked": True,
                    'timeset': cert_info['timestamp'],
                    'reason': cert_info.get('reason', b'').decode()
                }
        
        return {
            "revoked": False,
            "timeset": 0,
            "reason": ""
        }
    
    
class OCSP:
    class server:
        def __init__(self):
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._is_running = False
            self.logger = Micro_Logger("OCSP_Server")
            self.version = stpc.stpc.__version__.encode()
            self.client_socket: socket.socket = None
            self.time_normal = Time()  # safer as instance
            self._ = self.time_normal.get_time()

        def start(self, CRL_List: bytes, RootCA_private_key: bytes, RootCA_public_key, server_port: int, alg_id: int):
            """Start the OCSP server."""
            self._is_running = True
            _, self.alg_class = SignatureAlgorithms().get_by_id(alg_id)

            # Socket options for low latency
            try:
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.logger.info("SO_REUSEADDR enabled")
            except OSError:
                self.logger.warning("Failed to enable SO_REUSEADDR")

            try:
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.logger.info("TCP KeepAlive enabled")
            except OSError:
                self.logger.warning("Failed to enable SO_KEEPALIVE")

            # Linux-specific TCP tuning (ignore if not available)
            for opt, val, setval, name in [
                (socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPIDLE', 0), 30, "TCP_KEEPIDLE"),
                (socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPINTVL', 0), 10, "TCP_KEEPINTVL"),
                (socket.IPPROTO_TCP, getattr(socket, 'TCP_KEEPCNT', 0), 3, "TCP_KEEPCNT"),
                (socket.SOL_TCP, getattr(socket, 'TCP_FASTOPEN', 0), 1, "TCP_FASTOPEN"),
                (socket.IPPROTO_TCP, getattr(socket, 'TCP_NODELAY', 0), 1, "TCP_NODELAY"),
                (socket.IPPROTO_TCP, getattr(socket, 'TCP_QUICKACK', 0), 1, "TCP_QUICKACK"),
            ]:
                try:
                    self.server_socket.setsockopt(opt, val, setval)
                    self.logger.info(f"{name} enabled")
                except OSError:
                    self.logger.warning(f"Failed to enable {name}")

            self.server_socket.bind(("0.0.0.0", server_port))
            self.logger.info(f"OCSP Server listening on 0.0.0.0:{server_port}")

            self.server_socket.listen(5)

            try:
                while self._is_running:
                    self.logger.debug("Waiting for client connections...")
                    try:
                        self.client_socket, addr = self.server_socket.accept()
                        self.logger.info(f"New connection from: {addr}")
                    except OSError:
                        if not self._is_running:
                            break
                        raise

                    try:
                        data = self.client_socket.recv(32768)
                        if not data:
                            self.logger.warning("Empty request received, closing connection.")
                            self.client_socket.close()
                            continue

                        self.logger.debug(f"Received {len(data)} bytes from client")

                        # Parse incoming request (version, serial_number, timeset)
                        fields = {0x01: "version", 0x02: "serial_number", 0x03: "timeset"}
                        fields_parsed = {}

                        for tag, val in Utils.unpack_blocks_safe(data):
                            key = fields.get(tag, f"UNKNOWN_{tag:02X}")
                            if tag == 0x03:
                                fields_parsed[key] = int.from_bytes(val, byteorder="big")
                            else:
                                try:
                                    fields_parsed[key] = val.decode('utf-8')
                                except UnicodeDecodeError:
                                    fields_parsed[key] = val.hex()
                        
                        # Проверка формата серийного номера
                        if not re.match(r'^[a-fA-F0-9]+$', fields_parsed["serial_number"]):
                            self.logger.warning(f"Invalid serial number format: {fields_parsed['serial_number']}")
                            self.client_socket.close()
                            continue
                            
                        # Логируем только хэш серийного номера
                        if "serial_number" in fields_parsed:
                            self.logger.debug(f"Parsed serial_number (hash): {hashlib.sha256(str(fields_parsed['serial_number']).encode()).hexdigest()[:8]}")
                        else:
                            self.logger.debug(f"Parsed fields: {fields_parsed}")

                        now = self.time_normal.get_time()
                        if not (now - 5 <= fields_parsed["timeset"] <= now + 5):
                            self.logger.critical("Invalid timeset in request! Possible replay attack.")
                            self.client_socket.close()
                            continue

                        self.logger.debug("Timeset is valid, checking certificate status in CRL...")

                        status = CRL.check_SN(CRL_List, fields_parsed["serial_number"], RootCA_public_key)

                        if status["revoked"]:
                            timestamp = int(status["timeset"]).to_bytes(8, "big")
                            reason = status["reason"].encode()
                            self.logger.warning(f"Certificate with serial (hash): {hashlib.sha256(str(fields_parsed['serial_number']).encode()).hexdigest()[:8]} is REVOKED")
                        else:
                            timestamp = (0).to_bytes(8, "big")
                            reason = b""
                            self.logger.info(f"Certificate with serial (hash): {hashlib.sha256(str(fields_parsed['serial_number']).encode()).hexdigest()[:8]} is GOOD")

                        # Build signed response
                        data = Utils.pack_blocks(
                            (0x01, self.version),
                            (0x02, alg_id.to_bytes(8, "big")),
                            (0x03, fields_parsed["serial_number"].encode()),
                            (0x04, timestamp),
                            (0x05, reason),
                            (0x06, int(self.time_normal.get_time()).to_bytes(8, "big"))
                        )
                        signature = self.alg_class.sign(data, RootCA_private_key)

                        super_data = Utils.pack_blocks(
                            (0x01, data),
                            (0x02, signature),
                            (0x03, int(self.time_normal.get_time()).to_bytes(8, "big"))
                        )

                        self.client_socket.sendall(super_data)
                        self.logger.info(f"Sent {len(super_data)} bytes to client and closed connection.")

                    except Exception as e:
                        self.logger.error(f"Error processing client request: {e}")
                    finally:
                        try:
                            self.client_socket.close()
                        except Exception:
                            pass

            except KeyboardInterrupt:
                self.logger.critical("Server stopped by KeyboardInterrupt.")
            except Exception as e:
                self.logger.critical(f"Server error: {e}")
            finally:
                self.close()

        def close(self):
            """Stops the server and closes all sockets."""
            self._is_running = False
            try:
                if self.client_socket:
                    self.client_socket.close()
            except Exception:
                pass
            try:
                # Добавляем shutdown перед close для корректного закрытия сокета
                self.server_socket.shutdown(socket.SHUT_RDWR)
                self.server_socket.close()
            except Exception:
                pass
            self.logger.info("OCSP server stopped.")


    class client:
        def _parse_response(self, response_data: bytes) -> dict:
            """Parse OCSP response bytes and return status dict (used in tests)."""
            fields = {0x01: "data", 0x02: "signature", 0x03: "timeset"}
            parsed = {fields.get(tag, f"UNKNOWN_{tag:02X}"): val
                      for tag, val in Utils.unpack_blocks_safe(response_data)}

            inner_fields = {
                0x01: "version",
                0x02: "alg_id",
                0x03: "serial_number",
                0x04: "timestamp",
                0x05: "reason",
                0x06: "timeset"
            }
            inner_parsed = {inner_fields.get(tag, f"UNKNOWN_{tag:02X}"): val
                            for tag, val in Utils.unpack_blocks_safe(parsed["data"])}

            serial_number = inner_parsed["serial_number"].decode()
            revoked = int.from_bytes(inner_parsed["timestamp"], "big") != 0
            timestamp = int.from_bytes(inner_parsed["timestamp"], "big")
            reason = inner_parsed["reason"].decode() if inner_parsed["reason"] else ""

            return {
                "status": "revoked" if revoked else "good",
                "serial_number": serial_number,
                "revoked": revoked,
                "timestamp": timestamp,
                "reason": reason
            }
        def _prepare_request(self, serial_number: str) -> bytes:
            """Сформировать TLV-запрос для OCSP (используется в тестах)."""
            return Utils.pack_blocks(
                (0x01, stpc.stpc.__version__.encode()),
                (0x02, serial_number.encode()),
                (0x03, int(self.time_sync.get_time()).to_bytes(8, 'big'))
            )
        def __init__(self, server_host: str, server_port: int, root_ca_pubkey: bytes, alg_id: int):
            self.host = server_host
            self.port = server_port
            self.logger = Micro_Logger("OCSP_Client")
            self.time_sync = Time()
            self.alg_id = alg_id
            _, self.alg_class = SignatureAlgorithms().get_by_id(alg_id)
            self.root_ca_pubkey = root_ca_pubkey

        def check_certificate(self, serial_number: str) -> dict:
            """Send OCSP request and verify the signed response."""
            # Проверка формата серийного номера перед отправкой
            if not re.match(r'^[a-fA-F0-9]+$', serial_number):
                self.logger.error("Invalid serial number format")
                return {"status": "error", "reason": "invalid serial number format"}

            self.logger.info(f"Connecting to OCSP server {self.host}:{self.port} for serial {hashlib.sha256(serial_number.encode()).hexdigest()[:8]}")

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Low-latency socket options like server
            for opt, val, setval, name in [
                (socket.IPPROTO_TCP, getattr(socket, 'TCP_NODELAY', 0), 1, "TCP_NODELAY"),
                (socket.SOL_TCP, getattr(socket, 'TCP_FASTOPEN', 0), 1, "TCP_FASTOPEN"),
            ]:
                try:
                    sock.setsockopt(opt, val, setval)
                    self.logger.debug(f"{name} enabled on client")
                except OSError:
                    self.logger.warning(f"Failed to enable {name} on client")

            try:
                sock.connect((self.host, self.port))
                self.logger.info("Connected to OCSP server.")

                # Build TLV request
                request_data = Utils.pack_blocks(
                    (0x01, stpc.stpc.__version__.encode()),
                    (0x02, serial_number.encode()),
                    (0x03, int(self.time_sync.get_time()).to_bytes(8, 'big'))
                )
                sock.sendall(request_data)
                self.logger.debug(f"Sent {len(request_data)} bytes request to server.")

                # Receive response
                response_data = sock.recv(32768)
                if not response_data:
                    self.logger.error("Empty response from OCSP server.")
                    return {"status": "error", "reason": "empty response"}

                self.logger.info(f"Received {len(response_data)} bytes from server.")

                # Parse response
                fields = {0x01: "data", 0x02: "signature", 0x03: "timeset"}
                parsed = {fields.get(tag, f"UNKNOWN_{tag:02X}"): val
                          for tag, val in Utils.unpack_blocks_safe(response_data)}

                inner_fields = {
                    0x01: "version",
                    0x02: "alg_id",
                    0x03: "serial_number",
                    0x04: "timestamp",
                    0x05: "reason",
                    0x06: "timeset"
                }
                inner_parsed = {inner_fields.get(tag, f"UNKNOWN_{tag:02X}"): val
                                for tag, val in Utils.unpack_blocks_safe(parsed["data"])}

                # Serial number verification
                sn_server = inner_parsed["serial_number"].decode()
                if sn_server != serial_number:
                    self.logger.critical(f"Serial mismatch! Requested {hashlib.sha256(serial_number.encode()).hexdigest()[:8]}, got {hashlib.sha256(sn_server.encode()).hexdigest()[:8]}")
                    return {"status": "error", "reason": "serial mismatch"}

                # Verify signature
                if not self.alg_class.verify(parsed["data"], parsed["signature"], self.root_ca_pubkey):
                    self.logger.critical("Invalid signature from OCSP server!")
                    return {"status": "error", "reason": "invalid signature"}

                # Replay-attack protection: check timeset in response
                now = self.time_sync.get_time()
                server_time = int.from_bytes(inner_parsed["timeset"], "big")
                if not (now - 5 <= server_time <= now + 5):
                    self.logger.critical(f"Invalid timeset in OCSP response! now={now}, server_time={server_time}")
                    return {"status": "error", "reason": "invalid timestamp"}

                self.logger.info("OCSP response signature is valid.")

                # Interpret status
                revoked = int.from_bytes(inner_parsed["timestamp"], "big") != 0
                timestamp = int.from_bytes(inner_parsed["timestamp"], "big")
                reason = inner_parsed["reason"].decode() if inner_parsed["reason"] else ""

                self.logger.info(f"Certificate status: {'REVOKED' if revoked else 'GOOD'}")
                if revoked:
                    self.logger.warning(f"Reason: {reason}, Time: {datetime.fromtimestamp(timestamp)}")

                return {
                    "status": "revoked" if revoked else "good",
                    "serial_number": serial_number,
                    "revoked": revoked,
                    "timestamp": timestamp,
                    "reason": reason
                }

            except Exception as e:
                self.logger.error(f"Client error: {e}")
                return {"status": "error", "reason": str(e)}

            finally:
                try:
                    sock.close()
                except Exception:
                    pass
                self.logger.debug("Client socket closed.")