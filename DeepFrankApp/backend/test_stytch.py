#!/usr/bin/env python3
"""Test script to diagnose Stytch connection issues"""
import sys
import traceback
from services.auth_service import AuthService

try:
    print("Initializing AuthService...")
    service = AuthService()
    print("AuthService initialized successfully")
    
    print("\nAttempting to send magic link...")
    result = service.send_magic_link('test@example.com')
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

