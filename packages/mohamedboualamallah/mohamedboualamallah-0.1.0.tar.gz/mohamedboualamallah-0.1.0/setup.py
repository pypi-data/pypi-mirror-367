from setuptools import setup, find_packages

setup(
    name='mohamedboualamallah',  # New package name for PyPI
    version='0.1.0',
    author='Mohamed Boualamallah',
    author_email='mohamedboualamallah@icloud.com',
    description='A modular application for audio processing and Finch robot control.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    namespace_packages=["mohamedboualamallah"],  # Enables the namespace package
    install_requires=[
        'sounddevice',
        'numpy',
        'webrtcvad',
        'scipy',
        'gradio-client',
        'google-genai',
        'playsound',
        'birdbrain-python-library',
        'Pillow'
    ],
    entry_points={
        'console_scripts': [
            'fiji_ai=mohamedboualamallah.fiji_ai.main:main',
        ],
    },
)