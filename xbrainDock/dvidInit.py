#This path leads to where your data is stored.
imagePath = "./publicData/proj4"

call(["docker", "pull", "flyem/dvid"])
call(["docker", "run", "-v", imagePath + ":/dataLoad/", "/var/run/docker.sock:/var/run/docker.sock" ,"--name", "xbrain_repr", "-d", "flyem/dvid"])
print("Running your container...")
call(["docker", "run", "--volumes-from", "xbrain_repr", "-p", "8000" + ":" + "8000", "--name", "xbrain_port1", "-t", "flyem/dvid"])
