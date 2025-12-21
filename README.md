carsdedo backend scaffold
-------------------------
- Mobile number + OTP login (no real SMS gateway in this scaffold; prints OTP to logs)
- JWT authentication via simplejwt
- Models: User (custom), Car, Wishlist, Booking, VisitedCar, AppliedFilter
- Docker + Postgres setup

Quickstart:
1. Copy .env.example -> .env and set values
2. docker compose up --build
3. Create cars via admin or API (admin at /admin)
4. Request OTP and verify to obtain JWT tokens
