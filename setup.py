import setuptools



setuptools.setup(

     name='datetimeeventstore',  

     version='0.2',

     author="Nacer Soualmi",

     author_email="nacer.soualmi@gmail.com",

     description="An implementation of an time event store in Python",

     long_description="An implementation of an time event store in Python",

   long_description_content_type="text/markdown",

   install_requires=['pymongo'],

     url="https://github.com/cereddy/time-event-store",

     packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: MIT License",

         "Operating System :: OS Independent",

     ],

 )