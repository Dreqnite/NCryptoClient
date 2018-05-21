from cx_Freeze import setup, Executable

build_exe_options = {'excludes': ['Config']}
setup(
    name='NCryptoClient',
    version='0.5.2',
    description='A client-side application of the NCryptoChat',
    options={
        'build_exe': build_exe_options
    },
    executables=[Executable('NCryptoClient\\launcher.py')]
)