# Websocket message flows

## Initial connection:

S: authentication-required

## Client authentication successful

S: authentication-required
C: authenticate
S: authenticated

## Client authentication unsuccessful

S: authentication-required
C: authenticate
S: authentication-failed
