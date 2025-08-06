# from setuptools import setup, find_packages

# setup(
#     name="auth_api",
#     version="0.1.1",
#     packages=find_packages(),
#     install_requires=[
#         "fastapi",
#         "python-jose[cryptography]",
#     ],
#     author="Sajjad",
#     description="Reusable FastAPI Auth component",
# )



from setuptools import setup, find_packages

setup(
    name='auth_api_intra',       # Must be unique on PyPI
    version='0.1.0',                 # Increment this for each update
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "python-jose[cryptography]",
    ],
    author='Sajjad',
    author_email='syedsajjadali258@gmail.com',
    description='Reusable Auth API logic component',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Intra-preneur/monorepo',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.9',
)
