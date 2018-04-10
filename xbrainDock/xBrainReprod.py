from intern.resource import Resource
from io import BytesIO
from subprocess import call
import numpy as np
import requests
import json
import ast

call(["mkdir", "xbrainReprod"])
call([""])
call(["docker", "pull", "flyem/dvid"])
call(["docker", "run", "-v", imagePath + ":/dataLoad/", "--name", repoName, "-d", "flyem/dvid"])
print("Running your container...")
call(["docker", "run", "--volumes-from", repoName, "-p", port + ":" + port, "--name", portName, "-t", "flyem/dvid"])
