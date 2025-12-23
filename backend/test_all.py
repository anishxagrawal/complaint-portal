#!/usr/bin/env python
"""
Test All Authentication System
Run from backend/ directory: python test_all.py
"""

import sys
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test(name):
    """Decorator to mark test functions"""
    def decorator(func):
        def wrapper():
            print(f"\n{BLUE}{'='*60}{RESET}")
            print(f"{BLUE}TEST: {name}{RESET}")
            print(f"{BLUE}{'='*60}{RESET}")
            try:
                func()
                print(f"{GREEN}✓ PASSED{RESET}")
                return True
            except Exception as e:
                print(f"{RED}✗ FAILED: {str(e)}{RESET}")
                return False
        return wrapper
    return decorator


@test("1. Import Config")
def test_config():
    from app.core.config import settings
    print(f"  SECRET_KEY: {settings.SECRET_KEY[:20]}...")
    print(f"  ALGORITHM: {settings.ALGORITHM}")
    print(f"  OTP_EXPIRE_MINUTES: {settings.OTP_EXPIRE_MINUTES}")
    print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")


@test("2. Import Security Functions")
def test_security():
    from app.core.security import (
        create_access_token,
        verify_token,
        hash_password,
        verify_password,
        generate_otp_secret,
        verify_otp,
        get_otp_code
    )
    print("  ✓ create_access_token")
    print("  ✓ verify_token")
    print("  ✓ hash_password")
    print("  ✓ verify_password")
    print("  ✓ generate_otp_secret")
    print("  ✓ verify_otp")
    print("  ✓ get_otp_code")


@test("3. Import Schemas")
def test_schemas():
    from app.schemas.auth import (
        SendOTPRequest,
        SendOTPResponse,
        VerifyOTPRequest,
        VerifyOTPResponse,
        Token,
        TokenPayload
    )
    print("  ✓ SendOTPRequest")
    print("  ✓ SendOTPResponse")
    print("  ✓ VerifyOTPRequest")
    print("  ✓ VerifyOTPResponse")
    print("  ✓ Token")
    print("  ✓ TokenPayload")


@test("4. Import Auth Service")
def test_auth_service():
    from app.services.auth_service import auth_service, OTPNotSentError, InvalidOTPError, AccountLockedError
    print("  ✓ auth_service")
    print("  ✓ OTPNotSentError")
    print("  ✓ InvalidOTPError")
    print("  ✓ AccountLockedError")


@test("5. Import Auth Router")
def test_auth_router():
    from app.routers.auth import router
    print("  ✓ auth router loaded")
    print(f"  Routes: {len(router.routes)} endpoints")


@test("6. Import Dependencies")
def test_deps():
    from app.deps import get_current_user, security
    print("  ✓ get_current_user")
    print("  ✓ security (HTTPBearer)")


@test("7. Import Database")
def test_database():
    from app.database import SessionLocal, get_db
    db = SessionLocal()
    print("  ✓ Database connection established")
    db.close()


@test("8. Import Models")
def test_models():
    from app.models.users import User
    print("  ✓ User model")


@test("9. Full App Import")
def test_full_app():
    from app.main import app
    print("  ✓ FastAPI app loaded")
    print(f"  Title: {app.title}")
    print(f"  Routes: {len(app.routes)} endpoints")


@test("10. Create/Verify Test User")
def test_create_user():
    from app.database import SessionLocal
    from app.models.users import User
    
    db = SessionLocal()
    user = db.query(User).filter(User.phone_number == '+919876543210').first()
    
    if user:
        print(f"  ✓ Test user exists (ID: {user.id})")
    else:
        user = User(
            phone_number='+919876543210',
            full_name='Test User',
            email='test@example.com',
            residential_address='Test Address'
        )
        db.add(user)
        db.commit()
        print(f"  ✓ Test user created (ID: {user.id})")
    
    db.close()


