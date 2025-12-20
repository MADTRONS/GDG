"""Tests for password hashing and verification utilities."""
import pytest

from app.utils.security import hash_password, verify_password


def test_hash_password():
    """Test that password is hashed and not reversible."""
    password = 'mypassword123'
    hashed = hash_password(password)
    
    # Hashed password should be different from plain text
    assert hashed != password
    
    # Hashed password should be a string
    assert isinstance(hashed, str)
    
    # Bcrypt hashes start with $2b$
    assert hashed.startswith('$2b$')
    
    # Hash should be consistent length (60 chars for bcrypt)
    assert len(hashed) == 60


def test_hash_password_different_salts():
    """Test that same password produces different hashes (salt is random)."""
    password = 'samepassword'
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Different hashes due to different salts
    assert hash1 != hash2
    
    # But both should verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_verify_password_correct():
    """Test correct password verification."""
    password = 'correctpassword'
    hashed = hash_password(password)
    
    # Verification should succeed
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test incorrect password is rejected."""
    password = 'correctpassword'
    wrong_password = 'wrongpassword'
    hashed = hash_password(password)
    
    # Verification should fail
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_case_sensitive():
    """Test password verification is case-sensitive."""
    password = 'MyPassword'
    hashed = hash_password(password)
    
    # Wrong case should fail
    assert verify_password('mypassword', hashed) is False
    assert verify_password('MYPASSWORD', hashed) is False
    
    # Correct case should succeed
    assert verify_password('MyPassword', hashed) is True


def test_verify_password_empty_string():
    """Test that empty password can be hashed and verified."""
    password = ''
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password('notempty', hashed) is False