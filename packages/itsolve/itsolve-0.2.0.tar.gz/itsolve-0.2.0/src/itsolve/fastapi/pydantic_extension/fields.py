from typing import Annotated

from pydantic import EmailStr, Field

EmailField = Annotated[
    EmailStr, Field(..., max_length=32, description="Email address")
]
PasswordField = Annotated[
    str, Field(..., description="Password", min_length=8)
]
TelephoneField = Annotated[
    str, Field(..., description="Phone number", examples=["375111111111"])
]

String50Field = Annotated[
    str, Field(..., description="String max length 50", max_length=50)
]