@test("11. Test Token Creation & Verification")
def test_token_flow():
    from app.core.security import create_access_token, verify_token
    
    # Create token
    token = create_access_token({"user_id": 1})
    print(f"  ✓ Token created: {token[:50]}...")
    
    # Verify token
    payload = verify_token(token)
    print(f"  ✓ Token verified")
    print(f"  User ID in token: {payload.get('user_id')}")
    print(f"  Expiration: {payload.get('exp')}")


@test("12. Test OTP Generation & Verification")
def test_otp_flow():
    from app.core.security import generate_otp_secret, verify_otp, get_otp_code
    
    # Generate secret
    secret = generate_otp_secret()
    print(f"  ✓ OTP secret generated: {secret[:10]}...")
    
    # Get current OTP code
    otp_code = get_otp_code(secret)
    print(f"  ✓ OTP code: {otp_code}")
    
    # Verify OTP code
    is_valid = verify_otp(secret, otp_code)
    print(f"  ✓ OTP verified: {is_valid}")


@test("13. Test Send OTP Service")
def test_send_otp_service():
    from app.database import SessionLocal
    from app.services.auth_service import auth_service
    
    db = SessionLocal()
    result = auth_service.send_otp(db, '+919876543210')
    print(f"  ✓ OTP sent: {result['message']}")
    db.close()


@test("14. Test Verify OTP Service")
def test_verify_otp_service():
    from app.database import SessionLocal
    from app.services.auth_service import auth_service
    from app.core.security import get_otp_code
    from app.models.users import User
    
    db = SessionLocal()
    
    # First send OTP
    auth_service.send_otp(db, '+919876543210')
    
    # Get OTP code
    user = db.query(User).filter(User.phone_number == '+919876543210').first()
    otp_code = get_otp_code(user.otp_secret)
    
    # Verify OTP
    result = auth_service.verify_otp(db, '+919876543210', otp_code)
    print(f"  ✓ OTP verified")
    print(f"  Access token: {result['access_token'][:50]}...")
    print(f"  Token type: {result['token_type']}")
    
    db.close()


@test("15. Test Pydantic Schemas")
def test_pydantic_schemas():
    from app.schemas.auth import SendOTPRequest, VerifyOTPRequest
    
    # Test valid data
    send_otp = SendOTPRequest(phone_number="+919876543210")
    print(f"  ✓ SendOTPRequest validation passed")
    print(f"    Phone: {send_otp.phone_number}")
    
    # Test OTP request
    verify_otp = VerifyOTPRequest(phone_number="+919876543210", otp_code="123456")
    print(f"  ✓ VerifyOTPRequest validation passed")
    print(f"    Phone: {verify_otp.phone_number}, OTP: {verify_otp.otp_code}")


def main():
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}AUTHENTICATION SYSTEM - COMPREHENSIVE TEST{RESET}")
    print(f"{YELLOW}Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    
    tests = [
        test_config(),
        test_security(),
        test_schemas(),
        test_auth_service(),
        test_auth_router(),
        test_deps(),
        test_database(),
        test_models(),
        test_full_app(),
        test_create_user(),
        test_token_flow(),
        test_otp_flow(),
        test_send_otp_service(),
        test_verify_otp_service(),
        test_pydantic_schemas(),
    ]
    
    passed = sum(1 for t in tests if t)
    total = len(tests)
    
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}TEST SUMMARY{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"Total Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {total - passed}{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{'✓'*30}{RESET}")
        print(f"{GREEN}ALL TESTS PASSED! System is ready.{RESET}")
        print(f"{GREEN}{'✓'*30}{RESET}")
        print(f"\n{BLUE}Next step: Run the server{RESET}")
        print(f"{BLUE}uvicorn app.main:app --reload{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'✗'*30}{RESET}")
        print(f"{RED}SOME TESTS FAILED! Fix errors before running server.{RESET}")
        print(f"{RED}{'✗'*30}\n{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())