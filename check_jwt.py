try:
    import jwt
    print('PyJWT version:', getattr(jwt, '__version__', 'unknown'))
    print('Has encode:', hasattr(jwt, 'encode'))
    print('Has decode:', hasattr(jwt, 'decode'))
    print('Module type:', type(jwt))
    print('Module path:', jwt.__file__)
except Exception as e:
    print('Error:', e)