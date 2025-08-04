from stpc import stpc
from stpc.main import RootCertificates, Certificates, CRL, CRLRevokedError
from stpc.time_sync import Time

time_agent = Time()
_ = time_agent.get_time()

private_key_root, public_key_root = stpc.Ed25519.generate_keypair()

private_key_server, public_key_server = stpc.Ed25519.generate_keypair()

ROOT_CERT = RootCertificates.generate_cert(
    0x02,
    b"STP_Root_CA",
    b"Konstantin",
    b"Gorshkov",
    b"Crypto",
    b"STP Foundation",
    b"Moscow",
    b"RU",
    public_key_root,
    3600 * 24 * 365.25 * 10, # 10 years
    private_key_root,
)

PARSED_ROOT_CERT = RootCertificates.parse_cert(ROOT_CERT)
PEM = RootCertificates.serialize_cert(ROOT_CERT)

print("="*50, "ROOT CERT", "="*50)
print(ROOT_CERT)
print("\n")
print(PEM)
print("\n")
print(PARSED_ROOT_CERT)




server_cert = Certificates.generate_cert(
    0x02,
    b"Delevopment",
    b"localhost",
    b"Konstantin",
    b"Gorshkov",
    b"Crypto",
    b"STP Foundation",
    b"Moscow",
    b"RU",
    public_key_server,
    3600,
    private_key_root
)

parsed_server_cert = Certificates.parse_cert(server_cert, public_key_root)
pem = Certificates.serialize_cert(server_cert)

print("="*50, "SERVER CERT", "="*50)
print(server_cert)
print("\n")
print(pem)
print("\n")
print(parsed_server_cert)



crl_list = CRL.generate_CRL(
    [
        (parsed_server_cert["subject"]["Serial_Number"].encode(), int(time_agent.get_time()).to_bytes(8, "big"), b"test")
    ],
    b"Delevopment",
    private_key_root,
    0x02
)


checked_crl = CRL.check_SN(crl_list, parsed_server_cert["subject"]["Serial_Number"].encode(), public_key_root)
pem = CRL.serialize_CRL(crl_list)

print("="*50, "CRL LIST", "="*50)
print(crl_list)
print("\n")
print(pem)
print("\n")
print(checked_crl)

try:
    Certificates.parse_cert(server_cert, public_key_root, crl_list)
except CRLRevokedError:
    print("REVOKED")
    pass



from stpc import stpc
from stpc.main import RootCertificates, Certificates, CRL, OCSP, Utils
from stpc.time_sync import Time
import time
import threading

# Initialize time and keys
time_agent = Time()
_ = time_agent.get_time()

# Generate root CA keys
private_key_root, public_key_root = stpc.Ed25519.generate_keypair()

# Generate server keys
private_key_server, public_key_server = stpc.Ed25519.generate_keypair()

# Generate OCSP responder keys
private_key_ocsp, public_key_ocsp = stpc.Ed25519.generate_keypair()

# Create root certificate
ROOT_CERT = RootCertificates.generate_cert(
    0x02,  # Ed25519
    b"STP_Root_CA",
    b"Konstantin",
    b"Gorshkov",
    b"Crypto",
    b"STP Foundation",
    b"Moscow",
    b"RU",
    public_key_root,
    3600 * 24 * 365.25 * 10,  # 10 years
    private_key_root,
)

# Create server certificate
server_cert = Certificates.generate_cert(
    0x02,  # Ed25519
    b"STP_Root_CA",
    b"localhost",
    b"Konstantin",
    b"Gorshkov",
    b"Crypto",
    b"STP Foundation",
    b"Moscow",
    b"RU",
    public_key_server,
    3600,  # 1 hour
    private_key_root
)

# Parse server cert to get serial number
parsed_server_cert = Certificates.parse_cert(server_cert, public_key_root)
server_serial = parsed_server_cert["subject"]["Serial_Number"]

# Create CRL with server certificate revoked
crl_list = CRL.generate_CRL(
    [
        (server_serial.encode(), 
         int(time_agent.get_time()).to_bytes(8, "big"), 
         b"Testing revocation")
    ],
    b"STP_Root_CA",
    private_key_root,
    0x02  # Ed25519
)

# =============================================
# OCSP Server Tests
# =============================================

def test_ocsp_server():
    print("="*50, "OCSP SERVER TEST", "="*50)
    
    # Start OCSP server in a separate thread
    ocsp_server = OCSP.server()
    server_thread = threading.Thread(
        target=ocsp_server.start,
        args=(crl_list, private_key_root, public_key_root, 8080, 0x02),
        daemon=True
    )
    server_thread.start()
    
    # Give server time to start
    time.sleep(1)
    
    try:
        # Test with good certificate (not in CRL)
        good_serial = "1234567890abcdef"
        
        # Test with revoked certificate (server cert)
        revoked_serial = server_serial
        
        # Create OCSP client
        ocsp_client = OCSP.client("localhost", 8080, public_key_root, 0x02)
        
        # Test good certificate
        print("\nTesting GOOD certificate:")
        result = ocsp_client.check_certificate(good_serial)
        print(result)
        assert result["status"] == "good", "Good certificate check failed"
        assert not result["revoked"], "Good certificate reported as revoked"
        
        # Test revoked certificate
        print("\nTesting REVOKED certificate:")
        result = ocsp_client.check_certificate(revoked_serial)
        print(result)
        assert result["status"] == "revoked", "Revoked certificate check failed"
        assert result["revoked"], "Revoked certificate not detected"
        assert "Testing revocation" in result["reason"], "Revocation reason not matched"
        
        # Test error cases
        print("\nTesting error cases:")
        
        # Test with invalid server
        bad_client = OCSP.client("localhost", 9999, public_key_root, 0x02)
        result = bad_client.check_certificate(good_serial)
        print("Invalid port test:", result)
        assert result["status"] == "error", "Invalid port test failed"
        
        # Test with invalid serial format (не hex-строка)
        result = ocsp_client.check_certificate("not_a_hex_string!@#")
        print("Invalid serial test:", result)
        assert result["status"] == "error", "Invalid serial test failed"
        
        print("\nOCSP server tests passed successfully!")
        
    finally:
        # Clean up
        ocsp_server.close()
        server_thread.join(timeout=1)

