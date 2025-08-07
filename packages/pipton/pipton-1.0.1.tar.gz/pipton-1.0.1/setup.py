from setuptools import setup

setup(
    name='pipton',
    version='1.0.1',
    py_modules=['pipton_repl', 'run_pipton'],  # ← اضافه شد

    include_package_data=True,

    entry_points={
        'console_scripts': [
            'pipton = pipton_repl:start_repl',   # REPL اجرا
            'pipton-run = run_pipton:main',      # اجرای فایل پیتون
        ],
    },

    install_requires=[],  # اگه نیاز هست اضافه کن

    author='AmirhosseinPython',
    author_email='amirhossinpython03@gmail.com',

    description='A custom language with Persian-flavored syntax and full Python power',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',

    url='https://github.com/amirhossinpython/pipton_lang',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Intended Audience :: Developers",
        "Natural Language :: Persian",
    ],

    python_requires='>=3.6',
)
