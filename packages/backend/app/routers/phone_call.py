"""Phone call integration router for submitting phone numbers to external form."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional
import requests
from loguru import logger

from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/phone", tags=["phone"])


class PhoneCallRequest(BaseModel):
    """Request schema for phone call submission."""
    phone: str
    counselor: str


class PhoneCallResponse(BaseModel):
    """Response schema for phone call submission."""
    success: bool
    message: str


@router.post(
    "/submit",
    response_model=PhoneCallResponse,
    summary="Submit phone number for voice call",
    description="Forwards phone number to external form automation for voice calling.",
    status_code=status.HTTP_200_OK
)
async def submit_phone_number(
    request: PhoneCallRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Submit phone number to external form automation.
    
    This endpoint acts as a proxy to avoid CORS issues when the frontend
    tries to submit phone numbers directly to the external form service.
    
    Args:
        request: Request containing phone number and counselor name
        current_user: Authenticated user from JWT
        
    Returns:
        Success status and message
        
    Raises:
        HTTPException 500: If form submission fails
    """
    # Configure your n8n webhook URL here
    webhook_url = "http://localhost:5678/webhook-test/lead-test"
    
    # Set to False to use webhook, True to just log
    use_database_only = False
    
    if use_database_only:
        # Just log the phone submission - you can process it later
        logger.info(
            f"Phone call requested: {request.phone} for {request.counselor} "
            f"by user {current_user['email']}"
        )
        
        return PhoneCallResponse(
            success=True,
            message=f"Call request received for {request.phone}. You will be contacted shortly."
        )
    
    try:
        logger.info(f"Calling webhook for user {current_user['email']} to counselor {request.counselor}")
        
        # Send data to n8n webhook
        payload = {
            "phone": request.phone,
            "phoneNumber": request.phone,  # Alternative field name
            "counselor": request.counselor,
            "counselorName": request.counselor,  # Alternative field name
            "user_email": current_user.get("email"),
            "user_id": str(current_user.get("user_id")),
            "timestamp": None  # Will use current time
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        response.raise_for_status()
        
        logger.info(f"Webhook call successful for {request.phone}")
        
        return PhoneCallResponse(
            success=True,
            message=f"Call initiated to {request.phone}"
        )
        logger.info(f"Submitting phone number for user {current_user['email']} to counselor {request.counselor}")
        
        # Forward the request to the external form
        response = requests.post(
            form_url,
            json={
                "phone": request.phone,
                "counselor": request.counselor,
                "user_email": current_user.get("email"),
                "user_id": current_user.get("user_id")
            },
            timeout=10
        )
        
        response.raise_for_status()
        
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook call failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate call: {str(e)}"
        )
