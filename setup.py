from setuptools import setup

setup(
   name='Golrang',
   version='2.1',
   description='A foxy module',
   author='Ali Ashja',
   author_email='AliAshja@Gmail.com',
   packages=['Golrang'],  #same as name
   install_requires=['wheel', 'bar', 'greek'], #external packages as dependencies
   # scripts=[]
)