# =============================================
# OCSP Client Tests
# =============================================

def test_ocsp_client():
    print("="*50, "OCSP CLIENT TEST", "="*50)
    
    # Create test client
    client = OCSP.client("localhost", 8080, public_key_root, 0x02)
    
    # Test request generation
    print("\nTesting request generation:")
    serial = "test123456789"
    request = client._prepare_request(serial)
    print(f"Request for serial {serial}: {request.hex()}")
    assert len(request) > 0, "Empty request generated"
    
    # Test response parsing
    print("\nTesting response parsing:")
    
    # Create a mock good response
    mock_good_data = Utils.pack_blocks(
        (0x01, stpc.__version__.encode()),
        (0x02, (0x02).to_bytes(8, "big")),  # Ed25519
        (0x03, serial.encode()),
        (0x04, (0).to_bytes(8, "big")),  # Not revoked
        (0x05, b""),  # No reason
        (0x06, int(time_agent.get_time()).to_bytes(8, "big"))
    )
    mock_good_sig = stpc.Ed25519.sign(mock_good_data, private_key_root)
    mock_good_response = Utils.pack_blocks(
        (0x01, mock_good_data),
        (0x02, mock_good_sig),
        (0x03, int(time_agent.get_time()).to_bytes(8, "big"))
    )
    
    # Parse the mock response
    result = client._parse_response(mock_good_response)
    print("Good response parse result:", result)
    assert result["status"] == "good", "Good response parsing failed"
    assert result["serial_number"] == serial, "Serial number mismatch in good response"
    
    # Create a mock revoked response
    revoke_time = int(time_agent.get_time())
    mock_revoked_data = Utils.pack_blocks(
        (0x01, stpc.__version__.encode()),
        (0x02, (0x02).to_bytes(8, "big")),  # Ed25519
        (0x03, serial.encode()),
        (0x04, revoke_time.to_bytes(8, "big")),  # Revoked
        (0x05, b"Test revocation"),  # Reason
        (0x06, int(time_agent.get_time()).to_bytes(8, "big"))
    )
    mock_revoked_sig = stpc.Ed25519.sign(mock_revoked_data, private_key_root)
    mock_revoked_response = Utils.pack_blocks(
        (0x01, mock_revoked_data),
        (0x02, mock_revoked_sig),
        (0x03, int(time_agent.get_time()).to_bytes(8, "big"))
    )
    
    # Parse the mock revoked response
    result = client._parse_response(mock_revoked_response)
    print("Revoked response parse result:", result)
    assert result["status"] == "revoked", "Revoked response parsing failed"
    assert result["timestamp"] == revoke_time, "Revocation time mismatch"
    assert "Test revocation" in result["reason"], "Revocation reason mismatch"
    
    print("\nOCSP client tests passed successfully!")

# =============================================
# Run all tests
# =============================================

import timeit

def benchmark():
    print("\n" + "="*50, "BENCHMARKS", "="*50)

    # 1. Генерация ключей
    t1 = timeit.timeit(lambda: stpc.Ed25519.generate_keypair(), number=100)
    print(f"Ed25519 keypair generation: {t1/100:.6f} sec per keypair (~{100/t1:.1f} ops/sec)")

    # 2. Генерация сертификата
    def gen_cert():
        priv, pub = stpc.Ed25519.generate_keypair()
        Certificates.generate_cert(
            0x02,
            b"STP_Root_CA",
            b"localhost",
            b"Konstantin",
            b"Gorshkov",
            b"Crypto",
            b"STP Foundation",
            b"Moscow",
            b"RU",
            pub,
            3600,
            private_key_root
        )
    t2 = timeit.timeit(gen_cert, number=100)
    print(f"Server cert generation: {t2/100:.6f} sec per cert (~{100/t2:.1f} certs/sec)")

    # 3. CRL проверка
    serial = parsed_server_cert["subject"]["Serial_Number"].encode()
    t3 = timeit.timeit(lambda: CRL.check_SN(crl_list, serial, public_key_root), number=1000)
    print(f"CRL check: {t3/1000:.6f} sec per check (~{1000/t3:.1f} checks/sec)")

    # 4. OCSP round-trip (локально, через TCP)
    ocsp_client = OCSP.client("localhost", 8080, public_key_root, 0x02)
    start = time.perf_counter()
    for _ in range(5):
        ocsp_client.check_certificate(server_serial)
    end = time.perf_counter()
    dur = end - start
    print(f"OCSP check: {dur/100:.6f} sec per query (~{100/dur:.1f} req/sec)")

if __name__ == "__main__":
    test_ocsp_server()
    test_ocsp_client()
    benchmark()
    print("\nAll OCSP tests completed successfully!")
