from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models, security, database
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/auth", tags=["Authentication"])


def send_reset_email(email: str, reset_token: str):
    """
    Send password reset email
    NOTE: For development, this just prints to console
    Configure SMTP for production
    """
    reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"

    # For development - print to console
    print("\n" + "=" * 50)
    print("📧 PASSWORD RESET EMAIL (Development Mode)")
    print("=" * 50)
    print(f"To: {email}")
    print(f"Reset Link: {reset_link}")
    print("=" * 50 + "\n")

    # For production, uncomment and configure SMTP:
    """
    msg = MIMEMultipart()
    msg['From'] = "noreply@yourstore.com"
    msg['To'] = email
    msg['Subject'] = "Password Reset Request"

    # body = f"""
    # Hello,
    #
    # You
    # requested
    # a
    # password
    # reset.Click
    # the
    # link
    # below
    # to
    # reset
    # your
    # password:
    #
    # {reset_link}
    #
    # This
    # link
    # expires in 1
    # hour.
    #
    # If
    # you
    # didn
    # 't request this, please ignore this email.
    #
    # Best
    # regards,
    # E - commerce
    # Team
    """

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@gmail.com', 'your_app_password')
    server.send_message(msg)
    server.quit()
    """


@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_pw,
        full_name=user.full_name,
        is_admin=user.is_admin,
        phone=user.phone,
        address=user.address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = security.create_access_token(
        data={"sub": db_user.email, "role": "admin" if db_user.is_admin else "customer"},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(database.get_db)
):
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not db_user or not security.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = "admin" if db_user.is_admin else "customer"
    access_token = security.create_access_token(
        data={"sub": db_user.email, "role": role},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
def forgot_password(
        request: schemas.ForgotPassword,
        db: Session = Depends(database.get_db)
):
    """
    Request a password reset token
    Sends reset link to user's email
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate reset token
    reset_token = security.create_reset_password_token(user.email)

    # Save token to database
    user.reset_password_token = reset_token
    user.reset_password_expires = security.datetime.utcnow() + timedelta(minutes=60)
    db.commit()

    # Send email
    send_reset_email(user.email, reset_token)

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
def reset_password(
        request: schemas.ResetPassword,
        db: Session = Depends(database.get_db)
):
    """
    Reset password using the token from email
    """
    # Validate passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Validate password strength
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    # Verify token
    email = security.verify_reset_password_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Find user
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    # Check token matches database (extra security)
    if user.reset_password_token != request.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )

    # Check token not expired
    if user.reset_password_expires and user.reset_password_expires < security.datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Update password
    user.hashed_password = security.get_password_hash(request.new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()

    return {"message": "Password has been reset successfully"}


@router.post("/logout")
def logout(current_user: models.User = Depends(security.get_current_user)):
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=schemas.UserDisplay)
def get_current_user_info(current_user: models.User = Depends(security.get_current_user)):
    """Get current authenticated user info"""
    return current_user