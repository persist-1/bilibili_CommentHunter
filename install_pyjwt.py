import subprocess
import sys

print('Installing PyJWT...')
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'PyJWT'])

print('\nChecking PyJWT installation...')
try:
    import jwt
    print('PyJWT version:', getattr(jwt, '__version__', 'unknown'))
    print('Has encode:', hasattr(jwt, 'encode'))
    print('Has decode:', hasattr(jwt, 'decode'))
    print('Module type:', type(jwt))
    print('Module path:', jwt.__file__)
except Exception as e:
    print('Error:', e)