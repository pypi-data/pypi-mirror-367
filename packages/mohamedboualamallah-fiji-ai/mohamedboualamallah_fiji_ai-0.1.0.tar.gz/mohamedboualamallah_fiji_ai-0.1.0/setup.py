from setuptools import setup, find_packages

setup(
    name='mohamedboualamallah_fiji-ai',  # changed package name
    version='0.1.0',
    author='Mohamed Boualamallah',
    author_email='mohamedboualamallah@icloud.com',
    description='A modular application for audio processing and Finch robot control.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'sounddevice',
        'numpy',
        'webrtcvad',
        'scipy',
        'gradio-client',
        'google-genai',
        'playsound',
        'BirdBrain'
    ],
    entry_points={
        'console_scripts': [
            'my_app=my_app.main:main',
        ],
    },
)